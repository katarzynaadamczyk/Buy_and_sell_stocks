import os
from decouple import config

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import mysql.connector
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to MySQL database

db_mysql = mysql.connector.connect(user=config("MYSQL_DATABASE_USER"), 
                             password=config("MYSQL_DATABASE_PASSWORD"), 
                             host=config("MYSQL_DATABASE_HOST"), 
                             database=config("MYSQL_DATABASE_DB"))

# create cursor to MySQL database to use stored procedures 
cursor = db_mysql.cursor()

# Make sure API key is set
API_KEY = config("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    cash = db.execute("SELECT cash FROM users WHERE id=:uid", uid=session["user_id"])
    value = cash[0]["cash"]

    portfolio = db.execute("SELECT symbol, shares FROM user_index WHERE user_id=:uid ORDER BY symbol", uid=session["user_id"])
    for row in portfolio:
        # TO DO
        data = lookup(row["symbol"])
        row["price"] = float(data["price"])
        row["name"] = data["name"]
        row["total"] = row["shares"] * row["price"]
        value += row["total"]

    return render_template("index.html", portfolio=portfolio, cash=cash[0]["cash"], value=value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get('symbol')
        data = lookup(symbol)
        if not data:
            return apology("EMPTY / WRONG SYMBOL")

        cash = db.execute("SELECT cash FROM users WHERE id=:uid", uid=session["user_id"])
        shares = request.form.get('shares')

        if not shares.isdigit():
            return apology("WRONG TYPE OF SHARES")

        shares = int(shares)

        if shares * data["price"] > cash[0]["cash"]:
            return apology("YOU DON'T HAVE ENOUGH MONEY")

        db.execute("UPDATE users SET cash=:cash WHERE id=:uid",
                   cash=cash[0]["cash"] - shares * data["price"], uid=session["user_id"])
        db.execute("INSERT INTO history (user_id, symbol, shares, price, dtype, total_amount) VALUES (:uid, :symbol, :shares, :price, :dtype, :total_amount)",
                   uid=session["user_id"], symbol=data["symbol"], shares=shares, price=data["price"], dtype="BUY", total_amount=shares * data["price"])

        owned_shares = db.execute("SELECT shares FROM user_index WHERE user_id=:uid AND symbol=:symbol",
                                  uid=session["user_id"], symbol=data["symbol"])
        if len(owned_shares) > 0:
            db.execute("UPDATE user_index SET shares=:shares WHERE user_id=:uid AND symbol=:symbol",
                       shares=shares + owned_shares[0]["shares"], uid=session["user_id"], symbol=data["symbol"])
        else:
            db.execute("INSERT INTO user_index (user_id, symbol, shares) VALUES (:uid, :symbol, :shares)",
                       uid=session["user_id"], symbol=data["symbol"], shares=shares)

        flash('You succesfully bought shares!')
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    transactions = db.execute(
        "SELECT symbol, shares, price, dtype, transacted FROM history WHERE user_id=:uid", uid=session["user_id"])

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        data = lookup(request.form.get('symbol'))

        if data:
            return render_template("quoted.html", data=data)
        else:
            return apology("WRONG / BLANK SYMBOL")

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("username")
        if not name:
            return apology("You have not put in any name")

        names = cursor.callproc('check_if_user_exists', [name, 0])

        if names[1]:
            return apology("Your name already exists, please choose a different one.")

        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")
        if not password1 or not password2 or password1 != password2:
            return apology("You put in blank or different passwords")
        
        # db.execute("INSERT INTO users (username, hash) VALUES (:name, :password)",
        #           name=name, password=generate_password_hash(password1))
        # newid = db.execute("SELECT id FROM users WHERE username=:name", name=name)
        
        id2 = cursor.callproc('insert_new_user_and_return_his_id', [name, generate_password_hash(password1), 10000.0, 0])
        db_mysql.commit()
        print('id2')
        print(id2)
        session["user_id"] = id2[3]
        
        flash('You succesfully registered!')
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        # get data from form
        symbol = request.form["symbol"]
        shares = int(request.form.get("shares"))

        # get possession for the user
        possession = db.execute("SELECT symbol, shares FROM user_index WHERE user_id=:uid", uid=session["user_id"])

        # check if data provided from form is correct

        confirm = False
        owned_shares = 0

        for row in possession:
            if symbol == row["symbol"]:
                if shares > int(row["shares"]) or shares < 0:
                    return apology("You want to sell too many shares or you put in negative number of shares.")
                else:
                    owned_shares = row["shares"]
                    confirm = True
                    break

        data = lookup(symbol)

        if not confirm or not data:
            return apology("You do not own any shares of mentioned company.")

        # update cash in users table

        cash = db.execute("SELECT cash FROM users WHERE id=:uid", uid=session["user_id"])
        cash[0]["cash"] += shares * float(data["price"])
        db.execute("UPDATE users SET cash=:cash WHERE id=:uid", cash=cash[0]["cash"], uid=session["user_id"])

        # update / delete symbol in user_index table

        if shares == owned_shares:
            # delete
            db.execute("DELETE FROM user_index WHERE user_id=:uid AND symbol=:symbol",
                       uid=session["user_id"], symbol=data["symbol"])
        else:
            # update
            owned_shares -= shares
            db.execute("UPDATE user_index SET shares=:shares WHERE user_id=:uid AND symbol=:symbol",
                       shares=owned_shares, uid=session["user_id"], symbol=data["symbol"])

        # add sell to history
        db.execute("INSERT INTO history (user_id, symbol, shares, price, dtype, total_amount) VALUES (:uid, :symbol, :shares, :price, :dtype, :total_amount)",
                   uid=session["user_id"], symbol=data["symbol"], shares=shares, price=data["price"], dtype="SELL", total_amount=shares * data["price"])

        flash('You succesfully sold ' + str(shares) + ' shares of ' + data["symbol"] + '!')
        return redirect("/")
    else:

        possession = db.execute("SELECT symbol, shares FROM user_index WHERE user_id=:uid", uid=session["user_id"])

        return render_template("sell.html", possession=possession)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run()