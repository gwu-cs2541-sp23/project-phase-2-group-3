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

def sessionStatus():
    return session['uid']

def sessionType():
    return session['type']

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

@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))

# system admin
@app.route("/SAhome")
def SAhome():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT address, uid FROM users WHERE username = %s", (session['username'],))
    data = cur.fetchone()
    mydb.commit()

    return render_template("SAhome.html", title = 'Admin Logged In', data = data)
  else:
    return redirect('/')
  
@app.route('/viewform1/<id>')
def viewform1(id):
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT cid FROM form1_answer WHERE student_uid = %s", (id,))
    data = cur.fetchall()
    mydb.commit()

    cur.execute("SELECT * from classes")
    classes = cur.fetchall()
    mydb.commit()

    return render_template("view_form1.html", data = data, classes = classes)

  else:
    return redirect('/')
  
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
  
# update grades
@app.route('/updategrade/<studID>/<courID>', methods=['GET', 'POST'])
def updategrade(studID, courID):
  #connect to the database
  cur = mydb.cursor(dictionary = True)

  if sessionType() == 'sysadmin':

    if request.method == 'POST':
      #update grade
      if((request.form["grade"])):
        cur.execute("UPDATE student_classes SET grade = %s WHERE student_uid = %s and cid = %s", ( str((request.form["grade"])), studID, courID))
        mydb.commit()

    return redirect('/')

  else:
    return redirect('/')
  
# list of courses a stuent is taking
@app.route('/student_courseslist')
def studentcourse():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT cid FROM student_classes WHERE student_uid = %s", (session['uid'], ))
    course_id = cur.fetchall()
    mydb.commit()
    return course_id

  else:
    return redirect('/')
  
# list of all employees
@app.route('/facultylist')
def facultylist():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT * FROM users WHERE user_type = %s", ('employee', ))
    data = cur.fetchall()
    mydb.commit()
    return render_template("faculty_list.html", data = data)

  else:
    return redirect('/')
  
# list of all students
@app.route('/gradlist')
def gradlist():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    # get all masters students
    cur.execute("SELECT uid FROM students WHERE degree_type = %s", ('MS', ))
    masters_uid = cur.fetchall()
    mydb.commit()
    masters = list()
    for x in range(len(masters_uid)):
       cur.execute("SELECT * FROM users WHERE uid = %s", (masters_uid[x], ))
       masters_info = cur.fetchall()
       masters.append(masters_info)

    # get all phd students
    cur.execute("SELECT uid FROM students WHERE degree_type = %s", ('PHD', ))
    phd_uid = cur.fetchall()
    phd = list()
    for x in range(len(masters_uid)):
       cur.execute("SELECT * FROM users WHERE uid = %s", (phd_uid[x], ))
       phd_info = cur.fetchall()
       phd.append(phd_info)
    mydb.commit()

    return render_template("grad_list.html", masters=masters, phd=phd)

  else:
    return redirect('/')
  
# approve student's thesis
@app.route('/approvethesis/<id>')
def approvethesis(id):
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)
    cur.execute("UPDATE students SET thesis_approved = %s WHERE uid = %s", (True, id))
    mydb.commit()
    return redirect('/')
  else:
    return redirect('/')

# list all graduate secretaries
@app.route('/gradseclist')
def gradseclist():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT * FROM users WHERE user_type = %s", ('gradsec', ))
    data = cur.fetchall()
    mydb.commit()
    return render_template("gradsec_list.html", data = data)
  else:
    return redirect('/')
  
# list all alumni
@app.route('/alumnilist')
def alumnilist():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT * FROM users WHERE user_type = %s", ('alumni', ))
    data = cur.fetchall()
    mydb.commit()
    return render_template("alumni_list.html", data = data)
  else:
    return redirect('/')
  
