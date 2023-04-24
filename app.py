import mysql.connector
from flask import Flask, session, render_template, redirect, url_for, request
import random

app = Flask('app')
app.secret_key = 'this is super secret'
app.config["SESSION_PERMANENT"] = False

mydb = mysql.connector.connect(
  host = "group3phase2-taylor23.c71jatiazsww.us-east-1.rds.amazonaws.com",
  user = "admin",
  password = "marksheilazack",
  database = "university"
)

@app.route('/', methods = ['GET', 'POST'])
def login():
  cursor = mydb.cursor(dictionary=True)

  session['error'] = ''

  if request.method == 'POST':
        name = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (name, password))
        x = cursor.fetchone()
        
        if x:
            session['username'] = name
            session['password'] = password
            session['type'] = x['user_type']
            session['uid'] = x['uid']
            session['first_name'] = x['first_name']
            session['last_name'] = x['last_name']

            if x['user_type'] == "sysadmin":
               return redirect(url_for('SAhome'))
               
            if x['user_type'] == "gradsec":
               return redirect(url_for('GShome'))

            if x['user_type'] == "employee":
               return redirect(url_for('Fhome'))

            if x['user_type'] == "student":
               return redirect(url_for('Shome'))

            if x['user_type'] == "applicant":
               return redirect(url_for('Ahome'))

        else:
          session['error'] = 'That username or password is not valid'

  return render_template('Login.html')

# Account Registration Page 
@app.route('/register', methods=['GET', 'POST'])
def register():
  cursor = mydb.cursor(dictionary=True)

  session['error_account_creation'] = ''
  if request.method == 'POST':
    if 'username' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'ssn' in request.form and 'address' in request.form:
      uid = random.randrange(10000000, 99999999)
      val = (
          uid,
          request.form['username'],
          request.form['password'],
          request.form['first_name'],
          request.form['last_name'],
          request.form['ssn'],
          request.form['address'],
          'applicant')
      
      cursor.execute(
          'INSERT INTO users (uid, username, password, first_name, last_name, ssn, address, user_type) values (%s, %s, %s, %s, %s, %s, %s, %s);', val)
      cursor.execute(
         'INSERT INTO applicant (uid, appStatus, decision) values (%s, %s, %s);', (uid, 'Application Incomplete', 'Pending'))
      mydb.commit()

      return redirect('/')
    else:
      session['error_account_creation'] = 'Please fill fields before clicking submit'

  return render_template('register.html')

@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))

@app.route("/SAhome")
def SAhome():
  return render_template('SAhome.html')

@app.route("/GShome")
def GShome():
  return render_template('GShome.html')

@app.route("/Fhome")
def Fhome():
  return render_template('Fhome.html')

@app.route("/Shome")
def Shome():
  return render_template('Shome.html')

@app.route("/Ahome")
def Ahome():

  cursor = mydb.cursor(dictionary=True)

  if(session['type'] != "applicant"):
      return redirect(url_for('logout'))
  
  if request.method == 'POST':
     if request.form['button'] == "fill":
        return redirect(url_for('applicationFillout'))
    
     if request.form['button'] == "status":
        return redirect(url_for('seeStatus'))

  return render_template("Ahome.html")

@app.route('/seeStatus', methods=['GET', 'POST'])
def seeStatus():

  if(session['type'] != "applicant"):
    return redirect(url_for('logout'))

  cursor = mydb.cursor(dictionary=True)

  cursor.execute("SELECT appStatus FROM applicant WHERE uid = %s", (session["uid"],))
  status = cursor.fetchone()
  cursor.execute("SELECT transcriptStatus FROM applicationForm WHERE uid = %s", (session["uid"],))
  transcriptstatus = cursor.fetchone()
  cursor.execute("SELECT r1status FROM applicationForm WHERE uid = %s", (session["uid"],))
  r1status = cursor.fetchone()
  cursor.execute("SELECT r2status FROM applicationForm WHERE uid = %s", (session["uid"],))
  r2status = cursor.fetchone()
  cursor.execute("SELECT r3status FROM applicationForm WHERE uid = %s", (session["uid"],))
  r3status = cursor.fetchone()
  cursor.execute("SELECT decision FROM applicant WHERE uid = %s", (session["uid"],))
  decision = cursor.fetchone()

  return render_template ("seeStatus.html", status = status, transcriptstatus = transcriptstatus, r1status = r1status, r2status = r2status, r3status = r3status, decision = decision)

app.run(host='0.0.0.0', port=8080)