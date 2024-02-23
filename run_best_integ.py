"""Main script to run image classification."""

import argparse
import sys
import time
import threading
import os
import uuid

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

from firebase_admin import credentials, initialize_app, storage

import RPi.GPIO as GPIO
from gpiozero import Servo
from rpi_ws281x import PixelStrip, Color

GPIO.setmode(GPIO.BCM)
PIR = 4
BEAM_PIN1 = 5
BEAM_PIN2 = 6
BEAM_PIN3 = 13
BEAM_PIN4 = 16
CHOOSE_PIN = 17
LOCK_PIN = 27

FULL_IND = 18
INTERIOR = 12

# LED strip configuration:
LED_COUNT = 8        # Number of LED pixels.
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
full = PixelStrip(LED_COUNT, FULL_IND, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
inside = PixelStrip(LED_COUNT, INTERIOR, LED_FREQ_HZ, 8, LED_INVERT, 100, 0)

# Intialize the library (must be called once before other functions).
full.begin()
inside.begin()

# Example: Fill the NeoPixels with a color
def fill_color(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    
#colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]  # Red, Green, Blue
 #     for color in colors:
  #      fill_color(inside, color)
    #    time.sleep(1)  # Delay for 1 second

# Servo setup  
buff = 0.60
maxPW = (1.0 + buff) / 1000
minPW = (1.0 - buff) / 1000
chooseServo = Servo(CHOOSE_PIN, min_pulse_width=minPW, max_pulse_width=maxPW)
chooseServo.mid()
lockServo = Servo(LOCK_PIN, min_pulse_width=minPW, max_pulse_width=maxPW)
lockServo.min()
time.sleep(1.5)
chooseServo.value = None
lockServo.value = None

# Motion Sensor setup
GPIO.setup(PIR, GPIO.IN)
last_motion_time = 0

def motion_callback(channel):
    global last_motion_time
    current_time = time.time()
    
    # Check if enough time has passed since the last motion detection
    if (current_time - last_motion_time) > 1.5 and GPIO.input(PIR):
        # Record the time of the latest motion detection
        last_motion_time = current_time
        return True
    else:
        return False

GPIO.add_event_detect(PIR, GPIO.FALLING, callback=motion_callback)

def lock(x):
    lockServo.max()
    time.sleep(2)
    lockServo.value = None
    fill_color(full, Color(x,0,0))
    
def toggle(cat):
    if cat == 'recycle':
      chooseServo.min()
      time.sleep(2)
      if not GPIO.input(BEAM_PIN2):
          lock(255)
          time.sleep(2)
      chooseServo.mid()
      time.sleep(2)
      chooseServo.value = None
    elif cat == 'nonRecyclable':
        chooseServo.max()
        time.sleep(2)
        if not GPIO.input(BEAM_PIN2):
            print('LOCKED')
            lock(255)
        time.sleep(2)
        chooseServo.mid()
        time.sleep(2)
        chooseServo.value = None
        
def breakbeam_callback(channel):
  time.sleep(10)
  if not GPIO.input(channel):
    lock(255)
        
GPIO.setup(BEAM_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BEAM_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BEAM_PIN3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BEAM_PIN4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(BEAM_PIN1, GPIO.FALLING, callback=breakbeam_callback)
GPIO.add_event_detect(BEAM_PIN2, GPIO.FALLING, callback=breakbeam_callback)
GPIO.add_event_detect(BEAM_PIN3, GPIO.FALLING, callback=breakbeam_callback)
GPIO.add_event_detect(BEAM_PIN4, GPIO.FALLING, callback=breakbeam_callback)

cred = credentials.Certificate("private.json")
initialize_app(cred, {'storageBucket': 'smart-recycling-bin-bbcaa.appspot.com'})
bucket = storage.bucket()
# Visualization parameters
_ROW_SIZE = 20  # pixels
_LEFT_MARGIN = 24  # pixels
_TEXT_COLOR = (0, 0, 255)  # red
_FONT_SIZE = 3
_FONT_THICKNESS = 1
_FPS_AVERAGE_FRAME_COUNT = 10
_FRAME_WIDTH = 800
_FRAME_HEIGHT = 800

# Bin Parameters
_UNLOCK_THRESHOLD = 0.6
_TIME_FOR_CHALLENGING = 10
time_of_last_classification = 0

# Classification Model Parameters
_MAX_RESULTS = 3
_SCORE_THRESHOLD = 0.20
_NUM_THREADS = 4
_CAMERA_ID = 0

def run(model: str, save_images_on: bool) -> None:

  model_path = f'./models/{model}'


  # Initialize the image classification model
  base_options = core.BaseOptions(
      file_name=model_path, use_coral=False, num_threads=_NUM_THREADS)

  # Enable Coral by this setting
  classification_options = processor.ClassificationOptions(
      max_results=_MAX_RESULTS, score_threshold=_SCORE_THRESHOLD)
  options = vision.ImageClassifierOptions(
      base_options=base_options, classification_options=classification_options)

  classifier = vision.ImageClassifier.create_from_options(options)

  # Variables to calculate FPS
  counter, fps = 0, 0
  start_time = time.time()
  time_of_last_classification = 0

  # Start capturing video input from the camera
  cap = cv2.VideoCapture(_CAMERA_ID)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, _FRAME_WIDTH)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _FRAME_HEIGHT)

  last_challenged_image = None # quick fix for variable used before assignemt error
  # Continuously capture images from the camera and run inference
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      sys.exit(
          'ERROR: Unable to read from webcam. Please verify your webcam settings.'
      )
    key_press = cv2.waitKey(2)

    # Only classify the image when spacebar is pressed
    if key_press == 32 or motion_callback(PIR): # Spacebar code
      fill_color(inside, Color(246,231,210))
      
      time.sleep(1)
      counter += 1
      image = cv2.flip(image, 1)
      # Convert the image from BGR to RGB as required by the TFLite model.
      rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

      # Create TensorImage from the RGB image
      tensor_image = vision.TensorImage.create_from_array(rgb_image)
      # List classification results
      categories = classifier.classify(tensor_image)

      best_guess = max(categories.classifications[0].categories, key=lambda x:x.score)
      category_name = best_guess.category_name
      score = best_guess.score

      last_classified_image = image
      last_classified_image_category = category_name
      time_of_last_classification = time.time()
      text_location = (_LEFT_MARGIN, _ROW_SIZE)

      result_text = category_name + ' (' + str(score) + ')'
      cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
          _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

      # Decide to unlock or not
      if("nonRecyclable" not in category_name and score > _UNLOCK_THRESHOLD):
        cap.release()
        cap = cv2.VideoCapture(_CAMERA_ID)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, _FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _FRAME_HEIGHT)
        toggle('recycle')
        fill_color(inside, Color(0,255,0))
        if(save_images_on):
          write_out_image_to_classified_directory(image, category_name)
        time.sleep(4)
      else:
        category_name = "nonRecyclable"
        fill_color(inside, Color(220,40,0))
        toggle(category_name)
        time.sleep(2)
      fill_color(inside, Color(0,0,0))
      fill_color(full, Color(0,0,0))
      
    # Stop the program if the ESC key is pressed.
    elif key_press == 27:
      fill_color(full, Color(0,0,0))
      fill.show()
      full.close()
      fill_color(inside, Color(0,0,0))
      inside.show()
      inside.close()
      break
    # Calculate the FPS
    if counter % _FPS_AVERAGE_FRAME_COUNT == 0:
      end_time = time.time()
      fps = _FPS_AVERAGE_FRAME_COUNT / (end_time - start_time)
      start_time = time.time()

    # Show the FPS
    fps_text = 'FPS = ' + str(int(fps))
    text_location = (_LEFT_MARGIN, _ROW_SIZE)
    cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

    cv2.imshow('image_classification', image)

  cap.release()
  cv2.destroyAllWindows()

