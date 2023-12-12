from flask import Flask, redirect, render_template, url_for, request, flash, session
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import razorpay
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'thozhilurappu1'

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'thozhilurappu1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

razorpay_client = razorpay.Client(auth=("<APP_ID>", "<APP_SECRET>"))


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_DEFAULT_SENDER'] = 'cts.students.project@gmail.com'
app.config['MAIL_USERNAME'] = 'cts.students.project@gmail.com'
app.config['MAIL_PASSWORD'] = 'cts@123456'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/admin/payment/<jm_id>/<amount>/charge', methods=['POST'])
def app_charge(jm_id,amount):
    amount = request.form['amount']
    payment_id = request.form['razorpay_payment_id']
    pid = request.form['pid']
    jm_id = request.form['jm_id']
    razorpay_client.payment.capture(payment_id, amount)
    sql = "insert into payment values(%s,%s,current_date)"
    vals = (pid, jm_id)
    setData(sql, vals)
    # return json.dumps(razorpay_client.payment.fetch(payment_id))
    return render_template('admin/paymentComplete.html')


def getData(sql, vals=0):
    con = mysql.connect()
    cur = con.cursor()
    if vals == 0:
        cur.execute(sql)
    else:
        cur.execute(sql, vals)
    res = cur.fetchall()
    cur.close()
    con.close()
    return res


def setData(sql, vals=0):
    con = mysql.connect()
    cur = con.cursor()
    if vals == 0:
        cur.execute(sql)
    else:
        cur.execute(sql, vals)
    con.commit()
    cur.close()
    con.close()
    res = cur.rowcount
    return res


@app.route('/getUserData/', methods=['POST'])
def userData():
    uid = session['uid']
    sql = "select name,'%s' as role,photo from user_details where uid=%s" % (
        session['role'].title(), uid)
    res = getData(sql)
    return json.dumps(res)


@app.route('/mate/getAttendance/', methods=['POST'])
def getAttendance():
    data = request.form
    sql = "select u.name,if(a.status=1,'Present','Absent') as status,a.aid from attendance a join job_employee_request je on je.je_id=a.je_id join user_details u on u.uid=je.uid where je.jm_id=%s and a.date=%s"
    vals = (data['jm_id'], data['date'])
    res = getData(sql, vals)
    return json.dumps(res)


@app.route('/mate/getAttDate/', methods=['POST'])
def getAttDate():
    sql = "select if(current_date<start_date,0,1) as st from job_mate_request where jm_id=%s" % request.form[
        'jm_id']
    res = getData(sql)
    if res[0][0] == 0:
        return '0'
    else:
        sql = "select if(current_date>end_date,0,1) as st from job_mate_request where jm_id=%s" % request.form[
            'jm_id']
        res = getData(sql)
        if res[0][0] == 0:
            return '3'
        else:
            sql = "select ifnull(max(a.aid),0) as st from job_mate_request jm join job_employee_request je on je.jm_id=jm.jm_id join attendance a on a.je_id=je.je_id where a.date=current_date and jm.jm_id=%s" % request.form[
                'jm_id']
            res = getData(sql)
            if res[0][0] == 0:
                return '1'
            else:
                return '2'


@app.route('/mate/getAttEmployee/', methods=['POST'])
def getAttEmployee():
    sql = "select je.je_id,u.name from job_mate_request jm join job_employee_request je on je.jm_id=jm.jm_id join user_details u on u.uid=je.uid where jm.jm_id=%s and je.status=1" % request.form[
        'jm_id']
    res = getData(sql)
    return json.dumps(res)


@app.route('/mate/attendance/reports/<aid>/')
def mateEmployeeReports(aid):
    sql = "select * from employee_attendance_report where aid=%s and status=0" % aid
    res = getData(sql)
    return render_template('mate/employee_report.html', data=res)


@app.route('/employee/attendance/', methods=['POST'])
def getEmployeeAttendance():
    je_id = request.form['je_id']
    sql = "select left(date,10) date,if(status=0,'Absend','Present') status,aid from attendance where je_id=%s" % je_id
    res = getData(sql)
    return json.dumps(res)


