from tkinter import *   # Progress Bar UI
from tkinter.ttk import *   # Progress Bar UI
from guizero import App, Text, Box, Window, PushButton  # Main GUI Library
import bluetooth    # Bluetooth communication
import serial   # Serial communication
import time # Time manipulation
import os   # File manipulation

# Characters used for specific purposes
#   0, Stop signal to Arduino
#   1, Start main operation signal to Arduino
#   2, Start sanitize operation signal to Arduino
#   5, First classification (syringe presence) to RPi(ML)
#   6, Second classifcation (classify syringe) to RPi(ML)

# Characters used for ML 
#   0, Dirty
#   1, Dry
#   2, Wet

# Global variables 
running = True  # Start/Stop Main Operation
sanitizeRunning = True # Start/Stop Sanitize Operation
START_TIME = time.time() # Elapsed Time
syringeStatusList = [] # List of detected syringe statuses

# Start Main operation
# Enable/Disable widgets
def StartMainOps():
    global running, START_TIME, syringeStatusList
    syringeStatusList = []
    btnStartMainOps.disable()
    btnStopMainOps.enable()
    btnMainOpsBack.disable()
    btnSyringeStatus.disable()
    ReadCalcEstiamtedTime()
    START_TIME = time.time()
    MainOps()

# Perform main operations (Whole flow)
# Updates widgets 
def MainOps():
    start = time.time()

    # Starting Phase (First 10% of progress bar):
    # - Start Arduino
    # - Send/Receive message to/from RPi(ML)
    # - Send/Receive signals to/from Arduino
    # - Update widgets
    if progressBarMainOps['value'] < 10 and running == True:
        syringeDetected = 0
        SerialComm('1') # Start Arduino
        textMainOpsStatus.value = f"Detecting Syringe(s) Presence 2/12... {progressBarMainOps['value']}%"
        windowMainOps.update()  # Update UI
        syringeDetected += SyringeClassifyOne()

        # First syringe classification (Syringe Presence) and rack rotation (6x)
        for i in range(2, 7):
            textMainOpsStatus.value = f"Detecting Syringe(s) Presence {i*2}/12... {progressBarMainOps['value']}%"
            windowMainOps.update()  # Update UI
            SerialComm('a')
            syringeDetected += SyringeClassifyOne()
        
        print("Syringe Detected: " + str(syringeDetected))

        # If no syringe detected, stop main operation to allow user to put in syringes
        # Else, inform user that a syringe is present by showing on the UI
        if syringeDetected == 0:
            textMainOpsSyringeDetection.value = "No syringe detected!"
            StopMainOps()
            return
        else:
            textMainOpsSyringeDetection.value = "Syringe(s) Detected!"
    
    # Classifying syringe phase (80% of progress bar)
    # - Send/Receive message to/from RPi(ML)
    # - Send/Receive signals to/from Arduino
    # - Update widgets
    if progressBarMainOps['value'] == 80 and running == True:
        if(serial1.in_waiting >0):
            print(serial1.readline())
            textMainOpsStatus.value = f"Classifying Syringe(s) 2/12... {progressBarMainOps['value']}%"
            windowMainOps.update()  # Update UI
            bytesSyringeClass = SyringeClassifyTwo()
            for i in bytesSyringeClass:
                syringeStatusList.append(int(i))

            # Second syringe classification and rack rotation (6x)
            for i in range(2, 7):
                textMainOpsStatus.value = f"Classifying Syringe(s) {i*2}/12... {progressBarMainOps['value']}%"
                windowMainOps.update()  # Update UI
                SerialComm('a')
                bytesSyringeClass = SyringeClassifyTwo()
                for i in bytesSyringeClass:
                    syringeStatusList.append(int(i))
            
            print(syringeStatusList)
            progressBarMainOps['value'] += 10
        else:
            textMainOpsStatus.value = f"Drying... {progressBarMainOps['value']}%"
            boxMainOpsStatus.after(2000, MainOps)
            return

    # Sanitizing phase (90% of progress bar)
    # - Wait for signal from Arduino
    # - Once signal received that sanitization is completed, complete the progress bar
    if progressBarMainOps['value'] == 90 and running == True:
        if(serial1.in_waiting >0):
            print(serial1.readline())
            progressBarMainOps['value'] += 10
        else:
            textMainOpsStatus.value = f"Sanitizing... {progressBarMainOps['value']}%"
            boxMainOpsStatus.after(2000, MainOps)
            return

    # Progress bar moves every 10 seconds until reaches 80%
    if progressBarMainOps['value'] < 80 and running == True:
        progressBarMainOps['value'] += 10
        textMainOpsStatus.value = f"Washing... {progressBarMainOps['value']}%"
        boxMainOpsStatus.after(7000, MainOps)
        return
    
    # Perform operations on completion
    #   - Determine dry/dirty/wet status of every slots in the syringe rack 
    #   - Display the total number of dirty/dry/wet syringes
    #   - Update Widgets
    if progressBarMainOps['value'] == 100:
        btnStopMainOps.disable()
        dirtySyringe = 0
        drySyringe = 0
        wetSyringe = 0
        textMainOpsStatus.value = "Task is completed!"
        completionTime = time.time() - START_TIME
        WriteEstimatedTime(completionTime)
        print(syringeStatusList)
        for idx, val in enumerate(syringeStatusList):
            if val == 0:
                dirtySyringe += 1
                textSyringeDirty.value += f" {idx},"
            elif val == 1:
                drySyringe += 1
                textSyringeDry.value += f" {idx},"
            elif val == 2:
                wetSyringe += 1
                textSyringeWet.value += f" {idx},"

        textSyringeTotal.value = f"Total Dirty: {dirtySyringe}   Dry: {drySyringe}   Wet: {wetSyringe}"
        btnStartMainOps.enable()
        btnMainOpsBack.enable()
        btnSyringeStatus.enable()

    # Measure how long it takes for the processes to run
    end = time.time()
    print(end - start)

