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
    query = "SELECT * \
            FROM ticket NATURAL JOIN flight \
            WHERE customer_email = %s AND departure_date >= NOW()"
    cursor.execute(query, (email))
    flights = cursor.fetchall()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        # creates a session for the the user
        # session is a built in
        session['username'] = email
        return render_template('home.html', username=email, customer=True, flights=flights)
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

@app.route('/spending')
def customerSpending():
    cursor = conn.cursor()

    cust_email = session['username']
    query = '''SELECT SUM(Sold_price) total
            FROM purchases
            WHERE Customer_email = %s
            AND purchases_date >= NOW() - INTERVAL 1 YEAR
            AND Purchases_date <= NOW();'''
    cursor.execute(query, cust_email)
    total_spent = cursor.fetchall()

    query = '''SELECT SUM(Sold_price) total, MONTHNAME(Purchases_date) month
            FROM  purchases
            WHERE Customer_email = %s
            AND purchases_date >= NOW() - INTERVAL 6 MONTH
            AND Purchases_date <= NOW()
            GROUP BY MONTHNAME(Purchases_date);'''

    cursor.execute(query, cust_email)
    monthly = cursor.fetchall()

    return render_template('customer_spending.html', spent = total_spent, past_six = monthly)

@app.route('/customer_spending_results', methods=['GET', 'POST'])
def customer_spending_results():
    starting_date = request.form['startingdate']
    ending_date = request.form['endingdate']
    cursor = conn.cursor()

    cust_email = session['username']
    query = '''SELECT SUM(Sold_price) total
            FROM purchases
            WHERE Customer_email = %s
            AND purchases_date >= %s
            AND Purchases_date <= %s;'''
    cursor.execute(query, (cust_email, starting_date, ending_date))
    total_spent = cursor.fetchall()

    query = '''SELECT SUM(Sold_price) total, MONTHNAME(Purchases_date) month
            FROM  purchases
            WHERE Customer_email = %s
            AND purchases_date >= %s
            AND Purchases_date <= %s
            GROUP BY MONTHNAME(Purchases_date);'''

    cursor.execute(query, (cust_email, starting_date, ending_date))
    monthly = cursor.fetchall()


    return render_template('customer_spending_results.html', spent = total_spent, within_given = monthly)


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

@app.route('/revenue')
def revenue():
    cursor = conn.cursor()

        # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']
    #revenue by month
    query = '''SELECT SUM(sold_price) total
        FROM ticket NATURAL JOIN purchases NATURAL JOIN FLIGHT
        WHERE airline_name = %s
        AND Arrival_date >= NOW() - INTERVAL 1 MONTH;'''
    cursor.execute(query, (airline_name))
    revenue_month = cursor.fetchall()
    #revenue by year
    query = '''SELECT SUM(sold_price) as total
            FROM ticket NATURAL JOIN purchases NATURAL JOIN FLIGHT
            WHERE airline_name = %s
            AND Arrival_date >= NOW() - INTERVAL 1 YEAR;'''
    cursor.execute(query, (airline_name))
    revenue_year = cursor.fetchall()
    #reveunue by travel class
    query = '''SELECT SUM(sold_price) total, Travel_class
            FROM ticket NATURAL JOIN purchases NATURAL JOIN FLIGHT
            WHERE airline_name = %s
            AND Arrival_date <= NOW()
            GROUP BY Travel_class;'''
    cursor.execute(query, (airline_name))
    revenue_by_class = cursor.fetchall()

    cursor.close()

    return render_template('revenue.html', month=revenue_month, year=revenue_year, by_class = revenue_by_class)

@app.route('/tickets_sold', methods=['GET', 'POST'])
def tickets_sold():

    return render_template("tickets_sold.html")

@app.route('/tickets_sold_result', methods=['GET', 'POST'])
def tickets_sold_result():
    starting_date = request.form['startingdate']
    ending_date = request.form['endingdate']
    cursor = conn.cursor()

        # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']
    query = '''SELECT COUNT(ticket_id) total
            FROM ticket NATURAL JOIN purchases
            WHERE airline_name = %s
            AND Purchases_date >= %s
            AND Purchases_date <= %s;'''
    cursor.execute(query, (airline_name, starting_date, ending_date))
    total_tickets = cursor.fetchall()

    airline_name = data['airline_name']
    query = '''SELECT COUNT(ticket_id) total, MONTHNAME(Purchases_date) month
            FROM ticket NATURAL JOIN purchases
            WHERE airline_name = %s
            AND Purchases_date >= %s
            AND Purchases_date <= %s
            GROUP BY MONTHNAME(Purchases_date);'''

    cursor.execute(query, (airline_name, starting_date, ending_date))
    monthly = cursor.fetchall()

    cursor.close()

    return render_template('tickets_sold_results.html', sold = total_tickets, by_month = monthly)


@app.route('/flightRatings')
def flightRatings():

    cursor = conn.cursor()

            # find current staff' airline
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['username'])
    data = cursor.fetchone()
    airline_name = data['airline_name']

    query = '''SELECT AVG(rating) rating, Flight_num
                FROM flight_reviews NATURAL JOIN flight
                WHERE airline_name = %s
                GROUP BY Flight_num;'''
    cursor.execute(query, airline_name)
    review = cursor.fetchall()

    cursor.close()


    return render_template("airline_flight_reviews.html", avg = review)


@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();

    return render_template('home.html', username=username)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@app.route('/searchUpcomingFlights', methods=['GET', 'POST'])
