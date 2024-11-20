from flask import Flask, render_template, session, request, redirect, url_for, flash
from forms import NameForm, LoginForm
import hashlib
from datetime import timedelta, datetime
 
from db_connector import database

db = database()

app = Flask(__name__)
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}
app.secret_key = "fortnite"
app.permanent_session_lifetime = timedelta(minutes = 2)


@app.route('/')
def home():
    return render_template('index.html', name="Torin")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/register', methods = ['GET','POST'])
def register():
    title = "Registration Page"
    current_user=session.get('user')
    if request.method == "POST":
        user = request.form['nm']
        password = request.form['pword']
        email = request.form['email']

        hashed_password = hashlib.md5(str(password).encode()).hexdigest()
        hashed_email = hashlib.md5(str(email).encode()).hexdigest()
        result = db.queryDB("SELECT * FROM users WHERE name = ? OR email = ?",[user,hashed_email])
        if result:
            flash('Email or User Name already Exists, please try a different one', "danger")
            return redirect(url_for('register'))
        db.updateDB("INSERT INTO users (name,email,password) VALUES (?,?,?)",[user,hashed_email,hashed_password])
        return render_template('login.html', title = 'login')
    else:
        return render_template('register.html', title = title)

@app.route('/login', methods = ['GET','POST'])
def login():
    title = "LOG IN"
    form = LoginForm()
    if request.method == "POST":
        user = request.form ['email']
        password = request.form ['password']
        
        hashed_password = hashlib.md5(str(password).encode()).hexdigest()
        found_user = db.queryDB("SELECT * FROM users WHERE name = ?",[user])

        if found_user:
            stored_password = found_user [0][3]
            if stored_password == hashed_password:
                session['user'] = user
                session['email'] = found_user [0][2]
                print("login successfull")
                return redirect(url_for("home"))
            else:
                flash(" Incorrect password","danger")
        else:
            flash(" user not found","danger")
    if "user" in session:
        flash("Already logged in !","danger")
        return redirect(url_for("user"))

    return render_template('login.html', title=title, form=form)

@app.route('/logout')
def logout():
    current_user = session.get('user')
    flash("You have been logged out!", "danger")
    session.pop("user" , None)
    session.pop("email", None)
    session.pop("password", None)

    return redirect(url_for("home"))

@app.route("/user")
def user():
    title = "User Page"
    current_user = session.get('user')
    return render_template('user.html', title=title, current_user=current_user)


@app.route('/book_details/<int:book_id>')
def book_details(book_id):
    
    book = db.queryDB("SELECT * FROM Books WHERE book_id = ?",[book_id])
    return render_template('book_details.html', book=book)

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/delete/<int:book_id>', methods=['get','POST'])
def delete(book_id):
    # fetch book by ID

    db.updateDB("DELETE FROM Books WHERE  book_id= ?"[book_id])
    flash('book Deleted !!!')
    return redirect (url_for('index.html'))


if __name__ == '__main__':
    app.run(debug=True)