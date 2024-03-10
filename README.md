
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

## Hardware Setup
Before you begin, ensure you have set up your Raspberry Pi with Raspberry Pi OS, preferably updated to Buster. 
Additionally, connect the necessary hardware components as outlined below:

### Camera
Connect the Arducam 4K 8MP IMX219 camera to any available USB port on the Raspberry Pi. This camera will 
be used for capturing images for classification.

### Sorting Servo Motor (DS3235-270)
- **Power Supply:** Connect the power wire of the DS3235-270 sorting servo motor to pin 2 (5V) on
- the Raspberry Pi.
- **Ground:** Connect the ground wire of the servo motor to pin 6 (ground) on the Raspberry Pi.
- **Control Signal:** Connect the control wire of the servo motor to GPIO pin 17 on the Raspberry Pi.

### Door Locking Servo Motor (SG90)
- **Power Supply:** Connect the power wire of the SG90 door locking servo motor to pin 4 (5V) on the Raspberry Pi.
- **Ground:** Connect the ground wire of the servo motor to pin 6 (ground) on the Raspberry Pi.
- **Control Signal:** Connect the control wire of the servo motor to GPIO pin 18 on the Raspberry Pi.

### Item Sensor: PIR Motion Sensor
- **Power Supply:** Connect the VCC (power) wire of the PIR motion sensor to pin 2 (5V) on the Raspberry Pi.
- **Ground:** Connect the ground wire of the PIR motion sensor to pin 6 (ground) on the Raspberry Pi.
- **Output Signal:** Connect the output wire of the PIR motion sensor to GPIO pin 4 on the Raspberry Pi.

### Capacity Sensor: Break Beam
- **Emitter (Transmitter):** Connect the emitter wire of the break beam capacity sensor to GPIO pin 23 on
-  the Raspberry Pi.
- **Receiver:** Connect the receiver wire of the break beam capacity sensor to GPIO pin 24 on the Raspberry Pi.

### Capacity LED: NeoPixel 8 Stick
- **Power Supply:** Connect the VCC (power) wire of the NeoPixel 8 Stick LED to pin 2 (5V) on the Raspberry Pi.
- **Ground:** Connect the ground wire of the LED to pin 6 (ground) on the Raspberry Pi.
- **Data Input:** Connect the data input wire of the LED to GPIO pin 10 on the Raspberry Pi.

### Camera LED: NeoPixel 8 Stick
- **Power Supply:** Connect the VCC (power) wire of the NeoPixel 8 Stick LED to pin 2 (5V) on the Raspberry Pi.
- **Ground:** Connect the ground wire of the LED to pin 6 (ground) on the Raspberry Pi.
- **Data Input:** Connect the data input wire of the LED to GPIO pin 9 on the Raspberry Pi.

### Power Converter: Integrated within LiPo Battery
Ensure the power converter is integrated within the LiPo battery setup. This setup will provide power to the
Raspberry Pi and other components.

### Solar Panel: 25 Watt
Connect the 25 Watt solar panel to the power converter setup. This panel will harness solar energy to recharge the LiPo battery.

### Battery: LiPo
Ensure the LiPo battery is connected to the power converter setup. This battery will store energy from the solar panel
for powering the smart recycling bin.

Ensure all connections are secure and properly configured to enable the efficient operation of the smart recycling bin.
<br/><br/>
<img src="https://github.com/drurytc/SmartBin_Prototype/blob/master/GPIO_Pins.png" width="50%" height="50%">
<br/><br/>

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
git clone https://github.com/drurytc/SmartBin_Prototype.git
cd SampleImageClassification
```

***Activate the virtual enviroment. Run this command every time you open a new terminal or restart the PI.***

```
source ~/tflite/bin/activate
```

***Run the following to install the required dependencies.***

```
sh setup.sh
```

***If accessing your Pi remotely, run this command***

```
export DISPLAY=:0.0
```

## Running from Command Line Interface

***Run the classifier without hardware***

```
python3 run.py
```

***All hardware connected***

```
python3 run_physical.py
```

A new window will appear with the camera stream being displayed. Use this window to ensure the camera can see the recyclable object. Hold recyclable object in front of the attached camera. Press the spacebar to take a picture of the object. The controller will then display in the terminal if the bin is to be unlocked or not for the run.py and nothing for run_physical.py. 

## Error Troubleshooting 

ImportError: libcblas.so.3: cannot open shared object file: No such file or directory
you can fix it by installing an OpenCV dependency that is missing on your Raspberry Pi.

```
sudo apt-get install libatlas-base-dev
```

