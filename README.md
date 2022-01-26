# Recete

![Recete social preview](https://user-images.githubusercontent.com/67752997/150200809-46b25b03-989f-4c89-b31a-1584fbc0ac39.png)

## About
Recete is a receipt management application that allows users to easily track purchases, recall receipts for easy returns, split bills, and get a snapshot of their spending habits. I have styled Recete after Venmo because I believe that Venmo would benefit from providing some or all of these functionalities within their own application.
[Click here](https://www.youtube.com/watch?v=fMJopiHMkEI "Recete Video Demo - YouTube") to view a full-length video demo on YouTube, or watch a quick version below:


https://user-images.githubusercontent.com/67752997/150202033-6dc08e10-cc91-4645-ba0e-b391cb28f243.mp4


## Features
### Home
This is the homepage of your application. It provides a quick way to get a quick snapshot of your spending habits.
* See your spending by cateogry in a pie chart
* Check your total amount of money spent
* Quickly glance at your last few transactions

### Receipt Manager
This is the bread and butter of Recete. The Receipt Manager houses all of your captured receipts and presents helpful data for you to browse. 
* Sort and search to find any receipts you may need
* Access the image of the receipt for easy returns
* Split the bill's total automatically for shared expenses


## Upcoming Features
### High Priority
* Refactor the code base
* Replace all apology() function calls with flash alerts, remove apology function altogether
* Change information displayed in graph on home.html to represent spending per category as a percent of total spending, not a simple percentage of total receipts as it is now
* Reformat manager.html to be mobile-friendly by collapsing or transforming the table using JavaScript for usability on small screen sizes. [Examples shown here](https://medium.com/appnroll-publication/5-practical-solutions-to-make-responsive-data-tables-ff031c48b122). For the modification I'm striving for, there is more info [here](https://elvery.net/demo/responsive-tables/#:~:text=%3C/table%3E-,No%20More%20Tables,-This%20technique%20was) and [here](https://css-tricks.com/responsive-data-tables/)

### Medium Priority 
* Add OCR function to manager.html via PyTesseract
* Add Edit feature to manager.html to allow users to update a previous entry
* Add an Export to Venmo feature to enable users to select a bill that they have split, and send that information to Venmo to initiate a Request transaction

### Low Priority
* Fix the positioning on manager.html to keep the title/header fixed while the table scrolls on small screen sizes


## Contributing
1. Pick a feature from the Upcoming Features list above
1. Fork it
1. Create your feature branch

    `git checkout -b my-new-feature`

1. Work on your code until you're happy with it, then add and commit your changes

    `git add files-you-changed`

    `git commit -m "Describe your change" -m "If necessary, please also provide a more detailed description of your change"`

1. Push to the branch

    `git push origin my-new-feature`

1. Create new Pull Request
1. Collaborate together until we're happy with the results!

### Database Set Up
Recete uses a lightweight SQLite3 database to manage user data. For security purposes, this repo does not contain the actual database from the web app. If you want to help and test on your own machine, set up your own SQLite3 database with the name `recete.db` and the following schema:

`CREATE TABLE users(id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id));`

`CREATE TABLE receipts(id INTEGER, user_id INTEGER NOT NULL, date DATE NOT NULL, company TEXT NOT NULL, trans_type TEXT NOT NULL, split INTEGER, total FLOAT NOT NULL, og_img TEXT, tiff_img TEXT, thumbnail_img TEXT, PRIMARY KEY(id));`


## Development Log

12/28/2021 and onward - Development continues. New features are being planned and implemented, starting with a password reset feature and remote hosting on a web server.

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
