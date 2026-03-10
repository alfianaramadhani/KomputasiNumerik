import numpy as np
import cv2
import os
import sys
import glob 
import random
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter
import time
import serial
import threading

import matplotlib
import matplotlib.pyplot as plt


modelpath='detect.tflite'
lblpath='labelmap.txt'
min_conf=0.5

#cap = cv2.VideoCapture('prambanan.mp4')
cap = cv2.VideoCapture(0)

interpreter = Interpreter(model_path=modelpath)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

float_input = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

with open(lblpath, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# FPS
prev_frame_time = 0

# folder dataset
dataset_dir = "dataset"
os.makedirs(dataset_dir, exist_ok=True)

capture_count = {}

capture_message = ""
capture_time = 0

# ================= SERIAL ARDUINO =================
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)
ser.reset_input_buffer()
print("Serial OK")

arduino_trigger = False

def read_serial():
    global arduino_trigger

    while True:
        if ser.in_waiting > 0:
            try:
                data = ser.read().decode('utf-8').strip()
                print("Received:", data)

                if data == 'C':
                    arduino_trigger = True

            except:
                pass

        time.sleep(0.01)

serial_thread = threading.Thread(target=read_serial)
serial_thread.daemon = True
serial_thread.start()

while True:

    ret, frame = cap.read()
    if not ret:
        break

    # FPS
    new_frame_time = time.time()
    fps = int(1/(new_frame_time-prev_frame_time))
    prev_frame_time = new_frame_time

    # preprocessing
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imH, imW, _ = frame.shape

    image_resized = cv2.resize(image_rgb, (width, height))
    input_data = np.expand_dims(image_resized, axis=0)

    if float_input:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[1]['index'])[0]
    classes = interpreter.get_tensor(output_details[3]['index'])[0]
    scores = interpreter.get_tensor(output_details[0]['index'])[0]

    # keyboard input
    key = cv2.waitKey(1) & 0xFF

    for i in range(len(scores)):

        if (scores[i] > min_conf) and (scores[i] <= 1.0):

            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))

            class_id = int(classes[i])
            object_name = labels[class_id]

            # draw bounding box
            cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(10,255,0),2)

            label = '%s: %d%%' % (object_name, int(scores[i]*100))
            cv2.putText(frame,label,(xmin,ymin-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)

    # ===== CAPTURE SAAT TEKAN C ATAU DARI ARDUINO =====
    if key == ord('c') or arduino_trigger:

        class_folder = os.path.join(dataset_dir, str(class_id))
        os.makedirs(class_folder, exist_ok=True)

        if class_id not in capture_count:
            capture_count[class_id] = 0

        cropped = frame[ymin:ymax, xmin:xmax]

        filename = os.path.join(
            class_folder,
            f"img_{capture_count[class_id]}.jpg"
        )

        cv2.imwrite(filename, cropped)

        print("Saved:", filename)

        capture_count[class_id] += 1

        capture_message = f"Captured class {class_id}"
        capture_time = time.time()

        # ================= KIRIM KE ARDUINO =================
        try:
            arduino_class_id = class_id + 1
            message = f"{arduino_class_id}\n"
            ser.write(message.encode('utf-8'))
            print("Sent to Arduino:", arduino_class_id)
        except:
            print("Serial send failed")

        # reset trigger
        arduino_trigger = False
    
     #tampilkan FPS
    cv2.putText(frame,f"FPS: {fps}",(30,50),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
    # tampilkan pesan capture selama 2 detik
    if time.time() - capture_time < 2:
        cv2.putText(frame,
                    capture_message,
                    (30,90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,255),
                    3,
                    cv2.LINE_AA)

    cv2.imshow('output',frame)

    # keluar
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()