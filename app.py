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
        return redirect('/f17336pteam3'+url_for('index'))
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
        return redirect('/f17336pteam3'+url_for('index'))
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
                session['id'] = response[3]
                session['username'] = response[2]
                return redirect('/f17336pteam3'+url_for('index'))
    return render_template('login.html',logged_in=is_logged_in())

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if is_logged_in()[0]:
        session.pop('username')
    return redirect('/f17336pteam3'+url_for('index'))

@app.route('/', methods=['GET', 'POST']) 
def index():
    c = db.connect()
    cur = c.cursor()
    cur.execute('SELECT * FROM stations_copy;')
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
        # print('POTENTIAL TRAINS\n', potential_trains)
        listings = []
        for row in potential_trains:

            free, cost = checkTrip(row, departure_station, arrival_station, travel_date)
            if free:
                depart, arrive = getTimes(row, departure_station, arrival_station)
                listings.append({
                    'cost': str(cost),
                    'departure_station': stations[departure_station-1][1],
                    'arrival_station': stations[arrival_station-1][1],
                    'depart_time': str(depart),
                    'arrive_time': str(arrive)
                    })
        if not listings:
            flash('Sorry, there are no listings for the specified trip')
            return redirect('/f17336pteam3'+url_for('index'))
        # print('LISTINGS HERE\n',listings)
        # train_days
        # 0 is weekends
        # 1 is weekdays
        session['listings'] = listings
        session['date'] = request.form['travel_date']
        session['to'] = stations[arrival_station-1][1]
        session['from'] = stations[departure_station-1][1]
        return redirect('/f17336pteam3'+url_for('viewTrains'))
    return render_template('index.html', stations=stations, logged_in=is_logged_in())

@app.route('/trains', methods=['GET', 'POST'])
def viewTrains():
    if not 'listings' in session:
        return redirect('/f17336pteam3'+url_for('index'))
    if request.method == 'POST':
        if not is_logged_in()[0]:
            flash('You need to log in or register to book this ticket')
            return redirect('/f17336pteam3'+url_for('viewTrains'))
        # handle reserve
        c = db.connect()
        cur = c.cursor()
        info=request.form['select'] 
        allinfo=info.split("//")
        print('INFO',type(allinfo),allinfo)
        passenger_id=int(session.get('id'))
        cur.execute("SELECT preferred_card_number,preferred_billing_address from passengers WHERE passenger_id=%s",(passenger_id))
        results=cur.fetchone()
        print('RESULTS',results)
        #inserting into reservations 
        command="INSERT INTO reservations (reservation_date,paying_passenger_id,card_number,billing_address) VALUES (%s,%s,%s,%s);"
        stampdate=session.get('date')+" "+allinfo[2]         
        cur.execute(command,(stampdate,passenger_id,results[0],results[1]))
        c.commit()
        #getting reservation_id
        command0="SELECT reservation_id from reservations WHERE reservation_date=%s AND paying_passenger_id=%s"
        cur.execute(command0,(stampdate,passenger_id))
        results03=cur.fetchone()
        realresults=results03[0]
        if results03[0] is None:
            results03[0]=69
        #getting station i'ds
        firstS=allinfo[0]
        command01='SELECT station_id FROM stations WHERE station_name LIKE "'+str(firstS)+'";'
        print(command01,(firstS))
        cur.execute=(command01)
        bNa=cur.fetchone()
        print('bNa\n',bNa)
        if bNa[0] is None:
            bNa[0]=69
        secondS=allinfo[1]
        cur.execute=(command01,(secondS))
        wR=cur.fetchone()
        if wR[0] is None:
            wR[0]=69
        #inserting into trips table
        command2="INSERT INTO trips (trip_date,trip_station_start,trip_station_ends,fare_type,fare,trip_train_id,reservation_id) VALUES(%s,%s,%s,%s,%s,%s,%s);"
        temp=bNa[0]
        temp1=wR[0]
        fare_type=1 
        train_id=23
        realfare=allinfo[4] 
        tHd=session.get('date')
        cur.execute(command,(tHd,temp,temp1,fare_type,realfare,train_id,realresults))
        c.commit() 
        return render_template('index.html',logged_in=is_logged_in()) 
        #return render_template('index.html', logged_in=is_logged_in(), headers=headers, results=results)
    return render_template('trains.html', logged_in=is_logged_in())

@app.route('/mytrips', methods=['GET'])
def viewTrips():
    if not is_logged_in()[0]:
        return redirect('/f17336pteam3'+url_for('index'))
    c = db.connect()
    cur = c.cursor()
    cur.execute('SELECT * FROM reservations WHERE paying_passenger_id=' + str(session['id']) + ' ORDER BY reservation_date;')
    reservations = cur.fetchall()
    trips = []
    for reservation in reservations:
        cur.execute('SELECT * FROM trips WHERE reservation_id=' + str(reservation[0]) + ';')
        trip = cur.fetchone()
        #start_seg = 
        trips.append({
            'reservation_id': reservation[0],
            'reservation_date': reservation[1],
            'departure_station': stations[int(trip['trip_station_start'])][1],
            'arrival_station': stations[int(trip['trip_station_ends'])][1],
            'trip_date': trip['trip_date'],
            'fare': trip['fare']
            })
    return render_template('mytrips.html', trips=trips, logged_in=is_logged_in())

