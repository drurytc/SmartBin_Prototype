
# Smart Recycling Bin - Physical Prototype

## Introduction

The Smart Recycling Bin Prototype focuses on creating a solution for recycling contamination in public spaces like parks, airports, 
and event venues. By distinguishing between recyclable and non-recyclable items, the bin aims to improve waste sorting efficiency 
and promote sustainable recycling practices. Additionally, previous capstone projects at Oregon State University have explored image
processing software models for waste sorting, providing valuable insights for this project.

## Design Process & Considerations

Building upon previous work, the project integrates image processing software with new sensors and actuators to utilize the sorting
capabilities of the past capstone's software. The design process involves developing proof of concept for each subsystem of the bin,
followed by integration into a cohesive mechanical design. Stakeholders include the project sponsor, Greg Fitzpatrick, and 
advisor, Dr. Layne Clemen, as well as the general public, institutions, and local businesses. New sensors include a motion sensor
and IR break beam sensors, which are integrated to trigger functionality within the code. The sorting mechanism is controlled by a
servo motor, with safety features such as a chute with a torsion spring door to prevent accidents. The torsion door also can be
locked when capacity is met by a latched servo motor. The design is proposed as an attachment to existing commingled recycling bins.

## Components

### Software

- **Image Classification**: Custom-trained TensorFlow Lite model
- **Decision Making**: Rule-based system for lid control
- **Maintainer Interaction**: Command line interface (CLI)
- **User Interface**: Visual LED Indicators & Physical Bin Interaction

### Hardware

- **Camera**: Arducam 4K 8MP IMX219
- **Sorting Servo Motor**: DS3235-270
- **Door Locking Servo Motor**: SG90
- **Microprocessor**: Raspberry Pi 4 B
- **Item Sensor**: PIR Motion Sensor
- **Capacity Sensor**: Break Beam
- **Capacity LED**: NeoPixel 8 Stick
- **Camera LED**: NeoPixel 8 Stick
- **Power Converter**: Integrated within LiPo Battery
- **Solar Panel**: 20 Watt
- **Battery**: LiPo

## Set up your hardware

Before you begin, you need to [set up your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up) with
Raspberry Pi OS (preferably updated to Buster).

You also need to connect a USB camera to the Raspberry Pi. (Any USB port will work)

And to see the results from the PI, you need a monitor connected
to the Raspberry Pi. It's okay if you're using SSH to access the Pi shell
(you don't need to use a keyboard connected to the Pi)—you only need a monitor
attached to the Pi to see the camera stream. The UNLOCK/LOCK decision is printed to
the terminal, as well as the challenged image upload aknowledgement.

<br/><br/>

(Optional) connect LEDs to represent the state of the UNLOCK/LOCK desicions

You will need one 4 RGB LED, four MtF jumper wires, three resistors, and a breadboard.
If the item is deemed recyclable, the LED pin will light green, if not, it will light red.

<img src="https://github.com/jakeengstrom3/SmartBin/blob/master/raspi_gpio_LED.JPG" width="30%" height="30%">

I used pin 9 for grounding and pins 11, 13, and 15 for the LED's after connecting them with resistors. 
You can follow this [tutorial](https://www.youtube.com/watch?v=sCYMENrtjiI) for more instructions. 

<br/><br/>

(Optional) connect Servo to represent the state of the UNLOCK/LOCK desicions

You will need one servo and 3 MtF jumper wires.
If the item is deemed recyclable, the servo will soin 90 degress, if not, it will spin -90 degrees.

<img src="https://github.com/jakeengstrom3/SmartBin/blob/master/raspi_gpio_servo.JPG" width="30%" height="30%">

I used pin 4 for power supply, pin 6 for grounding and pin 12 for connecting. 
You can follow this [tutorial](https://www.youtube.com/watch?v=40tZQPd3z8g) for more instructions. 

[*original image source](https://www.elektronik-kompendium.de/sites/raspberry-pi/1907101.htm)
## Set Up virtual Enviroment

Once the PI is up and running, open the termial, and enter the follow commands:

Show your Raspberry Pi OS version.

```
cat /etc/os-release
```

Update packages on your Raspberry Pi OS.

```
sudo apt-get update
```

Check your Python version. You should have Python 3.7 or later.

```
python3 --version
```

Install virtualenv and upgrade pip.

```
python3 -m pip install --user --upgrade pip
```

```
python3 -m pip install --user virtualenv
```

Create a Python virtual environment for the TFLite samples (optional but strongly recommended)

```
python3 -m venv ~/tflite
```

***Run this command whenever you open a new Terminal window/tab to activate the environment.***

```
source ~/tflite/bin/activate
```

***Clone this repository***

```
git clone https://github.com/jakeengstrom3/SampleImageClassification.git
cd SampleImageClassification
```

***Activate the virtual enviroment. Run this command every time you open a new terminal or restart the PI.***

```
source ~/tflite/bin/activate
```

***Run this [script](https://github.com/jakeengstrom3/SampleImageClassification/blob/master/setup.sh) to install the required dependencies.***

```
sh setup.sh
```

***If accessing your Pi remotely, run this command***

```
export DISPLAY=:0.0
```

## Run the [classifier](https://github.com/jakeengstrom3/SampleImageClassification/blob/master/run.py)

```
python3 run.py
```

***If you have the LED and servo connected, run the run_with_hardware.py***

```
python3 run_with_hardware.py
```

A new window will appear with the camera stream being displayed. Use this window to ensure the camera can see the recyclable object. Hold recyclable object in front of the attached camera. Press the spacebar to take a picture of the object. The controller will then display in the terminal if the bin is to be unlocked or not. If you beleive the object is not properly classified, press 'c' to upload the incorrectly classified image to the project's cloud storage, lcoated [here](https://console.cloud.google.com/storage/browser/smart-recycling-bin-bbcaa.appspot.com;tab=objects). See the retraining section of the readme for more.

# If you see an error running the sample:

ImportError: libcblas.so.3: cannot open shared object file: No such file or directory
you can fix it by installing an OpenCV dependency that is missing on your Raspberry Pi.

```
sudo apt-get install libatlas-base-dev
```

