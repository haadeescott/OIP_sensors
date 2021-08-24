from PIL import Image

def crop_image(input_image, output_image, start_x, start_y, width, height):
    
    input_img = Image.open(input_image)

    # input_img = input_img.transpose(Image.ROTATE_90)
    box = (start_x, start_y, start_x + width, start_y + height)
    output_img = input_img.crop(box)
    output_img.save(output_image +".jpg")

def main():
    # crop 1st slot
    # crop_image("popo4.jpg","new_output2", 900, 350, 1000, 2000)
    # crop 2nd slot
    crop_image("popo4.jpg","new_output3", 1600, 350, 600, 2000)

if __name__ == '__main__': main()