# ShadowChess
![101](https://user-images.githubusercontent.com/125653767/219675648-a4f0e703-fc39-4077-9661-854d3522c01c.jpg)

## Description

This is ShadowChess, a Chess variant with a story and a different turn system.
While in chess players move one after another (first white then black then white again...) giving advantage to white, in ShadowChess the currently playing player will have the move advantage. ShadowChess naturally has a lot of systems and mechanics attached as it is an interactive story set in a fictional universe, with fictional characters, struggling for a moral lesson or at least trying to make the player reflect on it.

## Bug reporting

You can report bugs by installing all dependencies and running ShadowChess in Python or simply using the .exe provided by the Itch.io page (https://shadow9876.itch.io/shadowchess).
Either way you should mainly report bugs that can be reproduced, here below I'll list the steps of reporting bugs.
1. You encounter a bug
2. Can I reproduce it? If so, what steps are required to make this same bug happen?
3. Now open GitHub and navigate to ShadowChess, open the Issues tab and create a New issue
4. Try to explain the bug and provide as much context as you can (or think is necessary)
5. Submit your findings

(It's not a problem if you can't reproduce the bug, but in that case try to give as much context as necessary)

![100](https://user-images.githubusercontent.com/125653767/219676260-e628222c-a800-442f-8771-c44867844929.jpg)

## Prerequisites
1. Python 3.11 - https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe
2. Pip - https://pip.pypa.io/en/stable/cli/pip_download/
3. All modules included in "ShadowChess.py" - pip install \<module name\> (Some modules you'll have to install are "Cython", "numpy", "customtkinter" and "Pillow")

## How to run
1. Open "Command Prompt" and navigate to the folder called "ShadowChess" (cd \<PATH to folder\>)
2. Run the following command: "python ShadowChess.py"
  
## How to convert it into an .exe
  
Because ShadowChess uses customtkinter it's necessary to follow these steps: https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging
