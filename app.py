import os
import Tools
from flask import jsonify, Flask, request   # type: ignore
from flask_cors import CORS                 # type: ignore
from werkzeug.utils import secure_filename  # type: ignore
from Tools import *

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.abspath("./content")
UPLOAD_FOLDER = './content/'  # Define the folder where uploaded files will go
ALLOWED_EXTENSIONS = {'docx', 'doc', 'xls', 'xlsx', 'pdf', 'md'}  # Allowed file types



# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload/<gradeLetter>/<gradeNumber>", methods=["POST"])
def handleUploadFile(gradeLetter: str, gradeNumber: str):
    """
    Handles file upload, converts it to Markdown, and moves the file 
    to the appropriate grade-specific folder.
    """
    # Define grade path (e.g., "9/B")
    grade = f"{gradeLetter}/{gradeNumber}"

    # Check if the request contains a file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file was selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Validate the file type
    if file and allowed_file(file.filename):
        # Sanitize filename
        filename = secure_filename(file.filename)

        # Define the temporary folder and file path
        temp_folder = os.path.join(UPLOAD_FOLDER, 'temp')
        temp_path = os.path.join(temp_folder, filename)

        # Ensure the temp folder exists
        os.makedirs(temp_folder, exist_ok=True)

        try:
            # Save the uploaded file to the temp folder
            file.save(temp_path)
            log(
                message=f"Uploaded file {filename} saved to temporary folder.",
                app_route=f"/upload/{gradeLetter}/{gradeNumber}",
                ip=request.remote_addr
            )

            # Attempt to convert the file to Markdown
            try:
                converted_temp_path = convert_to_markdown(temp_path)

                # Validate that the converted file exists
                if not converted_temp_path or not os.path.exists(converted_temp_path):
                    raise FileNotFoundError(f"Converted file does not exist: {converted_temp_path}")

                # Define the grade folder and ensure it exists
                grade_folder = os.path.join(UPLOAD_FOLDER, grade)
                os.makedirs(grade_folder, exist_ok=True)

                # Move the converted Markdown file to the grade folder
                converted_filename = os.path.basename(converted_temp_path)
                converted_path = os.path.join(grade_folder, converted_filename)
                os.rename(converted_temp_path, converted_path)

                log(
                    message=f"File {filename} successfully converted to Markdown and moved to {converted_path}.",
                    app_route=f"/upload/{gradeLetter}/{gradeNumber}",
                    ip=request.remote_addr
                )
                os.remove(f"./content/temp/{filename}")
                return jsonify({
                    "success": f"File {filename} uploaded, converted to Markdown, and saved to {converted_path}"
                }), 200

            except Exception as e:
                log(
                    message=f"Error converting file {filename} to Markdown: {str(e)}",
                    app_route=f"/upload/{gradeLetter}/{gradeNumber}",
                    ip=request.remote_addr
                )
                return jsonify({"error": f"Failed to convert the file to Markdown: {str(e)}"}), 500

        except Exception as e:
            log(
                message=f"Failed to upload file {filename}: {str(e)}",
                app_route=request.path,
                ip=request.remote_addr
            )
            return jsonify({"error": f"Failed to save the file: {str(e)}"}), 500

    # If the file type is invalid
    return jsonify({"error": "Invalid file type"}), 400


# Route for handling posterboard files
@app.route("/posterboard/<gradeNum>/<gradeLetter>", methods=["GET"])
def handle_file(gradeNum: str, gradeLetter: str):
    if gradeNum in [".", ".."] or gradeLetter in [".", ".."]:
        log(message="Recieved request, trying to access parent folder", ip=request.remote_addr, app_route=request.path)
        return jsonify({"error": "Bad request"}), 400
    grade = f"{gradeNum}/{gradeLetter}"
    return Tools.assemble(grade=grade)

# Route for displaying the upload page

@app.route("/manage/", methods=['GET'])
def show_manage_page():
    log(message="Accesed Management page", ip=request.remote_addr, app_route=request.path)
    return Tools.html("./web/management/index.html", "./web/management/management.css")

# Route for fetching the directory tree
@app.route("/get/tree/", methods=["GET"])
def tree():
    path = request.args.get("path", "").strip("/")
    full_path = os.path.abspath(os.path.join(BASE_DIR, path))

    # Validate that full_path is within BASE_DIR
    if not full_path.startswith(BASE_DIR) or not os.path.isdir(full_path):
        return jsonify({"error": "Invalid directory path"}), 400

    try:
        def build_tree(directory):
            tree = {"name": os.path.basename(directory), "type": "directory", "children": []}
            for entry in sorted(os.listdir(directory)):
                entry_path = os.path.join(directory, entry)
                if os.path.isdir(entry_path):
                    tree["children"].append(build_tree(entry_path))
                else:
                    tree["children"].append({"name": entry, "type": "file"})
            return tree

        # Build directory tree from the BASE_DIR
        tree = build_tree(full_path)
        log(message="Request tree", ip=request.remote_addr, app_route=request.path)
        return jsonify(tree), 200

    except Exception as e:
        return jsonify({"error": f"Unable to read directory: {str(e)}"}), 500

# Route for fetching the content of a file
@app.route("/get/file/", methods=["GET"])
def get_file():
    
    path = request.args.get("path", "").strip("/")
    requested_path = os.path.abspath(os.path.join(BASE_DIR, path))
    print(f"Request file: {requested_path}")
    # Validate that the path is within the base directory and is a file
    if not os.path.isfile(requested_path) or not requested_path.startswith(BASE_DIR):
        return jsonify({"error": "Invalid file path"}), 400

    try:
        with open(requested_path, "r", encoding="utf-8") as file:
            content = file.read()
        log(message="Request tree", ip=request.remote_addr, app_route=request.path)
        return jsonify({"content": content}), 200
        
    except Exception as e:
        return jsonify({"error": f"Unable to read file: {str(e)}"}), 500



def main(port: int, debug: bool):
    app.run(port=port, debug=debug)