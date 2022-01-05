import re
from flask import Flask,render_template,request,url_for,session,redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from mapbox import Maps,Geocoder, StaticStyle
from mapbox.services.base import Service
from mapbox.services.static import Static


app=Flask(__name__)

app.secret_key="password"

mysql=MySQL(app)
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="password"
app.config["MYSQL_DB"]="project"



@app.route('/')
def home():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('index.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/admin')
def adminhome():
    if 'loggedin2' in session:
        # User is loggedin show them the home page
        return render_template('admin.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('admin_login'))


@app.route('/register', methods=['POST','GET'])
def register():
    print("akashregister")
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL,%s, %s, %s,NULL)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="SELECT * FROM accounts WHERE username = %s AND password = %s AND adm = null"
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            print("no user '%s' ",username)
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)



@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username1 = request.form['username']
        password1 = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username = %s AND password = %s AND adm = 'yes'", (username1, password1))
        print(username1,password1)
        account2 = cursor.fetchone()
        print(account2)
        if account2:
            session['loggedin2'] = True
            session['id'] = account2['id']
            session['username'] = account2['username']
            return redirect(url_for('adminhome'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('admin_login.html', msg=msg)


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))


if __name__=="__main__":
    app.run(debug=True)

