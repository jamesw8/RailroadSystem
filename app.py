# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session
import dbhelper as db

app = Flask(__name__)
app.secret_key = 'amwatrak'

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
                return redirect(url_for('index'))
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
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST']) 
def index():
    if request.method == 'POST':
        c = db.connect()
        cur = c.cursor()
        command = request.form['command']
        cur.execute('describe stations;')
        headers = cur.fetchall()
        print(headers)
        cur.execute(command)
        results = cur.fetchall()
        print(results)
        return render_template('index.html', headers=headers, results=results)
    return render_template('index.html', logged_in=is_logged_in())

@app.route('/stations', methods=['GET', 'POST'])
def viewStations():
    print(request.path,url_for('viewStations'))
    if request.method == 'POST':
        c = db.connect()
        cur = c.cursor()
        command = request.form['command']
        cur.execute('describe stations;')
        headers = cur.fetchall()
        print(headers)
        cur.execute(command)
        results = cur.fetchall()
        print(results)
        return render_template('index.html', headers=headers, results=results)
    return render_template('index.html', logged_in=is_logged_in())

@app.route('/reservation', methods=['GET','POST'])
def MakeReservation():
        print(request.path,url_for('MakeReservation'))
        if request.method == 'POST':
                command =request.form['command']
                cur.execute('describe stattions;')
                headers=cur.fetchall()
                print(headers);
                cur.execute(command)
                return render_template('makereservation.html')
        return render_template('makereservation.html',logged_in=is_logged_in())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)
