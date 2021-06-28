# finance_CS50
Project for CS50 course, extended by me. CS50 only wanted to create a Flask app for buying stocks, but I decided to do something more. 
Instead on working just on sqlite3 database (easy connection when you have CS50 library) I decided to change it to MySQL database. As well as add some more features to the projects that were not in the scope of CS50 course. 


## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)


## General Information
This is an extended project for CS50 course on Harvard. The goal of this project was to implement a website on which an user can buy and sell stocks for learning purposes. The money and stocks are fictional. 
Some of the code was already prepared by the stuff of the course - all of the file: helpers.py and layout.html as well as template in the application.py. 
My job was to implement features of the project - routes and pages for buy, sell, login, register, history and quote. 
The original project was implemented using cs50 library which contained connection to sqlite3 database. I changed this connection to connection with MySQL database. 
The project for the course had just API_KEY set by writing export API_KEY = xxx in the terminal before running the application. I changed this and used decouple library. I keep my login and password for MySQL database as well as the API_KEY in .env file on my computer. 
More enhancements can be found in open/closed issues. 


## Technologies Used
- Python - version 3.9.0
- Jinja - version 3.0.0
- Python libraries:
  - os
  - decouple
  - flask
  - mysql.connector
  - tempfile
  - werkzeug
- Javascript 
- HTML
- CSS


## Features
- Registering a new user
- Buying stocks
- Selling stocks
- Viewing history of transactions for the user


## Screenshots
TODO
![Example screenshot](./img/screenshot.png)
<!-- If you have screenshots you'd like to share, include them here. -->


## Setup
Project's requirements are listed in /requirements.txt. 
To run the project on your computer you need to have a VirtualEnv installed on your desktop (just follow this tutorial: https://timmyreilly.azurewebsites.net/python-flask-windows-development-environment-setup/).
Then you need to create MySQL Database on your computer (TODO).
You will need to get an API_KEY - for that I created a free account on https://iexcloud.io/
After that you need to make and .env file containing: 
'MYSQL_DATABASE_USER = ?
MYSQL_DATABASE_PASSWORD = ?
MYSQL_DATABASE_DB = ?
MYSQL_DATABASE_HOST = ?
API_KEY = ?' 
Then you should be able to work on VirtualEnv by entering the folder with application.py and working on your individual virtual environment.


## Usage
The user is able to register, then check the stock by going to the quote section and writing there stocks abbreviations (4 letters). Then, if user has enough virtual cash, he can buy the stock in buy section or, if he needs money, he can sell the stock in sell section. As well as he can check the history in history section.


## Project Status
Project is: in progress.


## Room for Improvement
All things I may improve are listed in open issues.
