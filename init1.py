# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airport_project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


# Define a route to hello function
@app.route('/')
def index():
    return render_template('index.html')


# Define route for login
@app.route('/login')
def login():
    return render_template('login.html')


# Define route for register
@app.route('/register')
def register():
    return render_template('register.html')


# Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM user WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        # returns an error message to the templates page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)


# Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerType():
    # grabs information from the forms
    user_type = request.form['usertype']

    if user_type == "customer":
        return render_template('register_customer.html')
    else:
        return render_template('register_staff.html')


@app.route('/registerCustomer', methods=['GET', 'POST'])
def registerAuthCustomer():
    # grabs information from the forms
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    date_of_birth = request.form['dateofbirth']
    building_num = request.form['buildingnum']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    passport_num = request.form['passportnum']
    passport_exp = request.form['passportexp']
    passport_country = request.form['passportcountry']

    # cursor used to send queries
    cursor = conn.cursor()

    # executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))

    # stores the results in a variable
    data = cursor.fetchone()

    # use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = '''INSERT INTO customer (email, name, password, 
                    building_num, street, city, state, passport_num, 
                    passport_exp, passport_country, date_of_birth) 
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(ins, (email, name, password, building_num, street, city,
                             state, passport_num, passport_exp, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        session['username'] = name
        return render_template('home.html')

@app.route('/registerStaff', methods=['GET', 'POST'])
def registerAuthStaff():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    date_of_birth = request.form['dateofbirth']
    airline_name = request.form['airlinename']

    # cursor used to send queries
    cursor = conn.cursor()

    # executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))

    # stores the results in a variable
    data = cursor.fetchone()

    # use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = '''INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, airline_name) 
                    VALUES(%s, %s, %s, %s, %s, %s)'''
        cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        session['username'] = username
        return render_template('home.html')

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();
    return render_template('home.html', username=username)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