@app.route('/employee/report/', methods=['POST'])
def employeeReport():
    data = request.form
    sql = "select ifnull(max(ar_id),0)+1 from employee_attendance_report"
    ar_id = getData(sql)[0][0]
    sql = "insert into employee_attendance_report values(%s,%s,%s,0)"
    vals = (ar_id, data['aid'], data['desc'])
    res = setData(sql, vals)
    return str(res)


@app.route('/mate/report/<action>/<ar_id>/<aid>/')
def employeeReportAction(action, ar_id, aid):
    if action == 'reject':
        sql = "update employee_attendance_report set status=2 where ar_id=%s" % ar_id
        setData(sql)
    elif action == 'accept':
        sql = "update employee_attendance_report set status=1 where ar_id=%s" % ar_id
        setData(sql)
        sql = "update attendance set status=1 where aid=%s" % aid
        setData(sql)
    return redirect('/mate/attendance/reports/%s/' % aid)


@app.route('/admin/employee/attendance/', methods=['POST'])
def adminJobAttendance():
    jm_id = request.form['jm_id']
    sql = "select u.name,je.je_id,count(a.status),count(a.status)*300 from attendance a join job_employee_request je on je.je_id=a.je_id join job_mate_request jm on jm.jm_id=je.jm_id join user_details u on u.uid=je.uid where je.jm_id=%s and a.status=1 group by a.je_id order by je_id asc" % jm_id
    res = getData(sql)
    return json.dumps(res)


@app.route('/admin/totalAttendance/', methods=['POST'])
def totalAttendance():
    sql = 'select count(*) from attendance a join job_employee_request je on je.je_id=a.je_id join job_mate_request jm on jm.jm_id=je.jm_id where je.jm_id=%s group by a.je_id limit 1' % request.form[
        'jm_id']
    res = getData(sql)
    return str(res[0][0])


@app.route('/admin/paymentStatus/', methods=['POST'])
def getPaymentStatus():
    jm_id = request.form['jm_id']
    sql = "select count(*) from payment where jm_id=%s" % jm_id
    res = getData(sql)[0][0]
    if res == 0:
        return '1'
    else:
        return '0'


@app.route('/admin/payment/<jm_id>/<amount>/')
def setPayment(jm_id, amount):
    sql = "select ifnull(max(pid),0)+1 from payment"
    pid = getData(sql)[0][0]
    return render_template('admin/payNow.html', amount=amount, pid=pid, jm_id=jm_id)
    # return redirect('/admin/job/requests/payment/%s/' % jm_id)


@app.route('/password/change/', methods=['POST'])
def changePassword():
    data = request.form
    sql = "update login set password=%s where password=%s and log_id=%s"
    vals = (data['npword'], data['pword'], session['uid'])
    res = setData(sql, vals)
    return str(res)


@app.route('/employee/changePassword/')
def employeeChangePassword():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    return render_template('employee/change_password.html')


@app.route('/mate/changePassword/')
def mateChangePassword():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    return render_template('mate/change_password.html')


@app.route('/landowner/changePassword/')
def landownerChangePassword():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    return render_template('landowner/change_password.html')


@app.route('/')
def home():
    if 'uid' in session and 'role' in session:
        return redirect('/'+session['role']+'/home')
    sql = "select * from notifications where type=0"
    res = getData(sql)
    return render_template('public/home.html', notifications=res)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        sql = "select log_id,role from login where username=%s and password=%s"
        vals = (data['uname'], data['pword'])
        res = getData(sql, vals)
        if len(res):
            session['uid'] = res[0][0]
            session['role'] = res[0][1]
            return redirect('/'+res[0][1]+'/home')
        else:
            flash('Invalid login details')
    return render_template('public/login.html')

