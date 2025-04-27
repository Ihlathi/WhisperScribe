from PIL import Image as image

def preprocess_image(image_path):
    # crop to top line
    original_image = image.open(image_path)
    crop_size = (0, 260, 1600, 600)
    cropped_image = original_image.crop(crop_size)
    preprocessed_image = cropped_image.rotate(180)
    preprocessed_image.save("processed_image.jpg")
    print("image preprocessed")
