import pymysql

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
    #return (False, "An account already exists with that email")
    if '@' not in email:
        return (False, "Invalid email")
    if len(password) < 6:
        return (False, "Password must be at least 6 characters")
    #add to db
    c = connect()
    cur = c.cursor()
    command="INSERT INTO passengers (fname,lname,email,password,preferred_card_number,preferred_billing_address) VALUES (%s,%s,%s,%s,%s,%s);"
    cur.execute(command,(fname,lname,email,password,preferred_card_number,preferred_billing_address))
    c.commit() 
    return (True, "Registration successful")    
    
def auth_login(email, password):
    #check if combo in db
    #return (False, "Email and/or password incorrect") 
    c = connect()
    cur = c.cursor()
    command="SELECT email,password FROM passengers WHERE email=%s AND password=%s;"
    cur.execute(command,(email,password))
    results = cur.fetchall()
    exist=False
    for row in results:
         exist=True
    if exist:
        return (True, "Login successful", "Jeff")
    return(False,"Email and/or password incorrect ")
