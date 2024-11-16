from app import app
from app.controller import FaceRecognitionController
from flask import request

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/api/face-recognition', methods=['GET'])
def all():
    return FaceRecognitionController.index()

@app.route('/api/face-recognition/add', methods=['POST'])
def add():
    return FaceRecognitionController.addFaceRecognition(request.form['user_id'], request.files['face_embedding'].filename)

if __name__ == '__main__':
    app.run(debug=True)