from flask import Flask, request

app = Flask(__name__)

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

    main.do_thing()

    return "Success", 200 # return 200 for success


if __name__ == '__main__':  
   app.run(host='0.0.0.0', port=5002, debug=True) 
