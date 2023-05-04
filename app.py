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

  session.clear()

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
            
            if x['user_type'] == "recommender":
               return redirect(url_for('Rhome'))
            
            if x['user_type'] == "alumni":
               return redirect(url_for("alum_home"))

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

@app.route('/Rhome', methods=['GET', 'POST'])
def Rhome():
   if session['user_type'] != 'recommender':
    return redirect(url_for('login'))
   
   cursor = mydb.cursor(dictionary=True)
   
   if request.method == "POST":
      uid = request.form["studentID"]
      number = request.form["number"]
      field1 = number + "letter"
      field2 = number + "status"
      letter = request.form["letter"]

      cursor.execute("UPDATE applicationForm SET " + field1 + " = %s WHERE uid = %s", (letter,uid))
      cursor.execute("UPDATE applicationForm SET " + field2 + " = %s WHERE uid = %s", ("Recieved",uid))
      mydb.commit()
      return redirect(url_for("logout"))
   
   return render_template("Rhome.html")

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

@app.route("/SAhome", methods = ["GET", "POST"])
def SAhome():
  if session['user_type'] != 'sysadmin':
    return redirect(url_for('login'))

  cursor = mydb.cursor(dictionary=True)

  if request.method == 'POST':
      if request.form["Form_Type"] == "Submit": #submit changes to existing user
          uid = request.form["uid"]
          username = request.form["username"]
          first_name = request.form["first_name"]
          last_name = request.form["last_name"]
          ssn = request.form["ssn"]
          address = request.form["address"]
          user_type = request.form["user_type"]

          user_data = (username, first_name, last_name,
                       ssn, address, user_type, uid)
          query = "UPDATE users SET username=(%s), first_name=(%s), last_name=(%s), ssn=(%s), address=(%s), user_type=(%s) WHERE uid=(%s)"
          cursor.execute(query, user_data)
          mydb.commit()

          if user_type == "employee":
              is_professor = is_reviewer = is_review_chair = is_advisor = False
              privileges = request.form.getlist("employee_privileges")
              if "professor" in privileges:
                is_professor = True
              if "reviewer" in privileges:
                is_reviewer = True
              if "chair" in privileges:
                is_review_chair = True
              if "advisor" in privileges:
                is_advisor = True
              
              cursor.execute("UPDATE employee SET is_professor=(%s), is_reviewer=(%s), is_review_chair=(%s), is_advisor=(%s) WHERE uid=(%s)", (is_professor, is_reviewer, is_review_chair, is_advisor, uid))
              mydb.commit()
          elif user_type == "student":
             degree_type = request.form["degree_type"]
             cursor.execute("UPDATE students SET degree_type=(%s) WHERE uid=(%s)", (degree_type, uid))
             mydb.commit()
              
      elif request.form["Form_Type"] == "Add User": #create new user
        uid = random.randrange(10000000, 99999999)
        user_data = (
            uid,
            request.form['username'],
            'password',
            request.form['first_name'],
            request.form['last_name'],
            request.form['ssn'],
            request.form['address'],
            request.form['user_type'])
        cursor.execute('INSERT INTO users (uid, username, password, first_name, last_name, ssn, address, user_type) values (%s, %s, %s, %s, %s, %s, %s, %s);', user_data)
        mydb.commit()

        if request.form['user_type'] == "student":
           cursor.execute('INSERT INTO students VALUES (%s, %s, %s, %s, %s)', (uid, 'MS', False, False, False))
           mydb.commit()
        elif request.form['user_type'] == "employee":
           cursor.execute('INSERT INTO employee VALUES (%s, %s, %s, %s, %s)', (uid, False, False, False, False))
           mydb.commit()
        elif request.form['user_type'] == "applicant":
           cursor.execute('INSERT INTO applicant VALUES (%s, %s, %s,%s,%s)', (uid, 'Application Incomplete', 'Pending',False, False))
           mydb.commit()

      elif request.form["Form_Type"] == "Delete": # remove existing user
         cursor.execute("DELETE FROM users WHERE uid = %s", (request.form["uid"],))
         mydb.commit()

  cursor.execute("SELECT * FROM users ORDER BY CASE WHEN user_type = 'sysadmin' THEN 0 ELSE 1 END, user_type")
  searched_users = cursor.fetchall()
  cursor.execute("SELECT * FROM students")
  students = cursor.fetchall()
  student_types = dict()
  for student in students:
     student_types[student['uid']] = student['degree_type']
     
  cursor.execute("SELECT * FROM employee")
  result = cursor.fetchall()
  employee_privs = dict()
  for employee in result:
     employee_privs[employee['uid']] = {'is_professor' : employee['is_professor'],
                                        'is_reviewer' : employee['is_reviewer'],
                                        'is_review_chair' : employee['is_review_chair'],
                                        'is_advisor' : employee['is_advisor'],}
     
  return render_template('SAhome.html', searched_users=searched_users, student_types=student_types, employee_privs=employee_privs)
 
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

    if request.form["type"] == "searchuid":
      name = request.form["search"]
      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE applicant.uid LIKE %s", ('%' + name + '%',))
      applicants = cursor.fetchall()
      return render_template("GSApps.html", applicants=applicants)
       
    if request.form["type"] == "searchlname":
      name = request.form["search"]
      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE users.last_name LIKE %s", ('%' + name + '%',))
      applicants = cursor.fetchall()
      return render_template("GSApps.html", applicants=applicants)
            
    if request.form["type"] == "updatestat":
            
      cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", (request.form["status"],request.form["id"]))
      mydb.commit()

    if request.form["type"] == "updatedecision":
            
      cursor.execute("UPDATE applicant SET decision = %s WHERE uid = %s", (request.form["decision"],request.form["id"]))
      cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", ("Decision Delivered",request.form["id"]))
      mydb.commit()

    if request.form["type"] == "app":

      cursor.execute("SELECT * FROM applicationForm WHERE uid = %s", (request.form["id"],))
      app = cursor.fetchone()

      id = request.form["id"]

      return render_template("GSseeapps.html", app=app, id=id)

    if request.form["type"] == "review":

      cursor.execute("SELECT * FROM review_form WHERE student_uid = %s", (request.form["id"],))
      forms = cursor.fetchall()

      id = request.form["id"]

      return render_template("GSseereviews.html", forms=forms, id=id)

  cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid")
  applicants = cursor.fetchall()

  return render_template("GSApps.html", applicants=applicants)
  

