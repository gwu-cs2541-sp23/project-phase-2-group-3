from flask import Flask, session, render_template, redirect, url_for, request
import mysql.connector

app = Flask('app')
app.secret_key = 'this is super secret'

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
    password = request.form['password']
    session['uid'] = request.form['username']
    
    cursor.execute('SELECT * FROM users WHERE uid = %s', (session['uid'], ))
    user_info = cursor.fetchone()
    mydb.commit()
    cursor.close()

    if user_info is None:
      session['error'] = 'That username is not valid'
    elif user_info['password_hash'] == password:
      session['uid'] = str(user_info['uid'])
      session['first_name'] = user_info['first_name']
      session['middle_initial'] = user_info['middle_initial']
      session['last_name'] = user_info['last_name']
      session['address'] = user_info['address']
      session['birthday'] = user_info['birthday']
      session['user_type'] = user_info['user_type']
      return redirect('/Portal')
    else:
      session['error'] = 'That\'s the wrong password you silly goose'

  return render_template('Login.html')

@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))