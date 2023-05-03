import mysql.connector
from flask import Flask, session, render_template, redirect, url_for, request

import time, random, datetime

app = Flask('app')
app.secret_key = 'this is super secret'
app.config["SESSION_PERMANENT"] = False

mydb = mysql.connector.connect(
  host = "group3phase2-taylor23.c71jatiazsww.us-east-1.rds.amazonaws.com",
  user = "admin",
  password = "marksheilazack",
  database = "university"
)

# login page for all users 
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
# update personal information
@app.route('/updateinfo', methods=['GET', 'POST'])
def updateinfo():
  #connect to the database
  cur = mydb.cursor(dictionary = True)

  if request.method == 'POST':
    #update the sql database here
    if((request.form["lname"])):
      cur.execute("UPDATE users SET last_name = %s WHERE uid = %s", ( str((request.form["lname"])), session['uid']))
      mydb.commit()

    if((request.form["fname"])):
      cur.execute("UPDATE users SET first_name = %s WHERE uid = %s", ( str((request.form["fname"])), session['uid']))
      mydb.commit()

    if((request.form["address"])):
      cur.execute("UPDATE users SET address = %s WHERE uid = %s", ( str((request.form["address"])), session['uid']))
      mydb.commit()
    
    #reset the session variables to change if the first and last name was updated
    cur.execute("SELECT username, password, uid, first_name, last_name FROM users WHERE uid = %s", (session['uid'], ))
    data = cur.fetchone()
    mydb.commit()
    session['first_name'] = data['first_name']
    session['last_name'] = data['last_name']
    return redirect('/')
  

@app.route('/updateuserinfo/<id>', methods=['GET', 'POST'])
def updateuserinfo(id):
  #connect to database
  cur = mydb.cursor(dictionary = True)

  if request.method == 'POST':
    # update sql database 
    if((request.form["last_name"])):
      cur.execute("UPDATE users SET last_name = %s WHERE uid = %s", ( str((request.form["last_name"])), id))
      mydb.commit()

    if((request.form["first_name"])):
      cur.execute("UPDATE users SET first_name = %s WHERE uid = %s", ( str((request.form["first_name"])), id))
      mydb.commit()

    if((request.form["address"])):
      cur.execute("UPDATE users SET address = %s WHERE uid = %s", ( str((request.form["address"])), id))
      mydb.commit()
    
    return redirect('/')
 
@app.route("/GShome", methods=['GET', 'POST'])
def GShome():

  if(session['user_type'] != "gradsec"):
        return redirect("/")

  if request.method == 'POST':
    if request.form['button'] == "students":
      return redirect(url_for('GSstudents'))
    
    if request.form['button'] == "applicants":
      return redirect(url_for('GSapps'))
    
    if request.form['button'] == "alumni":
       return redirect(url_for('GSalumni'))

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
  

@app.route("/GSstudents", methods=['GET', 'POST'])
def GSstudents():
  # get name, id, courses, and grades for all current students
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)
    students = list()

    cur.execute("SELECT first_name, last_name, uid FROM users WHERE user_type = %s", ('student', ))
    students = cur.fetchall()
    for student in students:
       cur.execute ("SELECT degree_type FROM students WHERE uid = %s", (student['uid'], ))
       degree = cur.fetchone()
       degree_type = {'degree_type': degree}
       student
    
  return render_template('GSstudents.html', students=students)

student_info = list()

