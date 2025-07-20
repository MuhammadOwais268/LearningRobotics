# File: server.py

from flask import Flask, request, jsonify
import os
import json
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- CONFIGURATION & SETUP ---
DATA_DIR = "server_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CLASS_DIR = os.path.join(DATA_DIR, "classes")

# In-memory stores (cleared on server restart)
SESSIONS = {}  # { "session_token": "user_email" }
ACTIVE_USERS_IN_CLASS = {} # { "class_code": { "user_email": last_seen_timestamp }}

def setup_server():
    """Create necessary directories and files if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CLASS_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    print("Server setup complete. Ready to accept connections.")

def get_user_from_token(token):
    """Finds a user's email from their session token."""
    return SESSIONS.get(token)

def cleanup_inactive_users():
    """Removes users who haven't pinged recently."""
    now = time.time()
    for class_code, users in list(ACTIVE_USERS_IN_CLASS.items()):
        for email, last_seen in list(users.items()):
            if now - last_seen > 15: # 15-second timeout
                del ACTIVE_USERS_IN_CLASS[class_code][email]

# --- USER MANAGEMENT ENDPOINTS ---

@app.route("/signup", methods=['POST'])
def signup():
    data = request.json
    with open(USERS_FILE, 'r+') as f:
        users = json.load(f)
        if data['email'] in users:
            return jsonify({"success": False, "message": "Email already exists."}), 400
        
        # Check developer key for developer role
        if data['role'] == 'developer':
            from src.config import DEVELOPER_SECRET_KEY # A bit of a hack, but fine for simple app
            if data.get('developer_key') != DEVELOPER_SECRET_KEY:
                return jsonify({"success": False, "message": "Invalid Developer Key."}), 403

        users[data['email']] = {
            "password_hash": generate_password_hash(data['password']),
            "role": data['role']
        }
        f.seek(0)
        json.dump(users, f, indent=4)
    return jsonify({"success": True, "message": "User created successfully."})

@app.route("/login", methods=['POST'])
def login():
    data = request.json
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    user_data = users.get(data['email'])
    if not user_data or not check_password_hash(user_data['password_hash'], data['password']):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401
    
    token = str(uuid.uuid4())
    SESSIONS[token] = data['email']
    return jsonify({"success": True, "token": token, "role": user_data['role']})

# --- CLASSROOM MANAGEMENT ENDPOINTS ---

@app.route("/class/create", methods=['POST'])
def create_class():
    token = request.headers.get('Authorization', '').split(' ')[-1]
    user_email = get_user_from_token(token)
    if not user_email: return jsonify({"success": False, "message": "Not authenticated."}), 401

    class_code = f"CLASS-{uuid.uuid4().hex[:4].upper()}"
    class_file = os.path.join(CLASS_DIR, f"{class_code}.json")
    
    with open(class_file, 'w') as f:
        json.dump(request.json.get("curriculum"), f, indent=4)
    
    return jsonify({"success": True, "class_code": class_code})

@app.route("/class/<class_code>", methods=['GET'])
def get_class(class_code):
    token = request.headers.get('Authorization', '').split(' ')[-1]
    user_email = get_user_from_token(token)
    if not user_email: return jsonify({"success": False, "message": "Not authenticated."}), 401

    # Mark user as active
    now = time.time()
    if class_code not in ACTIVE_USERS_IN_CLASS:
        ACTIVE_USERS_IN_CLASS[class_code] = {}
    ACTIVE_USERS_IN_CLASS[class_code][user_email] = now

    class_file = os.path.join(CLASS_DIR, f"{class_code}.json")
    if not os.path.exists(class_file):
        return jsonify({"success": False, "message": "Class not found."}), 404
        
    with open(class_file, 'r') as f:
        curriculum = json.load(f)
    return jsonify({"success": True, "curriculum": curriculum})

@app.route("/class/<class_code>/update", methods=['POST'])
def update_class(class_code):
    token = request.headers.get('Authorization', '').split(' ')[-1]
    user_email = get_user_from_token(token)
    if not user_email: return jsonify({"success": False, "message": "Not authenticated."}), 401

    # Authorization check: only developers can update
    with open(USERS_FILE, 'r') as f: users = json.load(f)
    if users[user_email]['role'] != 'developer':
        return jsonify({"success": False, "message": "Permission denied."}), 403

    class_file = os.path.join(CLASS_DIR, f"{class_code}.json")
    with open(class_file, 'w') as f:
        json.dump(request.json.get("curriculum"), f, indent=4)
        
    return jsonify({"success": True, "message": "Class updated."})

@app.route("/class/<class_code>/student_count", methods=['GET'])
def student_count(class_code):
    token = request.headers.get('Authorization', '').split(' ')[-1]
    user_email = get_user_from_token(token)
    if not user_email: return jsonify({"success": False, "message": "Not authenticated."}), 401

    # Update this user's 'last_seen' time
    if class_code in ACTIVE_USERS_IN_CLASS:
        ACTIVE_USERS_IN_CLASS[class_code][user_email] = time.time()
    
    cleanup_inactive_users()
    
    count = 0
    if class_code in ACTIVE_USERS_IN_CLASS:
        # Don't count the developer in the student count
        with open(USERS_FILE, 'r') as f: users = json.load(f)
        for email in ACTIVE_USERS_IN_CLASS[class_code]:
            if users[email]['role'] == 'student':
                count += 1
                
    return jsonify({"success": True, "student_count": count})

if __name__ == "__main__":
    setup_server()
    app.run(host='0.0.0.0', port=5000)