from flask import Flask, render_template, request, Response
from lipstick import apply_makeup
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)

current_product = {"type": None, "color": "ff0000"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/<product_type>')
def product(product_type):
    return render_template('product.html', product_type=product_type)

@app.route('/tryon/<product_type>', methods=["GET", "POST"])
def tryon(product_type):
    if request.method == "POST":
        current_product["type"] = product_type
        current_product["color"] = request.form.get("color", "ff0000")
    return render_template('tryon.html', product_type=product_type)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = apply_makeup(frame, current_product)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
