# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                        port = 8889,
                       user='root',
                       password='root',
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
def loginType():
    # grabs information from the forms
    user_type = request.form['usertype']

    if user_type == "customer":
        return render_template('login_customer.html')
    else:
        return render_template('login_staff.html')


@app.route('/loginCustomer', methods=['GET', 'POST'])
def loginAuthCustomer():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()

    # executes query
    query = 'SELECT * FROM customer WHERE email = %s and password = %s'
    cursor.execute(query, (email, password))

    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        # creates a session for the the user
        # session is a built in
        session['username'] = email
        return render_template('home.html', username=email, customer=True)
    else:
        # returns an error message to the templates page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

@app.route('/loginStaff', methods=['GET', 'POST'])
def loginAuthStaff():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()

    # executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
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
        return render_template('home.html', username=username, staff=True)
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
        return render_template('home.html', username=name, customer=True)


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
        return render_template('home.html', username=first_name, staff=True)

@app.route('/bookFlight')
def book():
    return render_template('book_flight.html')

@app.route('/pastFlights')
def viewOldFlights():
    return render_template('pastflights.html')

@app.route('/futureFlights')
def futureFlights():
    return render_template('futureFlights.html')

@app.route('/createFlight')
def create():
    cursor = conn.cursor()

    # find current staff's airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()

    query = '''SELECT * FROM flight WHERE departure_date >= NOW() AND
                departure_date <= NOW() + INTERVAL 30 DAY AND airline_name = %s'''
    cursor.execute(query, (data['airline_name']))
    data = cursor.fetchall()

    return render_template('create_flight.html', data=data)

