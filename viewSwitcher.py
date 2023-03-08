from maya import cmds, mel
import maya.api.OpenMayaUI as mui
import maya.api.OpenMaya as api

import time

#------------------------------------------------------------------------------#
# GLOBALS
#------------------------------------------------------------------------------#

global TIME_START
global SHOT_CAM

MENU_NAME        = "ViewSwitcherMenu"
TIME_START       = 0.0
SHOT_CAM         = "persp"
CUSTOM_SHOT_CAM  = "shotCam"
CURRENT_PANEL    = ""
MM_REGISTRY      = {}

# ---------------------------------------------------------------------------- #

class ViewportMarkingMenu(object):
    def __init__(self, name):
        # Data type to hold panel and associated callbackID
        self.name = name
        self.callbackRegistry = {}
        self.toggleCamQueue = self._setupCamQueue()

        self._installCallback()

    def run(self):
        self._removeOld()
        self._build()

    def camToggle(self):
        current_panel = isPanel()
        if isPanel():
            view = mui.M3dView.getM3dViewFromModelPanel(current_panel)
            camDag = api.MFnDagNode(self.toggleCamQueue[1])
            camDagPath = camDag.getPath()
            view.setCamera(camDagPath)
            view.refresh() # Without this, nothing ever happens

    def _setupCamQueue(self):
        # Start with a working camera queue
        currentCamera = self._getCurrentCamera()
        return [currentCamera, currentCamera]

    def _cameraChangeCallback(self, panel, curCamMObj, clientDataObj):
        # curCamMObj is an mObject
        # fnCam = api.MFnCamera(curCamMObj)
        if not curCamMObj:
            curCamMObj = get_camera()
        camDag = api.MFnDagNode(curCamMObj)
        camDagPath = camDag.getPath()
        self.toggleCamQueue.pop(-1)
        self.toggleCamQueue.insert(0, camDagPath) # New method using api

    def _installCallback(self):
        currentPanel = isPanel()
        if currentPanel:
            if not currentPanel in self.callbackRegistry:
                # print("Added callback for %s" % currentPanel)
                self.callbackRegistry[currentPanel] = mui.MUiMessage.addCameraChangedCallback(currentPanel, self._cameraChangeCallback)

    def _removeCallback(self):
        # Just in case I need to reset
        for currentPanel in self.callbackRegistry:
            if self.callbackRegistry[currentPanel]:
                self.callbackRegistry[currentPanel] = mui.MUiMessage.removeCallback(self.callbackRegistry[currentPanel])

    def _removeOld(self):
        if cmds.popupMenu(self.name+MENU_NAME, ex=1):
            cmds.deleteUI(self.name+MENU_NAME)

    def _build(self):
        cmds.popupMenu(self.name+MENU_NAME,
                       markingMenu         = 1,
                       allowOptionBoxes    = 1,
                       button              = 1,
                       ctrlModifier        = 0,
                       altModifier         = 0,
                       shiftModifier       = 0,
                       parent              = "viewPanes", # This might bite me in the ass
                       postMenuCommandOnce = 1,
                       postMenuCommand     = self._buildMarkingMenu)

    def _getCurrentCamera(self):
        if isPanel():
            view = mui.M3dView.active3dView()
            cam = view.getCamera()
            camDag = api.MFnDagNode(cam)
            camDagPath = camDag.getPath()
            return camDagPath

    def _buildMarkingMenu(self, menu, parent):
        ## Radial positioned
        cmds.menuItem(p=menu, l="persp", rp="N", c=perspView)
        cmds.menuItem(p=menu, l="side", rp="E", c=sideView)
        cmds.menuItem(p=menu, l="front", rp="S", c=frontView)#, i="mayaIcon.png")
        cmds.menuItem(p=menu, l="top", rp="W", c=topView)
        cmds.menuItem(p=menu, l=CUSTOM_SHOT_CAM, rp="NW", c=camView)
        cmds.menuItem(p=menu, ob=1, c=setShotCam)
        cmds.menuItem(p=menu, l="other side", rp="NE", c=mirrorView)

        ## List
        #cmds.menuItem(p=menu, l="ackToggleCams", c=ackToggleCams)
        #cmds.menuItem(p=menu, l="Rebuild Marking Menu", c=rebuildMarkingMenu)

# ---------------------------------------------------------------------------- #

def press(*args):
    global CURRENT_PANEL
    CURRENT_PANEL = isPanel()
    if isPanel():
        # Add to the registry
        if not (CURRENT_PANEL in MM_REGISTRY):
            MM_REGISTRY[CURRENT_PANEL] = ViewportMarkingMenu(CURRENT_PANEL)
        # Deploy
        MM_REGISTRY[CURRENT_PANEL].run()

        # Start the timer
        global TIME_START
        TIME_START = time.time()

def release(*args):
    global CURRENT_PANEL
    global TIME_START
    if CURRENT_PANEL:
        if cmds.popupMenu(CURRENT_PANEL+MENU_NAME, ex=1):
            cmds.deleteUI(CURRENT_PANEL+MENU_NAME)
        if (time.time() - TIME_START) < 0.15: # Quick button press
            MM_REGISTRY[CURRENT_PANEL].camToggle()

# ---------------------------------------------------------------------------- #

def isPanel(*args):
    currentPanel = cmds.getPanel(wf=True) # Working with names is ok here
    if cmds.getPanel(to=currentPanel) == 'modelPanel':
        return currentPanel
    else:
        return False

