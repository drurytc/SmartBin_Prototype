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

***Clone this repository***
```
git clone https://github.com/jakeengstrom3/SampleImageClassification.git
cd SampleImageClassification
```

## Run this [script](https://github.com/jakeengstrom3/SampleImageClassification/blob/master/setup.sh) to install the required dependencies and download the TFLite models.

```
sh setup.sh
```

if accessing your Pi remotely, run this command
```
export DISPLAY=:0.0
```

## Run the [classifier](https://github.com/jakeengstrom3/SampleImageClassification/blob/master/run.py) 

```
python3 run.py
```
A new window will appear with the camera stream being displayed. Use this window to ensure the camera can see the recyclable object. Hold recyclable object in front of the attached camera. Press the spacebar to take a picture of the object. The controller will then display in the terminal if the bin is to be unlocked or not. If you beleive the object is not properly classified, press 'c' to upload the incorrectly classified image to the project's cloud storage, lcoated [here](https://console.cloud.google.com/storage/browser/smart-recycling-bin-bbcaa.appspot.com;tab=objects). See the retraining section of the readme for more.

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
## To Retrain the model on new data
Head over to this Google Collab (public access).
```
https://colab.research.google.com/drive/17hy3TuT37Ua-ai9njKngECdYpVkJQ2mH#scrollTo=VTniC8nkCOmq
```
Load in (only) verified images from the project's cloud storage (https://console.cloud.google.com/storage/browser/smart-recycling-bin-bbcaa.appspot.com). The new data is located in the verified_images folder, and the base dataset (in case the new data is insufficient) is located in the Recyclables folder. 

Once you have a zipped file called Recyclables.zip loaded into Colab's files under /content/ (instructions for this are in the collab):
Press ctrl+F9 to run the collab. This will create a new model, and download it to your local computer. 
Once you have the new model, either add it to the /models folder, and use the --model option to choose the new model, or replace the default_model.tflite to make the retrained model the new default (recommened). 

A sample Recyclables folder (the one that will be compresses into a zip file) is given in the repository, but for the future additions to Recyclables.zip, it should be formatted to have separate sub-folders named with the classification of the objects inside (a plastic folder should contain images of plastic recyclables)

