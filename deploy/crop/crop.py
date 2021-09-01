from PIL import Image

def crop_image(input_image, output_image, start_x, start_y, width, height):
    
    input_img = Image.open(input_image)

    # input_img = input_img.transpose(Image.ROTATE_90)
    box = (start_x, start_y, start_x + width, start_y + height)
    output_img = input_img.crop(box)
    output_img.save(output_image +".jpg")

def main():
    # crop 1st slot
    # crop_image("test100.jpg","test100_crop", 970, 210, 570, 2050) //DRY
    # crop_image("test101.jpg","test101_crop", 1000, 210, 570, 2050) //WET
    # DIRTY
    # crop_image("test102.jpg","test102_crop", 1370, 210, 570, 2050) 
    # crop 2nd slot
    # crop_image("test100.jpg","test100_crop2", 1770, 210, 570, 2050) 
    # crop_image("testDirty2.jpg","testDirty2_crop", 0, 0, 300, 700)

if __name__ == '__main__': main()