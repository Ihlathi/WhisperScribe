import easyocr

def get_image_text(image):
    reader = easyocr.Reader(['en']) # instantiates ocr reader object
    results = reader.readtext(image, rotation_info = [90, 180, 270]) # flips and reads the image
    text = "".join (text + " " for _, text, _ in results)
    return text # returns just the text from each tuple entry in the array [location, text, confidence]