#Flask app with CORS running for path /doc/<gradeNumber>:<gradeLetter>
import Tools
from flask import jsonify, Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/posterboard/<gradeNum>/<gradeLetter>", methods=['GET'])
def handleFile(gradeNum: str, gradeLetter: str):
    grade = f"{gradeNum}/{gradeLetter}"
    contentPath = f"./content/{grade}/"
    return Tools.assemble(grade)
app.run(port=5500, debug=True)