import subprocess
import os
import sys
from subprocess import Popen, PIPE
import numpy as np
from PIL import Image

syringeRack =[0,0,0,0,0,0]

classificationSyringeRack = [0,0,0,0,0,0,0,0,0,0,0,0]

def getImage():
    os.system('raspistill -o testImage.jpg')

def crop_image(input_image, output_image, start_x, start_y, width, height):
    
    input_img = Image.open(input_image)
    input_img = input_img.transpose(Image.ROTATE_270)
    box = (start_x, start_y, start_x + width, start_y + height)
    output_img = input_img.crop(box)
    output_img.save(output_image +".jpg")

def saveImgSlotA():
    crop_image("testOutput.jpg","output", 400, 400, 780, 2000)

def saveImgSlotB():
    crop_image("testOutput.jpg","output", 600, 400, 780, 2000)

def classifyPresenceOfSyringe():
    getImage()
    result = ""
    # input image: GotSyringe.jpg - for presence of syringe | NoSyringe.jpg = for absence of syringe | GotSyringe_cropped.jpg - for cropped image
    output = subprocess.run(['python3 classify_image.py --model classify_presence_of_syringe/model_edgetpu.tflite --labels classify_presence_of_syringe/labels.txt --input classify_presence_of_syringe/GotSyringe.jpg'], shell=True, capture_output=True)

    mainOutput = output.stdout.decode()
    
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    
    return str(new_mstr)


def classifySyringeType():
    getImage()

    result = ""
    
    # input image: DirtySyringe.jpg - for dirty syringe | WetSyringe.jpg - for wet syringe | DrySyringe.jpg - for dry syringe
    output = subprocess.run(['python3 classify_image.py --model classify_syringe_cleanliness/model_edgetpu.tflite --labels classify_syringe_cleanliness/labels.txt --input classify_syringe_cleanliness/DrySyringe.jpg'], shell=True, capture_output=True)

    mainOutput = output.stdout.decode()
    
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    
    return str(new_mstr)

classifySyringeType()

# for i in range(0,5):

#     syringeRack[i] = classifyPresenceOfSyringe()
#     if syringeRack[i] == 'Syringe':
#         gotSyringeBool = 1

# print(syringeRack)

# if gotSyringeBool == 1:
#     print("Syringe Tubes/Plungers detected.")
# else:
#     print("Please place at least 1 Syringe Tube/Plungers on the syringe rack to begin cleaning.")


    
# for i in range(0,11):
#     # get Syringe tube on left side
#     if i == 0 or 2 or 4 or 6 or 8 or 10:
#         saveImgSlotA()
#         classificationSyringeRack[i] = classifySyringeType()
    
#     # get Syringe plunger on right side
#     elif i == 1 or 3 or 5 or 7 or 9 or 11:
#         saveImgSlotB()
#         classificationSyringeRack[i] = classifySyringeType()
   
# print(classificationSyringeRack)

# for i in range(0,11):
#     if classificationSyringeRack[i] == 'Dry':
#         print("The Syringe Tube/Plunger at slot %d is DRY", i+1)

#     if classificationSyringeRack[i] == 'Wet':
#         print("The Syringe Tube/Plunger at slot %d is WET", i+1)

#     if classificationSyringeRack[i] == 'Dirty':
#         print("The Syringe Tube/Plunger at slot %d is DIRTY", i+1)