@app.route('/GSupdateapp', methods=['GET','POST'])
def GSupdateapp():

    if(session['user_type'] != "gradsec"):
        return redirect("/")

    cursor = mydb.cursor(dictionary = True)

    if request.method == 'POST':
        if request.form["type"] == "transcript":
            
            pdf = request.form["transcriptdoc"]

            cursor.execute("UPDATE applicationForm SET transcriptpdf = %s WHERE uid = %s", (pdf,request.form["id"]))
            cursor.execute("UPDATE applicationForm SET transcriptstatus = %s WHERE uid = %s", ("Transcript Recieved",request.form["id"]))
            mydb.commit()

        if request.form["type"] == "r1":

            cursor.execute("UPDATE applicationForm SET r1status = %s WHERE uid = %s", ("Rec Letter 1 Recieved",request.form["id"]))
            mydb.commit()

        if request.form["type"] == "r2":

            cursor.execute("UPDATE applicationForm SET r2status = %s WHERE uid = %s", ("Rec Letter 2 Recieved",request.form["id"]))
            mydb.commit()

        if request.form["type"] == "r3":

            cursor.execute("UPDATE applicationForm SET r3status = %s WHERE uid = %s", ("Rec Letter 3 Recieved",request.form["id"]))
            mydb.commit()

        if request.form["type"] == "r1let":

            name = request.form["r1pdf"]
            cursor.execute("UPDATE applicationForm SET r1letter = %s WHERE uid = %s", (name,request.form["id"]))
            mydb.commit()

        if request.form["type"] == "r2let":

            name = request.form["r2pdf"]
            cursor.execute("UPDATE applicationForm SET r2letter = %s WHERE uid = %s", (name,request.form["id"]))
            mydb.commit()

        if request.form["type"] == "r3let":

            name = request.form["r3pdf"]
            cursor.execute("UPDATE applicationForm SET r3letter = %s WHERE uid = %s", (name,request.form["id"]))
            mydb.commit()

    cursor.execute("SELECT * FROM applicationForm WHERE uid = %s", (request.form["id"],))
    app = cursor.fetchone()

    return render_template("GSseeapps.html", app=app)

@app.route("/GSappsqueries", methods=['GET', 'POST'])
def GSappsqueries():

  if(session['user_type'] != "gradsec"):
    return redirect("/")

  cursor = mydb.cursor(dictionary = True)

  if request.method == "POST":
    if request.form["type"] == "appsdate":
      search = request.form["criteria1"]

      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid INNER JOIN applicationForm ON applicationForm.uid = users.uid WHERE startDate = %s", (search,))
      applicants = cursor.fetchall()

      return render_template("GSqueryapps.html", applicants=applicants, search=search)

    if request.form["type"] == "appsdeg":
      search = request.form["criteria2"]

      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid INNER JOIN applicationForm ON applicationForm.uid = users.uid WHERE degreeSeeking = %s", (search,))
      applicants = cursor.fetchall()

      return render_template("GSqueryapps.html", applicants=applicants, search=search)

    if request.form["type"] == "acceptdate":
      search = request.form["criteria3"]

      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid INNER JOIN applicationForm ON applicationForm.uid = users.uid WHERE startDate = %s AND applicant.decision LIKE %s", (search, '%' + 'Admit' + '%'))
      applicants = cursor.fetchall()

      return render_template("GSqueryaccepts.html", applicants=applicants, search=search)
       
    if request.form["type"] == "acceptdeg":
      search = request.form["criteria4"]

      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid INNER JOIN applicationForm ON applicationForm.uid = users.uid WHERE degreeSeeking = %s AND applicant.decision LIKE %s", (search, '%' + 'Admit' + '%'))
      applicants = cursor.fetchall()

      return render_template("GSqueryaccepts.html", applicants=applicants, search=search)
       
    if request.form["type"] == "statsdate":
      search = request.form["criteria5"]

      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid INNER JOIN applicationForm ON applicationForm.uid = users.uid WHERE startDate = %s", (search,))
      applicants = cursor.fetchall()

      numapps = 0
      numadmits = 0
      numrejects = 0
      avgGRE = 0
      numGRE = 0

      for applicant in applicants:
         numapps += 1
         if applicant['decision'] == "Admit" or applicant['decision'] == "Admit With Aid":
            numadmits +=1
         elif applicant['decision'] == "Reject":
            numrejects +=1
         
         numGRE +=1
         avgGRE += applicant['GREverbal']
         avgGRE += applicant['GREquantitative']

      if numGRE != 0:
        avgGRE = avgGRE/numGRE

      return render_template("GSquerystats.html", applicants=applicants, search=search, numapps=numapps, numrejects=numrejects, numadmits=numadmits, avgGRE=avgGRE)
       
    if request.form["type"] == "statsdeg":
      search = request.form["criteria6"]

      cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid INNER JOIN applicationForm ON applicationForm.uid = users.uid WHERE degreeSeeking = %s", (search,))
      applicants = cursor.fetchall()

      numapps = 0
      numadmits = 0
      numrejects = 0
      avgGRE = 0
      numGRE = 0

      for applicant in applicants:
         numapps += 1
         if applicant['decision'] == "Admit" or applicant['decision'] == "Admit With Aid":
            numadmits +=1
         elif applicant['decision'] == "Reject":
            numrejects +=1
         
         numGRE +=1
         avgGRE += applicant['GREverbal']
         avgGRE += applicant['GREquantitative']

      avgGRE = avgGRE/numGRE

      return render_template("GSquerystats.html", applicants=applicants, search=search, numapps=numapps, numrejects=numrejects, numadmits=numadmits, avgGRE=avgGRE)
       
   
  cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid")
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
        cur.execute("SELECT credit_hours FROM classes WHERE cid = %s", (student_grades[i]['cid'], ))
        course_hours = cur.fetchall()
        if student_grades[i]['cid'] == 100 or 101 or 102:
            req_courses_ctr = req_courses_ctr + 1
        if student_grades[i]['cid'] == 119 or 120 or 121:
            outside_courses_ctr = outside_courses_ctr + 1
        if student_grades[i]['cid'] != 119 or 120 or 121:
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
  
