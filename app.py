from flask import Flask, render_template, request, url_for
import pymysql
app = Flask(__name__)

# create connection
try:
	with open('passwd', 'r') as pwd:
		passwd = pwd.read().rstrip('\n')
	conn = pymysql.connect(host='127.0.0.1', port=3306, user='F17336Pteam3', passwd=passwd, database='F17336Pteam3')
	cur = conn.cursor()
except:
	print('ERROR: CANNOT RETRIEVE DB PASSWORD')
	pass

@app.route('/', methods=['GET', 'POST']) 
def index():
	if request.method == 'POST':
		command = request.form['command']
		cur.execute('describe stations;')
		headers = cur.fetchall()
		print(headers)
		cur.execute(command)
		results = cur.fetchall()
		print(results)
		return render_template('index.html', headers=headers, results=results)
	return render_template('index.html')

@app.route('/f17336pteam/stations', methods=['GET', 'POST'])
def viewStations():
	print(request.path,url_for('viewStations'))
	if request.method == 'POST':
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