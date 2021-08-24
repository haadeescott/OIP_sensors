import subprocess
import os
import sys
from subprocess import Popen, PIPE
import numpy as np

syringeRack =[0,0,0,0,0,0]


def getImage():
    os.system('raspistill -o testImage.jpg')

def classifyPresenceOfSyringe():
    # getImage()
    result = ""
    # input image: GotSyringe.jpg - for presence of syringe | NoSyringe.jpg = for absence of syringe
    output = subprocess.run(['python3 classify_image.py --model classify_presence_of_syringe/model_edgetpu.tflite --labels classify_presence_of_syringe/labels.txt --input classify_presence_of_syringe/GotSyringe.jpg'], shell=True, capture_output=True)

    mainOutput = output.stdout.decode()
    
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    
    return str(new_mstr)


def classifySyringeType():
    # getImage()

    result = ""
    
    # input image: DirtySyringe.jpg - for dirty syringe | WetSyringe.jpg - for wet syringe | DrySyringe.jpg - for dry syringe
    output = subprocess.run(['python3 classify_image.py --model classify_syringe_cleanliness/model_edgetpu.tflite --labels classify_syringe_cleanliness/labels.txt --input classify_syringe_cleanliness/DrySyringe.jpg'], shell=True, capture_output=True)

    mainOutput = output.stdout.decode()
    
    new_mstr = "\n".join(mainOutput.splitlines()[-1:])
    
    return str(new_mstr)

# rotating motor value
mV = 0

for i in range(0,6):
    
    post_mV = mv + 60

    if mV == (post_mV):
        syringeRack[i] = classifyPresenceOfSyringe()
    

print(syringeRack)
    
for i in range(0,6):

    syringeRack[i] = classifySyringeType()

print(syringeRack)