# GS - list all alumni
@app.route("/GSalumni")
def GSalumni():
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)
    alumni_info = list()

    # get all alumni names/uids
    cur.execute("SELECT first_name, last_name, uid FROM users WHERE user_type = %s", ('alumni', ))
    info1 = cur.fetchall()
    for x in range(len(info1)):
       cur.execute("SELECT email FROM alumni WHERE uid = %s", (info1[x]['uid'], ))
       info2 = cur.fetchall()
       info1.append(info2)
       alumni_info.append(info1)

    return render_template("GSalumni_list.html", alumni_info=alumni_info)

  else:
    return redirect('/')
  
# all alumni with master's degree
@app.route("/GSalumni/masters")
def GSalumni_masters():
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)
    alumni_info = list()

    # get all alumni names/uids
    cur.execute("SELECT first_name, last_name, uid FROM users WHERE user_type = %s", ('alumni', ))
    info1 = cur.fetchall()
    for x in range(len(info1)):
       cur.execute("SELECT email FROM alumni WHERE uid = %s AND degree_type = %s", (info1[x]['uid'], 'MS'))
       info2 = cur.fetchall()
       if info2:
        info1.append(info2)
        alumni_info.append(info1)

    return render_template("GSalumni_list_ms.html", alumni_info=alumni_info)

  else:
    return redirect('/')
  
# all alumni with phd
@app.route("/GSalumni/phd")
def GSalumni_phd():
  if session['user_type'] == 'gradsec':
    cur = mydb.cursor(dictionary = True)
    alumni_info = list()

    # get all alumni names/uids
    cur.execute("SELECT first_name, last_name, uid FROM users WHERE user_type = %s", ('alumni', ))
    info1 = cur.fetchall()
    for x in range(len(info1)):
       cur.execute("SELECT email FROM alumni WHERE uid = %s AND degree_type = %s", (info1[x]['uid'], 'PHD'))
       info2 = cur.fetchall()
       # if there are such alum
       if info2:
        info1.append(info2)
        alumni_info.append(info1)

    return render_template("GSalumni_list_phd.html", alumni_info=alumni_info)

  else:
    return redirect('/')
  
# list alumni by semester/year
@app.route("/GSalumni/gradyear", methods=['GET', 'POST'])
def GSalum_gradyear():
   if session['user_type'] == 'gradsec':
      cur = mydb.cursor(dictionary = True)

      if request.method == 'POST':
        # get grad year from search bar
        grad_year = (str)(request.form["search"])

        alumni = list()
        # get all alumni who graduated that year
        cur.execute("SELECT uid, email FROM alumni WHERE grad_year = %s", (grad_year, ))
        alum_uids = cur.fetchall()

        for x in range(len(alum_uids)):
          # get names of alumni
          cur.execute("SELECT first_name, last_name FROM users WHERE uid = %s", (alum_uids[x]['uid'], ))
          alum_name = cur.fetchall()
          if alum_name:
             alum_uids.append(alum_name)
             alumni.append(alum_uids)

        return render_template("GSalum_gradyear.html", alumni=alumni, grad_year=grad_year)
      else:
         return redirect('/')

   else:
      return redirect('/')
   
# master list of all students who are approved for graduation
approved_grad = list()
# all masters students who are approved
approved_ms = list()
# all phd students who are approved
approved_phd = list()
# all students approved for graduation
@app.route("/GSapproved_grad")
def GSapproved_grad():
   if session['user_type'] == 'gradsec':

      # need to get all students that are approved for graduation
      cur = mydb.cursor(dictionary = True)
      # get uid of all students
      cur.execute("SELECT uid FROM students")
      students = cur.fetchall()

      for x in range(len(students)):
        student_info = list()
        degree = list()

        cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (students[x]['uid'], ))
        student_basic_info = cur.fetchall()
        student_info.insert(0, student_basic_info)
        eligible = {'eligible': 'True'}
        student_info.insert(1, eligible)

        # get degree_id
        cur.execute("SELECT degree_type, start_date FROM students WHERE uid = %s", (students[x]['uid'], ))
        degree = cur.fetchall()
        if not degree:
            degree = None
        student_info.insert(2, degree)

        # get courses and grades
        cur.execute("SELECT cid, grade FROM student_classes WHERE student_uid  = %s", (students[x]['uid'], ))
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
            cur.execute("SELECT credit_hours FROM classes WHERE cid = %s", (student_grades[i]['cid'], ))
            course_hours = cur.fetchall()
            if student_grades[i]['cid'] == 100 or 101 or 102:
                req_courses_ctr = req_courses_ctr + 1
            if student_grades[i]['cid'] == 119 or 120 or 121:
                outside_courses_ctr = outside_courses_ctr + 1
            if student_grades[i]['cid'] != 119 or 120 or 121:
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
            cur.execute("INSERT INTO students VALUES (%s) WHERE uid = %s", (True, students[x]['uid']))
            gs_all_suspended()

        # check if they've applied for graduation
        cur.execute("SELECT applied_grad FROM students WHERE uid = %s", (students[x]['uid'], ))
        applied = cur.fetchall()
        if not applied:
          student_info[1]['eligible'] = 'False'
        # requirements for master's students
        if student_info[2][0]['degree_type'] == 'MS':
            # check gpa
            if student_info[4]['gpa'] < 3.0:
                student_info[1]['eligible'] = 'False'
            # check credit hours
            if student_info[5]['total_credit_hours'] < 30:
                student_info[1]['eligible'] = 'False'
            # check for grades below a B
            if bad_grade_ctr > 2:
                student_info[1]['eligible'] = 'False'
            # check for required courses
            if req_courses_ctr < 3:
                student_info[1]['eligible'] = 'False'
            # check for outside courses
            if outside_courses_ctr < 2:
                student_info[1]['eligible'] = 'False'

        # requirements for phd students
        if student_info[2][0]['degree_type'] == 'PHD':
            # check gpa
            if student_info[4]['gpa'] < 3.5:
                student_info[1]['eligible'] = 'False'
            # check credit hours
            if student_info[5]['total_credit_hours'] < 36:
                student_info[1]['eligible'] = 'False'
            # check for grades below a B
            if bad_grade_ctr > 1:
                student_info[1]['eligible'] = 'False'
            # check for 30 credits of CS courses
            if cs_credit_hours < 30:
                student_info[1]['eligible'] = 'False'

            # check if thesis has been approved
            cur.execute("SELECT thesis_approved FROM students WHERE uid = %s", (students[x]['uid'], ))
            thesis_approved = cur.fetchall()
            student_info.append(thesis_approved)
            if not thesis_approved:
              student_info[1]['eligible'] = 'False'

        # if they're approved, add them to the correct lists
        if student_info[1]['eligible'] == 'True':
           approved_grad.append(student_info)
           if student_info[2][0]['degree_type'] == 'MS':
              approved_ms.append(student_info)
           if student_info[2][0]['degree_type'] == 'PHD':
              approved_phd.append(student_info)

      return render_template("GSapproved_grad.html", approved_grad=approved_grad)
   else:
      return redirect('/')
   