# view students and alumni together
@app.route('/user/<id>/<type>')
def userinfo(id, type):
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    cur.execute("SELECT * FROM users WHERE uid = %s", (id, ))
    data = cur.fetchone()
    mydb.commit()
    studentcourses = None
    alumnicourses = None
    notappr = None
    suspended = None

    
    if type == 'student':
      studentcourses = "student"
      mydb.commit()
      cur.execute("SELECT * FROM students WHERE thesis_approved = %s", (False, ))
      notappr = cur.fetchall()
      cur.execute("SELECT grade FROM student_classes WHERE student_uid = %s", (id,))
      grades = cur.fetchall()

      invalid_grades = ['C', 'D', 'F']
      counter = 0
      for g in grades:
        if g in invalid_grades:
          counter += 1

      #three grades below a B --> suspend student
      if counter >= 3:
        cur.execute("UPDATE students SET is_suspended = %s WHERE uid = %s", (True, id))
        mydb.commit()
        
      cur.execute("SELECT is_suspended FROM students WHERE uid = %s", (id,))
      suspended = cur.fetchone()
      mydb.commit()

    if type == 'alumni': 
      alumnicourses = "alumni"
      mydb.commit()

    return render_template("user_info.html", data = data, alumnicourses = alumnicourses, studentcourses = studentcourses, notappr = notappr, suspended = suspended)
  
  else:
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
  
# after a student has been assigned an advisor
@app.route('/assigned', methods=['GET', 'POST'])
def assigned():
  if sessionType() == 'sysadmin':
    if request.method == "POST":

      cur = mydb.cursor(dictionary = True)

      student = (int)(request.form["student"])
      advisor = (int)(request.form["advisor"])

      cur.execute("DELETE from advisor_assignments WHERE student_uid = %s ", (student, ))
      mydb.commit()
      cur.execute("INSERT into advisor_assignments (student_uid, advisor_uid) VALUES (%s, %s)", (student, advisor))
      mydb.commit()

      return redirect('/')
  else:
    return redirect('/')
  
# assign advisor to student
@app.route('/assignadvsior')
def assignadvisor():
  if sessionType() == 'sysadmin':
    cur = mydb.cursor(dictionary = True)

    # get all advisors
    cur.execute("SELECT uid from employee where is_advisor = %s", (True, ))
    advisor_ids = cur.fetchall()
    advisors = list()
    for x in range(len(advisor_ids)):
       cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (advisor_ids[x], ))
       advisors = cur.fetchall()

    # get masters students
    cur.execute("SELECT uid from students where degree_type = %s", ('MS', ))
    ms_ids = cur.fetchall()
    mstudents = list()
    for x in range(len(ms_ids)):
       cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (ms_ids[x],))
       ms_student = cur.fetchall()
       mstudents.append(ms_student)

    cur.execute("SELECT uid from students where degree_type = %s", ('PHD', ))
    phd_ids = cur.fetchall()
    pstudents = list()
    for x in range(len(ms_ids)):
       cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (phd_ids[x],))
       phd_student = cur.fetchall()
       pstudents.append(phd_student)

    return render_template("assign_advisor_sysadmin.html", advisors = advisors, mstudents = mstudents, pstudents = pstudents)
  
  else:
    return redirect('/')
  
# graduate any student
@app.route('/graduatethestudent/<id>/<type>', methods=['GET', 'POST'])
def graduatethestudent(id, type):
  if sessionType() == 'sysadmin': 

    if request.method == "POST":

      cur = mydb.cursor(dictionary = True)

      # change user type
      cur.execute("UPDATE users SET user_type = %s WHERE uid = %s", ('alumni', id))

      # add to alumni table
      cur.execute("INSERT into alumni (student_id, grad_year) VALUES (%s, %s)", (id, 2023))
      mydb.commit()

      # alumni don't have advisors
      cur.execute("DELETE from advisor_assignments WHERE student_uid = %s ", (id, ))
      mydb.commit()

      # remove from students table
      cur.execute("DELETE from students WHERE uid = %s ", (id, ))
      mydb.commit()

      return redirect('/')
  
  else:
    return redirect('/')
  
