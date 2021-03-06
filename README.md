
## About

__ViewSwitcher__ is a quick little markingmenu that solves two problems:
* One-button menu for camera switching (including a custom shotCam)
* One button press to hotswitch back to the previous camera

Each viewport will remember it's last active camera and allow you to hotswitch between the two.

Huge shoutout to [Vasil Shotarov](http://bindpose.com) for writing up these awesome articles to help get me through.
* http://bindpose.com/custom-marking-menu-maya-python
* http://bindpose.com/custom-marking-menus-maya-editors
* http://bindpose.com/custom-hotkey-marking-menu-maya/

## Install
Download and put the viewSwitcher.py file in your <MY_DOCUMENTS>/maya/scripts/ folder.

## Setup
You'll need to make two hotkey commands. One for the _press_ and one for _release_.\
Open the maya hotkey editor and open the Runtime Command Editor.
Hit 'New' and give it a name like:

<b>viewSwitcher_PRESS</b>

Paste this code into the command area:
```
import viewSwitcher
viewSwitcher.press()
```
Make sure to switch the language to <b>python</b>.\
When ready, hit Save.

Hit 'New' again and this time name it:

<b>viewSwitcher_RELEASE</b>

```
viewSwitcher.release()
```
When ready, hit Save. Now assign your hotkeys.
Make sure to set the release key to the same as the press key but using the dropdown menu to set it to 'release' mode.
![hotkeyEditor](https://i.imgur.com/B5bzlYLl.png)

## Usage

Hold the hotkey you assigned and left click (and hold) in any viewport - standard markingMenu summoning procedure.\
Letting go on any box will change the current panel to look through that camera.

If you quickly tap the hotkey, it will switch to the previous camera you were looking through (in the current viewPane).

By default, the 'shotCam' will be the 'persp' camera.
As soon as you choose the optionBox next to shotCam, the current viewport camera will be assigned as the shotCam.

![hotbox](https://i.imgur.com/Vjn7LZD.png)
