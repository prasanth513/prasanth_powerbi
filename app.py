import numpy as np
from flask import Flask, request, jsonify, render_template
import sqlite3
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import pandas as pd
import pickle
import cv2
import random
import smtplib 
from email.message import EmailMessage
from datetime import datetime
import os



app = Flask(__name__)


model_path2 = 'models/vggnet_extension.h5' 


model = load_model(model_path2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')


@app.route('/home')
def home():
	return render_template('home.html')


@app.route("/signup")
def signup():
    global otp, username, name, email, number, password
    username = request.args.get('user','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    otp = random.randint(1000,5000)
    print(otp)
    msg = EmailMessage()
    msg.set_content("Your OTP is : "+str(otp))
    msg['Subject'] = 'OTP'
    msg['From'] = "evotingotp4@gmail.com"
    msg['To'] = email
    
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("evotingotp4@gmail.com", "xowpojqyiygprhgr")
    s.send_message(msg)
    s.quit()
    return render_template("val.html")

@app.route('/predict_lo', methods=['POST'])
def predict_lo():
    global otp, username, name, email, number, password
    if request.method == 'POST':
        message = request.form['message']
        print(message)
        if int(message) == otp:
            print("TRUE")
            con = sqlite3.connect('signup.db')
            cur = con.cursor()
            cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
            con.commit()
            con.close()
            return render_template("signin.html")
    return render_template("signup.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("home.html")
    else:
        return render_template("signin.html")

@app.route("/notebook")
def notebook1():
    return render_template("Notebook.html")

def vibeAnnotate(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 10, 120])
    upper_red = np.array([15, 255, 255])
    mask = cv2.inRange (hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        for c in contours:
            #red_area = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            if w >= 5 and h >= 10:
                cv2.rectangle(img,(x, y),(x+w, y+h),(0, 0, 255), 2)
    return img  

@app.route('/predict2', methods=['POST'])
def predict2():
    if request.method == 'POST':
        image_file = request.files['files']
        if image_file:
            image = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
            
            # Perform prediction
            img = cv2.resize(image, (32, 32))
            im2arr = np.array(img)
            im2arr = im2arr.reshape(1, 32, 32, 3)
            img = np.asarray(im2arr)
            img = img.astype('float32')
            img = img / 255.0
            prediction = model.predict(img)
            predicted_class = np.argmax(prediction)
            
            # Annotate if fire detected
            if predicted_class == 1:
                image = vibeAnnotate(image)
            
            # Save the annotated image
            result_image_path = os.path.join('static/test.jpg')
            cv2.imwrite(result_image_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Display prediction result
            return render_template('prediction.html', result_image_path=result_image_path, predicted_class=('Fire Detected' if predicted_class == 1 else 'No Fire'))

    return render_template('index.html')






if __name__ == "__main__":
    app.run(debug=True)
