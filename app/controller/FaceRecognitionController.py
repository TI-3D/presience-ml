from app import response

import os
import cv2
import numpy as np
from PIL import Image as Img
from numpy import asarray, expand_dims
from keras_facenet import FaceNet
import pickle
from flask import jsonify
import base64

# Load Cascade Classifier and FaceNet Model
HaarCascade = cv2.CascadeClassifier(cv2.samples.findFile(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'))
MyFaceNet = FaceNet()

# Function to add face recognition data
def addFaceRecognition(image_path):
    try:
        upload_dir = "./uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Load and preprocess image
        file = image_path
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        img = cv2.imread(file_path)
        wajah = HaarCascade.detectMultiScale(img, 1.1, 4)

        if len(wajah) == 0:
            os.remove(file_path)
            return jsonify({"status": False, "message": "No face detected", "data": None}), 400
        if len(wajah) > 1:
            os.remove(file_path)
            return jsonify({"status": False, "message": "Multiple faces detected", "data": None}), 400

        x1, y1, width, height = wajah[0]
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Img.fromarray(img_rgb)
        img_array = asarray(img_pil)

        # Crop and resize face region
        face = img_array[y1:y2, x1:x2]
        face = Img.fromarray(face).resize((160, 160))
        face = asarray(face)
        face = expand_dims(face, axis=0)

        # Generate embedding for the face
        embedding = MyFaceNet.embeddings(face)
        embedding_blob = pickle.dumps(embedding)
        embedding_blob_base64 = base64.b64encode(embedding_blob).decode('ascii')

        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "status": True,
            "message": "Face embedding successfully added",
            "data": {
                "face_embedding_blob": embedding_blob_base64,
                "embedding_list": embedding.tolist(),
            },
        }), 200
    except Exception as e:
        return jsonify({
            "status": False,
            "message": "Failed to process face embedding",
            "data": {"error": str(e)},
        }), 500
        
def validate_face_recognition(image_path, database_embedding):
    try:
        # Read image file
        upload_dir = "./uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Load and preprocess image
        file = image_path
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)    

        # Decode embedding from Base64 (embedding is from database)
        embedding_data = base64.b64decode(database_embedding)
        embedding = pickle.loads(embedding_data)
        embedding = np.array(embedding, dtype=np.float32)
        
        if embedding.ndim == 1:
            embedding = np.expand_dims(embedding, axis=0)

        # Detect face
        img = cv2.imread(file_path)
        wajah = HaarCascade.detectMultiScale(img, 1.1, 4)
        if len(wajah) == 0:
            os.remove(file_path)
            return jsonify({"status": False, "message": "No face detected", "data": None}), 400
        
        x1, y1, width, height = wajah[0]
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Img.fromarray(img_rgb)
        img_array = asarray(img_pil)

        # Crop and resize face region
        face = img_array[y1:y2, x1:x2]
        face = Img.fromarray(face).resize((160, 160))
        face = asarray(face)
        face = expand_dims(face, axis=0)

        # Generate signature from the image
        signature = MyFaceNet.embeddings(face)
        embedding = np.reshape(embedding, (1, 512))
        print(f"Signature shape: {signature.shape}")
        print(f"Database embedding size: {embedding.size}")

        # Calculate similarity between provided embedding and the generated signature
        dist = np.linalg.norm(embedding - signature)
        dist = float(dist)
        print(f"Distance: {dist}")
        
        if os.path.exists(file_path):
            os.remove(file_path)

        # Threshold for face recognition
        FACE_RECOGNITION_THRESHOLD = 0.6
        if dist > FACE_RECOGNITION_THRESHOLD:
            return jsonify({
                "status": False, 
                "message": "Face not recognized", 
                "data": {"distance": dist},
            }), 400

        return jsonify({
            "status": True,
            "message": "Face recognized",
            "data": {"distance": dist},
        }), 200

    except Exception as e:
         return jsonify({
            "status": False,
            "message": {"error": str(e)},
            "data": None,
        }), 500