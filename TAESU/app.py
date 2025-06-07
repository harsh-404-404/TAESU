import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, make_response,send_file,jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta,datetime,date
from weasyprint import HTML
from os import remove
import pandas as pd

from helpers import login_required


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365 * 10)
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JS access
app.config["SESSION_COOKIE_SECURE"] = True    # turn false if using http (but always use https)

Session(app)

db = SQL("sqlite:///database.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", error="invalid username and/or password")

        # Remember which user has logged in
        if request.form.get('rememberme'):
            session.permanent = True
        else:
            session.permanent = False

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
 # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("name") or not request.form.get("username") or not request.form.get("password") or not request.form.get("city") or not request.form.get("pet") or not request.form.get("email") or not request.form.get("birthdate"):
            return render_template("register.html", error="Make sure not to leave any form field empty")
        if request.form.get("password") != request.form.get("c_password") :
            return render_template("register.html", error="Password and confirm paassword does not match ")

        user = db.execute("SELECT username FROM users WHERE username = ?",request.form.get("username"))
        if user:
            return render_template("register.html", error="Username already taken")
        e_mail = db.execute("SELECT email FROM users WHERE email = ?",request.form.get("email"))
        if e_mail:
            return render_template("register.html", error="email address already used")

        name = request.form.get("name")
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        email = request.form.get("email")
        city = request.form.get("city")
        pet = request.form.get("pet")
        birthdate = request.form.get("birthdate")

        db.execute("INSERT INTO users(name,username,hash,email,city,pet,birthdate) VALUES(?,?,?,?,?,?,?)", name,username,hash,email,city,pet,birthdate)
        # log user in #
        x = db.execute("SELECT id FROM users WHERE username = ?", username)
        session.permanent = True
        session["user_id"] = x[0]["id"]
        return redirect("/add")
    return render_template("register.html")



@app.route("/forgotpassword", methods=["POST", "GET"])
def forgot_password():



    if request.method == "POST":
        if not request.form.get("email") or not request.form.get("city") or not request.form.get("pet") or not request.form.get("birthdate"):
            return render_template("forgot_password.html")
        email = db.execute("SELECT email FROM users WHERE email = ?",request.form.get("email"))
        if not email:
            return render_template("forgot_password.html", error="No account is associated with the given email address")
        email = email[0]["email"]
        x = db.execute("SELECT id,city,pet,birthdate FROM users WHERE email = ?", email)
        if x[0]["city"] != request.form.get("city") or x[0]["pet"] != request.form.get("pet") or x[0]["birthdate"] != request.form.get("birthdate"):
            return render_template("forgot_password.html", error="One or more wrong answers")
                # log user in #
        session.permanent = True
        session["user_id"] = x[0]["id"]
        session["change_password_key"] = True      #give key to allow user to access change password
        return redirect("/changepassword")

    return render_template("forgot_password.html")


