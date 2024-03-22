from flask import Flask, redirect, g, render_template, request, session, jsonify, flash, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, is_valid_userName, is_valid_email
import sqlite3
import datetime
import os

# Configure Application
app = Flask(__name__)
DATABASE = "app.db"

#   Configure path to store uploaded folders
UPLOAD_FOLDER = './static/UPLOADS/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Secret Key
app.secret_key = os.urandom(24)

#   Function to create a new folder for each user's files
def create_user_folder(user_id):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

# Configure the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
        return db
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#   Row factory function
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


@app.route("/", methods=["GET","POST"])
def index():
    """SERVE THE DEFAULT HOME PAGE """
    return render_template("index.html")


# WORKER LOGIN
@app.route("/login/worker", methods=["GET", "POST"])
def woker_login():
    """"Log Workers In"""

    name = "Worker"

    conn = get_db()
    db = conn.cursor()

    #   Forget any Previous User Ids
    session.clear()

    #   User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username")
            print("Invalid Username")
            return render_template("worker-login.html", name=name)
        elif not password:
            flash("Must provide password")
            print("Invalid Password")
            return render_template("worker-login.html", name=name)
        
        # Query database for username
        user = db.execute("SELECT * FROM WORKERS WHERE username = ?", (username,)).fetchall()

        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["password_hash"], password):
            flash("Invalid username and/or password")
            return render_template("worker-login.html", name=name)
        
        # If all is good

        # Set the session of the user
        session["user_id"] = user[0]["id"]
        session["last_activity"] = datetime.datetime.now()

        # Commit the changes
        conn.commit()
        conn.close()

        # Redirect user to dashboard
        return redirect("/worker/dashboard/{}".format(user[0]["id"]))
    
    return render_template("worker-login.html", name=name)



@app.route("/login/employer", methods=["GET", "POST"])
def employer_login():
    """"Log Employers In"""
    name = "Employer"
    return render_template("employer-login.html", name=name)

@app.route("/register/employer", methods=["POST", "GET"])
def employer_signup():
    """ REGISTER NEW EMPLOYERS """

    name = "Employer"
    conn = get_db()
    db = conn.cursor()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("password_confirmation")
        first = request.form.get("first_name")
        last = request.form.get("last_name")
        company = request.form.get("company")

        print(f"Data entered:  {username}, {email}, {password}, {confirm_password}, {first}, {last}, {company}")

        if not is_valid_userName(username):
            flash("Username must be at least 4 characters long and contain only letters and numbers")
            return redirect("/register/employer")
        
        if not is_valid_email(email):
            flash("Invalid email address")
            return redirect("/register/employer")
        
        if password != confirm_password:
            flash("Passwords do not match")
            return redirect("/register/employer")
        
        hashed_password = generate_password_hash(password)
        
        db.execute("INSERT INTO EMPLOYERS (username, email, password_hash, first_name, last_name, company) VALUES (?, ?, ?, ?, ?, ?)",
                   (username, email, hashed_password, first, last, company))
        conn.commit()
        conn.close()
        
        flash("You have successfully registered")
        return redirect("/login/employer")
    
    return render_template("employer-sign-up.html", name=name)

        


@app.route("/register/worker", methods=["POST", "GET"])
def wokrer_signup():
    """ REGISTER NEW WORKERS """

    name = "Worker"
    conn = get_db()
    db = conn.cursor()
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("password_confirmation")
        first = request.form.get("first_name")
        last = request.form.get("last_name")

        if not is_valid_userName(username):
            flash("Username must be at least 4 characters long and contain only letters and numbers")
            return redirect("/register/worker")
        
        if not is_valid_email(email):
            flash("Invalid email address")
            return redirect("/register/worker")
        
        if password != confirm_password:
            flash("Passwords do not match")
            return redirect("/register/worker")
        
        hashed_password = generate_password_hash(password)
        
        db.execute("INSERT INTO WORKERS (username, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                   (username, email, hashed_password, first, last))
        conn.commit()
        conn.close()
        
        flash("You have successfully registered")
        return redirect("/login/worker")
    
    return render_template("worker-sign-up.html", name=name)

@app.route("/worker/dashboard/<int:id>", methods=["GET"])
@login_required
def worker_dashboard(id):
    user_details = {}
    user_docuemnts = {}
    conn = get_db()
    db = conn.cursor()
    user = db.execute("SELECT * FROM WORKERS WHERE id = ?", (id,)).fetchall()
    documents = db.execute("SELECT * FROM WORKER_DOCUMENTS WHERE user_id = ?", (id,)).fetchall()
    if len(user) != 1:
        return redirect("/login/worker")
    user_details = user[0]
    user_docuemnts = documents[0]
    conn.commit()
    conn.close()
    """ Worker Dashboard """
    return render_template("worker-dashboard.html", user_details=user_details, user_documents=documents)

@app.route('/upload_document', methods=['POST'])
def upload_document():
    if 'document_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['document_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        conn = get_db()
        db = conn.cursor()

        #   Get the user details
        user = db.execute("SELECT * FROM WORKERS WHERE id = ?", (session["user_id"],)).fetchall()
        if len(user) != 1:
            return redirect("/login/worker")
        user_details = user[0]

        document_type = request.form.get("document_type")
        filename = f"{user_details['username']} - {document_type} - {file.filename}"
        document_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Perform any additional processing (e.g., database update) here
        #   UPDATE THE DOCUMENTS DATABASE
        db.execute("INSERT INTO WORKER_DOCUMENTS (user_id, document_type, document_name, document_location) VALUES (?, ?, ?, ?)",
                   (session["user_id"], document_type, filename, document_location))
        
        conn.commit()
        conn.close()


        return redirect(url_for('worker_dashboard', id=session["user_id"]))
    
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

