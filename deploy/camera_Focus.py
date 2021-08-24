import subprocess
import os
import sys
from subprocess import Popen, PIPE
import numpy as np
from PIL import Image
import re
from string import digits

syringeRack =[0,0,0,0,0,0]

classificationSyringeRack = [0,0,0,0,0,0,0,0,0,0,0,0]

gotSyringeBool = False

pattern = r'[0-9]'

def getImage():
    os.system('raspistill -o testImage.jpg')

def crop_image(input_image, output_image, start_x, start_y, width, height):
    input_img = Image.open(input_image)
    input_img = input_img.transpose(Image.ROTATE_270)
    box = (start_x, start_y, start_x + width, start_y + height)
    output_img = input_img.crop(box)
    output_img.save(output_image +".jpg")

def saveImgSlotA():
    # getImage()
    crop_image("testImage.jpg","testImageSlot", 400, 400, 780, 2000)

def saveImgSlotB():
    # getImage()
    crop_image("testImage.jpg","testImageSlot", 600, 400, 780, 2000)

def classifyPresenceOfSyringe():
    # getImage()
    result = ""
    # input image: GotSyringe.jpg - for presence of syringe | NoSyringe.jpg = for absence of syringe | GotSyringe_cropped.jpg - for cropped image
    output = subprocess.run(['python3 classify_image.py --model classify_presence_of_syringe/model_edgetpu.tflite --labels classify_presence_of_syringe/labels.txt --input classify_presence_of_syringe/GotSyringe.jpg'], shell=True, capture_output=True)
    mainOutput = output.stdout.decode()
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    classification = re.sub("[^a-zA-Z0-9]+", "",new_mstr)
    finalOutput = re.sub(pattern, '', classification)

    return finalOutput


def classifySyringeType():
    # getImage()
    result = ""
    # input image: DirtySyringe.jpg - for dirty syringe | WetSyringe.jpg - for wet syringe | DrySyringe.jpg - for dry syringe
    # default image: takes from saveImageSlotA or B as they will crop the default test image out
    output = subprocess.run(['python3 classify_image.py --model classify_syringe_cleanliness/model_edgetpu.tflite --labels classify_syringe_cleanliness/labels.txt --input testImageSlot.jpg'], shell=True, capture_output=True)
    mainOutput = output.stdout.decode()
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    classification = re.sub("[^a-zA-Z0-9]+", "",new_mstr)
    result = re.sub(pattern, '', classification)
    
    return result

def verifyPresenceOfSyringe():
    for i in range(0,6):
        syringeRack[i] = classifyPresenceOfSyringe()
        if syringeRack[i] == 'Syringe':
            gotSyringeBool = True
    # print(syringeRack)

    if gotSyringeBool == True:
        print("Syringe Tubes/Plungers detected. Initiating cleaning operation.")

    else:
        print("Please place at least 1 Syringe Tube/Plungers on the syringe rack to begin cleaning.")

def verifyClassificationOfSyringe():
    for i in range(0,12):
        classificationSyringeRack[i] = classifySyringeType()
        # get Syringe tube on left side
        if i in (0, 2, 4, 6, 8, 10, 12):
            saveImgSlotA()
            classificationSyringeRack[i] = classifySyringeType()
        
        # get Syringe plunger on right side
        elif i in (1, 3, 5, 7, 9, 11):
            saveImgSlotB()
            classificationSyringeRack[i] = classifySyringeType()

    # print(classificationSyringeRack)

    for i in range(0,12):
        if classificationSyringeRack[i] == 'Dry':
            print("The Syringe Tube/Plunger at slot %d is DRY" % (i+1))

        if classificationSyringeRack[i] == 'Wet':
            print("The Syringe Tube/Plunger at slot %d is WET" % (i+1))

        if classificationSyringeRack[i] == 'Dirty':
            print("The Syringe Tube/Plunger at slot %d is DIRTY" % (i+1))


verifyClassificationOfSyringe()