@app.route('/student/<uid>', methods=['GET', 'POST'])
def gs_student_data(uid):
  if session['user_type'] == 'gradsec':

    cur = mydb.cursor(dictionary = True)

    degree = list()

    cur.execute("SELECT first_name, last_name, uid, address FROM users WHERE uid = %s", (uid, ))
    student_basic_info = cur.fetchall()
    student_info.insert(0, student_basic_info)
    eligible = {'eligible': 'True', 'reason': []}
    student_info.insert(1, eligible)

    # get degree_id
    cur.execute("SELECT degree_type FROM students WHERE uid  = %s", (uid, ))
    degree = cur.fetchall()
    if not degree:
        degree = None
    student_info.insert(2, degree)

    # get courses and grades
    cur.execute("SELECT cid, grade FROM student_classes WHERE student_uid  = %s", (uid, ))
    student_grades = cur.fetchall()
    if not student_grades:
        student_grades = list()
    student_info.insert(3, student_grades)

    # get gpa requirement for degree
    if degree == 'ms':
      gpa_req = 3
    
    if degree == 'phd':
       gpa_req = 3.6

    # get gpa and credit hours
    # counters for grades
    grade_points = 0
    total_credit_hours = 0
    num_courses = 0
    bad_grade_ctr = 0
    req_courses_ctr = 0
    outside_courses_ctr = 0
    cs_courses_ctr = 0
    cs_credit_hours = 0

    for i in range(len(student_grades)):
        cur.execute("SELECT credit_hours FROM courses WHERE id = %s", (student_grades[i]['course_id'], ))
        course_hours = cur.fetchall()
        if student_grades[i]['course_id'] == 100 or 101 or 102:
            req_courses_ctr = req_courses_ctr + 1
        if student_grades[i]['course_id'] == 119 or 120 or 121:
            outside_courses_ctr = outside_courses_ctr + 1
        if student_grades[i]['course_id'] != 119 or 120 or 121:
            cs_courses_ctr = cs_courses_ctr + 1
            cs_credit_hours = cs_credit_hours + course_hours[0]['credit_hours']
        total_credit_hours = total_credit_hours + course_hours[0]['credit_hours']
        grade = student_grades[i]['grade'] 
        
        if grade == 'A':
            grade_points = grade_points + 4
            num_courses = num_courses + 1
        if grade == 'A-':
            grade_points = grade_points + 3.7
            num_courses = num_courses + 1
        if grade == 'B+':
            grade_points = grade_points + 3.3
            num_courses = num_courses + 1
        if grade == 'B':
            grade_points = grade_points + 3
            num_courses = num_courses + 1
        if grade == 'B-':
            grade_points = grade_points + 2.7
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'C+':
            grade_points = grade_points + 2.3
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'C':
            grade_points = grade_points + 2
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'C-':
            grade_points = grade_points + 1.7
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'F':
            grade_points = grade_points + 0
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
    if num_courses == 0:
       num_courses = 1
    gpa = grade_points / num_courses
    gpa = round(gpa, 2)
    gpa_dict = {'gpa': gpa}
    total_credit_hours_dict = {'total_credit_hours': total_credit_hours}
    student_info.insert(4, gpa_dict)
    student_info.insert(5, total_credit_hours_dict)
    if bad_grade_ctr >= 3:
        cur.execute("INSERT INTO student_status VALUES (%s, %s)", (uid , "suspended"))
        gs_all_suspended()

    # check if they've applied for graduation
    cur.execute("SELECT applied_grad FROM students WHERE uid = %s", (uid, ))
    applied = cur.fetchall()
    if not applied:
       student_info[1]['eligible'] = 'False'
       student_info[1]['reason'].insert(-1, 'Has not applied to graduate')

    print(student_info)
    # requirements for master's students
    if student_info[2][0]['degree_type'] == 'MS':
        # check gpa
        if student_info[4]['gpa'] < 3.0:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met GPA requirement')
        # check credit hours
        if student_info[5]['total_credit_hours'] < 30:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met credit hour requirement')
        # check for grades below a B
        if bad_grade_ctr > 2:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has two or more grades below a B')
        # check for required courses
        if req_courses_ctr < 3:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not taken required courses')
        # check for outside courses
        if outside_courses_ctr < 2:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not taken enough classes outside of CS')

    # requirements for phd students
    if student_info[2][0]['degree_type'] == 'PHD':
        # check gpa
        if student_info[4]['gpa'] < 3.5:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met GPA requirement')
        # check credit hours
        if student_info[5]['total_credit_hours'] < 36:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met credit hour requirement')
        # check for grades below a B
        if bad_grade_ctr > 1:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has one or more grades below a B')
        # check for 30 credits of CS courses
        if cs_credit_hours < 30:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met CS course credit requirement')

        # check if thesis has been approved
        cur.execute("SELECT thesis_approved FROM students WHERE uid = %s", (uid, ))
        thesis_approved = cur.fetchall()
        student_info.append(thesis_approved)
        if not thesis_approved:
          student_info[1]['eligible'] = 'False'
          student_info[1]['reason'].append('Thesis has not been approved')

    # get advisor
    cur.execute("SELECT advisor_uid FROM advisor_assignments WHERE student_uid = %s", (uid, ))
    advisor_id = cur.fetchall()

    if not advisor_id:
        advisor_name = [{'first_name': "N/A"}]
        student_info.insert(6, advisor_name)
        return render_template ("student_data.html", student_info=student_info)
    
    cur.execute("SELECT first_name, last_name FROM users WHERE uid = %s", (advisor_id[0]['advisor_uid'], ))
    advisor_name = cur.fetchall()
    student_info.insert(6, advisor_name)
    
    return render_template ("student_data.html", student_info=student_info)
  
  else:
    return redirect('/')
  
