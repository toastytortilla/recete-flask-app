import os
import re
import sqlite3
import PIL
import plotly.graph_objects as go
# import pytesseract as tess
# tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR'

from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, connect_db, login_required, url_path, usd, allowed_image, convert_img, byte_wrapper

# Configure application
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
app.config["IMAGE_UPLOADS"] = "C:\\Users\\dvdic\\Documents\\Comp_Sci\\CS50x\\final_project\\recete\\static\\receipts"


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
    fig.write_html("templates/graphs/" + str(session["user_id"]) + ".html")

    # Get graph path for injection into HTML template
    graph_file = "graphs/" + str(session["user_id"]) + ".html"

    # Return temporary apology page
    return render_template("home.html", graph=graph_file, total_receipts=len(receipts), receipts=receipts[0:3], total_spent=total_spent)


@app.route("/manager", methods=["GET", "POST"])
@login_required
def manager():
    """Display user database of receipts"""
    if request.method == "POST":
        # Connect to recete.db with row_factory method and create cursor
        rec = connect_db()
        cur = rec.cursor()

        # Validate date input
        date = request.form.get("date")

        # Validate company input
        company = request.form.get("company")

        # Get transaction type
        trans_type = request.form.get("type")

        # Validate split input and calculate new total amount
        split = request.form.get("split")
        total = request.form.get("total")

        if int(split) > 1:
            total = (float(total)/float(split))

        total = float(total)

        # Upload, validate, and convert image
        if request.files:
            image = request.files["image"]

            if image.filename == "":
                flash("Oops, your upload is missing a file name!")
                return redirect(request.url)

            # Convert image and create thumbnail, capture path and create URL for each
            if allowed_image(image.filename):
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                og_img = "static/receipts/" + image.filename
                tiff_img = convert_img("static/receipts/" + image.filename, "tiff")
                thumbnail_img = convert_img("static/receipts/" + image.filename, "jpg")
                
                # Format each img path into just parent dir and filename to generate url
                og_url = url_path(og_img)
                tiff_url = url_path(tiff_img)
                thumbnail_url = url_path(thumbnail_img)

                flash("Upload successful!", "message")
                # return render_template("manager.html", show_img=url_for('static', filename="receipts/" + thmb_img.filename))
            
            else:
                flash("Please upload a .jpg/.jpeg or .heic")
                return redirect(request.url)

        # Add receipt to receipts table in recete.db
        cur.execute("INSERT INTO receipts (user_id, date, company, trans_type, split, total, og_img, tiff_img, thumbnail_img) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (session['user_id'], date, company, trans_type, split, total, url_for('static', filename=og_url), url_for('static', filename=tiff_url), url_for('static', filename=thumbnail_url)))
        print("Transaction added to database successfully.")
        rec.commit()

        # Commit changes to recete.db and close connection
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
    flash("Receipt deleted.", "message")
    
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

    # Generate url for full-size image
    og_img = url_path(og_img)

    return render_template("open_img.html", og_img=url_for('static', filename=og_img))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get data from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Connect db, create cursor
        rec = connect_db()
        cur = rec.cursor()

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()

        # Create list to store user acct info
        acct = []

        # Iterate over data from db and format into a list of dicts
        for item in rows:
            acct.append({k: item[k] for k in item.keys()})

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(acct[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = acct[0]["id"]

        # Close connection to recete.db
        cur.close()

        # Redirect user to home page
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

        # Validate email
        # regular expression (regex) for validating an email address without API's
        email_regex = r'\b[A-Za-z0-9._%+-=!#$^&*()`~]+@+[A-Za-z0-9.-]+\b.[A-Z|a-z]{2,}\b'

        # Obtain username from user
        username = request.form.get("username")

        # Check for valid username
        if not username:
            return apology("must provide username", 400)

        for char in username:
            if char == " ":
                return apology("Provide a valid email address", 400)

        if re.fullmatch(email_regex, username):
            print(f"Valid email: {username}")

        else:
            print(f"Invalid email: {username}")
            return apology("Provide a valid email address.", 400)

        """ Check if username is unique """

        # Connect db
        rec = connect_db()
        cur = rec.cursor()
        
        rows = len(cur.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall())

        print(f"Total rows are: {rows}")

        if rows > 0:
            return apology("Username already taken!", 400)

        """ Validate password """

        # Get password from user
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for both password fields to be filled
        if not request.form.get("password"):
            return apology("must provide username", 400)

        if not request.form.get("confirmation"):
            return apology("must provide username", 400)


        # Check for valid password
        flag_upper = False
        flag_lower = False
        flag_digit = False
        flag_char = False

        if len(password) < 8:
            return apology("Password must be at least 8 characters long.", 400)

        for char in password:
            if char.isupper():
                flag_upper = True

            if char.islower():
                flag_lower = True

            if char.isdigit():
                flag_digit = True

            if not char.isalpha() and not char.isdigit():
                flag_char = True

        if flag_upper and flag_lower and flag_digit and flag_char == True:
            pass

        else:
            return apology("Password does not meet the requirements.", 400)

        # Check passwords for match, hash if they do
        if password == confirmation:
            hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

        else:
            return apology("Passwords must match.", 400)

        print(f"username: {username}")
        print(f"pw: {hashed_pw}")

        # Submit new user to db
        cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_pw))

        # Save (commit the changes)
        rec.commit()

        # Close the db
        cur.close()

        # Redirect to Log In page
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/pw_change", methods=["POST"])
def pw_change():
    """ Allows a user to change their password """
    return apology("This page is under construction!", 400)

# Add usd helper function to jinja
app.jinja_env.globals.update(usd=usd)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
