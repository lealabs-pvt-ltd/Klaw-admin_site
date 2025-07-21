from flask import Flask, request
app = Flask(__name__)

@app.route('/api/basic_info', methods=['POST'])
def basic_info():
    print("Received basic_info:", request.json)
    return {"status": "success"}, 200

@app.route('/api/course_outcome', methods=['POST'])
def course_outcome():
    print("Received course_outcome:", request.json)
    return {"status": "success"}, 200

@app.route('/api/syllabus', methods=['POST'])
def syllabus():
    print("Received syllabus:", request.json)
    return {"status": "success"}, 200

@app.route('/api/questions', methods=['POST'])
def questions():
    print("Received questions:", request.json)
    return {"status": "success"}, 200

@app.route('/api/course_materials', methods=['POST'])
def course_materials():
    print("Received course_materials:", request.form, request.files)
    return {"status": "success"}, 200

@app.route('/api/process_file', methods=['POST'])
def process_file():
    print("Received process_file:", request.json)
    return {"status": "success"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)