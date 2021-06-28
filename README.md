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
* [Acknowledgements](#acknowledgements)


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
List the ready features here:
- Awesome feature 1
- Awesome feature 2
- Awesome feature 3


## Screenshots
![Example screenshot](./img/screenshot.png)
<!-- If you have screenshots you'd like to share, include them here. -->


## Setup
What are the project requirements/dependencies? Where are they listed? A requirements.txt or a Pipfile.lock file perhaps? Where is it located?

Proceed to describe how to install / setup one's local environment / get started with the project.


## Usage
How does one go about using it?
Provide various use cases and code examples here.

`write-your-code-here`


## Project Status
Project is: _in progress_ / _complete_ / _no longer being worked on_. If you are no longer working on it, provide reasons why.


## Room for Improvement
Include areas you believe need improvement / could be improved. Also add TODOs for future development.

Room for improvement:
- Improvement to be done 1
- Improvement to be done 2

To do:
- Feature to be added 1
- Feature to be added 2


## Acknowledgements
Give credit here.
- This project was inspired by...
- This project was based on [this tutorial](https://www.example.com).
- Many thanks to...


## Contact
Created by [@flynerdpl](https://www.flynerd.pl/) - feel free to contact me!


<!-- Optional -->
<!-- ## License -->
<!-- This project is open source and available under the [... License](). -->

<!-- You don't have to include all sections - just the one's relevant to your project -->