# Read, calculate and display average completion time
def ReadCalcEstiamtedTime():
    if os.path.exists("completion_time.txt"):
        with open('completion_time.txt', 'r') as f:
            data = [float(ln.strip()) for ln in f.readlines()]
        avgMins = float(sum(data))/len(data)/60 if len(data) > 0 else 0
        if avgMins != 0:
            textMainOpsEstimatedTime.value = f"Estimated average completion time: {round(avgMins)} mins"
        else:
            textMainOpsEstimatedTime.value = "Estimated average completion time: First Run (~9 mins)"
    else:
        textMainOpsEstimatedTime.value = "Estimated average completion time: First Run (~9 mins)"

# Write and append completion time to txt file
def WriteEstimatedTime(completionTime):
    if os.path.exists("completion_time.txt"):
        with open('completion_time.txt', 'a') as f:
            f.write(str(completionTime) + "\n")
    else:
        with open('completion_time.txt', 'w+') as f:
            f.write(str(completionTime) + "\n")

# Arduino and RPi communication through Serial
def SerialComm(signal):
    print(signal)
    while True:
        serial1.write(signal.encode())
        time.sleep(1)
        if(serial1.in_waiting >0):
            print(serial1.readline())
            break

# RPi and RPi communication through Bluetooth
# First syringe classification to detect if syringes are present or not
def SyringeClassifyOne():
    sock.send("5")
    data = client_sock.recv(1024)
    # print("received [%s]" % data)
    return int(data.decode())

# RPi and RPi communication through Bluetooth
# Second syringe classification to detect if syringes are wet/dry/dirty
def SyringeClassifyTwo():
    sock.send("6")
    data = client_sock.recv(1024)
    return data.decode()

# Stop main operations
# Update widgets
def StopMainOps():
    global running
    running = False
    SerialComm('0')
    progressBarMainOps['value'] = 0
    textMainOpsStatus.value = "Task is stopped"
    textMainOpsEstimatedTime.value = "Estimated completion time: -"
    textMainOpsSyringeDetection.value = "No syringe detected"
    btnStartMainOps.enable()
    btnStopMainOps.disable()
    btnMainOpsBack.enable()
    btnSyringeStatus.disable()

# Start Sanitizing
# Update Widgets
def StartSanitize():
    global sanitizeRunning, START_TIME
    sanitizeRunning = True
    btnStartSanitize.disable()
    btnStopSanitize.enable()
    btnSanitizeBack.disable()
    textSanitizeStatus.value = "Starting..."
    SerialComm('2') # Start Sanitize
    textSanitizeStatus.value = "Sanitizing..."
    START_TIME = time.time()
    Sanitize()

# Show elapsed time every second while sanitizing
def Sanitize():
    currentTime = time.time()
    elapsedTime = currentTime - START_TIME
    if sanitizeRunning == True and elapsedTime <= 960:
        textSanitizeElapsedTime.value = f"Elapsed time: {int(elapsedTime)}s"
        boxSanitizeStatus.after(1000, Sanitize)

# Stop Sanitizing
# Update Widgets
def StopSanitize():
    global sanitizeRunning
    sanitizeRunning = False
    SerialComm('0') # Stop Sanitize
    textSanitizeStatus.value = "Sanitizing stopped!"
    btnStartSanitize.enable()
    btnStopSanitize.disable()
    btnSanitizeBack.enable()

# Serial Comm (Could be /ttyACM0 or /ttyACM1)
serial1 = serial.Serial('/dev/ttyACM0', 9600)

# Bluetooth Connection
server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
recvPort = 1
sendPort = 2
bd_addr = "B8:27:EB:76:32:79"
sock.connect((bd_addr, sendPort))

# Listen and accept incoming Bluetooth connection from the ML RPi
server_sock.bind(("",recvPort))
server_sock.listen(1)
client_sock,address = server_sock.accept()
print("Accepted connection from ",address)

# App intitialization
app = App(title="Power On")

