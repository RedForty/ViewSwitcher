<<<<<<< HEAD
### mmViewSelect #
=======
# mmViewSelect #
>>>>>>> master

# To Install #

Put the mmViewSelect.py file in your <MY_DOCUMENTS>/maya/scripts/ folder.
***
**[Usage](#usage)**
---

Now you need to make two hotkey commands.
Open the maya hotkey editor and open the Runtime Command Editor.
Hit 'New' and give it a name like:
<b>mmViewSelect_PRESS</b>

Paste this code into the command area:
```
import mmViewSelect
mmViewSelect.press()
```
Make sure to switch the language to <b>python</b>.
When ready, hit Save.

Hit 'New' again and this time name it:
<b>mmViewSelect_RELEASE</b>

Paste this code into the command area:
```
mmViewSelect.release()
```
Again, make sure to switch the language to <b>python</b>.
When ready, hit Save.

---

Now assign both to the same key. One press and the other release.