# @app.route('/landowner_register',methods=['POST','GET'])
# def landOwnerRegister():
#     data = ''
#     if request.method == 'POST':
#         data = request.form
#         if data['pword'] == data['cpword']:
#             sql = "select count(*) from login where username='%s'" % data['email']
#             res = getData(sql)
#             if res[0][0] == 0:
#                 sql = "select count(*) from user_details where phone='%s'" % data['phone']
#                 res = getData(sql)
#                 if res[0][0] == 0:
#                     file = request.files['photo']
#                     fn = os.path.basename(file.filename).split('.')
#                     fn = fn[len(fn)-1]
#                     sql = "select ifnull(max(log_id),0)+1 from login"
#                     res = getData(sql)
#                     log_id = res[0][0]
#                     sql = "insert into login values(%s,%s,%s,'landowner')"
#                     vals = (log_id,data['email'],data['pword'])
#                     setData(sql,vals)
#                     fn = "%s.%s" % (log_id,fn)
#                     sql = "insert into landowner values(%s,%s,%s,%s,%s,%s,%s,%s,%s,0)"
#                     vals = (log_id,data['name'],data['address'],data['ward'],data['phone'],data['gender'],data['dob'],fn,fn1)
#                     setData(sql,vals)
#                     file.save('static/uploads/profile_pic/'+secure_filename(fn))
#                     file1.save('static/uploads/land/'+secure_filename(fn1))
#                     return redirect(url_for('login'))
#                 else:
#                     flash('Phone Number Already Exists')
#             else:
#                 flash('Email Already Exists')
#         else:
#             flash('Passwords Not Matching')
#     return render_template('public/landowner_register.html',data=data)


@app.route('/register/<user>/', methods=['POST', 'GET'])
def register(user):
    data = ''
    if request.method == 'POST':
        data = request.form
        if data['pword'] == data['cpword']:
            sql = "select count(*) from login where username='%s'" % data['email']
            res = getData(sql)
            if res[0][0] == 0:
                sql = "select count(*) from user_details where phone='%s'" % data['phone']
                res = getData(sql)
                if res[0][0] == 0:
                    file = request.files['photo']
                    fn = os.path.basename(file.filename).split('.')
                    fn = fn[len(fn)-1]
                    file1 = request.files['proof']
                    fn1 = os.path.basename(file1.filename).split('.')
                    fn1 = fn1[len(fn1)-1]
                    sql = "select ifnull(max(log_id),0)+1 from login"
                    res = getData(sql)
                    log_id = res[0][0]
                    sql = "insert into login values(%s,%s,%s,%s)"
                    vals = (log_id, data['email'], data['pword'], user)
                    setData(sql, vals)
                    fn = "%s.%s" % (log_id, fn)
                    fn1 = "%s.%s" % (log_id, fn1)
                    sql = "insert into user_details values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    vals = (log_id, data['name'], data['address'], data['place'], data['city'], data['pin'],
                            data['phone'], data['gender'], data['dob'], fn, fn1)
                    setData(sql, vals)
                    file.save('static/uploads/profile_pic/' +
                              secure_filename(fn))
                    file1.save('static/uploads/id_proof/'+secure_filename(fn1))
                    return redirect(url_for('login'))
                else:
                    flash('Phone Number Already Exists')
            else:
                flash('Email Already Exists')
        else:
            flash('Passwords Not Matching')
    return render_template('public/register.html', data=data, user=user.title())


