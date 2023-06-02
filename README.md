# Smart Recycling Bin

This is the software used to control the smart recycling bin. This project uses a custom trained TensorflowLite model to classify objects as recycleable or non-recycleable, then send a singal to a motor which swivels the bin's lid to the left (recycleable) or the right (trash). If the user believes the bin is wrong, they can challenge the bin, and send the image to cloud storage, where a project mainianter can verify the challenged images and create a new dataset to retrain the bin.

## Set up your hardware

Before you begin, you need to [set up your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up) with
Raspberry Pi OS (preferably updated to Buster).

You also need to connect a USB camera to the Raspberry Pi. (Any USB port will work)

And to see the results from the PI, you need a monitor connected
to the Raspberry Pi. It's okay if you're using SSH to access the Pi shell
(you don't need to use a keyboard connected to the Pi)—you only need a monitor
attached to the Pi to see the camera stream. The UNLOCK/LOCK decision is printed to
the terminal, as well as the challenged image upload aknowledgement.

(Optional) connect LEDs to represent the state of the UNLOCK/LOCK desicions

You will need one 4 RGB LED, three MtF jumper wires, three resistors, and a breadboard.
If the item is deemed recyclable, the LED pin will light green, if not, it will light red.
follow this [tutorial](https://www.youtube.com/watch?v=sCYMENrtjiI)

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

***If you have the LED connected, run the run_withLED.py***

```
python3 run_withLED.py
```

A new window will appear with the camera stream being displayed. Use this window to ensure the camera can see the recyclable object. Hold recyclable object in front of the attached camera. Press the spacebar to take a picture of the object. The controller will then display in the terminal if the bin is to be unlocked or not. If you beleive the object is not properly classified, press 'c' to upload the incorrectly classified image to the project's cloud storage, lcoated [here](https://console.cloud.google.com/storage/browser/smart-recycling-bin-bbcaa.appspot.com;tab=objects). See the retraining section of the readme for more.

# If you see an error running the sample:

ImportError: libcblas.so.3: cannot open shared object file: No such file or directory
you can fix it by installing an OpenCV dependency that is missing on your Raspberry Pi.

```
sudo apt-get install libatlas-base-dev
```

* You can optionally specify the `model` parameter to set the TensorFlow Lite
  model to be used:
  * The default value is `model.tflite`. The other models are in the models/ directory.

## To stop the classifier, press ESC.

## To exit the virtual enviroment run

```
deactivate
```

## To Retrain the model on new data

Head over to this Google Colab (public access).

```
https://colab.research.google.com/drive/17hy3TuT37Ua-ai9njKngECdYpVkJQ2mH#scrollTo=VTniC8nkCOmq
```

Load in (only) verified images from the project's cloud storage (`https://console.cloud.google.com/storage/browser/smart-recycling-bin-bbcaa.appspot.com`). The new data is located in the verified_images folder, and the base dataset (in case the new data is insufficient) is located in the Recyclables folder.

Once you have a zipped file called Recyclables.zip loaded into Colab's files under /content/ (instructions for this are in the collab):
Press ctrl+F9 to run the collab. This will create a new model, and download it to your local computer.
Once you have the new model, either add it to the /models folder, and use the --model option to choose the new model, or replace the default_model.tflite to make the retrained model the new default (recommened).

A sample Recyclables folder (the one that will be compresses into a zip file) is already included in the cloud storage, but for the future additions to Recyclables.zip, it should be formatted to have separate sub-folders named with the classification of the objects inside (a plastic folder should contain images of plastic recyclables)

## End-to-End System Diagram
![Project Diagram Image](https://github.com/jakeengstrom3/SmartBin/blob/master/Project_Diagram.png?raw=true)

Here is a diagram of the end-to-end system we completed. Starting on the left, a usb camera attached to a Raspberry Pi captures an image of the presented object upon button push (spacebar on the keyboard). The user is then altered of the decision made by the Raspberry PI (unlock or remain locked) with an LED, and the motor will either swivel to the left (recycle) or the right (trash).  
If the user believes the PI is wrong, they can push a separate button to send that image with the supposedly improper label to the cloud storage. This is hosted by a Google Cloud project’s ‘cloud storage’. Then, when enough new images have been uploaded (~1000), a maintainer of the project will need to manually sort the improperly labeled images into a new dataset. 
To do that, a user with admin access goes to the cloud console home page (linked in the github readme), and select ‘Cloud Storage>Buckets’ from the navigation menu. Then you would drag and drop the images from their folders in the ‘challenged_images’ directory to the proper folder in the ‘verified_images’ directory. (Note: this step is represented visually as a mobile app in the diagram, which we have not implemented). 
That new dataset can then be downloaded, and used in Google Colab to retrain the model, and improve its accuracy. The new model can then be manually loaded onto the PI, and used. The categories that the bin recognizes is based on the name of the folders in the dataset. This means that if you wanted to add a new category of recyclable, all you would need to do is retrain the model using a dataset that contains examples of that recyclable in its own folder. 

## To add people to cloud storage access
Go to the cloud storage project home page at https://console.cloud.google.com. Select the Smart Recycling Bin Project, or follow this link from the Github readme: https://console.cloud.google.com/welcome?project=smart-recycling-bin-bbcaa. At the top right, click the three dots, then select project settings. Go to the ‘IAM’ tab, then click the blue ‘Grant Access’ button. Add the new project maintainer’s email address to the principle section, then select ‘owner’ in the select a role section. Click save. The owner of the email address now has full access to the cloud project’s storage. 

## How to continue where we left off
To continue working on this project, clone the repository, and use that as a starting point. All of our work is open source, meaning anyone can copy it and add to their copies as much as they want. 
We finished a good prototype of the ‘Smart’ part of the SmartBin. The bin itself still needs work, however. We have a simple demonstration of a motor attached to the PI, that spins a lid to drop the item into a box below, but as far as physical bin design, there is a lot of work that can be done. For example, for the buttons to classify objects and challenge the decision, we just use a USB keyboard. This could be replaced with standalone buttons attached to the Raspberry PI’s IO pins. 
The ‘smart’ part is also just a prototype, and there is a lot of work that could be done there. For example, a separate project could be designing a web app for sorting the challenged images into the verified_images folder. We also added the functionality of the model distinguishing types of recycling, but our prototype only has two decisions (recyclable or not). It would be interesting to design a physical sorting system based on the type of recycling. 
The process of retraining can also be more streamlined, maybe the next team can explore the interaction between google cloud storage and google colab. [This](https://www.maskaravivek.com/post/how-to-access-files-from-google-cloud-storage-in-colab-notebooks/) could be a good place to start, so that the images from the cloud storage don’t have to be downloaded 1 by 1 and zipped up.