def searchUpcomingFlights():
    flight_type = request.form['flighttype']

    if flight_type == "roundtrip":
        return render_template("search_flights.html", roundtrip=True)
    else:
        return render_template("search_flights.html", oneway=True)

@app.route('/searchUpcomingFlightsOneway', methods=['GET','POST'])
def searchUpcomingFlightsOneway():
    source_airport = request.form['sourceairport']
    destination_airport = request.form['destinationairport']
    date_option = request.form['dateoption']
    date = request.form['date']

    if date_option == "departure_date":
        query = "SELECT * \
                FROM flight \
                WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s"

    else:
        query = "SELECT * \
                FROM flight \
                WHERE departure_airport = %s AND arrival_airport = %s AND arrival_date = %s"

    cursor = conn.cursor()
    cursor.execute(query, (source_airport, destination_airport, date))

    data = cursor.fetchall()

    if data:
        return render_template("view_future_flights.html", data=data)
    else:
        error = "No flights found"
        return render_template("view_future_flights.html", error=error)

@app.route('/searchUpcomingFlightsRoundtrip', methods=['GET', 'POST'])
def searchUpcomingFlightsRoundtrip():
    source_airport = request.form['sourceairport']
    destination_airport = request.form['destinationairport']
    departing_date = request.form['departingdate']
    arriving_date = request.form['arrivingdate']

    query = "SELECT * \
            FROM flight \
            WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s AND arrival_date = %s"

    cursor = conn.cursor()
    cursor.execute(query, (source_airport, destination_airport, departing_date, arriving_date))

    data = cursor.fetchall()

    if data:
        return render_template("view_future_flights.html", data=data)
    else:
        error = "No flights found"
        return render_template("view_future_flights.html", error=error)

@app.route('/searchActiveFlights', methods=['GET','POST'])
def searchActiveFlights():
    airline_name = request.form['airlinename']
    flight_num = request.form['flightnum']
    departure_airport = request.form['departureairport']
    arrival_airport = request.form['arrivalairport']

    cursor = conn.cursor()

    query = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND departure_airport = %s AND arrival_airport = %s"

    cursor.execute(query, (airline_name, flight_num, departure_airport, arrival_airport))

    data = cursor.fetchall()

    if data:
        return render_template("view_flight_status.html", data=data)
    else:
        error = "Flight not found"
        return render_template("view_flight_status.html", error=error)

@app.route('/bookFlightOnewayOrRoundtrip')
def book():
    return render_template('book_flight_oneway_or_roundtrip.html')

@app.route('/bookFlightOptions', methods=['GET','POST'])
def bookFlightOptions():
    flight_type = request.form['flighttype']

    if flight_type == "roundtrip":
        return render_template("book_flight_options.html", roundtrip=True)
    else:
        return render_template("book_flight_options.html", oneway=True)

@app.route('/bookFlightOneway', methods=['GET','POST'])
def bookFlightOneway():
    departing_airport = request.form['sourceairport']
    arriving_airport = request.form['destinationairport']
    date_option = request.form['dateoption']
    date = request.form['date']

    if date_option == "departure_date":
        query = "SELECT * \
                FROM flight \
                WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s"

    else:
        query = "SELECT * \
                FROM flight \
                WHERE departure_airport = %s AND arrival_airport = %s AND arrival_date = %s"

    cursor = conn.cursor()
    cursor.execute(query, (departing_airport, arriving_airport, date))

    data = cursor.fetchall()

    if data:
        return render_template("book_flight_oneway.html", data=data)
    else:
        error = "No flights found"
        return render_template("book_flight_oneway.html", error=error)

@app.route('/bookFlightRoundtrip', methods=['GET','POST'])
def bookFlightRoundtrip():
    departing_airport = request.form['sourceairport']
    arriving_airport = request.form['destinationairport']
    departing_date = request.form['departingdate']
    returning_date = request.form['returningdate']

    departing_query = "SELECT * \
            FROM flight \
            WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s"

    returning_query = "SELECT * \
            FROM flight \
            WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s"

    cursor = conn.cursor()
    cursor.execute(departing_query, (departing_airport, arriving_airport, departing_date))
    departure = cursor.fetchall()
    cursor.execute(returning_query, (arriving_airport, departing_airport, returning_date))
    arrival = cursor.fetchall()

    if departure and arrival:
        return render_template("book_flight_roundtrip.html", departure=departure, arrival=arrival)
    else:
        error = "No flights found"
        return render_template("book_flight_roundtrip.html", error=error)

@app.route('/bookFlight', methods=['GET','POST'])
def bookFlight():
    print("not done yet")

@app.route('/upcomingFlights', methods=['GET','POST'])
def upcomingFlights():
    query = "SELECT * \
            FROM ticket NATURAL JOIN flight \
            WHERE customer_email = %s AND departure_date >= NOW()"

    cursor = conn.cursor()
    cursor.execute(query, session['username'])
    data = cursor.fetchall()

    if data:
        return render_template("future_customer_flights.html", data=data)
    else:
        error = "No upcoming flights"
        return render_template("future_customer_flights.html", error=error)

@app.route('/pastFlights', methods=['GET','POST'])
def pastFlights():
    query = "SELECT * \
            FROM ticket NATURAL JOIN flight \
            WHERE customer_email = %s AND departure_date < NOW()"

    cursor = conn.cursor()
    cursor.execute(query, session['username'])
    data = cursor.fetchall()

    if data:
        return render_template("past_customer_flights.html", data=data)
    else:
        error = "No past flights"
        return render_template("past_customer_flights.html", error=error)


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