# remove any user
@app.route('/remove/<id>/<type>', methods=['GET', 'POST'])
def removeuser(id, type):
  if sessionType() == 'sysadmin':

    if request.method == "POST":
      cur = mydb.cursor(dictionary = True)

      if type == 'gradsec': 
        cur.execute("DELETE from users WHERE uid = %s", (id, ))
        mydb.commit()

      elif type == 'alumni': 
        cur.execute("DELETE from student_classes WHERE student_uid = %s ", (id, ))
        mydb.commit()
        cur.execute("DELETE from alumni WHERE uid = %s", (id, ))
        mydb.commit()
        cur.execute("DELETE from students WHERE uid = %s ", (id, ))
        mydb.commit()
        cur.execute("DELETE from users WHERE uid = %s", (id, ))
        mydb.commit()
    
      elif type == 'student': 
        cur.execute("DELETE from student_classes WHERE student_uid = %s ", (id, ))
        mydb.commit()
        cur.execute("DELETE from advisor_assignments WHERE student_uid = %s", (id, ))
        mydb.commit()
        cur.execute("DELETE from students WHERE uid = %s ", (id, ))
        mydb.commit()
        cur.execute("DELETE from users WHERE uid = %s", (id, ))
        mydb.commit()

      elif type == 'advisor':
        cur.execute("UPDATE advisor_assignments SET advisor_uid = %s WHERE advisor_uid = %s", (None, id))
        cur.execute("DELETE from users WHERE uid = %s", (id, ))
        mydb.commit()

      return redirect('/')

  else:
    return redirect('/')
  