@app.route('/graduate/<uid>')
def gs_graduate(uid):
  if session['user_type'] == 'gradsec':
    data = list()
    data.insert(0, uid)

    cur = mydb.cursor(dictionary = True)

    # get degree_id
    cur.execute("SELECT degree_type FROM students WHERE uid = %s", (uid, ))
    degree_id = cur.fetchall()
    data.insert(1, degree_id)

    cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (uid, ))
    name = cur.fetchall()
    data.insert(2, name)

    cur.execute("INSERT INTO alumni (uid, grad_year) VALUES (%s, %s)", (uid, 2023))
    cur.execute("DELETE FROM students WHERE uid = %s", (uid, ))
    cur.execute("UPDATE users SET user_type = %s WHERE user_id = %s", ('alumni', uid))

    return render_template("graduate.html", data=data)

  else:
    return redirect('/')
  
# lists all suspended students
@app.route('/all_suspended')
def gs_all_suspended():
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)
    suspended_students_names = list()

    cur.execute("SELECT uid FROM students WHERE is_suspended = %s", (True, ))
    all_suspended = cur.fetchall()

    for x in range(len(all_suspended)):
        cur.execute("SELECT first_name, last_name FROM users WHERE uid = %s", (all_suspended[x]['uid'], ))
        name = cur.fetchall()
        suspended_students_names.append(name)

    return render_template("suspension.html", suspended_students_names=suspended_students_names)
  else:
    return redirect('/')
  
# assign advisor to ALL students
@app.route('/assignadvisor')
def assignadvisor():
  if session['user_type'] == 'gradsec':
    type = session['user_type']
    cur = mydb.cursor(dictionary = True)

    # get all advisors
    cur.execute("SELECT uid from employee where is_advisor = %s", (True, ))
    advisor_ids = cur.fetchall()
    advisors = list()
    for x in range(len(advisor_ids)):
       cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (advisor_ids[x]['uid'], ))
       advisors = cur.fetchall()

    # get students
    cur.execute("SELECT uid, first_name, last_name FROM users WHERE user_type = %s", ('student', ))
    students = cur.fetchall()

    return render_template("assign_advisor.html", advisors = advisors, students=students, type = type)
  
  else:
    return redirect('/')

@app.route('/assigned', methods = ['GET', 'POST'])
def assigned():

  if session['user_type'] == 'gradsec':

    if request.method == "POST":
      cur = mydb.cursor(dictionary = True)
      student = (request.form["student"])
      advisor = (request.form["advisor"])

      # check if the student already has an advisor
      cur.execute("SELECT student_uid FROM advisor_assignments WHERE student_uid = %s", (student, ))
      student_uid = cur.fetchall()
      # if the student is already in the table, update their advisor
      if student_uid:
        cur.execute("UPDATE advisor_assignments SET advisor_uid = %s WHERE student_uid = %s", (advisor, student))
        mydb.commit()
      # if the student doesn't have an advisor, insert both of their information
      if not student_uid:
         cur.execute("INSERT INTO advisor_assignments (advisor_uid, student_uid) VALUES (%s, %s)", (advisor, student))
         mydb.commit()
      return redirect('/GSstudents')
  else:
    return redirect('/')

@app.route("/GSenrolled_masters")
def gs_enrolled_masters():
  if session['user_type'] == 'gradsec':
      
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT uid FROM students WHERE degree_type = %s", ('MS', ))
    masters_uids = cur.fetchall()

    masters_info = list()
    for x in range(len(masters_uids)):
        cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (masters_uids[x]['uid'], ))
        info = cur.fetchall()
        masters_info.append(info)

    return render_template("GSmasters.html", masters_info = masters_info)
  else:
     return redirect('/')
  
