import subprocess
import os
import sys
from subprocess import Popen, PIPE
import numpy as np
from PIL import Image
import re
from string import digits
import bluetooth
import time

rotationBuffer = '0'

# Bluetooth address of Main RPi
bd_addr = "B8:27:EB:1F:9C:84"

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
port1 = 1
port2 = 2

server_sock.bind(("",port2))
server_sock.listen(1)
otherClient_sock, address = server_sock.accept()
sock.connect((bd_addr, port1))


syringeRack =[0,0,0,0,0,0]

classificationSyringeRack = [0,0,0,0,0,0]
bufferArray1 = [0,0,0,0,0,0]
bufferArray2 = [0,0,0,0,0,0]

gotSyringeBool = False

pattern = r'[0-9]'

# Use RPi Camera to take picture
# Most methods use getImage but for demonstration purpose, the program will be fed a set of 2 curated images below
def getImage():
    os.system('raspistill -o sample_image.jpg')

def crop_image(input_image, output_image, start_x, start_y, width, height):
    input_img = Image.open(input_image)
    box = (start_x, start_y, start_x + width, start_y + height)
    output_img = input_img.crop(box)
    output_img.save(output_image +".jpg")

def saveImgSlotA():
    # getImage()
    # Crops out the Wet Syringe Tube portion of the picture for base_Wet.jpg
    crop_image("base_Wet.jpg","Cropped_Sample_ImageSlot", 1000, 210, 570, 2050)

    # Crops out the Dry Syringe Tube portion of the picture for base_Dry.jpg
    # crop_image("base_Dry.jpg","Cropped_Sample_ImageSlot", 970, 210, 570, 2050)

    # Crops out the Dirty Syringe Tube portion of the picture for base_Dirty.jpg
    # crop_image("base_Dirty.jpg","Cropped_Sample_ImageSlot", 1370, 210, 570, 2050)

def saveImgSlotB():
    # getImage()

    # Crops out the Plunger portion of the picture for base_Wet.jpg/base_Dry.jpg/base_Dirty.jpg
    crop_image("base_Wet.jpg","Cropped_Sample_ImageSlot", 1770, 210, 570, 2050)
    

def classifyPresenceOfSyringe():
    # getImage()
    result = ""
    data = otherClient_sock.recv(1024)
    global rotationBuffer
    rotationBuffer = data.decode()
    print("Received signal from Main RPi. Taking new picture from syringe rack.")
    time.sleep(3)
    if rotationBuffer == '5':
        # input image: GotSyringe.jpg - for presence of syringe | NoSyringe.jpg = for absence of syringe | GotSyringe_cropped.jpg - for cropped image
        # Below is the OS command line to run the classify_image script while feeding a curated image with full presence of Syringes on the syringe rack
        output = subprocess.run(['python3 classify_image.py --model classify_presence_of_syringe/model_edgetpu.tflite --labels classify_presence_of_syringe/labels.txt --input classify_presence_of_syringe/GotSyringe.jpg'], shell=True, capture_output=True)
        mainOutput = output.stdout.decode()
        new_mstr = "\n".join(mainOutput.splitlines()[-1:])
        classification = re.sub("[^a-zA-Z0-9]+", "",new_mstr)
        finalOutput = re.sub(pattern, '', classification)
        
        return finalOutput
    else:
        print("Fail")


def classifySyringeType():
    # getImage()
    result = ""
    # input image: DirtySyringe.jpg - for dirty syringe | WetSyringe.jpg - for wet syringe | DrySyringe.jpg - for dry syringe
    # default image: takes from saveImageSlotA or B as they will crop the default test image out
    output = subprocess.run(['python3 classify_image.py --model classify_syringe_cleanliness/model_edgetpu.tflite --labels classify_syringe_cleanliness/labels.txt --input Cropped_Sample_ImageSlot.jpg'], shell=True, capture_output=True)
    mainOutput = output.stdout.decode()
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    classification = re.sub("[^a-zA-Z0-9]+", "",new_mstr)
    result = re.sub(pattern, '', classification)
    return result


def verifyPresenceOfSyringe():
    global gotSyringeBool
    for i in range(0,6):
        syringeRack[i] = classifyPresenceOfSyringe()
        if syringeRack[i] == 'Syringe':
            gotSyringeBool = True
            sock.send("1")
        elif syringeRack[i] == 'Not Syringe':
            sock.send("0")

    if gotSyringeBool == True:
        print("Syringe Tubes/Plungers detected. Washing Syringes.")

    else:
        print("Please place at least 1 Syringe Tube/Plungers on the syringe rack to begin cleaning.")

def verifyClassificationOfSyringe():
    
    for i in range(0,6):
        result=""
        result1=""
        result2=""
        
        data = otherClient_sock.recv(1024)
        global rotationBuffer
        rotationBuffer = data.decode()
        
        time.sleep(3)
        if rotationBuffer == '6':
            print("Received signal from Main RPi. Taking picture...")
            saveImgSlotA()
            classificationSyringeRack[i] = classifySyringeType()
            bufferArray1[i] = classificationSyringeRack[i]
            if classificationSyringeRack[i] == 'Dirty':
                result1 = '0'
            elif classificationSyringeRack[i] == 'Dry':
                result1 = '1'
            elif classificationSyringeRack[i] == 'Wet':
                result1 = '2'
            
            saveImgSlotB()
            classificationSyringeRack[i] = classifySyringeType()
            bufferArray2[i] = classificationSyringeRack[i]
            if classificationSyringeRack[i] == 'Dirty':
                result2 = '0'
            elif classificationSyringeRack[i] == 'Dry':
                result2 = '1'
            elif classificationSyringeRack[i] == 'Wet':
                result2 = '2'
            
            result = result1+result2
            print("Sending classification result to Main RPi")
            sock.send(result)
            rotationBuffer = '0'


    finalClassificationOutput = np.dstack((bufferArray1,bufferArray2)).flatten()
    countDirty = 0
    countDry = 0
    countWet = 0
    for i in range(0,12):
        if finalClassificationOutput[i] == 'Dry':
            countDry += 1

        if finalClassificationOutput[i] == 'Wet':
            countWet += 1

        if finalClassificationOutput[i] == 'Dirty':
            countDirty += 1
            
    print(f"\nDirty: {countDirty} | Wet: {countWet} | Dry: {countDry}")


# Verifies the presence of Syringes on the Syringe Rack
verifyPresenceOfSyringe()
print("Completed Washing of Syringes. \n")

# Once Syringes are detected, boolean is returned
if gotSyringeBool == True:
    print("Drying Syringes now...")
    print("Loading...\n")

    # Classifies Syringes 
    verifyClassificationOfSyringe()
    print("\nCompleted Classification of Syringes.")
else:
    print("Please insert syringe tubes and plungers into the syringe rack.")

server_sock.close()