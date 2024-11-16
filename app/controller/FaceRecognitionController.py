from app.model.user import Users
from app import response, app, db
from flask import request

import os
import requests
import cv2
import numpy as np
from PIL import Image as Img
from numpy import asarray, expand_dims
from keras_facenet import FaceNet
import pickle

# Load Cascade Classifier and FaceNet Model
HaarCascade = cv2.CascadeClassifier(cv2.samples.findFile(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'))
MyFaceNet = FaceNet()

# Function to add face recognition data
def addFaceRecognition(user_id, image_path):
    try:
        # Load and preprocess image
        img = cv2.imread(image_path)
        wajah = HaarCascade.detectMultiScale(img, 1.1, 4)

        if len(wajah) > 0:
            x1, y1, width, height = wajah[0]
        else:
            print("No face detected.")
            return False

        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Img.fromarray(img_rgb)  # Convert from OpenCV to PIL
        img_array = asarray(img_pil)

        # Crop and resize face region
        face = img_array[y1:y2, x1:x2]
        face = Img.fromarray(face).resize((160, 160))
        face = asarray(face)
        face = expand_dims(face, axis=0)

        # Generate embedding for the face
        embedding = MyFaceNet.embeddings(face)
        
        # Convert embedding to a BLOB (binary) format for database storage
        embedding_blob = pickle.dumps(embedding)

        # Prepare data payload for Laravel API
        payload = {
            'user_id': user_id,
            'face_embedding': embedding_blob
        }
        
        # Endpoint Laravel untuk menyimpan embedding wajah
        laravel_url = 'http://laravel_backend_url/api/user/add_face_embedding'
        
        # Send data to Laravel API
        response = requests.post(laravel_url, files={'face_embedding': embedding_blob}, data={'user_id': user_id})

        if response.status_code == 200:
            print("Face embedding successfully added.")
            return True
        else:
            print("Failed to add face embedding:", response.text)
            return False

    except Exception as e:
        print("Error:", e)
        return False

def index():
    try:
        user = Users.query.all()
        data = formatarray(user)
        return response.success(data, "success")
    except Exception as e:
        print(e)
        return response.error("An error occurred while fetching data.")

def formatarray(datas):
    array = [singleObject(i) for i in datas]
    return array

def singleObject(data):
    data = {
        'id' : data.id,
        'username' : data.username,
        'password' : data.password,
        'nim' : data.nim,
        'name' : data.name,
        'avatar' : data.avatar,
    }

    return data