import easyocr

def get_image_text(image):
    reader = easyocr.Reader(['en']) # instantiates ocr reader object
    results = reader.readtext(image) # reads the image
    text = "".join (text + " " for _, text, _ in results)
    print("ocr processed, text: " + text)
    return text # returns just the text from each tuple entry in the array [location, text, confidence]