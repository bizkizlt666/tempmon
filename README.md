# TempMon
Temperature monitor, for Linux, with a builtin task-killer.
With a thin view, for games

How to install:

In terminal: 
>cd /YOURPATH/Homero

code:
>pip install -r requirements.txt

Start:
>python3 /YOURPATH/homero.py

################################################

You need to be installed Python 3.12.3

check:
>python3 --version

If python is not installed:
>sudo apt install python -y

#######################################################

Desktop icon:

#1)Go to yout Applications folder:
>/YOURPATH/.local/share/applications

Make a desktop file:
>nano tempmon.desktop

Paste it and save:

[Desktop Entry]
Type=Application
Name=Hőmérő
Icon=Temperature
Exec=/YOURPATH/Homero/homero.py
X-GNOME-Autostart-enabled=true

#2)Go to your desktop:
>cd /YOURDESKTOP/

Make a desktop file:
>nano tempmon.desktop

Paste it, and save:

[Desktop Entry]
Type=Application
Name=Temp Monitor
Comment=CPU and GPU temperature widget
Exec=python3 /YOURPATH/Homero/homero.py
Icon=utilities-system-monitor
Terminal=false
Categories=System;

!!!When you saved it, then right-click the file, go to Properties, 
and under the Permissions tab, check the "Allow executing file as 
program" option

YOURPATH=Change to your own destination.