@app.route("/changepassword", methods=["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        password = request.form.get("password")
        if not password :
            return render_template("change_password.html")
        if password != request.form.get("c_password"):
            return render_template("change_password.html", error="Password and confirm password does not match")
        db.execute("UPDATE users SET hash = ? WHERE id = ?",generate_password_hash(password), session["user_id"])
        return redirect("/dashboard")

    if session["change_password_key"] == True:   # if user needs key to use change password
        session["change_password_key"] = False   # taking the key away because now it has been used
        return render_template("change_password.html")
    return "<h1>Not allowed Error: 135795</h1>"



@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    return redirect("/dashboard")


@app.route("/add", methods=["GET","POST"])
@login_required
def add():
        if request.method == 'POST':
            if 'form1' in request.form:
                deadline_title = request.form.get("deadline_title")
                deadline_date = request.form.get("deadline_date")
                if not deadline_title:
                    return render_template("add.html",error=101)
                if not deadline_date :
                    return render_template("add.html",error=102)

                deadline_date = datetime.fromisoformat(deadline_date)
                current_date = datetime.fromisoformat(request.form.get("c_time"))
                countdown = (deadline_date - current_date).total_seconds()

                if countdown < 42200:             #43200s = 12 hours
                    return render_template("add.html",error=103)

                temp = db.execute("SELECT title FROM deadline WHERE user_id = ? AND title = ? AND date > ?", session["user_id"],deadline_title,current_date)
                if temp:
                    return render_template("add.html",error=104)
                del temp # to free temp variable
                db.execute("INSERT INTO deadline(user_id,title,date,log_date) VALUES(?,?,?,?)", session["user_id"],deadline_title,deadline_date,current_date)

                return render_template("add.html",success="success")





            elif 'form2' in request.form:

                if not request.form.get("start_date"):
                    return render_template("add.html",error=201)
                if not request.form.get("end_date"):
                    return render_template("add.html",error=202)
                if not request.form.get("task"):
                    return render_template("add.html",error=203)
                if len(request.form.get("task")) > 200:
                    return render_template("add.html",error=206)

                start_date = date.fromisoformat(request.form.get("start_date"))
                end_date = date.fromisoformat(request.form.get("end_date"))
                task = request.form.get("task")

                current_date = datetime.fromisoformat(request.form.get("c_time"))
                current_date = current_date.date()

# strip() removers extra whitespacese e.g. " moko" --> "moko" , "hi i am harsh " --> "hi i am harsh"
# lower() lowercase
                                    # to check given date is between existing entry
                if start_date < current_date or end_date < current_date or start_date > end_date:
                    return render_template("add.html",error=204)
                temp = db.execute("SELECT start,end FROM task_series WHERE user_id = ? AND lower(task) = ? AND start < ? AND end > ? ", session["user_id"], task.strip().lower(), start_date, end_date)
                if temp:
                    return render_template("add.html",error=205,list=temp)

                                    # to check given date is overlaping any existing entry
                temp = db.execute("SELECT start,end FROM task_series WHERE user_id = ? AND lower(task) = ? AND start >= ? AND start <= ? ", session["user_id"], task.strip().lower(), start_date, end_date)
                if temp:
                    return render_template("add.html",error=205,list=temp)


                db.execute("INSERT INTO task_series(user_id,task,start,end) VALUES(?,?,?,?)", session["user_id"], task.strip(), start_date, end_date)

                i = 0
                while start_date + timedelta(days=i) <= end_date:                       #you can not do +1 with datatype date.datetime
                    db.execute("INSERT INTO todo (user_id,date,task) VALUES (?,?,?)",session["user_id"], start_date + timedelta(days=i), task)
                    i += 1


                return render_template("add.html",success="success")











            elif 'form3' in request.form:


                if not request.form.get("note"):
                    return render_template("add.html",error=301)
                if not request.form.get("remind_date") :
                    return render_template("add.html",error=302)

                note = request.form.get("note")
                remind_date = date.fromisoformat(request.form.get("remind_date"))
                current_date = datetime.fromisoformat(request.form.get("c_time"))
                current_date = current_date.date()


                if db.execute("SELECT * FROM reminder WHERE user_id= ? AND lower(note) = ? AND date = ?", session["user_id"], note.lower().strip(), remind_date):
                    return render_template("add.html",error=303)


                if remind_date < current_date:
                    return render_template("add.html",error=304)

                db.execute("INSERT INTO reminder(user_id,note,date) VALUES(?,?,?)", session["user_id"], note.strip(), remind_date)
                return render_template("add.html",success="success")

        return render_template("add.html")




@app.route("/diary/date", methods=["POST"])
@login_required
def diary_date():
    json = request.get_json()
    if not json or not json["date"] or not json["c_date"]:
        return "Error"

    chosen_date = date.fromisoformat(json["date"])
    current_date = date.fromisoformat(json["c_date"])

    if current_date < chosen_date:
        return "invalid data"

    chosen_date_f = f"{chosen_date.day} {chosen_date.strftime('%b')},{chosen_date.year}"
    if chosen_date == current_date:
        temp = db.execute("SELECT data FROM diary WHERE user_id = ? AND date = ?",session["user_id"],current_date)
        if temp:
            return str(temp[0]["data"])
        else:
            return ""

    temp = db.execute("SELECT data FROM diary WHERE user_id = ? AND date = ?",session["user_id"],chosen_date)
    if not temp:
        return str(chosen_date_f) + "<div> <div><strong><span style='color: #e03e2d;'>Only save your changes if you’ve made edits. Don’t save if nothing was changed, and it's recommended that you remove the date written above.</span></strong></div> </div>"
    return temp[0]["data"]







@app.route("/diary", methods=["POST", "GET"])
@login_required
def diary():
    if request.method == "POST":
        if 'form_1' in request.form:
            if not request.form.get("date"):
                return render_template("diary.html",error="somthing went wrong")
            day = date.fromisoformat(request.form.get("date"))
            current_date = date.fromisoformat(request.form.get("c_date"))
            data = request.form.get("editor")
            if data == "":
                db.execute("DELETE FROM diary WHERE user_id = ? AND date = ?",session["user_id"],day)
                return render_template("diary.html",success="Saved successfully")
            if day > current_date:
                return render_template("diary.html",error="invalid date did unable to save")
            temp = db.execute("SELECT data FROM diary WHERE user_id = ? AND date = ?",session["user_id"],day)
            if temp:
                db.execute("UPDATE diary SET data = ? WHERE user_id = ? AND date = ?",data,session["user_id"],day)
                return render_template("diary.html",success="Saved successfully")
            db.execute("INSERT INTO diary(user_id,date,data) VALUES(?,?,?)",session["user_id"],day,data)
            return render_template("diary.html",success="Saved successfully")




    return render_template("diary.html")






@app.route("/diary/download", methods=["POST"]) #form x to y date
@login_required
def download():
    if 'form_2' in request.form:
        if not request.form.get("start_date"):
            return render_template("diary.html",error="201")
        if not request.form.get("end_date"):
            return render_template("diary.html",error="202")
        if not request.form.get("c_date"):
            return render_template("diary.html",error="error 203")

        start_date = date.fromisoformat(request.form.get("start_date"))
        end_date = date.fromisoformat(request.form.get("end_date"))
        current_date = date.fromisoformat(request.form.get("c_date"))

        if start_date > end_date or start_date > current_date or end_date > current_date:
            return render_template("diary.html",error="error 204")

        html_text = db.execute("SELECT date,data FROM diary WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date ASC",session["user_id"],start_date,end_date)
        # formathing text e.g: giving pdf header
        full_html = f"""<div style="page-break-after: always;"> <h1 style="text-align: center;"> <span style="text-decoration: underline;"> <span style="font-size: 36pt;">Index</span> </span> </h1> <h2 style="text-align: center;">From</h2> <p style="text-align: center;">{start_date.strftime("%d %b, %Y")}</p> <h2 style="text-align: center;">To</h2> <p style="text-align: center;">{end_date.strftime("%d %b, %Y")}</p> </div>"""
        for x in html_text:
            day = datetime.strptime(x["date"], "%Y-%m-%d").strftime("%d %b, %Y")
            day_html = f"<h3>{day}</h3><hr><p>&nbsp;</p>"
            entry_html = x['data'] + "<p>&nbsp;</p><p>&nbsp;</p>"
            full_html += day_html + entry_html

        # Write the full HTML to PDF once
        HTML(string=full_html).write_pdf("diary.pdf")

        return send_file("diary.pdf", as_attachment=True)

@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    success=False
    if request.method == "POST":
        if request.form.get("form_name") == "form_1":                                               # form 1=change username form 2=change email form 3,4,5 download userdata

            if not request.form.get("username"):
                return render_template("account.html")
            username = db.execute("SELECT username FROM users WHERE username = ?",request.form.get("username"))
            if username:
                    x = db.execute("SELECT name,email FROM users WHERE id = ?",session["user_id"])[0]
                    name = x["name"]
                    email = x["email"]
                    return render_template("account.html",username=request.form.get("username"),name=name,email=email,error=1001)
            db.execute("UPDATE users SET username = ? WHERE id = ?",request.form.get("username"),session["user_id"],)
            success=True





        if request.form.get("form_name") == "form_2":

            if not request.form.get("email"):
                return render_template("account.html")
            email = db.execute("SELECT email FROM users WHERE email = ?",request.form.get("email"))
            if email:
                    x = db.execute("SELECT name,username FROM users WHERE id = ?",session["user_id"])[0]
                    name = x["name"]
                    username = x["username"]
                    return render_template("account.html",username=username,name=name,email=request.form.get("email"),error=1002)
            db.execute("UPDATE users SET email = ? WHERE id = ?",request.form.get("email"),session["user_id"])
            success = True



        if 'form_3' in request.form:

            html_text = db.execute("SELECT date,data FROM diary WHERE user_id = ? ORDER BY date ASC",session["user_id"])
            full_html = f"""<div style="page-break-after: always;"> <h1 style="text-align: center;"> <span style="text-decoration: underline;"> <span style="font-size: 36pt;">Index</span> </span> </h1> <h2 style="text-align: center;">MY DIARY</h2></div>"""
            for x in html_text:
                day = datetime.strptime(x["date"], "%Y-%m-%d").strftime("%d %b, %Y")
                day_html = f"<h3>{day}</h3><hr><p>&nbsp;</p>"
                entry_html = x['data'] + "<p>&nbsp;</p><p>&nbsp;</p>"
                full_html += day_html + entry_html

            # Write the full HTML to PDF once

            HTML(string=full_html).write_pdf("diary.pdf")

            return send_file("diary.pdf", as_attachment=True)


        if 'form_4' in request.form:
            x = db.execute("SELECT title,log_date,date FROM deadline WHERE user_id = ? ORDER BY log_date",session["user_id"])
            #turn x in to excle
            df = pd.DataFrame(x)
            excel_path = "output.xlsx"
            df.to_excel(excel_path, index=False, engine='openpyxl')

            return send_file(excel_path, as_attachment=True)


        if 'form_5' in request.form:
            x = db.execute("SELECT date,note FROM reminder WHERE user_id = ? ORDER BY date",session["user_id"])
            #turn x in to excle
            df = pd.DataFrame(x)
            excel_path = "output.xlsx"
            df.to_excel(excel_path, index=False, engine='openpyxl')

            return send_file(excel_path, as_attachment=True)







    user = db.execute("SELECT name,username,email FROM users WHERE id = ?",session["user_id"])[0]
    username = user["username"]
    name = user["name"]
    email = user["email"]
    return render_template("account.html",username=username,name=name,email=email,success=success)









@app.route("/cheak_password", methods=["POST"])
@login_required
def cheak_password():
    json = request.get_json()
    if not json or not json["password"]:
        return "error"

    password = json["password"]

    x = db.execute("SELECT hash FROM users WHERE id = ?",session["user_id"])

    # Ensure username exists and password is correct
    if check_password_hash(x[0]["hash"], password):
            return "ok"
    else:
        return "error"





@app.route("/cheak_password_v2", methods=["POST"])
@login_required
def cheak_password_v2():
    json = request.get_json()
    if not json or not json["password"]:
        return "error"

    password = json["password"]

    x = db.execute("SELECT hash FROM users WHERE id = ?",session["user_id"])

    # Ensure username exists and password is correct
    if check_password_hash(x[0]["hash"], password):
        if not json["changepassword"]:                     #if this rout is used to cheak password becouse user has selected changepassword there will be changepassword in json
            return "ok"
        else:
            session["change_password_key"] = True
            return "redirect"
    else:
        return "error"






@app.route("/give_todo_list", methods=["POST"])
@login_required
def givetodolist():
    json = request.get_json()
    if not json["c_date"]:
        return
    day = date.fromisoformat(json["c_date"])
    data = db.execute("SELECT task,status,id FROM todo WHERE user_id = ? AND date = ? ORDER BY status",session["user_id"] ,day)
    return jsonify(data)


@app.route("/delete_todo_task", methods=["POST"])
@login_required
def delete_todo_task():
    json = request.get_json()
    if not json["id"]:
        return "Missing ID", 400

    db.execute("DELETE FROM todo WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"


@app.route("/complete_todo_task", methods=["POST"])
@login_required
def complete_todo_task():
    json = request.get_json()
    if not json["id"]:
        return  "Missing ID", 400

    db.execute("UPDATE todo SET status = 1 WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"


@app.route("/edit_todo_task", methods=["POST"])
@login_required
def edit_todo_task():
    json = request.get_json()
    if not json["id"]:
        return  "Missing ID", 400
    if not json["task"]:
        return  "Missing task", 400

    db.execute("UPDATE todo SET task = ? WHERE user_id = ? AND id = ?",json["task"],session["user_id"] ,json["id"],)
    return "ok"


@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    if request.method == "POST":
        if 'form1' in request.form:
            if not request.form.get("task"):
                return render_template("dashboard.html",error=101)
            if not request.form.get("c_date"):
                return render_template("dashboard.html",error=102)
            if len(request.form.get("task")) > 200:
                return render_template("dashboard.html",error=103)

            temp = db.execute("SELECT * FROM todo WHERE user_id = ? AND task = ? AND date = ?",session["user_id"],request.form.get("task"),request.form.get("c_date"))
            if temp:
                return render_template("dashboard.html",error=104)

            db.execute("INSERT INTO todo(task,user_id,date,status) VALUES(?,?,?,?) ",request.form.get("task"),session["user_id"],request.form.get("c_date"),0)
            return render_template("dashboard.html",success="success")


    return render_template("dashboard.html")

@app.route("/give_reminder_list", methods=["POST"])
@login_required
def givereminerlist():
    json = request.get_json()
    if not json["c_date"]:
        return
    day = date.fromisoformat(json["c_date"])
    data = db.execute("SELECT id,date,note,status FROM reminder WHERE user_id = ? AND date = ? ORDER BY status",session["user_id"] ,day)

    return jsonify(data)


@app.route("/update_reminder_status", methods=["POST"])
@login_required
def update_reminder_status():
    json = request.get_json()
    if not json["id"]:
        return  "Missing ID", 400

    if json["status"] == "0":                                     # 0 is stinggg  ( ｡ •̀ ᴖ •́ ｡)💢
        db.execute("UPDATE reminder SET status = 0 WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
        return "ok"
    else:
        db.execute("UPDATE reminder SET status = 1 WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
        return "ok"


@app.route("/edit_reminder_note", methods=["POST"])
@login_required
def edit_reminder_task():
    json = request.get_json()
    if not json["id"]:
        return  "Missing ID", 400
    if not json["note"]:
        return  "Missing task", 400

    db.execute("UPDATE reminder SET note = ? WHERE user_id = ? AND id = ?",json["note"],session["user_id"] ,json["id"])
    return "ok"



@app.route("/delete_reminder_note", methods=["POST"])
@login_required
def delete_reminder_note():
    json = request.get_json()
    if not json["id"]:
        return "Missing ID", 400

    db.execute("DELETE FROM reminder WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"


@app.route("/give_tomorrow_reminder_list", methods=["POST"])
@login_required
def givetomorrowreminerlist():
    json = request.get_json()
    if not json["c_date"]:
        return
    day = date.fromisoformat(json["c_date"]) + timedelta(days=1)

    data = db.execute("SELECT id,note FROM reminder WHERE user_id = ? AND date = ?",session["user_id"] ,day)

    return jsonify(data)

@app.route("/delete_reminder_tomorrow_note", methods=["POST"])
@login_required
def delete_reminder_tomorrow_note():
    json = request.get_json()
    if not json["id"]:
        return "Missing ID", 400

    db.execute("DELETE FROM reminder WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"


@app.route("/give_deadline_list", methods=["POST"])
@login_required
def givedeadlinelist():
    json = request.get_json()
    if not json["c_time"]:
        return
    day = datetime.fromisoformat(json["c_time"])

    data = db.execute("SELECT id,title,date FROM deadline WHERE user_id = ? AND date > ? ORDER BY date",session["user_id"] ,day)
    return jsonify(data)



@app.route("/delete_deadline", methods=["POST"])
@login_required
def delete_deadline():
    json = request.get_json()
    if not json["id"]:
        return "Missing ID", 400

    db.execute("DELETE FROM deadline WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"



@app.route("/give_yesterday_todo_task", methods=["POST"])
@login_required
def give_yesterday_todo_task():
    json = request.get_json()
    if not json["c_date"]:
        return
    y_date = date.fromisoformat(json["c_date"]) - timedelta(days=1)
    data = db.execute("SELECT task,status,id FROM todo WHERE user_id = ? AND date = ? ORDER BY status",session["user_id"] ,y_date)
    return jsonify(data)



@app.route("/update_yesterday_todo_status", methods=["POST"])
@login_required
def update_yesterday_todo_status():
    json = request.get_json()
    if not json["id"]:
        return  "Missing ID", 400

    db.execute("UPDATE todo SET status = 1 WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"



@app.route("/give_tomorrow_todo_task", methods=["POST"])
@login_required
def give_tomokrrow_todo_task():
    json = request.get_json()
    if not json["c_date"]:
        return
    t_date = date.fromisoformat(json["c_date"]) + timedelta(days=1)
    data = db.execute("SELECT task,id FROM todo WHERE user_id = ? AND date = ? ",session["user_id"] ,t_date)
    return jsonify(data)





@app.route("/give_miscellaneous_task", methods=["POST"])
@login_required
def give_miscellaneous_task():
    data = db.execute("SELECT task,id FROM miss_task WHERE user_id = ? AND end_date IS NULL ORDER BY log_date",session["user_id"])
    return jsonify(data)



@app.route("/add_miscellaneous_task", methods=["POST"])
@login_required
def add_miscellaneous_task():
    json = request.get_json()
    if not json["c_date"]:
        return 404
    if not json["task"]:
        return 404
    if len(json["task"]) > 200:
        return 422
    db.execute("INSERT INTO miss_task(user_id,task,log_date) VALUES(?,?,?)",session["user_id"], json["task"], json["c_date"])
    data = db.execute("SELECT task,id FROM miss_task WHERE user_id = ? AND task = ?",session["user_id"],json["task"])
    return jsonify(data)



@app.route("/delete_miss_task", methods=["POST"])
@login_required
def delete_miss_task():
    json = request.get_json()
    if not json["id"]:
        return "Missing ID", 400

    db.execute("DELETE FROM miss_task WHERE user_id = ? AND id = ?",session["user_id"] ,json["id"])
    return "ok"


@app.route("/complete_miss_task", methods=["POST"])
@login_required
def complete_miss_task():
    json = request.get_json()
    if not json["id"]:
        return "Missing ID", 400
    if not json["c_date"]:
        return 400

    db.execute("UPDATE miss_task SET end_date = ? WHERE user_id = ? AND id = ?",json["c_date"],session["user_id"] ,json["id"])
    return "ok"


@app.route("/download_miss_history", methods=["POST"])
@login_required
def download_miss_history():
            x = db.execute("SELECT task,log_date,end_date FROM miss_task WHERE user_id = ? ORDER BY log_date,end_date",session["user_id"])
            #turn x in to excle
            df = pd.DataFrame(x)
            excel_path = "miscellaneouou.xlsx"
            df.to_excel(excel_path, index=False, engine='openpyxl')

            return send_file(excel_path, as_attachment=True)


@app.route("/contact", methods=["POST", "GET"])
@login_required
def contact():
    if request.method == "POST":
        db.execute("INSERT INTO contact(user_id,name,email,message) VALUES(?,?,?,?)",session["user_id"],request.form.get("name"),request.form.get("email"),request.form.get("message"))


    return render_template("contact.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port)
