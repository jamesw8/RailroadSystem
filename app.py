# -*- coding: utf-8 -*-
import datetime
from flask import Flask, render_template, flash, request, redirect, url_for, session
import dbhelper as db

app = Flask(__name__)
app.secret_key = 'amwatrak'

# branch stations
branch_1 = [29, 38, 30, 31, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
branch_2 = [26, 27, 28, 39, 40, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
branch_3 = [32, 33, 34, 35, 36, 37, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

def is_logged_in():
    if 'username' in session:
        return (True, session['username'])
    return (False, None)

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if is_logged_in()[0]:
        return redirect(url_for('index'))
    if request.method == 'POST':
        #add new passenger to db
        fname = request.form['fname'].capitalize()
        lname = request.form['lname'].capitalize()
        email = request.form['email']
        password = request.form['password']
        preferred_card_number = request.form['card']
        preferred_billing_address = request.form['address']
        filled_out = True
        for field in [fname, lname, email, password, preferred_card_number, preferred_billing_address]:
            if len(field) == 0:
                filled_out = False        
        if filled_out:
            response = db.auth_register(fname, lname, email, password, preferred_card_number, preferred_billing_address)
            flash(response[1])
            if response[0]:
                return render_template('index.html',logged_in=is_logged_in()) 
        return render_template('index.html',logged_in=is_logged_in()) 
    return render_template('register.html',logged_in=is_logged_in() )

@app.route('/login', methods=['GET', 'POST']) 
def login():
    if is_logged_in()[0]:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        filled_out = True
        for field in [email, password]:
            if len(field) == 0:
                filled_out = False
        
        if filled_out:
            response = db.auth_login(email, password)
            flash(response[1])
            if response[0]:
                session['username'] = response[2]
                return redirect(url_for('index'))
    return render_template('login.html',logged_in=is_logged_in())

@app.route('/', methods=['GET', 'POST']) 
def index():
    c = db.connect()
    cur = c.cursor()
    cur.execute('SELECT * FROM stations;')
    stations = cur.fetchall()
    if request.method == 'POST':
        print(request.form)
        arrival_station = int(request.form['arrive'])
        departure_station = int(request.form['depart'])
        # 0 is south-bound train
        # 1 is north-bound train
        if arrival_station > departure_station:
            direction = 0
        elif arrival_station < departure_station:
            direction = 1
        else:
            flash('Arrival and Departure stations cannot be the same.')
            return render_template('index.html', stations=stations, logged_in=is_logged_in())
        travel_date = datetime.datetime.strptime(request.form['travel_date'], '%Y-%m-%d')
        
        # get date
        if travel_date.weekday() < 5: # if weekday
            day = 1
        else: # if weekend
            day = 0
        cur.execute('SELECT * FROM trains WHERE train_direction=' + str(direction) + ' and train_days=' + str(day) + ';')
        potential_trains = cur.fetchall()
        print('POTENTIAL TRAINS\n', potential_trains)
        listings = []
        for row in potential_trains:

            free, cost = checkTrip(row, departure_station, arrival_station, travel_date)
            if free:
                depart, arrive = getTimes(row, departure_station, arrival_station)
                listings.append({
                    'cost': cost,
                    'departure_station': stations[departure_station][1],
                    'arrival_station': stations[arrival_station][1],
                    'depart_time': depart,
                    'arrive_time': arrive
                    })
        print('LISTINGS HERE\n',listings)
        # train_days
        # 0 is weekends
        # 1 is weekdays
        return render_template('trains.html', logged_in=is_logged_in())
    return render_template('index.html', stations=stations, logged_in=is_logged_in())

@app.route('/trains', methods=['GET', 'POST'])
def viewTrains():
    if request.method == 'POST':
        c = db.connect()
        cur = c.cursor()
        command = request.form['command']
        cur.execute('describe stations;')
        headers = cur.fetchall()
        cur.execute(command)
        results = cur.fetchall()
        return render_template('index.html', headers=headers, results=results)
    return render_template('index.html', logged_in=is_logged_in())

@app.route('/reservation', methods=['GET','POST'])
def makeReservation():
        print(request.path,url_for('makeReservation'))
        if not session.get('logged_in'):
                flash("You need to log in or sign up to Book A Ticket")
                return redirect(url_for('f17336pteam3/login'))
        if request.method == 'POST':
                command = request.form['command']
                cur.execute('describe stations;')
                headers=cur.fetchall()
                cur.execute(command)
                return render_template('makereservation.html')
        return render_template('makereservation.html',logged_in=is_logged_in())

def checkTrip(train, start, end, travel_date):
    c = db.connect()
    cur = c.cursor()
    cost = 0
    train_id = train[0]
    segments = getSegments(train, start, end)
    free_seat = True
    for segment in segments[:-1]:
        cur.execute('SELECT * FROM segments WHERE segment_id=' + str(segment) + ';')
        queried_segment = cur.fetchall()[0]
        # add cost
        cost += queried_segment[3]

        # check if free seat
        cur.execute('SELECT * FROM seats_free WHERE train_id=' + train_id + ' and segment_id=' + queried_segment[0] + ' and seat_free_date=' + str(travel_date.year) + '-' + str(travel_date.month) + '-' + str(travel_date.day) + ';')
        queried_seats = cur.fetchall()[0]
        free_seats = queried_seats[3]
        if free_seats <= 0:
            free_seat = False
            break
    return free_seat, cost

def reduceSeat(train, segments, travel_date):
    c = db.connect()
    cur = c.cursor()
    for segment in segments:
        cur.execute('UPDATE seats_free SET freeseat=freeseat-1 WHERE train_id=' + train[0] + ' and segment_id=' + str(segment) + ' and seat_free_date=' + str(travel_date.year) + '-' + str(travel_date.month) + '-' + str(travel_date.day) + ';')

def getTimes(train, start, end):
    c = db.connect()
    cur = c.cursor()
    cur.execute('SELECT * FROM stops_at WHERE train_id=' + train[0] + ' and station=' + start + ';')
    # time out from departure station
    depart = cur.fetchall()[0][3]
    cur.execute('SELECT * FROM stops_at WHERE train_id=' + train[0] + ' and station=' + end + ';')
    # time in from arrival station
    arrive = cur.fetchall()[0][2]
    return depart, arrive

def getSegments(train, start, end):
    global branch_1
    global branch_2
    global branch_3

    train_start = train[1]
    train_end = train[2]
    # determine which branch
    if train_start in branch_1 and train_end in branch_1:
        branch = branch_1
    elif train_start in branch_2 and train_end in branch_2:
        branch = branch_2
    elif train_start in branch_3 and train_end in branch_3:
        branch = branch_3
    start_index = branch.index(start)
    end_index = branch.index(end)
    segments = branch[start_index:end_index+1]
    if not segments:
        segments = branch[end_index:start_index+1]
    return segments

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)
 
