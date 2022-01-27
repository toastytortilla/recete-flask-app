# Required Python libraries
import os
import re
import string
import secrets
import sqlite3

# External dependencies
import PIL
import plotly.graph_objects as go
# import pytesseract as tess
# tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR'

from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Custom helper functions from helpers.py
from helpers import apology, connect_db, login_required, pardir_path, usd, allowed_image, convert_img, validate_pw


"""Configure application"""
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Route uploaded images to static/receipts/ directory and establish accepted file exts
app.config["IMAGE_UPLOADS"] = "C:\\Users\\dvdic\\Documents\\Comp_Sci\\CS50x\\final_project\\recete\\static\\receipts\\"


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure flask_mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ['RECETE_EMAIL_USER']
app.config['MAIL_PASSWORD'] = os.environ['RECETE_EMAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = ('recete-bot', app.config['MAIL_USERNAME'])
mail = Mail(app)


TRANS_TYPES = [
    "Auto & Transport",
    "Bills & Utilities",
    "Business Services",
    "Dining",
    "Education",
    "Entertainment",
    "Fees & Charges",
    "Financial",
    "Gifts & Donations",
    "Groceries",
    "Health & Fitness",
    "Home",
    "Income",
    "Kids",
    "Misc Expenses",
    "Personal Care",
    "Pets",
    "Shopping",
    "Taxes",
    "Transfer",
    "Travel",
    "Uncategorized",
    "Work"
]



@app.route("/")
def index():
    """Show homepage graphics and register button"""
    return render_template("index.html")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """Show user homepage with pie chart"""
    # Connect to recete.db and create cursor
    rec = connect_db()
    cur = rec.cursor()

    # Query user data for pie chart
    receipt_history = cur.execute("SELECT * FROM receipts WHERE user_id = ? ORDER BY date DESC", [session["user_id"]]).fetchall()

    # Format data from db for pie chart
    receipts = []

    # Clean data into lists
    for item in receipt_history:
        receipts.append({i: item[i] for i in item.keys()})

    # Set total_spent to 0
    total_spent = 0

    # Iterate over all receipts in user's profile and incrementally add their totals together
    for item in receipts:
        total_spent += float(item["total"])

    # Get the distinct types of transactions from the user's profile
    trans_types = cur.execute("SELECT DISTINCT(trans_type) FROM receipts WHERE user_id = ? ORDER BY trans_type ASC", [session["user_id"]]).fetchall()

    # Format data into list
    transactions = []
    categories = []

    for item in trans_types:
        transactions.append({i: item[i] for i in item.keys()})

    for item in transactions:
        categories.append(item["trans_type"])

    # Use the category list to dynamically count how many of each transaction type there are in the user's list of receipts
    counts = []

    for item in categories:
        trans_types_counts = cur.execute("SELECT COUNT(trans_type) FROM receipts WHERE user_id = ? AND trans_type = ?", (session["user_id"], item)).fetchall()
        
        counts_dict = []

        for item in trans_types_counts:
            counts_dict.append({i: item[i] for i in item.keys()})

        for item in counts_dict:
            counts.append(item["COUNT(trans_type)"])

    # Generate and style the graph
    fig = go.Figure(data=[go.Pie(labels=categories, values=counts, hole=.6)])
    fig.update_layout(autosize=True, uniformtext_minsize=12, uniformtext_mode='hide', margin=dict(l=0, r=0, b=0, t=0, pad=0), paper_bgcolor='rgba(255, 255, 255, 0)')
    fig.update_layout(font_color='#444444', font_family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", hoverlabel_font_color="#ffffff")
    fig.update_layout(legend=dict(x=1, y=0.1, traceorder='normal'))
    fig.update_traces(textfont_color='#ffffff')

    # Get path for user's graph and create graph
    graph_path = os.path.dirname(os.path.realpath(__file__)) + "/templates/graphs/" + str(session["user_id"]) + ".html"
    fig.write_html(graph_path)

    # Isolate the parent_dir/user_id.html path for rendering in Jinja
    graph_file = pardir_path(graph_path)

    # Commit changes to recete.db and close connection
    rec.commit()
    cur.close()

    # Return user's home page
    return render_template("home.html", graph=graph_file, total_receipts=len(receipts), receipts=receipts[0:3], total_spent=total_spent)


@app.route("/manager", methods=["GET", "POST"])
@login_required
def manager():
    """Display user database of receipts"""
    if request.method == "POST":
        # Connect to recete.db with row_factory method and create cursor
        rec = connect_db()
        cur = rec.cursor()

        # Get date input
        date = request.form.get("date")

        # Get company input
        company = request.form.get("company")

        # Get transaction type
        trans_type = request.form.get("type")

        # Get split input and calculate new total amount
        split = request.form.get("split")
        total = request.form.get("total")

        if int(split) > 1:
            total = (float(total)/float(split))

        total = float(total)

        # Upload, validate, and convert image
        if request.files:
            image = request.files["image"]

            if image.filename == "":
                flash("Oops, your upload is missing a file name!", "warning")
                return redirect(request.url)

            # Convert image and create thumbnail, capture path and create URL for each
            if allowed_image(image.filename):
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                og_img = app.config["IMAGE_UPLOADS"]  + image.filename
                # tiff_img = convert_img(og_img, "tiff")
                thumbnail_img = convert_img(og_img, "jpg")
                
                # Format each img path into just parent dir and filename to generate url
                og_url = pardir_path(og_img)
                # tiff_url = pardir_path(tiff_img)
                tiff_url = 0 # This is a placeholder value which will be removed when the OCR function is built and .tiff files are needed
                thumbnail_url = pardir_path(thumbnail_img)

                flash("Upload successful!", "success")
            
            else:
                flash("Please upload a .jpg/.jpeg or .heic", "warning")
                return redirect(request.url)

        # Add receipt to receipts table in recete.db
        cur.execute("INSERT INTO receipts (user_id, date, company, trans_type, split, total, og_img, tiff_img, thumbnail_img) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (session['user_id'], date, company, trans_type, split, total, url_for('static', filename=og_url), url_for('static', filename=tiff_url), url_for('static', filename=thumbnail_url)))
        print("Transaction added to database successfully.")

        # Commit changes to recete.db and close connection
        rec.commit()
        cur.close()

        # Redirect to manager.html
        return redirect("/manager")

    else:
        # Connect to recete.db and create cursor
        rec = connect_db()
        cur = rec.cursor()

        # Query necessary data from receipts table
        receipt_history = cur.execute("SELECT * FROM receipts WHERE user_id = ? ORDER BY date DESC", [session["user_id"]]).fetchall()

        # Make empty lists to hold data extracted from database for user's receipt history
        receipts = []

        # Clean data into lists
        for item in receipt_history:
            receipts.append({i: item[i] for i in item.keys()})

        # Close connection to recete.db
        cur.close()

    return render_template("manager.html", receipts=receipts, len_receipts=len(receipts), types=TRANS_TYPES)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete transaction from user's receipt history"""
    # Connect to db
    rec = connect_db()
    cur = rec.cursor()

    # Delete receipt
    id = request.form.get("id")
    if id:
        cur.execute("DELETE FROM receipts WHERE id = ?", [id])
    flash("Receipt deleted.", "success")
    
    # Commit changes and close db cursor
    rec.commit()
    cur.close()

    return redirect("/manager")


@app.route("/open_img", methods=["GET", "POST"])
@login_required
def open_img():
    """Display full size image of a given receipt"""
    # Get desired receipt from user
    og_img = request.form.get("og_img")

    # Generate path to full-size image's location in filesystem
    og_img = pardir_path(og_img)

    return render_template("open_img.html", og_img=url_for('static', filename=og_img))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect db, create cursor
        rec = connect_db()
        cur = rec.cursor()

        # Get data from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Must provide username", "danger")
            return redirect(request.url)

        # Ensure password was submitted
        elif not password:
            flash("Must provide password", "danger")
            return redirect(request.url)

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()

        # Create list to store user acct info
        acct = []

        # Iterate over data from db and format into a list of dicts
        for item in rows:
            acct.append({k: item[k] for k in item.keys()})

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(acct[0]["hash"], password):
            flash("Invalid username and/or password", "danger")
            return redirect(request.url)

        # Remember which user has logged in
        session["user_id"] = acct[0]["id"]

        # Close connection to recete.db
        cur.close()

        # Redirect user to home page and flash success message
        flash('Login successful!', "success")
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Connect db
        rec = connect_db()
        cur = rec.cursor()

        """ Username validation"""
        # regular expression (regex) for validating an email address without API's
        email_regex = r'\b[A-Za-z0-9._%+-=!#$^&*()`~]+@+[A-Za-z0-9.-]+\b.[A-Z|a-z]{2,}\b'

        # Obtain username from user
        username = request.form.get("username")

        # Check for valid username
        if not username:
            flash("Must provide username", "danger")
            return redirect(request.url)

        for char in username:
            if char == " ":
                flash("Provide a valid email address", "danger")
                return redirect(request.url)

        if re.fullmatch(email_regex, username):
            print(f"Valid email: {username}")

        else:
            print(f"Invalid email: {username}")
            flash("Provide a valid email address", "danger")
            return redirect(request.url)

        # Check if username is unique      
        rows = len(cur.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall())

        if rows > 0:
            flash("Username already taken!", "danger")
            return redirect(request.url)

        """ Password validation """
        # Get password from user
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for both password fields to be filled
        if not request.form.get("password"):
            flash("Must provide password!", "danger")
            return redirect(request.url)

        if not request.form.get("confirmation"):
            flash("Must provide password!", "danger")
            return redirect(request.url)

        # Check for correct password length
        if len(password) < 8:
            flash("Password must be at least 8 characters", "danger")
            return redirect(request.url)

        # Check for valid password complexity
        if validate_pw(password) == False:
            flash("Password does not meet complexity requirements", "danger")
            return redirect(request.url)

        # Check if password and confirmation match
        if password != confirmation:
            flash("Passwords do not match", "danger")
            return redirect(request.url)

        # Hash user's password and add to db
        else:
            hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            flash("Success!", "success")

        # Submit new user to db
        cur.execute("UPDATE users SET hash = (?) WHERE id == (?)", (hashed_pw, session["user_id"]))

        # Commit changes and close db
        rec.commit()
        cur.close()

        # Redirect to Log In page
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/pw_reset", methods=["GET", "POST"])
def pw_reset():
    """ Landing route for password reset process """
    if request.method == "POST":
        # Connect db, create cursor
        rec = connect_db()
        cur = rec.cursor()

        # Get input from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Check for valid username
        if not username:
            flash("Must provide username", "danger")
            return redirect(request.url)

        for char in username:
            if char == " ":
                flash("Provide a valid email address", "danger")
                return redirect(request.url)

        # Ensure password was submitted
        if not password:
            flash("Must provide password", "danger")
            return redirect(request.url)

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()

        # Create list to store user acct info
        acct = []

        # Iterate over data from db and format into a list of dicts
        for item in rows:
            acct.append({k: item[k] for k in item.keys()})

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(acct[0]["hash"], password):
            flash("Invalid username and/or password", "danger")
            return redirect(request.url)

        else:
            # Log user in to save the username/email
            session["user_id"] = acct[0]["id"]

            # Close db
            cur.close()

            # Route user to pw_update.html
            return redirect("/pw_update")

    else:
        return render_template("pw_reset.html")


@app.route("/pw_update", methods=["GET", "POST"])
def pw_update():
    """ Form/logic for updating a password """
    if request.method == "POST":
        # Connect to db
        rec = connect_db()
        cur = rec.cursor()

        # Get input from user
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for both password fields to be filled
        if not request.form.get("password"):
            flash("Must provide password!", "danger")
            return redirect(request.url)

        if not request.form.get("confirmation"):
            flash("Must provide password!", "danger")
            return redirect(request.url)

        # Check for correct password length
        if len(password) < 8:
            flash("Password must be at least 8 characters", "danger")
            return redirect(request.url)

        # Check for valid password complexity
        if validate_pw(password) == False:
            flash("Password does not meet complexity requirements", "danger")
            return redirect(request.url)

        # Check if password and confirmation match
        if password != confirmation:
            flash("Passwords do not match", "danger")
            return redirect(request.url)

        # Hash user's password and add to db
        else:
            hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            flash("Success!", "success")

        # Submit new user to db
        cur.execute("UPDATE users SET hash = (?) WHERE id == (?)", (hashed_pw, session["user_id"]))

        # Commit changes and close db
        rec.commit()
        cur.close()

        # Sign user out so that they can log in again with their new pw
        session.clear()

        # Redirect user to login page
        return redirect("/login")

    else:
        # Get the id of the user who has arrived
        return render_template("pw_update.html")


@app.route("/pw_reset_email", methods=["POST"])
def pw_reset_email():
    """Sends email to user containing a password reset link"""
    # Connect db, create cursor
    rec = connect_db()
    cur = rec.cursor()    

    # Get input from user
    email = request.form.get("email")

    # Query database for username
    rows = cur.execute("SELECT * FROM users WHERE username = ?", [email]).fetchall()

    # Create list to store user acct info
    acct = []

    # Iterate over data from db and format into a list of dicts
    for item in rows:
        acct.append({k: item[k] for k in item.keys()})

    # Ensure username exists
    if len(rows) != 1:
        flash("Invalid email", "danger")
        return redirect(request.url)

    else:
        # Generate unique 11 digit password for user
        password = ""

        for item in range(0, 11):
            char = secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=[]/{/}//1234567890,.?<>")
            password += char

        # Hash password
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

        # Overwrite their previous password in the database
        cur.execute("UPDATE users SET hash = (?) WHERE username == (?)", (hashed_pw, email))

        # Commit change and close db
        rec.commit()
        cur.close()

        # Send email
        title = "Your password has been reset."
        msg = Message("Password reset", recipients=[email])
        msg.html = render_template('email_template.html', title=title, email=email, password=password)
        mail.send(msg)

        # Flash alert that tells user to check their email for the password reset link
        flash("Check your email for a password reset link", "warning")
        return redirect("/login")


# Add usd helper function to jinja
app.jinja_env.globals.update(usd=usd)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    flash(e.name + ", Code: " + str(e.code), "danger")
    return redirect(request.url)



# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