@app.route("/GSenrolled_phd")
def gs_enrolled_phd():
  if session['user_type'] == 'gradsec':
      
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT uid FROM students WHERE degree_type = %s", ('PHD', ))
    phd_uids = cur.fetchall()

    phd_info = list()
    for x in range(len(phd_uids)):
        cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (phd_uids[x]['uid'], ))
        info = cur.fetchall()
        phd_info.append(info)

    return render_template("GSphd.html", phd_info = phd_info)
  else:
     return redirect('/')
  
# GS - list all alumni
@app.route("/GSalumni")
def GSalumni():
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT uid FROM alumni")
    alumni_uids = cur.fetchall()
  
    alumni_info = list()
    for x in range(len(alumni_uids)):
       cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (alumni_uids[x]['uid'], ))
       info = cur.fetchall()
       alumni_info.append(info)

    return render_template("GSalumni_list.html", alumni_info=alumni_info)

  else:
    return redirect('/')
  

@app.route("/GSalumni/masters")
def GSalumni_masters():
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT uid FROM alumni WHERE degree_type = %s", ('MS', ))
    alumni_uids_ms = cur.fetchall()
  
    ms_alumni_info = list()
    for x in range(len(alumni_uids_ms)):
       cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (alumni_uids_ms[x]['uid'], ))
       info = cur.fetchall()
       ms_alumni_info.append(info)

    return render_template("GSalumni_list_ms.html", ms_alumni_info=ms_alumni_info)

  else:
    return redirect('/')



  
# END OF GRADSEC FUNCTIONALITY
  
@app.route("/advisor_home")
def advisor_home():
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT is_advisor FROM employee WHERE uid = %s", (session['uid'], ))
    is_advisor = cur.fetchall()

    if is_advisor:
      cur = mydb.cursor(dictionary = True)
      cur.execute("SELECT first_name, last_name, address, uid FROM users WHERE uid = %s", (session['uid'], ))
      data = cur.fetchone()
      mydb.commit()

      # see what type(s) of employee they are
      cur.execute("SELECT * FROM employee WHERE uid = %s", (data['uid'], ))
      employee_types = cur.fetchall()
      mydb.commit()

      return render_template("advisor_home.html", title = 'Advisor Home Page', data = data, employee_types = employee_types)
    else:
      return redirect('/Fhome')
  else:
    return redirect('/')
  
# list all phd advisees
@app.route('/faculty/advisees/phd')
def phd_students():
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT is_advisor FROM employee WHERE uid = %s", (session['uid'], ))
    is_advisor = cur.fetchall()
    if is_advisor:
   
    # get advisor id from login session 
      adv_id = session['uid']

      # get all PhD students
      cursor = mydb.cursor(dictionary=True)
      cursor.execute("SELECT uid FROM students WHERE degree_type = %s", ('PHD', ))
      phd_students = cursor.fetchall()

      phd_advisees = list()

      for x in range(len(phd_students)):
        # get students that belong to this specific advisor
        cursor.execute("SELECT student_uid FROM advisor_assignments WHERE advisor_uid = %s", (adv_id, ))
        info1 = cur.fetchall()
        print(info1[x])

        # get more info about each advisee
        cursor.execute("SELECT * FROM users WHERE uid = %s", (info1[x]['student_uid'], ))
        info2 = cur.fetchall()
        phd_advisees.append(info2)

      return render_template('phd_students.html', phd_advisees=phd_advisees)

  else:
    return redirect('/')

@app.route("/Fhome", methods=['GET', 'POST'])
def Fhome():

  if(session['user_type'] != "employee"):
        return redirect("/")
  
  if request.method == 'POST':
    if request.form['button'] == "professor":
      return redirect(url_for('?????'))
    
    if request.form['button'] == "advisor":
      return redirect(url_for('advisor_home'))
    
    if request.form['button'] == "chair":
      return redirect(url_for('?????'))
    
    if request.form['button'] == "reviewer":
      return redirect(url_for('FRhome'))
  
  cursor = mydb.cursor(dictionary = True)

  cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
  booleans = cursor.fetchone()

  print(booleans)

  return render_template('Fhome.html', booleans=booleans)

