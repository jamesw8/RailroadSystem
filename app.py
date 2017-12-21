from flask import Flask, render_template, request, url_for
import dbhelper as db
import sys

app = Flask(__name__)



@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        #add new passenger to db
        fname = request.form['fname'].capitalize()
        lname = request.form['lname'].capitalize()
        email = request.form['email']
        password = request.form['password']
        preferred_card_number = request.form['card']
        preferred_billing_address = request.form['address']
        
        response = db.auth_login(fname, lname, email, password, preferred_card_number, preferred_billing_address)
    return render_template("register.html")

        
    

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
    return render_template('index.html')

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
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)