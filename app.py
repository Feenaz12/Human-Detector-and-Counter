from flask import Flask, render_template, request, Response, redirect, url_for, session,flash
import cv2
import os
import time
from detector import detect_humans
from database import Database

app = Flask(__name__)
app.secret_key = "secret_key_123"   # required for login sessions

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

camera_on = False
cap = None

# Database
db = Database(
    host="localhost",
    user="root",
    password="Feenaz@123",
    database="human_detection"
)

# ---------------- AUTH ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # check if user already exists
        if db.get_user_by_email(email):
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for('signup'))

        if db.create_user(name, email, password):
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Database error. Please try again.", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db.verify_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- INDEX ----------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])


# ---------------- UPLOAD ----------------
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    files = request.files.getlist('files')
    results = []

    for file in files:
        filename = file.filename
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            img = cv2.imread(upload_path)
            img, count = detect_humans(img)

            out_name = f"out_{filename}"
            out_path = os.path.join(UPLOAD_FOLDER, out_name)
            cv2.imwrite(out_path, img)

            db.insert_result(user_id, filename, f"uploads/{out_name}", count)

            results.append({
                "image": f"uploads/{out_name}",
                "count": count,
                "original_name": filename
            })

    return render_template("results.html", results=results)


# ---------------- WEBCAM ----------------
@app.route('/start')
def start_cam():
    global cap, camera_on
    if not camera_on:
        cap = cv2.VideoCapture(0)
        camera_on = True
    return "Started"


@app.route('/stop')
def stop_cam():
    global cap, camera_on
    camera_on = False
    if cap:
        cap.release()
    return "Stopped"


def generate_frames():
    global cap, camera_on
    prev_time = 0

    while True:
        if not camera_on:
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            break

        frame, count = detect_humans(frame)

        curr = time.time()
        fps = int(1 / (curr - prev_time)) if prev_time else 0
        prev_time = curr

        cv2.putText(frame, f"Count: {count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
