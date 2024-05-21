import cv2
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Global variable to store information
server_info = {
    "fps": 0,
    "resolution": (0, 0)
}

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
