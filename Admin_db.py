'''importing required modules'''
from flask import Flask,request,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
'''Identifying resource using Identifier'''
app.config["SQLALCHMEY_DATABASE_URI"]="mydatabase+pymysql://root:1234@localhost:3036/mydatabase";
app.config["DATABASE_TRACK_MODIFICATIONS"]=True
db=SQLAlchemy(app)
'''bus details table'''
class Bus_booking(db.Model):
    __tablename__="Bus_Details"
    bus_id=db.Column(db.Integer,db.Sequence('seq',start=100),primary_key=True)
    bus_name=db.Column(db.String(25))
    From=db.Column(db.String(25))
    To=db.Column(db.String(25))
    Total_seat=db.Column(db.Integer)
    available_seat=db.Column(db.Integer)
    price=db.Column(db.Integer)
'''agent table details'''
class Agent_Details(db.Model):
    __tablename__="agent_Details"
    agent_id=db.Column(db.Integer,db.Sequence('seq',start=5000),primary_key=True)
    agent_name=db.Column(db.String(25))
    mobile=db.Column(db.String(25))
    password=db.Column(db.String(25))
    
'''seatavailability table'''
class seatavailability(db.Model):
    __tablename__="seating_Details"
    bus_id=db.Column(db.Integer,db.Sequence('seq',start=5000),primary_key=True)
    bus_name=db.Column(db.String(25))
    From=db.Column(db.String(25))
    To=db.Column(db.String(25))
    Ticket_booked=db.Column(db.String(10))
    Total_fare=db.Column(db.String(25))

'''agent functions--->booking tickets'''    
@app.route('/booktickets',methods=['GET','POST'])
def book_ticket():
    if request.method=='GET':
        return render_template("booktickets.html")
    elif request.method=='POST':
        id=request.form['id']
        no_of_tickets=request.form['no_of_tickets']
        bus=Bus_booking.query.filter(Bus_booking.bus_id==id).first()
        if(bus.Total_seat>no_of_tickets):
            bus.available_seat=int(bus.Total_seat)-int(no_of_tickets)
            busid=bus.bus_id
            busName=bus.bus_name
            From=bus.From
            To=bus.To 
            Ticket_booked=no_of_tickets
            Total_fare=(no_of_tickets)*bus.price
            obj1=seatavailability(bus_id=busid,bus_name=busName,From=From,To=To,Ticket_booked=Ticket_booked,Total_fare=Total_fare)
            db.session.add(obj1)
            db.session.commit()
        else:
            return "sorry,ticket not available"
        return render_template('booktickets.html')
'''agent function to view booking'''
@app.route('/show_booking',methods=['GET','POST']) 
def show_booking():
    if request.method=='GET':
        return render_template("show_booking.html")
    elif request.method=='POST':
        id=request.form['id']
        obj1=seatavailability.query.filter(seatavailability.bus_id==id).first()
        return render_template('show_booking_details.html',obj=obj1)
    return render_template('agent_menu.html')


'''agent function to respective functions they need'''
@app.route('/agent_menu',methods=['GET','POST']) 
def agent_menu():  
    if request.method=='GET':
        return render_template('agent_menu.html')  
    elif request.method=='POST':
        option=request.form['menu']
        if option=="Bus Details":
            list_of_bus=Bus_booking.query.all()
            return render_template('display_addbus.html',obj=list_of_bus) 
        elif option=="Book tickets":
            return redirect(url_for('booktickets'))
        elif option=="show booking":
            return redirect(url_for('show_booking'))
        elif option=="logout":
            return render_template('login.html')
        return render_template('agent_menu.html')
        
'''agent login-->agent_menu'''        
@app.route('/agent',methods=['GET','POST'])
def agent():   
    if request.method=='GET':
        return render_template('Agent_login.html')
    elif request.method=='POST':
        Agent_id=request.form['agent_id']
        password=request.form['Password']
        book=Agent_Details.query.filter(Agent_Details.agent_id==Agent_id).first()
        ''' password validation'''
        if book.password==password: 
            return redirect(url_for('agent_menu'))
        else:
            return "Enter valid credential"
        return render_template('login.html')
    
'''admin functions add->agent'''        
@app.route('/add_agent',methods=['GET','POST']) 
def add_agent():
    if request.method=='GET':
        return render_template("Add_agent.html")
    elif request.method=='POST':
        agent_name=request.form['agent_name']
        mobile=request.form['mobile']
        password=request.form['password']
        option=request.form["option"]
        if option=="add":
            agent_obj1=Agent_Details(agent_name=agent_name,mobile=mobile,password=password)
            db.session.add(agent_obj1)
            db.session.commit()
        elif option=="display":
            obj=Agent_Details.query.all()
            return render_template('display_agent.html',obj=obj)
        return render_template("Add_agent.html") 
    
    
'''admin-->addbus'''
@app.route('/add_bus',methods=['GET','POST'])
def add_bus():
    if request.method=='GET':
        return render_template("Add_bus.html")
    elif request.method=='POST':
        bus_name=request.form['bus_name']
        From=request.form['From']
        To=request.form['To']
        Total_seat=request.form['Total_seat']
        available_seat=request.form['booked_seat']
        price=request.form['price']
        option=request.form["option"]
        if option=="add":
            bus_obj1=Bus_booking(bus_name=bus_name,From=From,To=To,Total_seat=Total_seat,available_seat=available_seat,price=price)
            db.session.add(bus_obj1)
            db.session.commit()
        elif option=="display":
            obj=Bus_booking.query.all()
            return render_template('display_addbus.html',obj=obj)
        return render_template('Menu.html')
    
    
'''admin-->valid->addbus or addagent or logout'''   
@app.route('/valid',methods=['GET','POST']) 
def valid():
    if request.method=='GET':
        return render_template('Menu.html')
    elif request.method=='POST':
        option=request.form['menu']
        if option=="add_bus":
            return redirect(url_for('add_bus'))
        elif option=="add_agent":
            return redirect(url_for('add_agent'))
        elif option=="logout":
            return render_template('login.html')  
        
         
'''admin functions To use admin login--> enter admin email:"admin@gmail.com" and password=1234-->goes to valid router'''         
@app.route('/admin',methods=['GET','POST']) 
def admin():
    if request.method=='GET':
        return render_template('Admin.html')
    elif request.method=='POST':
        Email=request.form['Email']
        Password=request.form['Password']
        if Email == "admin@gmail.com" and Password == "1234" :
            return redirect(url_for('valid'))
        else:
            return "Enter valid credentials"
        return render_template('Admin.html')
    
    
    
'''enter the options'''
@app.route('/login',methods=['GET','POST'])
def login_details():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        option=request.form['input']
        if option=="1":
            '''router goes to admin page'''
            return redirect(url_for('admin'))
        elif option=="2":
            '''router goes to agent page'''
            return redirect(url_for('agent'))
        return render_template('login.html')
            
if __name__=="__main__":
    db.create_all()
    db.session.commit()
    app.run(debug=True,port=5000)
       
    