# add a new student
@app.route('/addthestudent', methods=['GET', 'POST'])
def addthestudent():
  if sessionType() == 'sysadmin':
    if request.method == "GET":
      return render_template("add_student.html")
    
    if request.method == "POST":
      cur = mydb.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      address =  (request.form["address"])
      type = (request.form["dates"])

      if(type == "MS"):
        degree_type = 'MS'
      if(type == "PHD"):
        degree_type = 'PHD'
    
      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT uid FROM users WHERE uid = %s", (id,))
        if not cur.fetchone():
          break

      cur.execute("SELECT username FROM users WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")

      mydb.commit()
      cur.execute("SELECT ssn FROM users WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")

      mydb.commit()

      cur.execute("INSERT into users (uid, user_type, first_name, last_name, username, password, address, ssn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id, 'student', fname, lname, unm, passwrd, address, ssn))
      mydb.commit()
      cur.execute("INSERT into students (student_id, degree_type, is_suspended, thesis_approved) VALUES (%s, %s, %s, %s)", (id, degree_type, False, False))
      mydb.commit()
      cur.execute("INSERT into advisor_assignments (student_uid, advisor_uid) VALUES (%s)", (id, None))
      mydb.commit()

      return redirect('/')

  else:
    return redirect('/')
  
# add advisors
@app.route('/add_advisor', methods=['GET', 'POST'])
def add_advisor():
  if sessionType() == 'sysadmin':
    if request.method == "GET":
      return render_template("add_advisor.html")

    if request.method == "POST":
      cur = mydb.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      address =  (request.form["address"])
      type = (request.form["type"])

      # randomly generates uid, checks if it's already taken
      while True:
        id_int = random.randint(10000000, 99999999)
        id = str(id_int)
        cur.execute("SELECT uid FROM users WHERE uid = %s", (id,))
        if not cur.fetchone():
          break
      mydb.commit()
    
      # check if username is taken
      cur.execute("SELECT username FROM users WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")

      mydb.commit()

      # checks if ssn is already used
      mydb.commit()
      cur.execute("SELECT ssn FROM users WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")
      mydb.commit()
      
      # if checks pass, add into users and employee tables
      cur.execute("INSERT into users (uid, user_type, first_name, last_name, username, password, address, ssn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id, type, fname, lname, unm, passwrd, address, ssn))
      cur.execute("INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES (%s, %s, %s, %s, %s)", (id, False, True, False, False))
      mydb.commit()
      return redirect('/')
    
@app.route('/addgradsec' , methods=['GET', 'POST'])
def addgradsec():
  if sessionType() == 'sysadmin':
    if request.method == "GET":
      return render_template("add_gradsec.html")

    if request.method == "POST":
      cur = mydb.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      address =  (request.form["address"])
      type = (int)(request.form["type"])

      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT uid FROM users WHERE uid = %s", (id,))
        if not cur.fetchone():
          break
    
      cur.execute("SELECT username FROM users WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")

      mydb.commit()

      mydb.commit()
      cur.execute("SELECT ssn FROM users WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")
      
      cur.execute("INSERT into users (uid, user_type, first_name, last_name, username, password, address, ssn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id, type, fname, lname, unm, passwrd, address, ssn))
      mydb.commit()
      return redirect('/')

  else:
    return redirect('/')

@app.route('/addalumni' , methods=['GET', 'POST'])
def addalumni():
  if sessionType() == 'sysadmin':
    if request.method == "GET":
      return render_template("add_alumni.html")

    if request.method == "POST":
      cur = mydb.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      address =  (request.form["address"])
      type = (int)(request.form["type"])
      year = (int)(request.form["gradyear"])

      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT uid FROM users WHERE uid = %s", (id,))
        if not cur.fetchone():
          break
    
      cur.execute("SELECT username FROM users WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")

      mydb.commit()

      mydb.commit()
      cur.execute("SELECT ssn FROM users WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("user_exists.html")
      
      cur.execute("INSERT into users (uid, user_type, first_name, last_name, username, password, address, ssn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id, type, fname, lname, unm, passwrd, address, ssn))
      mydb.commit()
      cur.execute("INSERT into alumni (uid, grad_year) VALUES (%s, %s)", (id, year))
      mydb.commit()
      return redirect('/')

  else:
    return redirect('/')

# END OF SYSTEM ADMIN FUNCTIONALITY

student_info = list()

@app.route("/GShome", methods=['GET', 'POST'])
def GShome():
  # get name, id, courses, and grades for all current students
  if sessionType() == 'gradsec':
    cur = mydb.cursor(dictionary = True)
    students = list()

    cur.execute("SELECT first_name, last_name, uid FROM users WHERE user_type = %s", ('student', ))
    students = cur.fetchall()
    
  return render_template('GShome.html', students=students)

@app.route('/student/<uid>', methods=['GET', 'POST'])
def gs_student_data(uid):
  if sessionType() == 'gradsec':

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
    student_info.insert(2, degree[0])

    # get courses and grades
    cur.execute("SELECT cid, grade FROM student_classes WHERE student_uid  = %s", (uid, ))
    student_grades = cur.fetchall()
    if not student_grades:
        student_grades = list()
    student_info.insert(3, student_grades)

    # get gpa requirement for degree
    if degree[0] == 'MS':
      gpa_req = 3
    
    if degree[0] == 'PHD':
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
    cur.execute("SELECT * FROM applied_grad WHERE uid  = %s", (uid , ))
    applied = cur.fetchall()
    if not applied:
       student_info[1]['eligible'] = 'False'
       student_info[1]['reason'].append('Has not applied to graduate')

    # requirements for master's students
    if student_info[2]['degree_type'] == 'MS':
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
    if student_info[2]['degree_type'] == 'PHD':
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
  if sessionType() == 'gradsec':
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
  if sessionType() == 'gradsec':
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
  
@app.route('/assign_advisor/<uid>', methods=['GET', 'POST'])
def gs_assign_advisor(uid):
  if sessionType() == 'gradsec':
    cur = mydb.cursor(dictionary = True)

    if request.method == "POST":
        advisor_id = request.form.get("advisor")
        cur.execute("INSERT INTO advisor_assignments VALUES (%s, %s)", (uid, advisor_id))

    # get student name
    cur.execute("SELECT first_name, last_name, uid, address FROM users WHERE uid = %s", (uid, ))
    student = cur.fetchall()

    # get advisor names
    cur.execute("SELECT first_name, last_name, uid FROM users WHERE user_type = %s", ('advisor', ))
    advisors = cur.fetchall()

    return render_template("assign_advisor_gradsec.html", advisors=advisors, student=student)

  else:
    return redirect('/')
  
# END OF GRADSEC FUNCTIONALITY

# faculty (advisor)
@app.route("/Fhome", methods=['GET', 'POST'])
def Fhome():
  # check if employee
  if sessionType() == 'employee':
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT first_name, last_name, address, uid FROM users WHERE uid = %s", (session['uid'], ))
    data = cur.fetchone()
    mydb.commit()

    # see what type(s) of employee they are
    cur.execute("SELECT * FROM employee WHERE uid = %s", (data['uid'], ))
    employee_types = cur.fetchall()
    mydb.commit()

    return render_template("Fhome.html", title = 'Faculty Home Page', data = data, employee_types = employee_types)
  else:
      return redirect('/')
  
# list all phd advisees
@app.route('/faculty/advisees/phd')
def phd_students():
  # check if employee
  if sessionType() == 'employee':
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
  
# list all masters advisees
@app.route('/faculty/advisees/masters')
def m_students():
  # check if employee
  if sessionType() == 'employee':
    print("in first if statement\n")
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT is_advisor FROM employee WHERE uid = %s", (session['uid'], ))
    is_advisor = cur.fetchall()
    if is_advisor:
      print("in second if statement\n")
   
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
  if sessionType() == 'employee':
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
  if sessionType() == 'employee':
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

  if sessionType() == 'student':
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT uaddress, uid, FROM users WHERE username = %s", (session['username'],))
    data = cur.fetchone()
    mydb.commit()

    #get the students grade
    cur.execute("SELECT grade FROM student_classes WHERE student_uid = %s", (session['uid'],))
    grades = cur.fetchall()
    invalid_grades = ['C', 'D', 'F']
    counter = 0

    for g in grades:
      if g in invalid_grades:
        counter += 1

    # three grades below a B --> change 'is_suspended' to true
    if counter >= 3:
      cur.execute("INSERT into students (is_suspended) VALUES %s", (1))
      mydb.commit()
        
    cur.execute("SELECT is_suspended FROM students WHERE student_uid = %s", (session['uid'],))
    suspended = cur.fetchone()
    mydb.commit()

    return render_template("SHome.html", title = 'Student Logged In', data = data, suspended = suspended)
  
  else:
    return redirect('/')

@app.route('/form1', methods=['GET', 'POST'])
def form():
  cur = mydb.cursor(dictionary = True)
  # check if student
  if sessionType() == 'student':

    if request.method == "GET":
      return render_template("form1_student.html")

    if request.method == 'POST':
      check = 0
      for i in range(100, 122):
        checkboxes = request.form.getlist(str(i))
        for checkbox in checkboxes:
          if(checkbox == "yes"):
            if (check == 0):
              cur.execute("DELETE from student_classes WHERE grade = %s and student_uid = %s", ('IP', session['uid'] ))
              mydb.commit()
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
                  cur.execute("INSERT into student_classes (student_uid, cid, grade) VALUES (%s, %s, %s)", (session['uid'], i, 'IP'))
                  mydb.commit()

            else:
              #print("reaches the else")
              cur.execute("INSERT into student_classes (student_uid, cid, grade) VALUES (%s, %s, %s)", (session['uid'], i, 'IP'))
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
   
  # might need an 'applied_grad' table to keep track of the students who've applied for graduation

   return render_template("applygrad.html")

# alumni
@app.route("/Ahome")
def Ahome():
    
    if sessionType() == 'alumni':
      cur = mydb.cursor(dictionary = True)
      cur.execute("SELECT address, uid FROM users WHERE username = %s", (session['username'],))
      data = cur.fetchone()
      mydb.commit()
      return render_template("Ahome.html", title = 'Alumni Logged In', data = data)
    
    else:
      return redirect('/')
    
# view course history for students, alumni, and system admin
@app.route('/coursehist/<id>', methods=['GET', 'POST'])
def coursehist(id):

  if sessionType() == 'sysadmin' or sessionType() == 'student' or sessionType() == 'alumni':
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
      return render_template("coursehist.html", data = data, courses = courses, id = id, gpa = gpa)
  else:
    return redirect('/')
  
  # END OF STUDENT FUNCTIONALITY

app.run(host='0.0.0.0', port=5003)