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
            # print(camDag.name())
            view.setCamera(camDagPath)
            view.refresh() # Without this, nothing ever happens

    def _setupCamQueue(self):
        # Start with a working camera queue
        currentCamera = self._getCurrentCamera()
        return [currentCamera, currentCamera]

    def _cameraChangeCallback(self, panel, curCamMObj, clientDataObj):
        # curCamMObj is an mObject
        fnCam = api.MFnCamera(curCamMObj)
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
        menu = cmds.popupMenu(self.name+MENU_NAME,
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



