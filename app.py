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
            session['user_type'] = x['user_type']
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

@app.route("/GShome", methods=['GET', 'POST'])
def GShome():

  if(session['user_type'] != "gradsec"):
        return redirect("/")

  if request.method == 'POST':
    if request.form['button'] == "students":
      return redirect(url_for('?????'))
    
    if request.form['button'] == "applicants":
      return redirect(url_for('GSapps'))

  return render_template('GShome.html')

@app.route("/GSapps", methods=['GET', 'POST'])
def GSapps():

  if(session['user_type'] != "gradsec"):
        return redirect("/")

  cursor = mydb.cursor(dictionary = True)

  if request.method == 'POST':
            
    if request.form["type"] == "updatestat":
            
      cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", (request.form["status"],request.form["id"]))
      mydb.commit()

    if request.form["type"] == "updatestat":
            
      cursor.execute("UPDATE applicant SET decision = %s WHERE uid = %s", (request.form["decision"],request.form["id"]))
      mydb.commit()

    if request.form["type"] == "app":

      cursor.execute("SELECT * FROM applicationForm WHERE uid = %s", (request.form["id"],))
      app = cursor.fetchone()

      id = request.form["id"]

      return render_template("GSseeapps.html", app=app, id=id)

    if request.form["type"] == "review":

      cursor.execute("SELECT * FROM reviewForm WHERE studentID = %s", (request.form["id"],))
      form = cursor.fetchone()

      id = request.form["id"]

      return render_template("GSseereviews.html", form=form, id=id)

  cursor.execute("SELECT * FROM applicant")
  applicants = cursor.fetchall()

  return render_template("GSApps.html", applicants=applicants)

@app.route("/Fhome")
def Fhome():
  return render_template('Fhome.html')

@app.route("/Shome")
def Shome():
  return render_template('Shome.html')

@app.route("/Ahome", methods=['GET', 'POST'])
def Ahome():

  if(session['user_type'] != "applicant"):
      return redirect(url_for('logout'))
  
  if request.method == 'POST':
     if request.form['button'] == "fill":
        return redirect(url_for('applicationFillout'))
    
     if request.form['button'] == "status":
        return redirect(url_for('seeStatus'))
     
  cursor = mydb.cursor(dictionary=True)

  cursor.execute("SELECT appStatus FROM applicant WHERE uid = %s", (session["uid"],))
  status = cursor.fetchone()

  return render_template("Ahome.html", status=status)

@app.route('/email', methods = ['GET', 'POST'])
def email():
    return render_template("email.html")

@app.route("/applicationFillout", methods=['GET', 'POST'])
def applicationFillout():

    if(session['user_type'] != "applicant"):
        return redirect("/")
    
    return render_template("fillApp.html")

@app.route ("/postSubmittingApp", methods=['GET', 'POST'])
def postSubmittingApp():

    if(session['user_type'] != "applicant"):
        return redirect("/")

    if request.method == 'POST':
                
        degreeSeeking = request.form["degreeSeeking"]
        MScheck = request.form["MScheck"]
        MSmajor = request.form["MSmajor"]
        MSuniversity = request.form["MSuniversity"]
        if(request.form["MSgpa"] == ""):
            MSgpa = 0
        else:
            MSgpa = float(request.form["MSgpa"])

        if(request.form["MSyear"] == ""):
            MSyear = 0
        else:
            MSyear = int(request.form["MSyear"])
        BAcheck = request.form["BAcheck"]
        BAmajor = request.form["BAmajor"]
        if(request.form["BAyear"] == ""):
            BAyear = 0
        else:
            BAyear = int(request.form["BAyear"])
        BAuniversity = request.form["BAuniversity"]
        if(request.form["BAgpa"] == ""):
            BAgpa = 0
        else:
            BAgpa = float(request.form["BAgpa"])
        if(request.form["GREverbal"] == ""):
            GREverbal = 0
        else:
            GREverbal = int(request.form["GREverbal"])
        if(request.form["GREquantitative"] == ""):
            GREquantitative = 0
        else:
            GREquantitative = int(request.form["GREquantitative"])
        if(request.form["GREyear"] == ""):
            GREyear = 0
        else:
            GREyear = int(request.form["GREyear"])
        if(request.form["GREadvancedScore"] == ""):
            GREadvancedScore = 0
        else:
            GREadvancedScore = int(request.form["GREadvancedScore"])
        GREadvancedSubject = request.form["GREadvancedSubject"]
        if(request.form["TOEFLscore"] == ""):
            TOEFLscore = 0
        else:
            TOEFLscore = int(request.form["TOEFLscore"])
        TOEFLdata = request.form["TOEFLdata"]
        priorWork = request.form["priorWork"]
        startDate = request.form["startDate"]
        transcriptStatus = "Not Received"
        r1status = "Not Recieved"
        r1writer = request.form["r1writer"]
        r1email = request.form["r1email"]
        r1title = request.form["r1title"]
        r1affiliation = request.form["r1affiliation"]
        r1letter = "Fill When Recieved"
        r2status = "Not Recieved"
        r2writer = request.form["r2writer"]
        r2email = request.form["r2email"]
        r2title = request.form["r2title"]
        r2affiliation = request.form["r2affiliation"]
        r2letter =  "Fill When Recieved"
        r3status = "Not Recieved"
        r3writer =  request.form["r3writer"]
        r3email = request.form["r3email"]
        r3title = request.form["r3title"]
        r3affiliation = request.form["r3affiliation"]
        r3letter =   "Fill When Recieved"
        cursor = mydb.cursor(dictionary= True)
        cursor.execute (
            "INSERT INTO applicationForm (uid, degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdate,priorWork,startDate,transcriptStatus,r1status,r1writer,r1email,r1title,r1affiliation,r1letter,r2status,r2writer,r2email,r2title,r2affiliation,r2letter,r3status,r3writer,r3email,r3title,r3affiliation,r3letter) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)", (session['uid'], degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdata,priorWork,startDate,transcriptStatus,r1status,r1writer,r1email,r1title,r1affiliation,r1letter,r2status,r2writer,r2email,r2title,r2affiliation,r2letter,r3status,r3writer,r3email,r3title,r3affiliation,r3letter)
        )
        mydb.commit()

        decision = "Application Awaiting Materials"
        cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", (decision,session['uid']))
        mydb.commit()

        return render_template("Ahome.html")
    
    return redirect ('/')

@app.route('/seeStatus', methods=['GET', 'POST'])
def seeStatus():

  if(session['user_type'] != "applicant"):
    return redirect(url_for('logout'))

  cursor = mydb.cursor(dictionary=True)

  cursor.execute("SELECT appStatus FROM applicant WHERE uid = %s", (session["uid"],))
  status = cursor.fetchone()

  if status != "Application Incomplete":

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