@app.route('/forgotPassword/', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        em = request.form['email']
        sql = "select password from login where username='%s'" % em
        res = getData(sql)
        if len(res):
            _topic = 'Your password to login is %s' % res[0][0]
            _sub = 'Account Recovery'
            _from = ''
            _to = [em]
            msg = Message(_sub, sender=_from, recipients=_to)
            msg.body = _topic
            mail.send(msg)
            flash("Your recovery password has send to your email")
        else:
            flash("Wrong Email Address")
    return render_template('public/forgotPassword.html')


@app.route('/admin/home', methods=['GET', 'POST'])
def adminHome():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        if data['n_type'] == 'gen':
            sql = "select ifnull(max(nid),0)+1 from notifications"
            res = getData(sql)
            nid = res[0][0]
            sql = "insert into notifications values(%s,%s,%s,current_date,%s)"
            vals = (nid, data['title'], data['description'], data['type'])
            setData(sql, vals)
        elif data['n_type'] == 'met':
            sql = "select ifnull(max(mn_id),0)+1 from meeting_notifications"
            res = getData(sql)
            mnid = res[0][0]
            sql = "insert into meeting_notifications values(%s,%s,%s,%s,current_date)"
            vals = (mnid, data['mate'], data['title'], data['description'])
            setData(sql, vals)
    sql = "select * from notifications"
    res = getData(sql)
    sql = "select jid,title from jobs"
    jobs = getData(sql)
    sql = "select * from meeting_notifications"
    res1 = getData(sql)
    return render_template('admin/home.html', notifications=res, jobs=jobs,notifications1=res1)


@app.route('/admin/getMates/get/', methods=['POST'])
def getMatesGet():
    jid = request.form['jid']
    sql = "select u.uid,u.name from job_mate_request jm join land_details l on l.lid=jm.land join user_details u on u.uid=jm.uid where l.jid=%s" % jid
    res = getData(sql)
    return json.dumps(res)


@app.route('/admin/landowner/<menu>/')
def manageLandowner(menu):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    status = ''
    if menu == 'requests':
        status = 0
    elif menu == 'approved':
        status = 1
    elif menu == 'rejected':
        status = 2
    sql = "select lid,address,ward,status from land_details where status=%s" % status
    res = getData(sql)
    return render_template('admin/manage_landowner.html', users=res)


@app.route('/admin/landowner/details/<lid>/')
def landownerDetails(lid):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select * from land_details l join login lg on lg.log_id=l.uid join user_details u on u.uid=l.uid where l.lid=%s" % lid
    res = getData(sql)
    print(res[0])
    return render_template('admin/landowner_details.html', data=res[0])


@app.route('/admin/managelandowner/<lid>/<status>/')
def landownerStatus(lid, status):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "update land_details set status=%s where lid=%s"
    vals = (status, lid)
    setData(sql, vals)
    return redirect(url_for('manageLandowner', menu='requests'))


@app.route('/admin/job/new/', methods=['GET', 'POST'])
def addJob():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "select ifnull(max(jid),0)+1 from jobs"
        res = getData(sql)
        jid = res[0][0]
        sql = "insert into jobs values(%s,%s,%s,%s,%s,%s,%s,1)"
        vals = (jid, data['title'], data['description'],
                data['location'], data['ward'], data['e_type'], data['e_no'])
        setData(sql, vals)
        return redirect('/admin/job/active/')
    return render_template('admin/add_job.html')


@app.route('/admin/job/<type>/')
def getJob(type):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    status = ''
    if type == 'active':
        status = 1
    elif type == 'previous':
        status = 0
    sql = "select * from jobs where status=%s" % status
    res = getData(sql)
    return render_template('admin/job_list.html', jobs=res)


@app.route('/admin/job/<status>/<jid>/')
def jobStatus(status, jid):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "update jobs set status=%s where jid=%s"
    vals = (status, jid)
    setData(sql, vals)
    t = ''
    if status == '0':
        t = 'active'
    elif status == '1':
        t = 'previous'
    return redirect(url_for('getJob', type=t))


@app.route('/admin/job/requests/<type>/')
def jobRequests(type):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    status = ''
    if type == 'approved':
        status = 1
    elif type == 'pending':
        status = 0
    elif type == 'rejected':
        status = 2
    elif type == 'completed':
        status = 3
    sql = "select jid,title from jobs"
    jobs = getData(sql)
    jid = 0
    if len(jobs):
        jid = jobs[0][0]
    sql = "select jm_id,jm.uid,request_date,response_date,jm.status,j.title,u.name from job_mate_request jm join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid join user_details u on u.uid=jm.uid where jm.status=%s and j.jid=%s" % (
        status, jid)
    res = getData(sql)
    return render_template('admin/job_requests.html', requests=res, jobs=jobs)


@app.route('/admin/jobRequests/get/', methods=['POST'])
def getJobRequestsGet():
    jid = request.form['jid']
    status = request.form['st']
    sql = "select jm_id,jm.uid,left(request_date,10),left(response_date,10),jm.status,j.title,u.name from job_mate_request jm join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid join user_details u on u.uid=l.uid where jm.status=%s and j.jid=%s" % (status, jid)
    res = getData(sql)
    return json.dumps(res)


@app.route('/admin/job/requests/payment/<jm_id>/')
def adminPayment(jm_id):
    return render_template('admin/job_payment.html')


@app.route('/admin/job/requests/manage/<status>/<jm_id>/')
def adminManageRequest(status, jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "update job_mate_request set status=%s,response_date=current_date where jm_id=%s"
    vals = (status, jm_id)
    setData(sql, vals)
    if status == '1':
        flash('Job Request Approved.')
    elif status == '2':
        flash('Job Request Rejected')
    return redirect(url_for('jobRequests', type='pending'))


@app.route('/admin/job/requests/details/<jm_id>/')
def admniJobRequestDetails(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select jm.jm_id,jm.request_date,jm.response_date,jm.start_date,jm.payment,j.title,j.description,j.location,j.ward,j.employee_type,j.employee_no,u.name,u.address,u.phone,u.gender,u.dob,u.photo,ud.name,l.address,l.ward,ud.phone,ud.gender,ud.dob,ud.photo,if(current_date<jm.start_date,0,1) as st from job_mate_request jm join user_details u on u.uid=jm.uid join land_details l on l.lid=jm.land join jobs j on j.jid = l.jid join user_details ud on ud.uid=l.uid where jm.jm_id=%s" % jm_id
    res = getData(sql)
    sql = "select je.uid,name,address,phone from job_employee_request je join user_details u on u.uid=je.uid where je.jm_id=%s and je.status=1" % jm_id
    emp = getData(sql)
    return render_template('admin/job_request_details.html', data=res[0], employees=emp)


@app.route('/admin/jobs/progress/<jm_id>/')
def adminJobprogress(jm_id):
    sql = "select * from job_updates where jm_id=%s" % jm_id
    res = getData(sql)
    return render_template('admin/job_progress.html', progress=res)


@app.route('/admin/jobs/edit/<jid>/', methods=['GET', 'POST'])
def adminEditJob(jid):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "update jobs set title=%s,description=%s,location=%s,ward=%s,employee_type=%s,employee_no=%s where jid=%s"
        vals = (data['title'], data['desc'], data['location'],
                data['ward'], data['e_type'], data['e_no'], jid)
        setData(sql, vals)
        return redirect('/admin/job/active/')
    sql = "select * from jobs where jid=%s" % jid
    res = getData(sql)
    return render_template('admin/edit_job.html', data=res[0])


@app.route('/admin/changePassword/', methods=['GET', 'POST'])
def adminChangePassword():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    return render_template('admin/change_password.html')


@app.route('/logout')
def logout():
    del session['uid']
    del session['role']
    return redirect('/')


@app.route('/mate/home')
def mateHome():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select * from notifications"
    res = getData(sql)
    sql = "select * from meeting_notifications where uid=%s" % session['uid']
    res1 = getData(sql)
    return render_template('mate/home.html', notifications=res,notifications1=res1)


@app.route('/mate/job/browse/')
def findJobs():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select * from jobs where status=1"
    res = getData(sql)
    return render_template('mate/job_list.html', jobs=res)


@app.route('/mate/getJobDetails/get/', methods=['POST'])
def getJobDetailsGet():
    jid = request.form['jid']
    sql = "select employee_type,employee_no from jobs where jid=%s" % jid
    res = getData(sql)[0]
    return json.dumps(res)


@app.route('/mate/job/landowners/<jid>/', methods=['POST', 'GET'])
def findLand(jid):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "select count(*) from job_mate_request where land=%s and status=1" % data['land']
        res = getData(sql)
        if res[0][0] == 0:
            sql = "select count(*) from job_mate_request where uid=%s and (status=1 or status=0)" % session['uid']
            res = getData(sql)
            if res[0][0] == 0:
                sql = "select ifnull(max(jm_id),0)+1 from job_mate_request"
                res = getData(sql)
                jm_id = res[0][0]
                sql = "insert into job_mate_request values(%s,%s,%s,current_date,'',%s,%s,%s,0)"
                vals = (jm_id, session['uid'], data['land'],
                        data['date'], data['edate'], data['payment'])
                setData(sql, vals)
            else:
                flash("You've Already Applied For a Contract")
        else:
            flash("Contract Already Assigned")
    sql = "select lid,u.name,l.address,u.phone from land_details l join user_details u on u.uid=l.uid where l.status=1 and l.jid=%s" % jid
    res = getData(sql)
    return render_template('mate/landowner_list.html', users=res, jid=jid)


@app.route('/mate/job/requests/<type>/')
def mateJobRequests(type):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    status = ''
    if type == 'pending':
        status = 0
    elif type == 'approved':
        status = 1
    elif type == 'rejected':
        status = 2
    elif type == 'completed':
        status = 3
    sql = "select jm_id,request_date,response_date,start_date,payment,j.title from job_mate_request jm join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid where jm.status=%s and jm.uid=%s" % (
        status, session['uid'])
    res = getData(sql)
    return render_template('mate/job_requests.html', jobs=res, t=type)


@app.route('/mate/job/cancel/<jm_id>/')
def mateCancelJob(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "delete from job_mate_request where jm_id=%s" % jm_id
    setData(sql)
    return redirect(url_for('mateJobRequests', type='pending'))


@app.route('/mate/employee/requests/')
def mateEmployeeRequests():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select je_id,je.request_date,j.title,u.name,u.phone from job_employee_request je join job_mate_request jm on jm.jm_id=je.jm_id join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid join user_details u on u.uid=je.uid where je.status=0"
    res = getData(sql)
    return render_template('mate/employee_requests.html', requests=res)


@app.route('/mate/employee/list/')
def mateEmployeeList():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select je_id,je.request_date,j.title,u.name,u.phone from job_employee_request je join job_mate_request jm on jm.jm_id=je.jm_id join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid join user_details u on u.uid=je.uid where je.status=1"
    res = getData(sql)
    return render_template('mate/employee_list.html', employees=res)


@app.route('/mate/employee/details/<je_id>/')
def mateEmployeeDetails(je_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select request_date,u.name,u.address,u.phone,u.gender,u.dob,u.photo,u.id_proof,l.username,je.status,je.je_id from job_employee_request je join user_details u on u.uid=je.uid join login l on l.log_id=u.uid where je.je_id=%s" % je_id
    res = getData(sql)
    return render_template('mate/employee_details.html', data=res[0])


@app.route('/mate/employee/request/manage/<je_id>/<status>/')
def manageEmployeeRequest(je_id, status):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "update job_employee_request set status=%s,response_date=current_date where je_id=%s"
    vals = (status, je_id)
    setData(sql, vals)
    return redirect(url_for('mateEmployeeRequests'))


@app.route('/mate/job/details/<jm_id>/')
def mateJobDetails(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select jm.jm_id,jm.request_date,jm.response_date,jm.start_date,jm.payment,jm.status,j.title,j.description,j.location,j.ward,j.employee_type,j.employee_no,ud.name,u.address,ud.phone,ud.gender,ud.dob,ud.photo,u.ward from job_mate_request jm join land_details u on u.lid=jm.land join jobs j on j.jid=u.jid join user_details ud on u.uid=ud.uid where jm.jm_id=%s" % jm_id
    res = getData(sql)
    sql = "select je.uid,name,address,phone from job_employee_request je join user_details u on u.uid=je.uid where je.jm_id=%s and je.status=1" % jm_id
    emp = getData(sql)
    return render_template('mate/job_details.html', data=res[0], employees=emp)


@app.route('/mate/job/manage/complete/<jm_id>/')
def mateJobComplete(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "update job_mate_request set status=3 where jm_id=%s" % jm_id
    setData(sql)
    sql = "update job_employee_request set status=3 where jm_id=%s" % jm_id
    setData(sql)
    return redirect(url_for('mateJobDetails', jm_id=jm_id))


@app.route('/mate/job/progress/<jm_id>/', methods=['POST', 'GET'])
def mateJobProgress(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "select count(*) from job_updates where jm_id='%s' and date=current_date" % jm_id
        res = getData(sql)
        if res[0][0] == 0:
            file = request.files['file']
            fn = os.path.basename(file.filename).split('.')
            fn = fn[len(fn)-1]
            sql = "select ifnull(max(ju_id),0)+1 from job_updates"
            res = getData(sql)
            ju_id = res[0][0]
            fn = "%s.%s" % (ju_id, fn)
            sql = "insert into job_updates values(%s,%s,%s,current_date,%s)"
            vals = (ju_id, jm_id, data['progress'], fn)
            setData(sql, vals)
            file.save('static/uploads/updates/'+secure_filename(fn))
            flash('Progress Uploaded Successfully')
        else:
            flash("You Have Already Uploaded Today's Progress")
    sql = "select * from job_updates where jm_id=%s" % jm_id
    res = getData(sql)
    sql = "select if(current_date<start_date,0,1) as st from job_mate_request where jm_id=%s" % jm_id
    r = getData(sql)
    return render_template('mate/job_progress.html', progress=res, st=r[0][0])


@app.route('/mate/job/attendance/<jm_id>/')
def mateJobAttendance(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    return render_template('mate/job_attendance.html', jm_id=jm_id)


@app.route('/mate/employee/attendance/', methods=["POST"])
def addAttendance():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    data = request.form
    sql = "select je.je_id from job_mate_request jm join job_employee_request je on je.jm_id=jm.jm_id where jm.jm_id=%s and je.status=1" % request.form[
        'jm_id']
    res = getData(sql)
    jm_id = data['jm_id']
    sql = "select ifnull(max(aid),0)+1 from attendance"
    aid = getData(sql)[0][0]
    for r in res:
        sql = "insert into attendance values(%s,%s,current_date,%s)"
        vals = (aid, r[0], data['emp%d' % r[0]])
        setData(sql, vals)
        aid += 1
    return redirect(url_for('mateJobAttendance', jm_id=data['jm_id']))


@app.route('/mate/profile/', methods=['POST', 'GET'])
def mateProfile():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "update user_details set name=%s,address=%s,phone=%s where uid=%s"
        vals = (data['name'], data['address'], data['phone'], session['uid'])
        setData(sql, vals)
        sql = "update login set username=%s where log_id=%s"
        vals = (data['email'], session['uid'])
        setData(sql, vals)
    sql = "select * from user_details u join login l on l.log_id=u.uid where u.uid=%s" % session['uid']
    res = getData(sql)
    return render_template('mate/profile.html', data=res[0])


@app.route('/landowner/profile/', methods=['POST', 'GET'])
def landownerProfile():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "update user_details set name=%s,address=%s,phone=%s where uid=%s"
        vals = (data['name'], data['address'], data['phone'], session['uid'])
        setData(sql, vals)
        sql = "update login set username=%s where log_id=%s"
        vals = (data['email'], session['uid'])
        setData(sql, vals)
    sql = "select * from user_details u join login l on l.log_id=u.uid where u.uid=%s" % session['uid']
    res = getData(sql)
    return render_template('landowner/profile.html', data=res[0])


@app.route('/employee/profile/', methods=['POST', 'GET'])
def employeeProfile():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "update user_details set name=%s,address=%s,phone=%s where uid=%s"
        vals = (data['name'], data['address'], data['phone'], session['uid'])
        setData(sql, vals)
        sql = "update login set username=%s where log_id=%s"
        vals = (data['email'], session['uid'])
        setData(sql, vals)
    sql = "select * from user_details u join login l on l.log_id=u.uid where u.uid=%s" % session['uid']
    res = getData(sql)
    return render_template('employee/profile.html', data=res[0])


@app.route('/profilepic/change/', methods=['POST'])
def changeProfilePic():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    file = request.files['file']
    fn = os.path.basename(file.filename).split('.')
    fn = fn[len(fn)-1]
    fn = "%s.%s" % (session['uid'], fn)
    sql = "update user_details set photo=%s where uid=%s"
    vals = (fn, session['uid'])
    setData(sql, vals)
    file.save('static/uploads/profile_pic/'+secure_filename(fn))
    return redirect('/'+session['role']+'/profile/')


@app.route('/employee/home')
def employeeHome():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select * from notifications where type=0"
    res = getData(sql)
    return render_template('employee/home.html', notifications=res)


@app.route('/employee/job/browse/')
def findEmployeeJobs():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select jm.jm_id,j.title,j.description,j.employee_no,j.location,j.ward from job_mate_request jm join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid where jm.status=1"
    res = getData(sql)
    return render_template('employee/job_list.html', jobs=res)


@app.route('/employee/job/details/<jm_id>/')
def employeeJobDetails(jm_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select jm.jm_id,jm.start_date,j.title,j.description,j.location,j.ward,j.employee_type,j.employee_no,u.name,u.address,u.phone,u.photo,ud.name,l.address,l.ward from job_mate_request jm join jobs j on j.jid=jm.jm_id join user_details u on u.uid=jm.uid join land_details l on l.lid=jm.land join user_details ud on ud.uid=l.uid where jm.jm_id=%s" % jm_id
    res = getData(sql)
    return render_template('employee/job_details.html', data=res[0])


@app.route('/mate/job/apply/<jm_id>/<e_no>/')
def employeeApplyJob(jm_id, e_no):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select count(*) from job_employee_request where uid=%s and (status=1 or status=0)" % session['uid']
    res = getData(sql)
    if res[0][0] == 0:
        sql = "select count(*) from job_employee_request where jm_id=%s and status=1" % jm_id
        res = getData(sql)
        if res[0][0] < int(e_no):
            sql = "select ifnull(max(je_id),0)+1 from job_employee_request"
            res = getData(sql)
            je_id = res[0][0]
            sql = "insert into job_employee_request values(%s,%s,%s,current_date,'',0)"
            vals = (je_id, jm_id, session['uid'])
            setData(sql, vals)
            flash("Job Request Applied Successfully")
        else:
            flash("Employee Limit Reached Maximum.")
    else:
        flash("You have Already Applied For a Job.")
    return redirect(url_for('employeeJobDetails', jm_id=jm_id))


@app.route('/employee/job/requests/<type>/')
def employeeJobRequests(type):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    status = ''
    if type == 'pending':
        status = 0
    elif type == 'approved':
        status = 1
    elif type == 'rejected':
        status = 2
    elif type == 'completed':
        status = 3
    sql = "select je.je_id,je.request_date,je.response_date,jm.start_date,j.title,u.name from job_employee_request je join job_mate_request jm on jm.jm_id=je.jm_id join land_details l on l.lid=jm.land join jobs j on j.jid=l.jid join user_details u on u.uid=jm.uid where je.status=%s and je.uid=%s"
    vals = (status, session['uid'])
    res = getData(sql, vals)
    return render_template('employee/job_requests.html', jobs=res, t=type)


@app.route('/employee/job/cancel/<je_id>/')
def employeeCancelJob(je_id):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "delete from job_employee_request where je_id=%s" % je_id
    setData(sql)
    return redirect(url_for('employeeJobRequests', type='pending'))


@app.route('/employee/job/attendace/<je_id>/')
def employeeAttendance(je_id):
    return render_template('employee/attendance.html')


@app.route('/landowner/home')
def landownerHome():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select * from notifications where type=0"
    res = getData(sql)
    return render_template('landowner/home.html', notifications=res)


@app.route('/landowner/job/browse/')
def findLandownerJobs():
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "select * from jobs where status=1"
    res = getData(sql)
    return render_template('landowner/job_list.html', jobs=res)


@app.route('/landowner/job/apply/<jid>/', methods=['POST', 'GET'])
def landRegister(jid):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        sql = "select ifnull(max(lid),0)+1 from land_details"
        res = getData(sql)
        lid = res[0][0]
        file = request.files['file']
        fn = os.path.basename(file.filename).split('.')
        fn = fn[len(fn)-1]
        fn = "%s.%s" % (lid, fn)
        sql = "insert into land_details values(%s,%s,%s,%s,%s,%s,0)"
        vals = (lid, session['uid'], jid, data['address'], data['ward'], fn)
        setData(sql, vals)
        file.save('static/uploads/land/'+secure_filename(fn))
        return redirect('/landowner/land/pending/')
    return render_template('/landowner/land_register.html')


@app.route('/landowner/land/<menu>/')
def landownerLandList(menu):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    status = ''
    if menu == 'pending':
        status = 0
    elif menu == 'approved':
        status = 1
    elif menu == 'rejected':
        status = 2
    elif menu == 'completed':
        status = 3
    sql = "select * from land_details l join jobs j on j.jid=l.jid where l.status=%s and uid=%s"
    vals = (status, session['uid'])
    res = getData(sql, vals)
    return render_template('landowner/land_list.html', lands=res, st=status)


@app.route('/landowner/job/cancel/<lid>/')
def deleteLand(lid):
    if 'uid' not in session or 'role' not in session:
        return redirect('/')
    sql = "delete from land_details where lid=%s" % lid
    setData(sql)
    return redirect('/landowner/land/pending/')


app.run(debug=True)
