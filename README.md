# TensorFlow Lite Python image classification example with Raspberry Pi.

This example uses [TensorFlow Lite](https://tensorflow.org/lite) with Python
on a Raspberry Pi to perform real-time image classification using images
taken from the camera.

## Set up your hardware

Before you begin, you need to [set up your Raspberry Pi](
https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up) with
Raspberry Pi OS (preferably updated to Buster).

You also need to connect a USB camera to the Raspberry Pi. (Any USB port will work)

And to see the results from the PI, you need a monitor connected
to the Raspberry Pi. It's okay if you're using SSH to access the Pi shell
(you don't need to use a keyboard connected to the Pi)—you only need a monitor
attached to the Pi to see the camera stream. The UNLOCK/LOCK decision is printed to
the terminal, as well as the challenged image upload aknowledgement. 

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

## Install the TensorFlow Lite runtime

In this project, all you need from the TensorFlow Lite API is the `Interpreter`
class. So instead of installing the large `tensorflow` package, we're using the
much smaller `tflite_runtime` package.

To install this on your Raspberry Pi, follow the instructions in the
[Python quickstart](https://www.tensorflow.org/lite/guide/python#install_tensorflow_lite_for_python).

You can install the TFLite runtime using this script.

```
sh setup.sh
```

# Run this script to install the required dependencies and download the TFLite models.

```
sh setup.sh
```

## Run the example

```
python3 run.py
```

# If you see an error running the sample:
ImportError: libcblas.so.3: cannot open shared object file: No such file or directory
you can fix it by installing an OpenCV dependency that is missing on your Raspberry Pi.

```
sudo apt-get install libatlas-base-dev
```

*   You can optionally specify the `model` parameter to set the TensorFlow Lite
    model to be used:
    *   The default value is `model.tflite`. The other models are in the models/ directory. 

## To stop the classifier, press ESC.
## To exit the virtual enviroment run
```
deactivate
```
