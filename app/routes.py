from app import app
from app.controller import FaceRecognitionController
from flask import request
from flask import jsonify
import logging

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/api/face-recognition/add', methods=['POST'])
def add():
    try:
        if 'face_image' not in request.files:
            return jsonify({"error": "No face image provided"}), 400

        face_image = request.files['face_image']
        result = FaceRecognitionController.addFaceRecognition(face_image)
        return result
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/validate-face', methods=['POST'])
def validate_face():
    try:
        if 'face_image' not in request.files or 'database_embedding' not in request.form:
            return jsonify({"error": "Invalid input"}), 400

        face_image = request.files['face_image']
        database_embedding = request.form['database_embedding']

        logging.basicConfig(level=logging.INFO)
        logging.info(f"Received embedding: {database_embedding}")

        result = FaceRecognitionController.validate_face_recognition(face_image, database_embedding)
        return result
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)