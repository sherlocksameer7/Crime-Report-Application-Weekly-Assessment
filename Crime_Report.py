from flask import Flask, request, render_template, session
import sqlite3

from flask_session import Session
from werkzeug.utils import redirect
from datetime import date


Connection = sqlite3.connect("Crime_for_Report.db", check_same_thread=False)
List_of_tables1 = Connection.execute("Select * from sqlite_master Where type = 'table' And name = 'Crime'").fetchall()
List_of_tables2 = Connection.execute("Select * from sqlite_master Where type = 'table' And name = 'User'").fetchall()

if List_of_tables1 != []:
    print("Crime Table Already Exists")
else:
    Connection.execute('''create table Crime(
                            Id Integer Primary Key Autoincrement,
                            Description Text,
                            Remarks Text,
                            Date Text);''')
    print("Crime Table created")


if List_of_tables2 != []:
    print("User table already exists")
else:
    Connection.execute('''Create Table User(
                            Id Integer Primary Key Autoincrement,
                            Name Text,
                            Address Text,
                            Email Text,
                            Phone Integer,
                            Password Text);''')
    print("User Table Created")


crime_app = Flask(__name__)


crime_app.config["SESSION_PERMANENT"] = False
crime_app.config["SESSION_TYPE"] = "filesystem"
Session(crime_app)



@crime_app.route('/', methods=['GET', 'POST'])
def Login_admin():
    if request.method == 'POST':
        getUsername = request.form["name"]
        getPassword = request.form["pass"]
        print(getUsername)
        print(getPassword)
        if getUsername == "admin" and getPassword == "12345":
            return redirect('/dashboard')
        else:
            return redirect('/')
    return render_template("adminLogin.html")



@crime_app.route('/dashboard')
def Admin_dashboard():
    return render_template("adminDash.html")



@crime_app.route('/view')
def View_report():
    cursor = Connection.cursor()
    count = cursor.execute("Select * from Crime")

    result = cursor.fetchall()
    return render_template("viewall.html", crime=result)



@crime_app.route('/sort', methods=['GET', 'POST'])
def Search_crime():
    if request.method == 'POST':
        getDate = str(request.form["date"])
        cursor = Connection.cursor()
        count = cursor.execute("Select * from Crime Where Date='"+getDate+"' ")
        result = cursor.fetchall()
        if result is None:
            print("There is no Crime on", getDate)
        else:
            return render_template("date_sorting.html", crime=result, status=True)
    else:
        return render_template("date_sorting.html", crime=[], status=False)



@crime_app.route('/register', methods=['GET', 'POST'])
def User_register():
    if request.method == 'POST':
        getName = request.form["name"]
        getAddress = request.form["address"]
        getEmail = request.form["email"]
        getPhone = request.form["phone"]
        getPass = request.form["pass"]
        print(getName, getAddress, getEmail, getPhone)
        try:
            Connection.execute("Insert into User(Name,Address,Email,Phone,Password) \
            Values('"+getName+"','"+getAddress+"','"+getEmail+"',"+getPhone+",'"+getPass+"')")
            Connection.commit()
            print("Inserted Successfully")
            return redirect('/complaint')
        except Exception as err:
            print(err)
    return render_template("register_page.html")



@crime_app.route('/user', methods=['GET', 'POST'])
def Login_user():
    if request.method == 'POST':
        getEmail = request.form["email"]
        getPass = request.form["pass"]
        cursor = Connection.cursor()
        query = "Select * from User Where Email='"+getEmail+"' And Password='"+getPass+"'"
        result = cursor.execute(query).fetchall()
        if len(result) > 0:
            for i in result:
                getName = i[1]
                getId = i[0]
                session["name"] = getName
                session["id"] = getId
                if (getEmail == i[3] and getPass == i[5]):
                    print("Password Correct")
                    return redirect('/usersession')

                else:
                    return render_template("userLogin.html", status=True)
    else:
        return render_template("userLogin.html", status=False)



@crime_app.route('/userdashboard')
def user_dash():
    return render_template("userDash.html")


@crime_app.route('/usersession')
def userpage():
    if not session.get("name"):
        return redirect('/')
    else:
        return render_template("usersession.html")



@crime_app.route('/complaint', methods=['GET', 'POST'])
def Report_crime():
    if request.method == 'POST':
        getDescrip = request.form["description"]
        getRemark = request.form["remark"]
        print(getDescrip)
        print(getRemark)
        getDate = str(date.today())
        cursor = Connection.cursor()
        query = "Insert into Crime(Description,Remarks,Date) Values('"+getDescrip+"','"+getRemark+"','"+getDate+"')"
        cursor.execute(query)
        Connection.commit()
        print(query)
        print("Inserted Successfully")

        return redirect('/user')
    return render_template("complaint_details.html")



@crime_app.route('/update', methods=['GET', 'POST'])
def Update_user():
    try:
        if request.method == 'POST':
            getUser = request.form["name"]
            cursor = Connection.cursor()
            count = cursor.execute("Select * from User Where Name='" + getUser + "' ")
            Result = cursor.fetchall()
            print(len(Result))
            return render_template("editUser.html", searchname=Result)
        return render_template("editUser.html")

    except Exception as err:
        print(err)



@crime_app.route('/edit', methods=['GET', 'POST'])
def User_edit():
    if request.method == 'POST':
        getName = request.form["name"]
        getAddress = request.form["address"]
        getEmail = request.form["email"]
        getPhone = request.form["phone"]
        getPass = request.form["pass"]
        try:
            query = "Update User Set Name='" + getName + "',Address='" + getAddress + "',Email='" + getEmail + "',Phone=" + getPhone + ",Password='" + getPass + "' Where Name='" + getName + "'"
            print(query)
            Connection.execute(query)
            Connection.commit()
            print("Edited Successfully")
            return redirect('/view')
        except Exception as err:
            print(err)
    return render_template("editUser.html")


@crime_app.route('/logout')
def Logout():
    session["name"] = None
    return redirect('/')



if __name__ == "__main__":
    crime_app.run()