@app.route("/GSapproved_ms")
def GSapproved_ms():
   if session['user_type'] == 'gradsec':
      return render_template("GSapproved_ms.html", approved_ms=approved_ms)
   else:
      return redirect('/')
   
@app.route("/GSapproved_phd")
def GSapproved_phd():
   if session['user_type'] == 'gradsec':
      return render_template("GSapproved_phd.html", approved_phd=approved_phd)
   else:
      return redirect('/')
   
@app.route("/GSapproved/admit", methods=['GET', 'POST'])
def GSapproved_admit():
   if session['user_type'] == 'gradsec':
      if request.method == 'POST':
        cur = mydb.cursor(dictionary = True)
        start_date = (str)(request.form["search"])
        result = list()
        # check if the start date is the same as the search
        for x in range(len(approved_grad)):
           if (str)(approved_grad[x][2][0]['start_date']) == start_date:
              result.append(approved_grad[x])
        return render_template("GSapproved_admit.html", result=result, start_date=start_date)
      else:
         redirect('/')
   else:
      return redirect('/')
   
@app.route("/GSadvisors")
def GSadvisors():
   if session['user_type'] == 'gradsec':
      cur = mydb.cursor(dictionary = True)
      # get all advisors
      cur.execute("SELECT uid FROM employee WHERE is_advisor = %s", (True, ))
      advisor_uids = cur.fetchall()

      advisor_info = list()
      for x in range(len(advisor_uids)):
         cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (advisor_uids[x]['uid'], ))
         info = cur.fetchall()
         advisor_info.append(info)
      return render_template("GSadvisors.html", advisor_info=advisor_info)
   else:
      return redirect('/')
   
@app.route("/GSadvisor/advisees/<uid>")
def GSadvisor_advisees(uid):
   if session['user_type'] == 'gradsec':
      cur = mydb.cursor(dictionary = True)
      uid = uid
      cur.execute("SELECT first_name, last_name FROM users WHERE uid = %s", (uid, ))
      advisor_name = cur.fetchall()

      cur.execute("SELECT student_uid FROM advisor_assignments WHERE advisor_uid = %s", (uid, ))
      advisee_uids = cur.fetchall()

      advisees = list()
      for x in range(len(advisee_uids)):
         cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (advisee_uids[x]['student_uid'], ))
         advisee = cur.fetchall()
         advisees.append(advisee)

      return render_template("GSadvisor_advisees.html", advisees=advisees, advisor_name=advisor_name)

   return redirect('/')

# END OF GRADSEC FUNCTIONALITY
  
# ADVISOR FUNCITONALITY
@app.route("/advisor_home")
def advisor_home():
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cur.fetchone()

    if booleans['is_advisor'] == False:
      return redirect('/')

    else:
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
    return redirect('/')
  
# list all phd advisees
@app.route('/faculty/advisees/phd')
def phd_students():
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cur.fetchone()

    if booleans['is_advisor'] == False:
      return redirect('/')

    else:
   
    # get advisor id from login session 
      adv_id = session['uid']

      # get all PhD students
      cursor = mydb.cursor(dictionary=True)

      # get all students that belong to this specific advisor
      cursor.execute("SELECT student_uid FROM advisor_assignments WHERE advisor_uid = %s", (adv_id, ))
      all_advisees = cur.fetchall()

      # get uid of all phd advisees
      phd_advisees = list()
      for x in range(len(all_advisees)):
         print(all_advisees[x])
         cur.execute("SELECT uid FROM students WHERE uid = %s AND degree_type = %s", (all_advisees[x]['uid'], 'PHD'))
         info1 = cur.fetchall()
         # get rest of student info
         if info1:
          cur.execute("SELECT * FROM users WHERE uid = %s", (info1[0]['uid'], ))
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
      return redirect(url_for('Chome'))
    
    if request.form['button'] == "reviewer":
      return redirect(url_for('FRhome'))
  
  cursor = mydb.cursor(dictionary = True)

  cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
  booleans = cursor.fetchone()

  return render_template('Fhome.html', booleans=booleans)

