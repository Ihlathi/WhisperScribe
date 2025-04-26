from PIL import Image as image

def preprocess_image(image_path):
    # crop to top line
    original_image = image.open(image_path)
    crop_size = (0, 900, 1600, 1200)
    cropped_image = original_image.crop(crop_size)
    cropped_image.save("processed_image.jpg")
