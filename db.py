import pymysql

def connect():
    try:
        with open('passwd', 'r') as pwd:
            passwd = pwd.read().rstrip('\n')
            conn = pymysql.connect(host='127.0.0.1', port=3306, user='F17336Pteam3', passwd=passwd, database='F17336Pteam3')
            return conn
    except IOError, e:
            print('Error: %s', e)
   	    return None

def auth_login(fname, lname, email, password, preferred_card_number, preferred_billing_address):
    return (False, "hi")    