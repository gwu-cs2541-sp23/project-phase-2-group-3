import mysql.connector
from flask import Flask, session, render_template, redirect, url_for, request

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

        cursor.execute("SELECT * FROM users WHERE username = %s AND userpass = %s", (name, password))
        x = cursor.fetchone()
        
        if x:
            session['username'] = name
            session['password'] = password
            session['type'] = x['usertype']
            session['uid'] = x['uid']

            if x['usertype'] == "Systems Administrator":
               return redirect(url_for('SAhome'))
               
            if x['usertype'] == "Graduate Secretary":
               return redirect(url_for('GShome'))

            if x['usertype'] == "Faculty":
               return redirect(url_for('Fhome'))

            if x['usertype'] == "Student":
               return redirect(url_for('Shome'))

            if x['usertype'] == "Applicant":
               return redirect(url_for('Ahome'))

        else:
          session['error'] = 'That username or password is not valid'

  return render_template('Login.html')

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
  return render_template('Ahome.html')

app.run(host='0.0.0.0', port=8080)