@app.route('/FRhome', methods=['GET', 'POST'])
def FRhome():

    if(session['user_type'] != "employee"):
        return redirect("/")

    cursor = mydb.cursor(dictionary = True)

    if request.method == 'POST':
      if request.form['button'] == "fill":
        return redirect(url_for('fillReviewForm'))
      
      if request.form['button'] == "view":
        return redirect(url_for('?????'))

    cursor.execute("SELECT * FROM applicant WHERE appStatus = %s", ("Application Under Review",))
    applicants = cursor.fetchall()

    return render_template("FRhome.html", applicants = applicants)

@app.route('/fillReviewForm', methods=['GET','POST'])
def fillReviewForm():

    if(session['user_type'] == "employee"):
    
        return render_template("fillReviewForm.html")
    
    else:
        return redirect("/")

@app.route('/submitReviewForm', methods=['GET','POST'])
def submitReviewForm():

    if(session['user_type'] == "employee"):

        cursor = mydb.cursor(dictionary = True)
        studentID = request.form["studentID"]
        reviewer = request.form["reviewer"]
        r1rating = request.form["r1rating"]
        r1generic = request.form["r1generic"]
        r1credible = request.form["r1credible"]
        r1from = request.form["r1from"]
        r2rating = request.form["r2rating"]
        r2generic = request.form["r2generic"]
        r2credible = request.form["r2credible"]
        r2from = request.form["r2from"]
        r3rating = request.form["r3rating"]
        r3generic = request.form["r3generic"]
        r3credible = request.form["r3credible"]
        r3from = request.form["r3from"]
        GASrating = request.form["GASrating"]
        deficiencies = request.form["deficiencies"]
        rejectReason = request.form["rejectReason"]
        thoughts = request.form["thoughts"]
        semesterApplied = request.form["semesterApplied"]
        decision = "pending"

        cursor.execute("INSERT INTO reviewForm (studentID,reviewer,r1rating,r1generic,r1credible,r1from,r2rating,r2generic,r2credible,r2from,r3rating,r3generic,r3credible,r3from,GASrating,deficiencies,rejectReason,thoughts,semesterApplied,decision) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (studentID,reviewer,r1rating,r1generic,r1credible,r1from,r2rating,r2generic,r2credible,r2from,r3rating,r3generic,r3credible,r3from,GASrating,deficiencies,rejectReason,thoughts,semesterApplied,decision,))
        mydb.commit()

        cursor.execute("UPDATE applicant SET appStatus = %s WHERE studentID = %s", ("application reviewed",studentID))
        mydb.commit()

        return redirect('/FRhome')
    
    else:
        return redirect("/")
    
# list all masters advisees
@app.route('/faculty/advisees/masters')
def m_students():
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT is_advisor FROM employee WHERE uid = %s", (session['uid'], ))
    is_advisor = cur.fetchall()
    if is_advisor:
      # get advisor id from login session 
      adv_id = session['uid']

      # get all master's students
      cursor = mydb.cursor(dictionary=True)
      cursor.execute("SELECT uid FROM students WHERE degree_type = %s", ('MS', ))
      m_students = cursor.fetchall()
      m_advisees = list()

      # get students that belong to this specific advisor
      cursor.execute("SELECT student_uid FROM advisor_assignments WHERE advisor_uid = %s", (adv_id, ))
      info1 = cur.fetchall()

      for x in range(len(m_students)):
        if not info1:
          break
        # get more info about each advisee
        cursor.execute("SELECT * FROM users WHERE uid = %s", (info1[x]['student_uid'], ))
        info2 = cur.fetchall()
        m_advisees.insert(1, info2)

      return render_template('masters_students.html', m_advisees=m_advisees)
    
    else:
      return redirect('/')

  else:
    return redirect('/')
  
# review transcript of advisee
@app.route('/faculty/advisees/<transcript_id>')
def faculty_transcript(transcript_id): 
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT is_advisor FROM employee WHERE uid = %s", (session['uid'], ))
    is_advisor = cur.fetchall()
    if is_advisor:
    
      if transcript_id != None:
            transcript_id = int(transcript_id)

            query = '''
          SELECT users.uid, users.user_type, users.first_name, users.last_name, advisor_assignments.student_uid, advisor_assignments.advisor_uid, students.uid, students.degree_type, 
              student_classes.student_uid, student_classes.cid, student_classes.grade, classes.cid, classes.dept, classes.class_number, classes.title, classes.credit_hours
              from users 
              JOIN advisor_assignments ON users.uid = advisor_assignments.student_uid
              JOIN students ON advisor_assignments.student_uid = students.uid
              JOIN student_classes ON users.uid = student_classes.student_uid
              JOIN classes ON classes.cid = student_classes.cid
              where user.uid=%s '''
        
            cursor= mydb.cursor(dictionary=True)

            cursor.execute(query,(transcript_id,) )
            result =cursor.fetchall()
            cursor.close()

            return render_template('student_transcript.html', transcript=result)

    else:
      return redirect('/')
    
# review form 1 answers from advisees
@app.route('/faculty/advisees/form1/<user_id>', methods=['GET', 'POST'])
def faculty_form(user_id): 
  
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT is_advisor FROM employee WHERE uid = %s", (session['uid'], ))
    is_advisor = cur.fetchall()

    if is_advisor:
      # get uid
      if request.method == "GET":
        if user_id != None:
            user_id = int(user_id)

            # get first and last name from student
            cur.execute("SELECT first_name, last_name, uid, FROM users WHERE uid = %s", (user_id, ))
            name = cur.fetchall()

            # get all class ids from form1_answer table for a student
            cur.execute("SELECT cid FROM form1_answer WHERE student_uid = %s", (user_id, ))
            class_ids = cur.fetchall()

            # get all info from classes listed in form1
            for x in range(len(class_ids)):
               cur.execute("SELECT * FROM classes WHERE cid = %s", (class_ids[x], ))
               form1_answer = cur.fetchall()

        return render_template('view_form1.html', name=name, form1_answer=form1_answer)
  
  else:
    return redirect('/')

# END OF ADVISOR FUNCTIONALITY

# student
@app.route("/Shome")
def Shome():

  if session['user_type'] == 'student':
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT address, uid FROM users WHERE username = %s", (session['username'], ))
    data = cur.fetchone()
    mydb.commit()

    # get degree type
    cur.execute("SELECT degree_type FROM students WHERE uid = %s", (session['uid'], ))
    degree = cur.fetchall()

    #get the students grade
    cur.execute("SELECT grade FROM student_classes WHERE student_uid = %s", (session['uid'], ))
    grades = cur.fetchall()
    invalid_grades = ['C', 'D', 'F']
    counter = 0

    for g in grades:
      if g in invalid_grades:
        counter += 1

    # three grades below a B --> change 'is_suspended' to true
    if counter >= 3:
      cur.execute("INSERT into students (is_suspended) VALUES %s", (True, ))
      mydb.commit()
        
    cur.execute("SELECT is_suspended FROM students WHERE uid = %s", (session['uid'], ))
    suspended = cur.fetchall()
    mydb.commit()

    return render_template("Shome.html", title = 'Student Logged In', data = data, suspended = suspended, degree = degree)
  
  else:
    return redirect('/')

@app.route('/form1', methods=['GET', 'POST'])
def form():

  ### can't tell if this works because there's nothing in the current_sections table ###

  cur = mydb.cursor(dictionary = True)
  # check if student
  if session['user_type'] == 'student':

    if request.method == "GET":
      return render_template("form1_student.html")

    if request.method == 'POST':
      check = 0
      for i in range(100, 122):
        checkboxes = request.form.getlist(str(i))
        for checkbox in checkboxes:
          if(checkbox == "yes"):
            if (check == 0):
              #cur.execute("DELETE from student_classes WHERE grade = %s and student_uid = %s", ('IP', session['uid'] ))
              #mydb.commit()
              cur.execute("DELETE from form1_answer WHERE student_uid = %s", (session['uid'], ))
              mydb.commit()
              check +=1

            cur.execute("SELECT grade FROM student_classes WHERE cid = %s and student_uid = %s", (i, session['uid']))
            grade = cur.fetchone()
            mydb.commit()

            invalid_grades = ['D', 'F']
            if grade != None:
              if grade in invalid_grades:
                  cur.execute("DELETE from student_classes WHERE cid = %s", (i, ))
                  mydb.commit()

                  # get section id from specific class
                  cur.execute("SELECT section_id FROM current_sections WHERE cid = %s", (i, ))
                  section_id = cur.fetchone()
                  mydb.commit()

                  # insert into student_classes
                  cur.execute("INSERT into student_classes (student_uid, cid, section_id, grade, finalized) VALUES (%s, %s, %s, %s, %s)", (session['uid'], i, section_id, 'IP', False))
                  mydb.commit()

            else:
              # get section id from specific class
              cur.execute("SELECT section_id FROM current_sections WHERE cid = %s", (i, ))
              section_id = cur.fetchone()
              mydb.commit()

              # insert into student_classes
              cur.execute("INSERT into student_classes (student_uid, cid, section_id, grade, finalized) VALUES (%s, %s, %s, %s, %s)", (session['uid'], i, section_id, 'IP', False))
              mydb.commit()

            cur.execute("INSERT into form1_answer (student_uid, cid) VALUES (%s, %s)", (session['uid'], i))
            mydb.commit()

            cur.execute("SELECT * from student_classes WHERE cid = %s and student_uid = %s", (i, session['uid']))
            data = cur.fetchall()
            
    return redirect('/')

  else:
    return redirect('/')

# allows student to apply for graduation
@app.route('/applygrad', methods=['GET', 'POST'])
def applygrad():
   
  if session['user_type'] == 'student':
  #connect to the database
    cur = mydb.cursor(dictionary = True)
    if request.method == "GET":
      return render_template("applying.html")

    if request.method == "POST":
      type = (request.form["dates"])
      if(type == "ms"):
        y = 20
      if(type == "phd"):
        y = 21
      cur.execute("INSERT into students (applied_grad) VALUES (%s) WHERE uid = %s", (True, session['uid']))
      mydb.commit()
      return render_template("applygrad.html")
  else:
    return redirect('/')


  return render_template("applygrad.html")

# alumni
@app.route("/alum_home")
def alum_home():
    
    if session['user_type'] == 'alumni':
      cur = mydb.cursor(dictionary = True)
      cur.execute("SELECT address, uid FROM users WHERE username = %s", (session['username'],))
      data = cur.fetchone()
      mydb.commit()
      return render_template("alum_home.html", title = 'Alumni Logged In', data = data)
    
    else:
      return redirect('/')
    
# view course history for students and alumni
@app.route('/coursehist/<id>', methods=['GET', 'POST'])
def coursehist(id):

  if session['user_type'] == 'student' or session['user_type'] == 'alumni':
    type = session['user_type']
    #connect to the database
    cur = mydb.cursor(dictionary = True)

    if request.method == "POST":
      # classes that the student is taking
      cur.execute("SELECT cid, grade FROM student_classes WHERE student_uid = %s", (id, ))
      data = cur.fetchall()

      #all available classes
      cur.execute("SELECT cid, title, class_number, credit_hours from classes")
      courses = cur.fetchall()
      mydb.commit()

      grade_points = 0
      num_courses = 0
      credits = 0
      cur.execute("SELECT cid, grade FROM student_classes WHERE student_uid = %s", (id, ))
      student_grades = cur.fetchall()

      for i in range(len(student_grades)):
        cur.execute("SELECT credit_hours FROM classes WHERE cid = %s", (student_grades[i]['cid'], ))
        course_hours = cur.fetchone()
        credits += course_hours['credit_hours']
        grade = student_grades[i]['grade'] 
        #num_courses = num_courses + 1
        if grade == 'A':
            grade_points = grade_points + 4
            num_courses = num_courses + 1
        if grade == 'A-':
            grade_points = grade_points + 3.7
            num_courses = num_courses + 1
        if grade == 'B+':
            grade_points = grade_points + 3.3
            num_courses = num_courses + 1
        if grade == 'B':
            grade_points = grade_points + 3
            num_courses = num_courses + 1
        if grade == 'B-':
            grade_points = grade_points + 2.7
            num_courses = num_courses + 1
        if grade == 'C+':
            grade_points = grade_points + 2.3
            num_courses = num_courses + 1
        if grade == 'C':
            grade_points = grade_points + 2
            num_courses = num_courses + 1
        if grade == 'C-':
            grade_points = grade_points + 1.7
            num_courses = num_courses + 1
        if grade == 'F':
            grade_points = grade_points + 0
            num_courses = num_courses + 1
      if num_courses == 0:
        num_courses = 1
      gpa = grade_points / num_courses
      gpa = round(gpa, 2)
      return render_template("coursehist.html", data = data, courses = courses, id = id, gpa = gpa, type = type)
  else:
    return redirect('/')
  
  # END OF STUDENT FUNCTIONALITY

# applicant
# home page
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

# after submitting application
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

# END OF APPLICANT

app.run(host='0.0.0.0', port=8080)