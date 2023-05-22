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

import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyCH9NwRnsl5Sk54bW8umXpDU24PiJxDMcI",
  "authDomain": "smart-recycling-bin-bbcaa.firebaseapp.com",
  "projectId": "smart-recycling-bin-bbcaa",
  "storageBucket": "smart-recycling-bin-bbcaa.appspot.com",
  "messagingSenderId": "138334020999",
  "appId": "1:138334020999:web:7d3bdbbb3ea858db96df22",
  "measurementId": "G-GS39XK3H6S",
  "serviceAccount": "private.json",
  "databaseURL": "https://smart-recycling-bin-bbcaa-default-rtdb.firebaseio.com/"
}

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

  # Initialize Database Connection
  firebase = pyrebase.initialize_app(firebaseConfig)
  storage = firebase.storage()

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
    if key_press == 32: # Spacebar code
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

      result_text = category_name + ' (' + str(score) + ')'
      cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
          _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

      # Decide to unlock or not
      if("nonRecyclable" not in category_name and score > _UNLOCK_THRESHOLD):
        cap.release()
        cap = cv2.VideoCapture(_CAMERA_ID)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, _FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _FRAME_HEIGHT)
        if(save_images_on):
          write_out_image_to_classified_directory(image, category_name)
        print("UNLOCKED")
        print(f"You are recycling {category_name} ({score * 100}% confidence) \
              \nIf this is incorrect, please press 'c' to submit the incorrect labelling for review")
        time.sleep(4)
        print("LOCKED")
      else:
        category_name = "nonRecyclable"
        print("NOT RECYCLEABLE. If this is incorrect, press the challenge button (c)")
        time.sleep(1)
      
    # Challenge the classification (save it to directory, and upload it to Firestore)
    elif key_press == ord('c'):
      # Gives 10 seconds to challenge the image
      ellapsed_time = time.time() - time_of_last_classification

      if ellapsed_time > _TIME_FOR_CHALLENGING:
        print("Time ran out of time to challenge the item. Try classifying again, then challenge.")
      elif last_classified_image is last_challenged_image:
        print("Can not challenge the same image twice")
      else:
          upload_to_fireStoreDB(last_classified_image, last_classified_image_category, storage)
          last_challenged_image = last_classified_image
      
    # Stop the program if the ESC key is pressed.
    elif key_press == 27:
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
  storage.child(path).put(path)
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

if __name__ == '__main__':
  main()
