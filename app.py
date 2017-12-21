from flask import Flask, render_template
import pymysql
app = Flask(__name__)

# create connection
try:
	with open('passwd', 'r') as pwd:
		passwd = pwd.read().rstrip('\n')
	conn = pymysql.connect(host='127.0.0.1', port=3306, user='F17336Pteam3', passwd=passwd, database='railroad1')
	cur = conn.cursor()
except:
	print('ERROR: CANNOT RETRIEVE DB PASSWORD')
	pass

@app.route('/', methods=['GET']) 
def index():
	print(cur)
	print('hi')
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8003)