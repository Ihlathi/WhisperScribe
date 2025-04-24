from flask import Flask, request
import easyocr
from openai import OpenAI

app = Flask(__name__)

AI = OpenAI(base_url='http://localhost:1234/v1', api_key="lm-studio")

def process_text(text):
    return

def get_image_text(image):
    reader = easyocr.Reader(['en']) # instantiates ocr reader object
    results = reader.readtext(image) # reads the image
    return [text for _, text, _ in results] # returns just the text from each tuple entry in the array [location, text, confidence]


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>" # testing endpoint

@app.route('/upload', methods=['POST'])
def upload():
    data = request.data # get request data

    if not data:
        return "No data", 400 # return 400 for no data
    
    with open("image.jpg", 'wb') as file:
        file.write(data) # after opening file as w (write) b (binary), write the file

    print(get_image_text('image.jpg'))

    return "Success", 200 # return 200 for success


if __name__ == '__main__':  
   app.run(host='0.0.0.0', port=5002, debug=True) 
