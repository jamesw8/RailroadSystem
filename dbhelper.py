import pymysql
from werkzeug import generate_password_hash, check_password_hash

def connect():
    try:
        with open('passwd', 'r') as pwd:
            passwd = pwd.read().rstrip('\n')
            conn = pymysql.connect(host='127.0.0.1', port=3306, user='F17336Pteam3', passwd=passwd, database='F17336Pteam3')
            return conn
    except IOError as e:
        print('Error: %s', e)
    return None

def auth_register(fname, lname, email, password, preferred_card_number, preferred_billing_address):
    #check that email not already tied to another user
    c = connect()
    cur = c.cursor()
    check=cur.execute("select * FROM passengers WHERE email=%s;",(emai) )
    if check is None:  
        return (False, "An account already exists with that email")
    
    if '@' not in email:
        return (False, "Invalid email")
    if len(password) < 6:
        return (False, "Password must be at least 6 characters")
    #add to db
    command="INSERT INTO passengers (fname,lname,email,password,preferred_card_number,preferred_billing_address) VALUES (%s,%s,%s,%s,%s,%s);"
    cur.execute(command,(fname,lname,email,generate_password_hash(password),preferred_card_number,preferred_billing_address))
    c.commit() 
    return (True, "Registration successful")    
    
def auth_login(email, password):
    #check if combo in db
    #return (False, "Email and/or password incorrect") 
    c = connect()
    cur = c.cursor()
    command="SELECT passenger_id,fname,email,password FROM passengers WHERE email=%s;"
    cur.execute(command,(email))
    results = cur.fetchone()
    if not results is None:
        if check_password_hash(results[3], password):
            return (True, "Login successful", results[1], results[0])
    return(False,"Email and/or password incorrect")
