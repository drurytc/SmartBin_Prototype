#!/bin/bash


# Install Python dependencies.
python3 -m pip install pip --upgrade
python3 -m pip install -r requirements.txt --upgrade


#LED dependencies
#sudo apt-get install python3-dev python3-rpi.gpio
pip3 install RPi.GPIO
pip3 install gpiozero 