@app.route('/Chome', methods=['GET', 'POST'])
def Chome():

    if(session['user_type'] != "employee"):
        return redirect("/")
    
    cursor = mydb.cursor(dictionary = True)
    
    cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cursor.fetchone()

    if booleans['is_review_chair'] == False:
      return redirect('/')
    
    if request.method == "POST":
      if request.form["type"] == "updatedecision":
        cursor.execute("UPDATE applicant SET decision = %s WHERE uid = %s", (request.form["decision"],request.form["id"]))
        cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", ("Decision Delivered",request.form["id"]))
        mydb.commit()

      if request.form['type'] == "fill":
        return redirect(url_for('fillReviewForm'))
      
      if request.form['type'] == "view":
        id = request.form['id']
        return redirect(url_for('viewApplication',studentID = id))

      if request.form["type"] == "searchuid":
        name = request.form["search"]
        cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE applicant.uid LIKE %s AND applicant.appStatus = %s", ('%' + name + '%',"Application Under Review"))
        applicants = cursor.fetchall()
        averages = {}

        for applicant in applicants:
          avg = 0
          ctr = 0

          cursor.execute("SELECT * FROM review_form WHERE student_uid = %s", (applicant["uid"],))
          reviews = cursor.fetchall()

          for review in reviews:
              ctr += 1
              avg += review["GASrating"]

          if ctr != 0:
              avg = avg/ctr

          averages[applicant["uid"]] = avg


        return render_template("Chome.html", applicants = applicants, averages=averages)
        
      if request.form["type"] == "searchlname":
        name = request.form["search"]
        cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE users.last_name LIKE %s AND applicant.appStatus = %s", ('%' + name + '%',"Application Under Review"))
        applicants = cursor.fetchall()
        averages = {}

        for applicant in applicants:
          avg = 0
          ctr = 0

          cursor.execute("SELECT * FROM review_form WHERE student_uid = %s", (applicant["uid"],))
          reviews = cursor.fetchall()

          for review in reviews:
              ctr += 1
              avg += review["GASrating"]

          if ctr != 0:
              avg = avg/ctr

          averages[applicant["uid"]] = avg


        return render_template("Chome.html", applicants = applicants, averages=averages)

    cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE appStatus = %s", ("Application Under Review",))
    applicants = cursor.fetchall()

    averages = {}

    for applicant in applicants:
       avg = 0
       ctr = 0

       cursor.execute("SELECT * FROM review_form WHERE student_uid = %s", (applicant["uid"],))
       reviews = cursor.fetchall()

       for review in reviews:
          ctr += 1
          avg += review["GASrating"]

       if ctr != 0:
          avg = avg/ctr

       averages[applicant["uid"]] = avg


    return render_template("Chome.html", applicants = applicants, averages=averages)

@app.route('/FRhome', methods=['GET', 'POST'])
def FRhome():

    if(session['user_type'] != "employee"):
        return redirect("/")
    
    cursor = mydb.cursor(dictionary = True)
    
    cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cursor.fetchone()

    if booleans['is_reviewer'] == False:
      return redirect('/')


    if request.method == 'POST':
      if request.form["type"] == "searchuid":
        name = request.form["search"]
        cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE applicant.uid LIKE %s AND applicant.appStatus = %s", ('%' + name + '%',"Application Under Review"))
        applicants = cursor.fetchall()
        return render_template("FRhome.html", applicants=applicants)
       
      if request.form["type"] == "searchlname":
        name = request.form["search"]
        cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE users.last_name LIKE %s AND applicant.appStatus = %s", ('%' + name + '%',"Application Under Review"))
        applicants = cursor.fetchall()
        return render_template("FRhome.html", applicants=applicants)
    
      if request.form['type'] == "fill":
        return redirect(url_for('fillReviewForm'))
      
      if request.form['type'] == "view":
        id = request.form['id']
        return redirect(url_for('viewApplication',studentID = id))

    cursor.execute("SELECT * FROM applicant INNER JOIN users ON applicant.uid = users.uid WHERE appStatus = %s", ("Application Under Review",))
    applicants = cursor.fetchall()

    return render_template("FRhome.html", applicants = applicants)

@app.route('/viewApplication/<studentID>', methods=['GET','POST'])
def viewApplication(studentID):


    if(session['user_type'] == "employee"):

      cursor = mydb.cursor(dictionary = True)
          
      cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
      booleans = cursor.fetchone()

      if booleans['is_reviewer'] == True or booleans['is_review_chair'] == True:

          cursor.execute("SELECT * FROM applicationForm WHERE uid = %s", (studentID,))
          app = cursor.fetchone()
          return render_template("viewApplication.html", app = app)
      
    else:
        return redirect("/")

@app.route('/fillReviewForm', methods=['GET','POST'])
def fillReviewForm():

    if(session['user_type'] == "employee"):
        
        cursor = mydb.cursor(dictionary = True)
        
        cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
        booleans = cursor.fetchone()

        if booleans['is_reviewer'] == True or booleans['is_review_chair'] == True:
    
          return render_template("fillReviewForm.html")
    
    else:
        return redirect("/")