# Initialize windows
windowMain = Window(app, title="Main Menu", visible=False)
windowMainOps = Window(app, title="Wash/Dry/Sanitize", visible=False)
windowSanitize = Window(app, title="Sanitize", visible=False)
windowSyringeStatus = Window(app, title="Syringe Status", visible=False)

# Power On Button
btnPowerOn = PushButton(app, image="OIP_GUI/assets/PowerOn.png", width=200, height=200, command=windowMain.show)

# Main Screen Elements
# Power Off components
boxPowerOff = Box(windowMain, width="fill")
btnPowerOff = PushButton(boxPowerOff, align="right", image="OIP_GUI/assets/PowerOn.png", width=50, height=50, command=windowMain.hide)
textPowerOff = Text(boxPowerOff, text="Power Off", size=10, align="right")

# Features components
boxMainOps = Box(windowMain, align="left", width="fill")
btnMainOps = PushButton(boxMainOps, image="OIP_GUI/assets/Water.png", command=windowMainOps.show)
textMainOps = Text(boxMainOps, text="Wash/Dry/Sanitize")
boxSanitize = Box(windowMain, align="right", width="fill")
btnSanitize = PushButton(boxSanitize, image="OIP_GUI/assets/Light.png", command=windowSanitize.show)
textSanitize = Text(boxSanitize, text="Sanitize")

# Main Ops Menu
# Back Feature
boxMainOpsBack = Box(windowMainOps, width="fill")
btnMainOpsBack = PushButton(boxMainOpsBack, image="OIP_GUI/assets/Arrow.png", align="left", command=windowMainOps.hide)
textMainOpsBack = Text(boxMainOpsBack, text="Back", size=10, align="left")

# Main Ops Status
boxMainOpsStatus = Box(windowMainOps, border=True, width="fill")
textMainOpsStatusTitle = Text(boxMainOpsStatus, text="Task Status")
textMainOpsEstimatedTime = Text(boxMainOpsStatus, text="Estimated completion time: -", size=10)
textMainOpsStatus = Text(boxMainOpsStatus, text="Idling", size=10)
# This bit comes from ttk
# --------------------------------------------------------------------------------
progressBarMainOps = Progressbar(boxMainOpsStatus.tk,orient=HORIZONTAL,length=200,mode='determinate')
progressBarMainOps.pack()
# --------------------------------------------------------------------------------
# Main Ops Syringe Detection Info
boxMainOpsSyringeStatus = Box(windowMainOps, border=True, width="fill")
textMainOpsSyringeStatusTitle = Text(boxMainOpsSyringeStatus, text="Syringe Presence Status")
textMainOpsSyringeDetection = Text(boxMainOpsSyringeStatus, text="No syringe detected", size=10)

# Main Ops Task Operations
btnStartMainOps = PushButton(windowMainOps, text="Start Task", align="left", command=StartMainOps)
btnStopMainOps = PushButton(windowMainOps, text="Stop Task", align="right", enabled=False, command=StopMainOps)
btnSyringeStatus = PushButton(windowMainOps, text="Syringe Status", align="bottom",  enabled=False, command=windowSyringeStatus.show)

# Syringe Status Menu
# Back Feature
boxSyringeStatusBack = Box(windowSyringeStatus, width="fill")
btnSyringeStatusBack = PushButton(boxSyringeStatusBack, image="OIP_GUI/assets/Arrow.png", align="left", command=windowSyringeStatus.hide)
textSyringeStatusBack = Text(boxSyringeStatusBack, text="Back", size=10, align="left")

# Syringe Info
boxSyringeStatus = Box(windowSyringeStatus, border=True, width="fill")
textSyringeStatusTitle = Text(boxSyringeStatus, text="Syringe Status")
textSyringeDirty = Text(boxSyringeStatus, text="Dirty Slot(s):", size=10)
textSyringeDry = Text(boxSyringeStatus, text="Dry Slot(s):", size=10)
textSyringeWet = Text(boxSyringeStatus, text="Wet Slot(s):", size=10)
textSyringeTotal = Text(boxSyringeStatus, text="Total Dirty: -   Dry: -   Wet: -", size=10)

# Sanitize Menu
# Back Feature
boxSanitizeBack = Box(windowSanitize, width="fill")
btnSanitizeBack = PushButton(boxSanitizeBack, image="OIP_GUI/assets/Arrow.png", align="left", command=windowSanitize.hide)
textSanitizeBack = Text(boxSanitizeBack, text="Back", size=10, align="left")

# Sanitize Status
boxSanitizeStatus = Box(windowSanitize, border=True, width="fill")
textSanitizeStatusTitle = Text(boxSanitizeStatus, text="Sanitize Status")
textSanitizeElapsedTime = Text(boxSanitizeStatus, text="Elapsed time: -", size=10)
textSanitizeStatus = Text(boxSanitizeStatus, text="Idling", size=10)

# Task Operations
btnStartSanitize = PushButton(windowSanitize, text="Start Sanitize", align="left", command=StartSanitize)
btnStopSanitize = PushButton(windowSanitize, text="Stop Sanitize", align="right", enabled=False, command=StopSanitize)

app.display()
