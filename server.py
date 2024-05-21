import cv2
import mediapipe as mp
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

server_info = {
    "fps": 0,
    "resolution": (0, 0)
}

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

def pose_detection(frame):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image

def generate_frames():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        server_info["fps"] = int(cap.get(cv2.CAP_PROP_FPS))
        server_info["resolution"] = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        
        frame = pose_detection(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Could not encode frame.")
            break
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/server_info')
def get_server_info():
    global server_info
    return jsonify(server_info)

if __name__ == '__main__':
    app.run(debug=True)
