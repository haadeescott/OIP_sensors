from PIL import Image

def crop_image(input_image, output_image, start_x, start_y, width, height):
    
    input_img = Image.open(input_image)
    input_img = input_img.transpose(Image.ROTATE_270)
    box = (start_x, start_y, start_x + width, start_y + height)
    output_img = input_img.crop(box)
    output_img.save(output_image +".png")

def main():
    crop_image("20210823_154644.jpg","test_output", 600, 600, 780, 2000)

if __name__ == '__main__': main()