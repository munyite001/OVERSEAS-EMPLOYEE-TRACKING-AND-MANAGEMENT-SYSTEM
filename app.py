from flask import Flask, redirect, g, render_template, request, session, jsonify, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, is_valid_userName, is_valid_email
import sqlite3
import datetime
import os

# Configure Application
app = Flask(__name__)
DATABASE = "app.db"

#   Configure path to store uploaded files
UPLOAD_FOLDER = './static/UPLOADS/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Secret Key
app.secret_key = os.urandom(24)

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

    # Connect to the database
    conn = get_db()
    db = conn.cursor()

    #   Clear Session
    session.clear()

    # If user is submitting data (POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username")
            return render_template("employer-login.html", name=name)
        elif not password:
            flash("Must provide password")
            return render_template("employer-login.html", name=name)

        #   Query database for username
        user = db.execute("SELECT * FROM EMPLOYERS WHERE username = ?", (username,)).fetchall()

        #   Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["password_hash"], password):
            flash("invalid username and/or password")
            return render_template("employer-login.html", name=name)
        
        # if all is good
        # set the session for the user
        session["user_id"] = user[0]["id"]
        session["last_activity"] = datetime.datetime.now()

        # commit the changes
        conn.commit()
        conn.close()

        #   Redirect user to dashboard
        return redirect("/employer/dashboard/{}".format(user[0]["id"]))

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

@app.route("/employer/dashboard/<int:id>", methods=["GET"])
@login_required
def employer_dashboard(id):
    user_details = {}
    conn = get_db()
    db = conn.cursor()

    # Check if logged-in user ID matches the provided ID in the URL
    if session["user_id"] != id:
        flash("Unauthorized access!")
        return redirect("/employer/dashboard/{}".format(session["user_id"]))
    user = db.execute("SELECT * FROM EMPLOYERS WHERE id = ?", (id,)).fetchall()
    
    if len(user) != 1:
        return redirect("/login/worker")
    user_details = user[0]

    conn.commit()
    conn.close()
    """ Employer Dashboard """
    return render_template("employer-dashboard.html", user_details=user_details)



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
    conn = get_db()
    db = conn.cursor()

    # Check if logged-in user ID matches the provided ID in the URL
    if session["user_id"] != id:
        flash("Unauthorized access!")
        return redirect("/worker/dashboard/{}".format(session["user_id"]))
    user = db.execute("SELECT * FROM WORKERS WHERE id = ?", (id,)).fetchall()
    documents = db.execute("SELECT * FROM WORKER_DOCUMENTS WHERE user_id = ?", (id,)).fetchall()
    incidents = db.execute("SELECT * FROM harassment_reports WHERE user_id = ?", (session["user_id"],)).fetchall()

    if len(user) != 1:
        return redirect("/login/worker")
    user_details = user[0]

    conn.commit()
    conn.close()
    """ Worker Dashboard """
    return render_template("worker-dashboard.html", user_details=user_details, user_documents=documents, incidents=incidents)

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
    
@app.route('/update_employment_details', methods=["POST"])
@login_required
def update_employment_details():
    if request.method == "POST":
        employed = True if request.form.get("employed") else False
        work_type = request.form.get("work_type")
        work_location = request.form.get("work_location")
        employer_name = request.form.get("employer_name")
        employer_contact = request.form.get("employer_contact")
        employment_start_date = request.form.get("employment_start_date")

        #   Connect to the database
        conn = get_db()
        db = conn.cursor()

        db.execute("UPDATE workers SET EMPLOYED=?, work_type=?, work_location=?, employer_name=?, employer_contact=?, employment_start_date=? WHERE id=?",
                   (employed, work_type, work_location, employer_name, employer_contact, employment_start_date, session["user_id"]))
        
        conn.commit()
        conn.close()
        flash("Employment details updated successfully", "success")
        return redirect(url_for('worker_dashboard', id=session["user_id"]))
    
@app.route("/report_harassment", methods=["POST"])
@login_required
def report_harassment():
    if request.method == 'POST':
        date = request.form.get("date")
        location = request.form.get("location")
        description = request.form.get("description")

        if not date or not location or not description:
            flash("Please fill in all the fields")
            return redirect(url_for('worker_dashboard', id=session["user_id"]))
        
        #   Connect to the database
        conn = get_db()
        db = conn.cursor()

        #   GET THE USER DETAIlS
        user = db.execute("SELECT * FROM workers WHERE id = ?", (session["user_id"],)).fetchone()
        if not user:
            return redirect("/login/worker")
        db.execute("INSERT INTO harassment_reports (user_id, date, location, description) VALUES (?, ?, ?, ?)",
                   (session["user_id"], date, location, description))
        conn.commit()
        conn.close()

        flash('Harassment report submitted successfully')
        return redirect(url_for('worker_dashboard', id=session["user_id"]))

    
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