def perspView(*args):
    if isPanel():
        cmds.lookThru('persp')

def frontView(*args):
    if isPanel():
        cmds.lookThru('front')

def sideView(*args):
    if isPanel():
        cmds.lookThru('side')

def topView(*args):
    if isPanel():
        cmds.lookThru('top')

def camView(*args):
    # global SHOT_CAM
    if not cmds.objExists(CUSTOM_SHOT_CAM):
        cmds.warning("{} does not exist!".format(CUSTOM_SHOT_CAM))
        return
    if isPanel():
        cmds.lookThru(CUSTOM_SHOT_CAM)

def setShotCam(*args):
    global CUSTOM_SHOT_CAM
    global SHOT_CAM
    if isPanel():
        SHOT_CAM = cmds.lookThru(q=True)
        CUSTOM_SHOT_CAM = SHOT_CAM

def _powerWordKILL(*args):
    # Just in case I need to reset
    for instance in MM_REGISTRY:
        MM_REGISTRY[instance]._removeCallback()

def get_camera():
    # Get current active camera via api
    camera_transform = mui.M3dView.active3dView().getCamera().transform()
    return api.MFnDagNode(camera_transform).fullPathName()

# ---------------------------------------------------------------------------- #



class Axis:
    """
    Fake enum as class with constant variable to represent the axis value that could change
    """
    kX = 'X'
    kY = 'Y'
    kZ = 'Z'
    values = [kX, kY, kZ]


def flip_matrix_axis_rot(matrix_list, axis=Axis.kX):
    """
    Utility function to mirror the x, y or z axis of an provided matrix.
    :param matrix_list: The matrix list to flip.
    :param axis: The axis to flip.
    :return: The resulting matrix list
    """

    if axis == Axis.kX:
        matrix_list[0] *= -1.0
        matrix_list[1] *= -1.0
        matrix_list[2] *= -1.0
    elif axis == Axis.kY:
        matrix_list[4] *= -1.0
        matrix_list[5] *= -1.0
        matrix_list[6] *= -1.0
    elif axis == Axis.kZ:
        matrix_list[8] *= -1.0
        matrix_list[9] *= -1.0
        matrix_list[10] *= -1.0
    else:
        raise Exception("Unsupported axis. Got {0}".format(axis))

    return matrix_list


def flip_matrix_axis_pos(matrix_list, axis=Axis.kX):

    if axis == Axis.kX:
        matrix_list[12] *= -1.0
    elif axis == Axis.kY:
        matrix_list[13] *= -1.0
    elif axis == Axis.kZ:
        matrix_list[14] *= -1.0
    else:
        raise Exception("Unsupported axis. Got {0}".format(axis))

    return matrix_list



def mirror_xform(transforms=[], pos_axis=None, rot_axis=None):
    """ Mirrors transform across hyperplane. 
    
    transforms -- list of Transform or string.
    across -- plane which to mirror across.
    behaviour -- bool 

    """  

    # No specified transforms, so will get selection
    if not transforms:
        transforms = cmds.ls(sl=1, type='transform')
    elif not isinstance(transforms, list): transforms = [transforms]
    
    # Sanitize the list
    for transform in transforms:
        if not cmds.nodeType(transform) == 'transform':
            transforms.remove(transform)

    # Validate plane which to mirror position across,
    if pos_axis:
        if not pos_axis in Axis.values: 
            raise ValueError("Keyword Argument: 'pos_axis' not of accepted type Axis.")        
        
    # Validate plane which to mirror rotation across,
    if rot_axis:
        if not rot_axis in Axis.values: 
            raise ValueError("Keyword Argument: 'rot_axis' not of accepted type Axis.")        
    
    stored_matrices = {}
    
    for transform in transforms:
    
        # Get the worldspace matrix, as a list of 16 float values
        matrix_list = cmds.xform(transform, q=True, ws=True, m=True)
        
        # Set matrix based on given plane, and whether to include behaviour or not.
        if pos_axis:
            
            matrix_list = flip_matrix_axis_pos(matrix_list, pos_axis)
            
        if rot_axis:
            
            matrix_list = flip_matrix_axis_rot(matrix_list, rot_axis)
            

        stored_matrices[transform] = matrix_list

    # Finally set matrix for transform,       
    for transform in transforms:
        
        # Locking scale axis for JUST IN CASE
        for axis in ['X','Y','Z']:
            cmds.setAttr(transform + '.scale{}'.format(axis), lock=True)
        
        # This is where the magic happens
        cmds.xform(transform, ws=True, m=stored_matrices[transform])         
        # - 
        
        # It's ugly, but I'm new to matrices and I don't know what I'm doing
        for axis in ['X','Y','Z']:
            cmds.setAttr(transform + '.scale{}'.format(axis), lock=False)


def mirrorView(*args):
    # Currently doesn't work on persp
    current_camera = get_camera()

    if "side" in current_camera:
        mirror_xform(current_camera, pos_axis=Axis.kX, rot_axis=Axis.kX)

    if "front" in current_camera:
        mirror_xform(current_camera, pos_axis=Axis.kZ, rot_axis=Axis.kX)

    if "top" in current_camera:
        mirror_xform(current_camera, rot_axis=Axis.kY) # Top
        mirror_xform(current_camera, rot_axis=Axis.kX) # Top

if __name__ == '__main__':
    # import view_switcher
    reload(view_switcher)
