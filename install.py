#!/usr/bin/env python3

import os

ONEZ_DIR  = os.path.dirname(os.path.realpath(__file__))
print("Installing Requirements ...")
os.system("apt-get -y install xdotool")
os.system("pip3 install pyperclip netifaces")
print("Copying Files ...")
os.system("cp -r %s /opt" %ONEZ_DIR)
print("Linking one-z ...")
os.system("ln -s /opt/one-z/main.py /usr/bin/one-z")
