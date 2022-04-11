from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='kusumachandashwini'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/project'
db=SQLAlchemy(app)

# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class Department(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    branch=db.Column(db.String(100))

class Status(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    caseno=db.Column(db.String(100))
    status=db.Column(db.Integer())

class Trig(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))





class Criminal(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    caseno=db.Column(db.String(50))
    cname=db.Column(db.String(50))
    uid=db.Column(db.Integer)
    gender=db.Column(db.String(50))
    branch=db.Column(db.String(50))
    date=db.Column(db.String(50))
    number=db.Column(db.String(12))
    comments=db.Column(db.String(100))
    

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/criminaldetails')
def criminaldetails():
    query=db.engine.execute(f"SELECT * FROM `criminal`") 
    return render_template('criminaldetails.html',query=query)

@app.route('/triggers')
def triggers():
    query=db.engine.execute(f"SELECT * FROM `trig`") 
    return render_template('triggers.html',query=query)

@app.route('/department',methods=['POST','GET'])
def department():
    if request.method=="POST":
        dept=request.form.get('dept')
        query=Department.query.filter_by(branch=dept).first()
        if query:
            flash("Department Already Exist","warning")
            return redirect('/department')
        dep=Department(branch=dept)
        db.session.add(dep)
        db.session.commit()
        flash("Department Added.","success")
    return render_template('department.html')

@app.route('/addstatus',methods=['POST','GET'])
def addstatus():
    query=db.engine.execute(f"SELECT * FROM `criminal`") 
    if request.method=="POST":
        caseno=request.form.get('caseno')
        attend=request.form.get('attend')
        print(attend,caseno)
        atte=Status(caseno=caseno,status=attend)
        db.session.add(atte)
        db.session.commit()
        flash("Status added","warning")

        
    return render_template('status.html',query=query)

@app.route('/search',methods=['POST','GET'])
def search():
    if request.method=="POST":
        caseno=request.form.get('caseno')
        bio=Criminal.query.filter_by(caseno=caseno).first()
        attend=Status.query.filter_by(caseno=caseno).first()
        return render_template('search.html',bio=bio,attend=attend)
        
    return render_template('search.html')

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    db.engine.execute(f"DELETE FROM `criminal` WHERE `criminal`.`id`={id}")
    flash("Slot Deleted Successfully","danger")
    return redirect('/criminaldetails')


@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    dept=db.engine.execute("SELECT * FROM `department`")
    posts=Criminal.query.filter_by(id=id).first()
    if request.method=="POST":
        caseno=request.form.get('caseno')
        cname=request.form.get('cname')
        uid=request.form.get('uid')
        gender=request.form.get('gender')
        branch=request.form.get('branch')
        date=request.form.get('date')
        num=request.form.get('num')
        comments=request.form.get('comments')
        query=db.engine.execute(f"UPDATE `criminal` SET `caseno`='{caseno}',`cname`='{cname}',`uid`='{uid}',`gender`='{gender}',`branch`='{branch}',`date`='{date}',`number`='{num}',`comments`='{comments}'")
        flash("Slot is Updated","success")
        return redirect('/criminaldetails')
    
    return render_template('edit.html',posts=posts,dept=dept)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        # newuser=User(username=username,email=email,password=encpassword)
        # db.session.add(newuser)
        # db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/addcriminal',methods=['POST','GET'])
@login_required
def addcriminal():
    dept=db.engine.execute("SELECT * FROM `department`")
    if request.method=="POST":
        caseno=request.form.get('caseno')
        cname=request.form.get('cname')
        uid=request.form.get('uid')
        gender=request.form.get('gender')
        branch=request.form.get('branch')
        date=request.form.get('date')
        num=request.form.get('num')
        comments=request.form.get('comments')
        query=db.engine.execute(f"INSERT INTO `criminal` (`caseno`,`cname`,`uid`,`gender`,`branch`,`date`,`number`,`comments`) VALUES ('{caseno}','{cname}','{uid}','{gender}','{branch}','{date}','{num}','{comments}')")
    

        flash("Record Uploaded","info")


    return render_template('criminal.html',dept=dept)
@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


app.run(debug=True)    