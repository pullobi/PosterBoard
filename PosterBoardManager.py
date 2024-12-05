import Tools
import Database
from flask import jsonify, Flask, request, make_response, redirect, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

style = "./web/style.css"

# Main app for handling GET requests called by the digital boards/clients.
@app.route("/posterboard/<gradeNum>/<gradeLetter>", methods=['GET'])
def handleFile(gradeNum: str, gradeLetter: str):
    if gradeNum in [".", ".."] or gradeLetter in [".", ".."]:
        return jsonify({"error": "Bad request"}), 400
    grade = f"{gradeNum}/{gradeLetter}"
    contentPath = f"./content/{grade}/"
    return Tools.assemble(grade), 200


@app.route("/login/", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    auth = Database.checkUser(username=username, password=password)
    if auth:
        print(f"Authorization correct: user {username} for password {password}, trying to save cookies")
        
        # Create a response and set cookies
        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie("USERNAME", username)
        response.set_cookie("PASSWORD", password)
        return response
    else:
        print(f"Unauthorized User: {username}, {password}")
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/login/")
def redirectToLogin():
    return Tools.html(stylesheet="./web/style.css", path="./web/auth/login.html")


@app.route("/register/")
def redirectToRegister():
    return Tools.html(stylesheet="./web.style.css", path="./web/auth/register.html")


@app.route("/register/", methods=['POST'])
def register():
    secret = request.headers.get('Register-Key')
    
    if not secret:
        return jsonify({"error": "No secret key provided in headers."}), 400
    
    with open("secret/register_key", 'r') as file:
        stored_secret = file.read().strip()
        if stored_secret == secret:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            Database.newUser(username=username, password=password)
            return jsonify({"message": "Success"}), 200
        else:
            return jsonify({"error": "Invalid key. Contact administrator."}), 403


@app.route("/upload/")
def showUploadPage():
    username = request.cookies.get("USERNAME")
    password = request.cookies.get("PASSWORD")

    if username and password and Database.checkUser(username, password):
        return Tools.assemble(stylePath=style, HTMLDocPath="./web/upload/index.html")
    else:
        return redirect("/login/")

# Debug routes for user management
@app.route("/debug")
def debug_panel():
    """Display the debug panel with user list and forms."""
    users = Database.listUsers()  # List all users
    return render_template('./web/debug/index.html', users=users, stylesheet=style)

@app.route("/debug/add_user", methods=["POST"])
def add_user():
    """Handle adding a new user."""
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username and password:
        Database.newUser(username, password)
        return redirect("/debug")
    else:
        return jsonify({"error": "Username and password are required."}), 400

@app.route("/debug/delete_user", methods=["POST"])
def delete_user():
    """Handle deleting a user."""
    username = request.form.get("username")
    
    if username:
        Database.deleteUser(username)
        return redirect("/debug")
    else:
        return jsonify({"error": "Username is required."}), 400

@app.route("/web/style.css")
def style():
    with open("./web/style.css", 'r') as file:
        return file.read()

# Run the Flask app
if __name__ == "__main__":
    Database.initialize_database()
    app.run(port=5500, debug=True)