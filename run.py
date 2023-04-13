# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
  "serviceAccount": "DELETEME.json",
  "databaseURL": "https://smart-recycling-bin-bbcaa-default-rtdb.firebaseio.com/"
}

# Visualization parameters
_ROW_SIZE = 20  # pixels
_LEFT_MARGIN = 24  # pixels
_TEXT_COLOR = (0, 0, 255)  # red
_FONT_SIZE = 3
_FONT_THICKNESS = 1
_FPS_AVERAGE_FRAME_COUNT = 10

# Bin Parameters
_UNLOCK_THRESHOLD = 0.6
_TIME_FOR_CHALLENGING = 10
time_of_last_classification = 0


def run(model: str, max_results: int, score_threshold: float, num_threads: int,
        enable_edgetpu: bool, camera_id: int, width: int, height: int, save_images_on: bool) -> None:
  """Continuously run inference on images acquired from the camera.

  Args:
      model: Name of the TFLite image classification model.
      max_results: Max of classification results.
      score_threshold: The score threshold of classification results.
      num_threads: Number of CPU threads to run the model.
      enable_edgetpu: Whether to run the model on EdgeTPU.
      camera_id: The camera id to be passed to OpenCV.
      width: The width of the frame captured from the camera.
      height: The height of the frame captured from the camera.
  """

  model_path = f'./models/{model}'

  # Initialize Database Connection
  firebase = pyrebase.initialize_app(firebaseConfig)
  storage = firebase.storage()


  # Initialize the image classification model
  base_options = core.BaseOptions(
      file_name=model_path, use_coral=enable_edgetpu, num_threads=num_threads)

  # Enable Coral by this setting
  classification_options = processor.ClassificationOptions(
      max_results=max_results, score_threshold=score_threshold)
  options = vision.ImageClassifierOptions(
      base_options=base_options, classification_options=classification_options)

  classifier = vision.ImageClassifier.create_from_options(options)

  # Variables to calculate FPS
  counter, fps = 0, 0
  start_time = time.time()
  time_of_last_classification = 0

  # Start capturing video input from the camera
  cap = cv2.VideoCapture(camera_id)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

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

      if("nonRecyclable" not in category_name and score > _UNLOCK_THRESHOLD):
        cap.release()
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if(save_images_on):
          write_out_image_to_classified_directory(image, category_name)
        print("UNLOCKED")
        print(f"You are recycling {category_name} ({score * 100}% confidence) \
              if this is incorrect, please press 'c' to submit the incorrect labelling for review")
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

  if not os.path.isdir(f'challenged_images/{category}/'): # Automatically creates a new directory for novel categories
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
      default='mobilenet_v2_psu_data.tflite')
  parser.add_argument(
      '--maxResults',
      help='Max of classification results.',
      required=False,
      default=3)
  parser.add_argument(
      '--scoreThreshold',
      help='The score threshold of classification results.',
      required=False,
      type=float,
      default=0.2)
  parser.add_argument(
      '--numThreads',
      help='Number of CPU threads to run the model.',
      required=False,
      default=4)
  parser.add_argument(
      '--enableEdgeTPU',
      help='Whether to run the model on EdgeTPU.',
      action='store_true',
      required=False,
      default=False)
  parser.add_argument(
      '--cameraId', help='Id of camera.', required=False, default=0)
  parser.add_argument(
      '--frameWidth',
      help='Width of frame to capture from camera.',
      required=False,
      default=1280)
  parser.add_argument(
      '--frameHeight',
      help='Height of frame to capture from camera.',
      required=False,
      default=960)
  parser.add_argument(
    '--saveImages', 
    help= 'Optionally save classified images in local dataset',
    action='store_true',
    required=False,
    default=False)
  args = parser.parse_args()

  run(args.model, int(args.maxResults),
      args.scoreThreshold, int(args.numThreads), bool(args.enableEdgeTPU),
      int(args.cameraId), args.frameWidth, args.frameHeight, bool(args.saveImages))


if __name__ == '__main__':
  main()
