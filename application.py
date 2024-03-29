import os
from decouple import config

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import mysql.connector
from mysql.connector.cursor import MySQLCursor
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

# create cursor to MySQL database to use stored procedures or execute queries
cursor = db_mysql.cursor()

# Make sure API key is set
os.environ.setdefault('API_KEY', config("API_KEY"))

if not os.environ.get('API_KEY'):
    raise RuntimeError("API_KEY not set")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    cash = cursor.callproc('check_cash_for_user', [session["user_id"], 0])
    value = cash[1]
    print(session["user_id"]) # remove the print statement

    # Query database for symbol and shares
    cursor.execute("SELECT symbol, shares FROM user_index WHERE user_id = %s ORDER BY symbol", (session["user_id"],))
    portfolio = cursor.fetchall()
    print(portfolio) # remove the print statement
    portfolio_dict = list()
    print(cursor.statement)

    for row in portfolio:
        dic = {}
        print(row[0])
        print(row[1])
        data = lookup(row[0])
        print(data)
        dic['symbol'] = row[0]
        dic['shares'] = row[1]
        dic["price"] = 0.0 if not data else float(data["price"]) 
        dic["name"] = '' if not data else data["name"]
        dic["total"] = dic["shares"] * dic["price"]
        value += dic["total"]
        portfolio_dict.append(dic)

    print(portfolio_dict) # remove the print statement
    
    return render_template("index.html", portfolio=portfolio_dict, cash=cash[1], value=value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get('symbol')
        data = lookup(symbol)
        if not data:
            return apology("EMPTY / WRONG SYMBOL")

        cash = cursor.callproc('check_cash_for_user', [session["user_id"], 0])
        shares = request.form.get('shares')

        if not shares.isdigit():
            return apology("WRONG TYPE OF SHARES")

        shares = int(shares)

        if shares * data["price"] > cash[1]:
            return apology("YOU DON'T HAVE ENOUGH MONEY")

        cursor.callproc('update_users_cash', [cash[1] - shares * data["price"], session["user_id"]])
        db_mysql.commit()
        cursor.callproc('insert_into_history', [session["user_id"], data["symbol"], shares, data['price'], 'BUY', shares * data["price"]])
        db_mysql.commit()

        owned_shares = cursor.callproc('get_shares_from_user_for_symbol', [session["user_id"], data["symbol"], 0])
        print(owned_shares) # remove print
        if owned_shares[2] >= 0:
            cursor.callproc('update_shares_for_user', [session["user_id"], data['symbol'], shares + owned_shares[2]])
            db_mysql.commit()
        else:
            cursor.callproc('insert_new_symbol_for_user', [session["user_id"], data['symbol'], shares])
            db_mysql.commit()
            
        flash('You succesfully bought shares!')
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    cursor.execute("SELECT symbol, shares, price, dtype, transacted FROM history WHERE user_id=%(uid)s", {'uid': session["user_id"]})
    transactions = cursor.fetchall()

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
        cursor.execute("SELECT hash, idusers FROM users WHERE username = %(name)s", {'name': request.form.get("username")})
        # prints need to be removed
        print(cursor.rowcount)
        rows = cursor.fetchall()
        print(cursor.rowcount)


        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][0], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][1]
        print(rows)
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
        
        id2 = cursor.callproc('insert_new_user_and_return_his_id', [name, generate_password_hash(password1), 10000.0, 0])
        db_mysql.commit()
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
        cursor.execute("SELECT symbol, shares FROM user_index WHERE user_id=%(uid)s", {'uid': session["user_id"]})
        possession = cursor.fetchall()

        # check if data provided from form is correct

        confirm = False
        owned_shares = 0

        for row in possession:
            if symbol == row[0]:
                if shares > int(row[1]) or shares < 0:
                    return apology("You want to sell too many shares or you put in negative number of shares.")
                else:
                    owned_shares = row[1]
                    confirm = True
                    break

        data = lookup(symbol)

        if not confirm or not data:
            return apology("You do not own any shares of mentioned company.")

        # update cash in users table

        cash = cursor.callproc('check_cash_for_user', [session["user_id"], 0])
        cash = cash[1] + shares * float(data["price"])
        cursor.callproc('update_users_cash', (cash, session["user_id"]))
        db_mysql.commit()

        # update / delete symbol in user_index table

        if shares == owned_shares:
            # delete
            cursor.callproc('delete_shares_for_user', (session["user_id"], symbol))
            db_mysql.commit()
        else:
            # update
            owned_shares -= shares # IN uid INT, IN sym VARCHAR(4), IN shrs int)
            cursor.callproc('update_shares_for_user', (session["user_id"], symbol, owned_shares))
            db_mysql.commit()

        # add sell to history
        cursor.callproc('insert_into_history', [session["user_id"], data["symbol"], shares, data['price'], 'SELL', shares * data["price"]])
        db_mysql.commit()

        flash('You succesfully sold ' + str(shares) + ' shares of ' + data["symbol"] + '!')
        return redirect("/")
    else:

        cursor.execute("SELECT symbol, shares FROM user_index WHERE user_id=%(uid)s", {'uid': session["user_id"]})
        possession = cursor.fetchall()

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
    cursor.close()
    db_mysql.close()