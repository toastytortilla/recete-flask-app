# Recete
#### Video Demo: https://www.youtube.com/watch?v=fMJopiHMkEI
#### Description:
Recete is a receipt management application that allows users to easily track purchases, recall receipts for easy returns, split bills, and get a snapshot of their spending habits. I have styled Recete after Venmo because I believe that Venmo would benefit from providing some or all of these functionalities within their own application.

## Features:
### Home
This is the homepage of your application. Information extracted from your receipts will be displayed in a graphical representation so that you can get a quick snapshot of your spending habits.

### Receipt Manager
This is the bread and butter of Recete. The Receipt Manager houses all of your captured receipts and presents helpful data for you to browse. Sort and search to find any receipts you may need, and access the image of the receipt for easy returns.
#### Bill Splitter 
This is a small tool within the Receipt Manager to help you split bills with friends. Either enter the amount of people you'd like to split the bill between when you enter the receipt, or come to this page to split it retroactively. Bill Splitter will divide the total by the amount of people, and then adjust it in your Receipt Manager. In the future, this tool will eventually allow you to export the bill to Venmo, where it will open up a blank transaction and auto-fill the amount. Then, simply add your friends and a comment and you're good to go!


## Development Log

12/27/2021 - Added conditional elements, graphics, and instructions to guide user if they have not stored any receipts in database yet. Adjusted vertical spacing and added a title to the recent transactions table home.html. Made demo video, uploaded demo video. Ported to github, cloned to CS50 IDE, submitted!

12/26/2021 - Ran final tests to ensure usability for users. Adjusted formatting on register.html. 


12/19-12/24/2021 - Completed home.html with dynamic graph and other helpful user data via plotly.py. Added button to home.html that directs to manager.html to add a receipt. Reformatted index.html, still not suited for mobile but looks great on browser. Changed behavior of success alerts, removed close button since it was non-functional. Corrected width and layout of table on manager.html.

12/18/2021 - Started work on home page that will graphically display how much money you've spent in each category over the past month. Fixed the formatting of open_img.html and tweaked the table spacing in manager.html.

12/17/2021 - Created downloads landing page: show_img.html. Turned receipt thumbnails into buttons that take user to a download page. Styled the images, updated code in the convert_img function to center and crop images into a square aspect ratio. Removed table formatting temporarily, will update manually tomorrow.

12/16/2021 - Researched and tried to install and import Tesseract and pytesseract, was unsuccessful.

12/10-12/15/2021 - Completed file registry image storage solution. Adjusted manager.html formatting to make the table fit the webpage left-to-right. Wrote custom function to generate URLs for each image before committing them to the databse. Implemented a way to delete receipts. Styled image upload button on receipt manager. Researched OCR modules (Google's Tesseract).

12/9/2021 - Added images to index.html, register.html via Flask. Linked Sign Up button on index.html to register.html. Began to implement file registry storage for images instead of database storage, unfinished. 

12/8/2021 - Solved "ValueError" from yesterday. Due to row_factory and sqlite3.Row function, parameters must be provided to SQL queries in tuple format. Made tasteful graphics for front end. Created index.html and styled it with basic branding. Added usd function to helpers.py to convert floats into usd formatted numbers for insertion into database.

12/7/2021 - Stuck on "ValueError: parameters are of unsupported type" when using session[user_id] to query the database for the receipts of the active user. 

12/6/2021 - Rediscovered how to use row_factory and sqlite.Row functions to manipulate database output into a dictionary and access it systematically.

12/3/2021 - Implemented logic in manager.html and application.py to take input from web form on manager.html. 

12/2/2021 - Improved manager.py by increasing dynamism with input statements and dynamic logic for accessing image files and querying the database. Created custom functions in helper.py to format and store images in a database. 

12/1/2021 - Applied image manipulation understanding from pics.py to manager.py. Stored image byte arrays in database and query them back out successfully. Solved image resizing issue: improved clarity of image by increasing it to (2000, 2000) pixels and opted for ImageOps.contain() function isntead of resize() function to preserve aspect ratio.

11/30/2021 - Struggled to understand what datatypes were at play when storing and accessing the image files from the database.

11/28/2021 - Resized and converted image file types and created thumbnails for input photos. Discovered and implemented a method to convert images to bytes and bytes back into images in prototype program pics.py.

11/27/2021 - Compiled information about how to convert images to bytes. Created thumbnails of input images in prototype program pics.py.

11/23/2021 - Created receipts table in database to store user input. Tested database commits with protoype program manager.py.

11/22/2021 - Fixed navbar link font color, styled general links. Created custom function in helpers.py to connect to the database and format rows as a dict. Tested registration logic on register.html. Added manual receipt entry form on manager.html front-end, must implement database queries on back-end still. 

11/19/2021 - Finally got my local development environment sorted and operational. I have explored and demoed the basics of non-CS50-based SQLite, git, and GitHub. Today, I ported the boilerplate code from pset9:finance to act as the base for Recete. Then, I converted the CS50 SQLite syntax into basic SQLite3 syntax and restructured the database. Next, I created the basic templates for the overall look of the website and implemented the register.html page.# recete-repo
