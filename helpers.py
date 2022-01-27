import os

import io
import sqlite3
import requests
import urllib.parse

from PIL import Image, ImageOps
from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def connect_db():
    """ Connect to db, format rows as dicts, and generate cursor """
    ROOT = os.path.dirname(os.path.realpath(__file__))
    db = sqlite3.connect(os.path.join(ROOT, 'recete.db'))
    db.row_factory = sqlite3.Row
    return db

def allowed_image(filename):
    """ 
    Check each uploaded image to ensure a permissible filetype and filename 
    Takes full filename as input, returns boolean if filename passes the check
    """
    allowed_img_ext = ["JPEG", "JPG", "HEIC"]

    # Ensure file has a . in the name
    if not "." in filename:
        return False

    # Split the extension and the file name
    exten = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if exten.upper() in allowed_img_ext:
        return True
    else:
        return False


def convert_img(infile, filetype):
    """ 
    Convert receipt photo to tiff for OCR and thumbnail for html display

    convert_img takes two arguments, the photo provided by the user and
    the desired type of output: tiff or jpg.

    returns the path of the converted photo as a string
    """
    # Open image
    receipt = Image.open(infile)

    # Create new filename for image
    file = receipt.filename
    filename, ext = os.path.splitext(file)

    # Format original image into a square
    receipt = ImageOps.fit(receipt, size=(2000, 2000), method=3, bleed=0.02, centering=(0.5, 0.5))
    receipt.save(file)
    
    # Convert receipt to .tiff file
    try:
        if filetype == "tiff":
            with receipt as tiff:
                ocr_img = filename + "." + filetype
                tiff = ImageOps.fit(receipt, size=(2000, 2000), method=3, bleed=0, centering=(0.5, 0.5))
                tiff.save(ocr_img)
                return(ocr_img)

        if filetype == "jpg":
            with receipt as thumbnail:
                thumbnail_img = filename + "_thumbnail" + "." + filetype
                thumbnail = ImageOps.fit(receipt, size=(128, 128), method=3, bleed=0, centering=(0.5, 0.5))
                thumbnail.save(thumbnail_img)
                return(thumbnail_img)
    
    except OSError:
        print("cannot convert image", receipt.filename)
        return apology("Image type not supported, upload a .jpg/.jpeg", 400)

    # Close input file
    receipt.close()

    return True


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def pardir_path(path):
    """Takes file path as input and returns parentdir/filename.ext as string"""

    # Split original path into head and tail (full/path/to/parent/dir/ and filename.ext)
    head_tail = os.path.split(path)

    # Isolate parent dir, and concatenate with filename.ext
    pardir_path = os.path.basename(head_tail[0]) + "/" + head_tail[1]

    # Return parentdir/filename.ext as string    
    return pardir_path


def validate_pw(password):
    """Validates passwords. Returns True if password meets complexity requirements, false if not"""

    # Check for valid password
    flag_upper = False
    flag_lower = False
    flag_digit = False
    flag_char = False

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
        return True

    else:
        return False