@app.route('/submitReviewForm', methods=['GET','POST'])
def submitReviewForm():

    if(session['user_type'] == "employee"):

        cursor = mydb.cursor(dictionary = True)
        
        cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
        booleans = cursor.fetchone()

        if booleans['is_reviewer'] == True or booleans['is_review_chair'] == True:
           
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
          semesterApplied = request.form["semester"] + " " + request.form["year"]
          decision = "pending"

          cursor.execute("INSERT INTO review_form (student_uid,reviewer_uid,r1rating,r1generic,r1credible,r1from,r2rating,r2generic,r2credible,r2from,r3rating,r3generic,r3credible,r3from,GASrating,deficiencies,rejectReason,thoughts,semesterApplied,decision) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (studentID,reviewer,r1rating,r1generic,r1credible,r1from,r2rating,r2generic,r2credible,r2from,r3rating,r3generic,r3credible,r3from,GASrating,deficiencies,rejectReason,thoughts,semesterApplied,decision,))
          mydb.commit()

          # cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", ("Decision Pending",studentID))
          # mydb.commit()
          cursor.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
          booleans = cursor.fetchone()

          if booleans['is_review_chair'] == True:
            return redirect('/Chome')

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
    cur.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cur.fetchone()

    if booleans['is_advisor'] == False:
      return redirect('/')
    else:
    # get advisor id from login session 
      adv_id = session['uid']

      # get all PhD students
      cursor = mydb.cursor(dictionary=True)

      # get all students that belong to this specific advisor
      cursor.execute("SELECT student_uid FROM advisor_assignments WHERE advisor_uid = %s", (adv_id, ))
      all_advisees = cur.fetchall()

      # get uid of all phd advisees
      m_advisees = list()
      for x in range(len(all_advisees)):
         cur.execute("SELECT uid FROM students WHERE uid = %s AND degree_type = %s", (all_advisees[x]['uid'], 'MS'))
         info1 = cur.fetchall()
         # get rest of student info
         if info1:
          cur.execute("SELECT * FROM users WHERE uid = %s", (info1[0]['uid'], ))
          info2 = cur.fetchall()
          m_advisees.append(info2)

      return render_template('masters_students.html', m_advisees=m_advisees)
    
  else:
     return redirect('/')
  
# review transcript of advisee
@app.route('/faculty/advisees/<transcript_id>')
def faculty_transcript(transcript_id): 
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cur.fetchone()

    if booleans['is_advisor'] == False:
      return redirect('/')
    
    else:
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
              where users.uid=%s '''
        
            cursor= mydb.cursor(dictionary=True)

            cursor.execute(query,(transcript_id,) )
            result =cursor.fetchall()
            cursor.close()

            return render_template('student_transcript.html', transcript=result)

    
# review form 1 answers from advisees
@app.route('/faculty/advisees/form1/<user_id>', methods=['GET', 'POST'])
def faculty_form(user_id): 
  
  # check if employee
  if session['user_type'] == 'employee':
    # check if advisor
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT * FROM employee WHERE uid = %s", (session["uid"],))
    booleans = cur.fetchone()

    if booleans['is_advisor'] == False:
      return redirect('/')
    
    else:
      # get uid
      if request.method == "GET":
        if user_id != None:
            user_id = int(user_id)

            # get first and last name from student
            cur.execute("SELECT first_name, last_name, uid FROM users WHERE uid = %s", (user_id, ))
            name = cur.fetchall()

            # get all class ids from form1_answer table for a student
            cur.execute("SELECT cid FROM form1_answer WHERE student_uid = %s", (user_id, ))
            class_ids = cur.fetchall()

            if not class_ids:
               form1_answer = []

            # get all info from classes listed in form1
            for x in range(len(class_ids)):
               cur.execute("SELECT * FROM classes WHERE cid = %s", (class_ids[x]['cid'], ))
               form1_answer = cur.fetchall()
               if not form1_answer:
                  form1_answer = []

        return render_template('view_form1.html', name=name, form1_answer=form1_answer)
  
  else:
    return redirect('/')

# END OF ADVISOR FUNCTIONALITY

def prereq_check(section_id):
  cursor = mydb.cursor(dictionary=True, buffered=True)

  cursor.execute('SELECT current_sections.cid, class_number, day, timeslot FROM current_sections JOIN classes ON current_sections.cid = classes.cid WHERE current_sections.section_id = %s',
                 (section_id, ))
  course = cursor.fetchone()

  eligable = True
  cursor.execute('SELECT prereq_cid FROM prerequisites WHERE class_cid = %s', (course['cid'], ))
  prereqs = cursor.fetchall()
  cursor.execute('SELECT cid FROM student_classes WHERE student_uid = %s and finalized = 1', (session['uid'], ))
  courses_taken = cursor.fetchall()

  for prereq in prereqs:
    if prereq not in courses_taken:
      eligable = False
          
  if session['user_type'] == 'student_p' and int(course['class_number']) < 6000:
    eligable = False

  cursor.execute('''
  SELECT current_sections.section_id, current_sections.day, current_sections.timeslot, current_sections.cid 
  FROM current_sections 
    JOIN classes ON classes.cid = current_sections.cid 
    JOIN users ON users.uid = current_sections.professor_uid
    JOIN student_classes ON student_classes.section_id = current_sections.section_id
  WHERE current_sections.year = %s 
    AND current_sections.semester = %s 
    AND student_classes.student_uid = %s''', 
                 (str(session['current_year']), str(session['current_semester']), session["uid"],))
  current_classes = cursor.fetchall()

  for c in current_classes:
    if c['day'] == course['day'] and abs(c['timeslot'] - course['timeslot']) != 2:
      eligable == False
    elif c['cid'] == course['cid']:
      eligable == False

  return eligable

def classes_search(department = "%", title = "%", number = "%"):
  cursor = mydb.cursor(dictionary=True)
    
  # can't pass null parameters into sql query so we have to figure out which are searched before querying
  cursor.execute('''
  SELECT * 
  FROM current_sections 
    JOIN classes ON classes.cid = current_sections.cid 
    JOIN users ON users.uid = current_sections.professor_uid
  WHERE current_sections.year = %s 
    AND current_sections.semester = %s 
    AND classes.dept LIKE (%s) 
    AND classes.title LIKE (%s) 
    AND classes.cid LIKE (%s)''',
                 (str(session['current_year']), str(session['current_semester']), department, title, number))
  all_classes = cursor.fetchall()

  cursor.execute('''
  SELECT current_sections.section_id 
  FROM current_sections 
    JOIN classes ON classes.cid = current_sections.cid 
    JOIN users ON users.uid = current_sections.professor_uid
    JOIN student_classes ON student_classes.section_id = current_sections.section_id
  WHERE current_sections.year = %s 
    AND current_sections.semester = %s 
    AND student_classes.student_uid = %s''', 
                 (str(session['current_year']), str(session['current_semester']), session["uid"],))
  current_classes = cursor.fetchall()

  session['lookup_results_classes'] = []
  for course in all_classes:
    if {'section_id': course['section_id']} not in current_classes:
      course['eligable'] = prereq_check(course['section_id'])
      session['lookup_results_classes'].append(course)

# student
@app.route("/Shome", methods = ['GET', 'POST'])
def Shome():

  if session['user_type'] == 'student':
    session['years'] = [2014, 2023, 2024]
    session['semesters'] = [1, 2, 3]
    session['student_portal_error'] = ''
    if 'current_year' not in session:
      session['current_year'] = 2023
    if 'current_semester' not in session:
      session['current_semester'] = 1
    session['semester_names'] = ['blank', 'spring', 'summer', 'fall'] # 'blank' becaues there is no 0 semester

    cur = mydb.cursor(dictionary = True)

    if 'schedule' not in session:
      session['schedule'] = []
      cur.execute('SELECT * FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id WHERE student_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s',
                      (session['uid'], str(session['current_year']), str(session['current_semester'])))
      classes_taking = cur.fetchall()
      for i in [1, 2, 3]:
        partial = []
        for j in ['M', 'T', 'W', 'R', 'F']:
          for k in classes_taking:
            if k['timeslot'] == i and k['day'] == j:
              partial.append([k['title'], k['section_id']])
          else:
            partial.append(['free period', 'none'])
        session['schedule'].append(partial)
    
    session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
    session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']

    if request.method == 'POST' and 'semester' in request.form:
      session['current_semester'] = int(request.form['semester'])
      session['current_year'] = int(request.form['year'])
      
      classes_search()

      # TODO: get all classes from database for that semester/year
      session['schedule'] = []
      cur.execute('SELECT * FROM student_classes INNER JOIN current_sections ON student_classes.student_uid = (%s) AND student_classes.cid = current_sections.cid AND current_sections.year = (%s) AND current_sections.semester = (%s) JOIN classes ON classes.cid = student_classes.cid ',
                      (session['uid'], session['current_year'], session['current_semester']))
      classes_taking = cur.fetchall()
      print(session['uid'])
      print(classes_taking)
      for i in [1, 2, 3]:
        partial = []
        for j in ['M', 'T', 'W', 'R', 'F']:
          for k in classes_taking:
            if k['timeslot'] == i and k['day'] == j:
              partial.append([k['title'], k['section_id']])
          else:
            partial.append(['free period', 'none'])
        session['schedule'].append(partial)
        # print(session['schedule'])

    elif request.method == 'POST' and 'class_lookup' in request.form:
      department = '%'
      title = '%'
      number = '%'

      if request.form['department'] != '':
        department = request.form['department']
      if request.form['title'] != '':
        title = request.form['title']
      if request.form['number'] != '':
        number = request.form['number']
      
      classes_search(department, title, number)
    elif request.method == 'POST':
      cur.execute('''
      SELECT * 
      FROM current_sections 
        JOIN classes ON classes.cid = current_sections.cid 
        JOIN users ON users.uid = current_sections.professor_uid
      WHERE current_sections.year = %s 
        AND current_sections.semester = %s ''',
                    (str(session['current_year']), str(session['current_semester'])))
      all_classes = cur.fetchall()

      cur.execute('''
      SELECT current_sections.section_id 
      FROM current_sections 
        JOIN classes ON classes.cid = current_sections.cid 
        JOIN users ON users.uid = current_sections.professor_uid
        JOIN student_classes ON student_classes.section_id = current_sections.section_id
      WHERE current_sections.year = %s 
        AND current_sections.semester = %s 
        AND student_classes.student_uid = %s''', 
                    (str(session['current_year']), str(session['current_semester']), session["uid"],))
      current_classes = cur.fetchall()

      for course in all_classes:
        if {'section_id': course['section_id']} in current_classes and course['title'] in request.form:
          session['schedule'][course['timeslot'] - 1][['M', 'T', 'W', 'R', 'F'].index(course['day'])] = ['free period', 'none']
          cur.execute('DELETE FROM student_classes WHERE student_classes.student_uid = %s AND student_classes.section_id = %s',
                        (session['uid'], course['section_id']))
          mydb.commit()
        elif course['title'] in request.form and prereq_check(course['section_id']):
          session['schedule'][course['timeslot'] - 1][['M', 'T', 'W', 'R', 'F'].index(course['day'])] = [course['title'], course['section_id']]
          cur.execute('INSERT INTO student_classes VALUE(%s, %s, %s, %s, %s)',
                        (session['uid'], course['cid'], course['section_id'], 'IP', 0))
          mydb.commit()
      
      classes_search()

    

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
              #cur.execute("INSERT into student_classes (student_uid, cid, section_id, grade, finalized) VALUES (%s, %s, %s, %s, %s)", (session['uid'], i, section_id, 'IP', False))
              #mydb.commit()

            cur.execute("INSERT into form1_answer (student_uid, cid) VALUES (%s, %s)", (session['uid'], i))
            mydb.commit()

            cur.execute("SELECT * from student_classes WHERE cid = %s and student_uid = %s", (i, session['uid']))
            data = cur.fetchall()
            
    return redirect('/Shome')

  else:
    return redirect('/')

# allows student to apply for graduation
@app.route('/applygrad', methods=['GET', 'POST'])
def applygrad():
  if session['user_type'] == 'student':
  #connect to the database
    cur = mydb.cursor(dictionary = True)

    if request.method == "POST":
       cur.execute("UPDATE students SET applied_grad = %s WHERE uid = %s", (True, session['uid'], ))
       return render_template("applygrad.html")
    else:
       return redirect('/')
  else:
    return redirect('/')

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

  if session['user_type'] == 'student' or 'alumni':

    print("in coursehist")

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

      class_info = list()
      cur.execute("SELECT cid, grade FROM student_classes WHERE student_uid = %s", (id, ))
      student_grades = cur.fetchall()

      for i in range(len(student_grades)):
        cur.execute("SELECT cid, title, class_number, credit_hours FROM classes WHERE cid = %s", (student_grades[i]['cid'], ))
        info1 = cur.fetchall()
        class_info.append(info1)

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

      for x in range(len(class_info)):
         class_info[x].append(student_grades[x])

      return render_template("coursehist.html", student_grades=student_grades, courses = courses, id = id, gpa = gpa, type = type, class_info=class_info)
  else:
    print("else statement")
    return redirect('/')
  
  # END OF STUDENT FUNCTIONALITY

# applicant
# home page
@app.route("/Ahome", methods=['GET', 'POST'])
def Ahome():

  cursor = mydb.cursor(dictionary=True)

  if(session['user_type'] != "applicant"):
      return redirect(url_for('logout'))
  
  if request.method == 'POST':
    if request.form['button'] == "fill":
      return redirect(url_for('applicationFillout'))
    
    if request.form['button'] == "status":
      return redirect(url_for('seeStatus'))
     
    if request.form['button'] == "accept":
      cursor.execute("SELECT degreeSeeking FROM applicationForm WHERE uid = %s", (session["uid"],))
      degree = cursor.fetchone()
      cursor.execute("SELECT startDate FROM applicationForm WHERE uid = %s", (session["uid"],))
      date = cursor.fetchone()
      cursor.execute("UPDATE users SET user_type = %s WHERE uid = %s", ("student",session["uid"]))
      cursor.execute("UPDATE applicant SET has_paid = %s WHERE uid = %s", (True,session["uid"]))
      cursor.execute("UPDATE applicant SET has_paid = %s WHERE uid = %s", (True,session["uid"]))
      cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", ("Matriculated",session["uid"]))
      cursor.execute("INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s)", (session["uid"],degree['degreeSeeking'], False, False, False,date['startDate']))
      mydb.commit()
      return redirect(url_for('logout'))
    
    if request.form["type"] == "update": #submit changes to existing user
          uid = session["uid"]
          username = request.form["username"]
          password = request.form["password"]
          first_name = request.form["first_name"]
          last_name = request.form["last_name"]
          ssn = request.form["ssn"]
          address = request.form["address"]

          user_data = (username, password, first_name, last_name,
                       ssn, address, uid)
          query = "UPDATE users SET username=(%s), password=(%s), first_name=(%s), last_name=(%s), ssn=(%s), address=(%s) WHERE uid=(%s)"
          cursor.execute(query, user_data)
          mydb.commit()
     
  cursor = mydb.cursor(dictionary=True)

  cursor.execute("SELECT appStatus FROM applicant WHERE uid = %s", (session["uid"],))
  status = cursor.fetchone()

  cursor.execute("SELECT decision FROM applicant WHERE uid = %s", (session["uid"],))
  decision = cursor.fetchone()

  return render_template("Ahome.html", status=status, decision=decision)

@app.route('/email/<recnum>', methods = ['GET', 'POST'])
def email(recnum):
    return render_template("email.html", recnum=recnum)

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
        if(MSgpa < 0):
           return redirect(url_for('applicationFillout'))
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
        if(BAgpa < 0):
           return redirect(url_for('applicationFillout'))
        if(request.form["GREverbal"] == ""):
            GREverbal = 0
        else:
            GREverbal = int(request.form["GREverbal"])
        if(GREverbal < 130 or GREverbal > 170):
           return redirect(url_for('applicationFillout'))
        if(request.form["GREquantitative"] == ""):
            GREquantitative = 0
        else:
            GREquantitative = int(request.form["GREquantitative"])
        if(GREquantitative < 130 or GREquantitative > 170):
           return redirect(url_for('applicationFillout'))
        if(request.form["GREyear"] == ""):
            GREyear = 0
        else:
            GREyear = int(request.form["GREyear"])
        if(request.form["GREadvancedScore"] == ""):
            GREadvancedScore = 0
        else:
            GREadvancedScore = int(request.form["GREadvancedScore"])
        if(GREadvancedScore < 130 or GREadvancedScore > 170):
           return redirect(url_for('applicationFillout'))
        GREadvancedSubject = request.form["GREadvancedSubject"]
        if(request.form["TOEFLscore"] == ""):
            TOEFLscore = 0
        else:
            TOEFLscore = int(request.form["TOEFLscore"])
        if(TOEFLscore < 0 or TOEFLscore > 120):
           return redirect(url_for('applicationFillout'))
        TOEFLdata = request.form["TOEFLdata"]
        priorWork = request.form["priorWork"]
        startDate = request.form["semester"] + " " + request.form["year"]
        pdf = request.form["transcriptdoc"]
        if pdf == None:
          transcriptStatus = "Not Received"
        else:
          transcriptStatus = "Recieved"
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
            "INSERT INTO applicationForm (uid, degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdate,priorWork,startDate,transcriptstatus,transcriptpdf,r1status,r1writer,r1email,r1title,r1affiliation,r1letter,r2status,r2writer,r2email,r2title,r2affiliation,r2letter,r3status,r3writer,r3email,r3title,r3affiliation,r3letter) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s)", (session['uid'], degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdata,priorWork,startDate,transcriptStatus,pdf,r1status,r1writer,r1email,r1title,r1affiliation,r1letter,r2status,r2writer,r2email,r2title,r2affiliation,r2letter,r3status,r3writer,r3email,r3title,r3affiliation,r3letter)
        )
        mydb.commit()

        decision = "Application Awaiting Materials"
        cursor.execute("UPDATE applicant SET appStatus = %s WHERE uid = %s", (decision,session['uid']))
        mydb.commit()

        cursor.execute("SELECT appStatus FROM applicant WHERE uid = %s", (session["uid"],))
        status = cursor.fetchone()

        cursor.execute("SELECT decision FROM applicant WHERE uid = %s", (session["uid"],))
        decision = cursor.fetchone()

        return render_template("Ahome.html", status=status, decision=decision)
    
    return redirect ('/')

# END OF APPLICANT

app.run(host='0.0.0.0', port=8080)