@app.route('/createFlightConfirmation', methods=['GET', 'POST'])
def create_confirmation():
    flight_num = request.form['flightnum']
    departure_date = request.form['departuredate']
    departure_time = request.form['departuretime']
    departure_airport = request.form['departureairport']
    arrival_date = request.form['arrivaldate']
    arrival_time = request.form['arrivaltime']
    arrival_airport = request.form['arrivalairport']
    base_price = request.form['baseprice']
    airplane_id = request.form['airplaneid']
    airline_name = request.form['airlinename']
    flight_status = request.form['status']

    # cursor used to send queries
    cursor = conn.cursor()

    # executes query
    query = 'SELECT * FROM flight where flight_num = %s AND departure_date = %s AND departure_time = %s'
    cursor.execute(query, (flight_num, departure_date, departure_time))

    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        cursor.close()
        # If the previous query returns data, then user exists
        error = "This flight already exists"
        return render_template('create_flight.html', error=error)
    else:
        query = '''INSERT INTO flight (flight_num, departure_date, departure_time, departure_airport, arrival_date,
                               arrival_time, arrival_airport, base_price, airplane_id, airline_name, flight_status)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(query, (flight_num, departure_date, departure_time, departure_airport, arrival_date,
                               arrival_time, arrival_airport, base_price, airplane_id, airline_name, flight_status))
        conn.commit()
        cursor.close()
        success = "Flight successfully added"
        return render_template('create_flight.html', success=success)

@app.route('/changeFlight')
def change_flight_status():
    cursor = conn.cursor()

    # find current staff's airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()

    # find future flights
    query = '''SELECT * FROM flight WHERE departure_date >= NOW() AND airline_name = %s'''
    cursor.execute(query, (data['airline_name']))
    data = cursor.fetchall()

    cursor.close()

    return render_template('change_flight.html', data=data)

@app.route('/changeFlightStatus', methods=['GET', 'POST'])
def change_flight_status_confirmation():
    flight_num = request.form['flightnum']
    departure_date = request.form['departuredate']
    departure_time = request.form['departuretime']
    flight_status = request.form['status']

    cursor = conn.cursor()

    query = '''UPDATE flight SET flight_status = %s WHERE flight.flight_num = %s
                AND flight.departure_date = %s AND flight.departure_time = %s'''
    cursor.execute(query, (flight_status, flight_num, departure_date, departure_time))

    conn.commit()

    # find current staff's airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()

    # find future flights
    query = '''SELECT * FROM flight WHERE departure_date >= NOW() AND airline_name = %s'''
    cursor.execute(query, (data['airline_name']))
    data = cursor.fetchall()

    cursor.close()
    success = "Flight successfully changed"
    return render_template('change_flight.html', data=data, success=success)

@app.route('/addAirplane')
def add_airplane():
    cursor = conn.cursor()

    # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()

    # find airplanes owned by that airline
    query = '''SELECT * FROM airplane WHERE owner = %s'''
    cursor.execute(query, (data['airline_name']))
    data = cursor.fetchall()

    cursor.close()

    return render_template('add_airplane.html', data=data)

@app.route('/addAirplaneConfirmation', methods=['GET', 'POST'])
def add_airplane_confirmation():
    airplane_id = request.form['airplaneid']
    seat_num = request.form['seatnum']
    manufacturer = request.form['manufacturer']
    age = request.form['age']

    cursor = conn.cursor()

    # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']

    query = "INSERT INTO airplane VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (airplane_id, airline_name, seat_num, manufacturer, age))
    conn.commit()

    # find airplanes owned by that airline
    query = '''SELECT * FROM airplane WHERE owner = %s'''
    cursor.execute(query, (airline_name))
    data = cursor.fetchall()

    cursor.close();
    success = "Airplane inserted successfully"
    return render_template('add_airplane.html', data=data, success=success)

@app.route('/addAirport')
def add_airport():
    cursor = conn.cursor()

    # find all airports
    query = "SELECT * FROM airport"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()

    return render_template('add_airport.html', data=data)

@app.route('/addAirportConfirmation', methods=['GET', 'POST'])
def add_airport_confirmation():
    airport_code = request.form['airportcode']
    name = request.form['name']
    city = request.form['city']
    country = request.form['country']
    airport_type = request.form['airporttype']

    cursor = conn.cursor()

    query = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(query, (airport_code, name, city, country, airport_type))
    conn.commit()

    # find all airports
    query = '''SELECT * FROM airport'''
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()

    success = "Airport successfully added"
    return render_template('add_airport.html', data=data, success=success)

@app.route('/customerStats')
def customer_statistics():
    cursor = conn.cursor()

    # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']

    # find all tickets from the airline in the last year
    query = '''SELECT Name
               FROM customer JOIN (SELECT Customer_email, MAX(total_tickets)
                                   FROM (SELECT customer_email, COUNT(Customer_email) as total_tickets
                                         FROM ticket NATURAL JOIN purchases
                                         WHERE airline_name = %s
                                         AND purchases_date >= NOW() - INTERVAL 1 YEAR
                                         AND purchases_date <= NOW()
                                         GROUP BY customer_email) as a) as b
               WHERE customer.Email = b.customer_email;'''
    cursor.execute(query, (airline_name))
    freq_customer = cursor.fetchall()

    query = 'SELECT name, email FROM customer'
    cursor.execute(query)
    customers = cursor.fetchall()

    cursor.close()

    return render_template('customer_stats.html', freq_customer=freq_customer, customers=customers)

@app.route('/listCustomerFlights', methods=['GET', 'POST'])
def list_customer_flights():
    email = request.form['customerflights']

    cursor = conn.cursor()

    # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']

    query = '''SELECT DISTINCT flight.Flight_num, flight.Departure_date, flight.Departure_time,
               flight.Departure_airport, flight.Arrival_date, flight.Arrival_time, flight.Arrival_airport
               FROM customer, ticket, flight, purchases
               WHERE customer.email = purchases.customer_email
               AND purchases.ticket_id = ticket.ticket_id
               AND ticket.flight_num = flight.flight_num
               AND flight.airline_name = %s
               AND customer.email = %s'''
    cursor.execute(query, (airline_name, email))
    flights = cursor.fetchall()

    cursor.close()
    return render_template('stats.html', name=email, flights=flights)

@app.route('/destinationStats')
def destination_statistics():
    cursor = conn.cursor()

    # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']

    # find top 3 destinations for last month
    query = '''SELECT airport.Airport_code, Name, Visitors
               FROM ( SELECT Arrival_date, Arrival_airport, COUNT(*) as visitors
                      FROM ticket NATURAL JOIN flight
                      WHERE airline_name = %s
                      AND Arrival_date >= NOW() - INTERVAL 1 MONTH
                      AND Arrival_date <= NOW()
                      GROUP BY Arrival_airport
                      ORDER BY visitors DESC ) as t, airport
               WHERE t.arrival_airport = airport.airport_code
               ORDER BY visitors DESC
               LIMIT 3;'''
    cursor.execute(query, (airline_name))
    destinations_month = cursor.fetchall()

    # find top 3 destinations for last year
    query = '''SELECT airport.Airport_code, Name, Visitors
               FROM ( SELECT Arrival_date, Arrival_airport, COUNT(*) as visitors
                      FROM ticket NATURAL JOIN flight
                      WHERE airline_name = %s
                      AND Arrival_date >= NOW() - INTERVAL 1 YEAR
                      AND Arrival_date <= NOW()
                      GROUP BY Arrival_airport
                      ORDER BY visitors DESC ) as t, airport
               WHERE t.arrival_airport = airport.airport_code
               ORDER BY visitors DESC
               LIMIT 3;'''
    cursor.execute(query, (airline_name))
    destinations_year = cursor.fetchall()

    cursor.close()

    return render_template('destination_stats.html', month=destinations_month, year=destinations_year)

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