def upload_to_fireStoreDB(image, category, storage):
  print("Uploading Challenged Image to Database")
  image_name = str(uuid.uuid4()) + ".jpg"

  path = f'challenged_images/{category}/{image_name}'

  if not os.path.isdir(f'challenged_images/{category}/'): # Automatically create a new directory for novel categories
    os.mkdir(f'challenged_images/{category}/')

  cv2.imwrite(path, image)
  blob = bucket.blob(path)
  blob.upload_from_filename(path)
  print("Image sucessfully uploaded to DB")

def write_out_image_to_classified_directory(image, category):
  path = f'./classified_images/{category}/'
  if not os.path.isdir(path):
    os.mkdir(path)
    name = '0.jpg'
  else:
    name = str(len(os.listdir(path))) + ".jpg"
  print(f'saving image named {name}, to {path}')
  cv2.imwrite(os.path.join(path , name), image)

def main():

  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model',
      help='Name of image classification model.',
      required=False,
      default='default_model.tflite')
  parser.add_argument(
    '--saveImages', 
    help= 'Optionally save classified images in local dataset',
    action='store_true',
    required=False,
    default=False)
  args = parser.parse_args()

  run(args.model, bool(args.saveImages))
  fill_color(full, Color(0,0,0))
  fill.show()
  full.close()
  fill_color(inside, Color(0,0,0))
  inside.show()
  inside.close()

if __name__ == '__main__':
  main()
