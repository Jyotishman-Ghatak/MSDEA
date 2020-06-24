from flask import Flask,render_template,request,redirect,session,url_for,flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/voting'
app.secret_key="hellothere"
admin_username='admin'
admin_password="1234"
db = SQLAlchemy(app)

class Voter(db.Model):                                                                  #DATABASE MODEL
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    DOB= db.Column(db.String(30), nullable=False)
    Register = db.Column(db.String(120), unique=True, nullable=False)
    Valid= db.Column(db.Boolean,nullable=False)
    Voted= db.Column(db.Boolean,nullable=False)

class Candidate(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), nullable=False)
    Register = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    DOB= db.Column(db.String(30), nullable=False)
    Branch= db.Column(db.String(30), nullable=False)
    Count = db.Column(db.Integer, nullable=False)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/admin_login', methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        print(username,password)
        if(admin_password==password and password==admin_password):
            return redirect(url_for("candidate_reg"))
        else:
            flash("Invalid Username and Password")
            return  render_template("admin_login.html")
    return render_template("admin_login.html")

@app.route('/candidate')
def candidate():
    candidates=Candidate.query.all()
    return render_template("candidate.html",candidates=candidates)

@app.route('/voter')
def voter():
    voters=Voter.query.filter(Voter.Valid.like(1)).all()
    return render_template("voter.html",voters=voters)

@app.route('/delete',methods=["GET","POST"])
def delete():
    if request.method=="POST":
        Register=request.form.get('Delete')
        voter=Voter.query.filter(Voter.Register.like(Register)).first()
        db.session.delete(voter)
        db.session.commit()
    return redirect('/validatevoter')
        
@app.route('/validatevoter',methods=["GET","POST"])
def validatevoter():
    if request.method=="POST":
        Register=request.form.get('Validate')
        print(Register)
        voter=Voter.query.filter(Voter.Register.like(Register)).first()
        voter.Valid=True
        db.session.commit()
        voters=Voter.query.filter(Voter.Valid.like(0)).all()
        flash("Voter Validated Successfully")
        return render_template("validatevoter.html",voters=voters)
        
    else:
        voters=Voter.query.filter(Voter.Valid.like(0)).all()
        print(len(voters))
        if(len(voters)>0):
            return render_template("validatevoter.html",voters=voters)
        else:
            flash("No voters to validate","info")
            return render_template("validatevoter.html")

@app.route('/candidate_reg', methods=["GET","POST"])
def candidate_reg():
    print(request.method)
    if request.method=="POST":
        try:
            Name=request.form.get('Name')
            email=request.form.get('email')
            DOB=request.form.get('DOB')
            Branch=request.form.get('Branch')
            Register=request.form.get('Register')
            entry= Candidate(Name=Name, email=email,DOB=DOB, Branch=Branch,Register=Register,Count=0)
            db.session.add(entry)
            db.session.commit()
            flash("Candidate Added Successfully!","info")
            return render_template("candireg.html")
        except:
            flash("Candidate Already Exist ","info")
            return render_template("candireg.html")
    else:
        return render_template("candireg.html")
        

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        Register=request.form.get('Register')
        DOB=request.form.get('DOB')
        voter=Voter.query.filter(Voter.Register.like(Register),Voter.DOB.like(DOB)).first()
        if(voter!=None and voter.Voted==False and voter.Valid==True):
            session['Register']=Register
            #if 'Register' in session:
            #return "Welcome to voting {}".format(voter.Name)
            candidates=Candidate.query.all()
            return render_template("castvote.html",candidates=candidates)
        elif(voter!=None and voter.Voted==True):
            flash("You Have Already Voted!")
            return render_template("login.html")
        elif(voter!=None and voter.Valid==False):
            flash("your data is not validated yet retry after some time. If this problem continues contact Admin for enquiry.","info")
            return render_template("login.html")
        else:
            flash("Invalid Username or DOB")
            return render_template("login.html") 
    else:

            return render_template('login.html')  
          
@app.route('/castvote',methods=["GET","POST"])
def castvote():
    if request.method=="POST":
        temp_candidate_register=request.form.get('vote')
        print(temp_candidate_register)
        temp_register=session['Register']
        print(temp_register)
        voter=Voter.query.filter(Voter.Register.like(temp_register)).first()
        candidate=Candidate.query.filter(Candidate.Register.like(temp_candidate_register)).first()
        candidate.Count+=1
        voter.Voted=True
        db.session.commit()
        flash("You Voted Sucessfully!","info")
        return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/signup', methods=["GET","POST"])
def signup():
    
    if request.method=="POST":
        Name=request.form.get('Name')
        email=request.form.get('email')
        DOB=request.form.get('DOB')
        Register=request.form.get('Register')
        try:
            entry=Voter(Name=Name,email=email,DOB=DOB,Register=Register,Valid=False,Voted=False)
            db.session.add(entry)
            db.session.commit()
            flash("User added successfully","info")
            return render_template("login.html")
        except:
            flash("User Already Exist!","info")
            return render_template("signup.html")        
    else:
        
        return render_template('signup.html')


if __name__=='__main__':
    app.run(debug=True)