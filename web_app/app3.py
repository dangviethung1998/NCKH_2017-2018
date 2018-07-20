import eventlet
eventlet.monkey_patch()
import RPi.GPIO as gpio
from flask import Flask, render_template, request,Response
from flask_socketio import SocketIO, emit, send
from flask_mail import Mail,Message
import os
import time
import sys
import cv2
import numpy as np
import math
import serial
gpio.setwarnings(False)

x =""
tmphm =[]

app = Flask(__name__)

mail_settings = {
	"MAIL_SERVER": "smtp.gmail.com",
	"MAIL_PORT": 465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	"MAIL_USERNAME": "",
	"MAIL_PASSWORD": ""
}
app.config.update(mail_settings)
mail = Mail(app)
socketio = SocketIO(app)

#define gpio for raspberry pi
c1=27
c2=22
c3=5
c4=6
gpio.setmode(gpio.BCM)
trig = 24
echo = 23
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)

gpio.setup(c1, gpio.OUT)
gpio.setup(c2, gpio.OUT)
gpio.setup(c3, gpio.OUT)
gpio.setup(c4, gpio.OUT)

gpio.output(c1 , False)
gpio.output(c2 , False)
gpio.output(c3, False)
gpio.output(c4, False)

ser = serial.Serial('/dev/ttyACM0',9600)

def send_email():
	msg = Message(subject="",
			sender=app.config.get("MAIL_USERNAME"),
			recipients=[""],
			body="")
	mail.send(msg)

#basic control
def left_side():
	gpio.output(c1, True)
	gpio.output(c2,	True)
	gpio.output(c3, False)
	gpio.output(c4, True)
	return 'true'
def right_side():
	gpio.output(c1 , False)
	gpio.output(c2 , True)
	gpio.output(c3 , False)
	gpio.output(c4 , False)
	return 'true'
def up_side():
	gpio.output(c1 , False)
	gpio.output(c2 , True)
	gpio.output(c3 , False)
	gpio.output(c4 , True)
	return 'true'
def down_side():
	gpio.output(c1 , True)
	gpio.output(c2 , False)
	gpio.output(c3 , True)
	gpio.output(c4 , False)
	return 'true'
def go_left():
	gpio.output(c1 , True)
	gpio.output(c2 , False)
	gpio.output(c3 , False)
	gpio.output(c4 , True)
	return 'true'
def go_right():
	gpio.output(c1 , False)
	gpio.output(c2 , True)
	gpio.output(c3 , True)
	gpio.output(c4 , False)
	return 'true'
def stop():
	gpio.output(c1 , False)
	gpio.output(c2 , False)
	gpio.output(c3 , False)
	gpio.output(c4 , False)
	return  'true'

#measure distance using HC-SR04
thread = None
def measure():
    gpio.output(trig, True)
    time.sleep(0.00001)
    gpio.output(trig, False)
    start = time.time()

    while gpio.input(echo)==0:
        start = time.time()

    while gpio.input(echo)==1:
        stop = time.time()

    elapsed = stop-start
    distance = elapsed * 17150
    distance = round(distance,2)
    return distance
def go_sensor():
	while 1:
		global x
        	x = measure()
		print x
		eventlet.sleep(1)

#read temp and humid from arduino through serial
def humid_temp():
	while 1:
		global tmphm
		tmphm = ser.readline().strip("\r\n").strip().split("+")
		eventlet.sleep(1)

def emit_to_client():
	emit('server side', str(x))

thread1 = None

#real-time updating data 
@socketio.on('something')
def send_all(json):
    print "receive: " + str(json)
    time.sleep(1)
    global thread
    global thread1
    if thread is None:
		thread = socketio.start_background_task(target = go_sensor) 
    if thread1 is None:
		thread1 = socketio.start_background_task(target = humid_temp) 
	emit('server side',{'data': str(x), 'data2': tmphm})

@socketio.on('update side')
def recvmess(msg):
    print "receive: " +str(msg)

#config route
@app.route("/")
def index():
	send_email()
	return render_template("index.html")

@app.route("/control", methods = ["GET","POST"])
def control():
	if request.method == "GET":
		return render_template("notfound.html")
	else:
		name = request.form.get("email")
		return render_template("selection.html")

@app.route("/manual", methods = ["GET","POST"])
def manual():
	if request.method == "GET":
	 	return render_template("notfound.html")
	else:	
		return render_template("controlrasp.html")

@app.route("/auto", methods = ["GET","POST"])
def auto():
	if request.method == "GET":
	 	return render_template("notfound.html")
	else:
		return render_template("autorasp.html")

@app.errorhandler(404)
def page_not_found(error):
	app.logger.error('Page not found: %s', (request.path))
	return render_template("notfound.html"),404

@app.route('/controller',methods=["GET", "POST"] )
def controller():
	act = request.form.get("act")
	if  act == 'stop' :
		stop()
	elif  act == 'down' : 
		down_side()
	elif  act == 'up' :
		up_side()
	elif  act == 'left' :
		left_side()
	elif  act == 'right' :
		right_side()
	elif  act == 'goleft' : 
		go_left()
	elif  act == 'goright' : 
		go_right()
	return Response()    

if __name__ == "__main__":
	print "Starting..."
	socketio.run(app, host = "0.0.0.0", port = 5000, debug = True)