@app.route('/reservation', methods=['GET','POST'])
def makeReservation():
        if not session.get('logged_in'):
                flash("You need to log in or sign up to Book A Ticket")
                return redirect('/f17336pteam3'+url_for('login'))
        if request.method == 'POST':
                command = request.form['command']
                cur.execute('describe stations;')
                headers=cur.fetchall()
                cur.execute(command)
                return render_template('makereservation.html')
        return render_template('makereservation.html',logged_in=is_logged_in())

@app.route('/cancel/<reservation_id>', methods=['GET','POST'])
def cancelReservation(reservation_id):
    if not session.get('logged_in'):
        flash("You need to log in to cancel a reservation")
        return redirect('/f17336pteam3'+url_for('login'))
    if request.method == 'POST':
        c = db.connect()
        cur = c.cursor()
        try:
            cur.execute('SELECT * FROM reservations WHERE reservation_id=' + reservation_id + ';')
            if cur.fetchone():
                cur.execute('DELETE FROM reservations WHERE reservation_id=' + reservation_id + ';')
                flash('You successfully cancelled your reservation')
                return redirect('/f17336pteam3'+url_for('viewTrips'))
            flash('Error cancelling your reservation')
        except:
            flash('Error cancelling your reservation')
    return redirect('/f17336pteam3'+url_for('viewTrips'))

def checkTrip(train, start, end, travel_date):
    c = db.connect()
    cur = c.cursor()
    cost = 0
    train_id = train[0]
    segments = getSegments(train, start, end)
    if not segments:
        return False, 0
    free_seat = True
    for segment in segments[:-1]:
        cur.execute('SELECT * FROM segments WHERE seg_n_end=' + str(segment) + ';')
        queried_segment = cur.fetchall()
        try:
            queried_segment = queried_segment[0]
        except:
            # segment doesn't exist
            return False, 0
        # add cost
        cost += queried_segment[3]
        # check if free seat
        cur.execute('SELECT * FROM seats_free WHERE train_id=' + str(train_id) + ' and segment_id=' + str(queried_segment[0]) + ' and seat_free_date="' + str(travel_date.year) + '-' + str(travel_date.month) + '-' + str(travel_date.day) + '";')
        queried_seats = cur.fetchall()
        try:
            queried_seats = queried_seats[0]
        except:
            return False, 0
        free_seats = queried_seats[3]
        if free_seats <= 0:
            free_seat = False
            break
    return free_seat, cost

def reduceSeat(train, segments, travel_date):
    c = db.connect()
    cur = c.cursor()
    for segment in segments:
        cur.execute('UPDATE seats_free SET freeseat=freeseat-1 WHERE train_id=' + str(train[0]) + ' and segment_id=' + str(segment) + ' and seat_free_date="' + str(travel_date.year) + '-' + str(travel_date.month) + '-' + str(travel_date.day) + '";')

def getTimes(train, start, end):
    c = db.connect()
    cur = c.cursor()
    cur.execute('SELECT * FROM stops_at_copy WHERE train_id=' + str(train[0]) + ' and station_id=' + str(start) + ';')
    # time out from departure station
    depart = cur.fetchall()[0][3]
    print(train, depart)
    cur.execute('SELECT * FROM stops_at_copy WHERE train_id=' + str(train[0]) + ' and station_id=' + str(end) + ';')
    # time in from arrival station
    arrive = cur.fetchall()[0][2]
    print(train,arrive)
    if train[3]:
        depart, arrive = arrive, depart
    return depart, arrive

def getSegments(train, start, end):
    global branch_1
    global branch_2
    global branch_3
    print(train, start, end)
    train_start = train[1]
    train_end = train[2]
    # determine which branch
    print('RESULTS',type(start),type(end))
    print(str(start)+' in '+str(branch_1)+' and '+str(end)+' in '+str(branch_1))
    print(start in branch_1 and end in branch_1)
    print(str(start)+' in '+str(branch_2)+' and '+str(end)+' in '+str(branch_2))
    print(start in branch_2 and end in branch_2)
    print(str(start)+' in '+str(branch_3)+' and '+str(end)+' in '+str(branch_3))
    print(start in branch_3 and end in branch_3)

    if start in branch_1 and end in branch_1:
        branch = branch_1
    elif start in branch_2 and end in branch_2:
        branch = branch_2
    elif start in branch_3 and end in branch_3:
        branch = branch_3
    else:
        return None
    print('START', start, '\nEND', end)
    # print('CHOSEN BRANCH\n', branch)
    start_index = branch.index(start)
    end_index = branch.index(end)
    segments = branch[start_index:end_index+1]
    if not segments:
        segments = branch[end_index:start_index+1]
    return segments

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)
 
