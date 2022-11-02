from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import config
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash

from models.ModelUsers import ModelUser

from models.entites.User import User

app = Flask(__name__)

db = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("invalid password..")
            return render_template('auth/login.html')

        else:
            flash("User not found..")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        encrip = generate_password_hash(request.form['password']) 
        cursor = db.connection.cursor()
        sql = """INSERT INTO user (username, password, fullname) VALUES ('{}','{}','{}')""".format(request.form['username'], encrip, request.form['fullname'])
        cursor.execute(sql)
        db.connection.commit() #confirm action
        return redirect(url_for('home'))
    else:
        return render_template('auth/register.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/API',  methods=['GET'])
def protected():
    try:
        cursor = db.connection.cursor()
        sql = "SELECT id, username, password, fullname FROM user"
        cursor.execute(sql)
        data = cursor.fetchall()
        list_users = []
        for row in data:
            user_data = {'id': row[0], 'username': row[1],
                         'password': row[2], 'fullname': row[3]}
            list_users.append(user_data)
        return jsonify({'list_users': list_users, 'message': "user data"})

    except Exception as ex:
        return jsonify({'message': "Error"})

@app.route('/API', methods=['POST'])
def register_user():
    # print(request.json)
    try:
        cursor = db.connection.cursor()
        encrip = generate_password_hash(request.json['password'])

        sql = """INSERT INTO user (username, password, fullname) 
                VALUES ('{}','{}','{}')""".format(request.json['username'], encrip, request.json['fullname'])
        cursor.execute(sql)
        db.connection.commit() #confirm
        return jsonify({'message': "message OK"})
    except Exception as ex:
        return jsonify({'ex':ex, 'message': "Error"})

@app.route('/API/<username>', methods=['PUT'])
def update_data(username):
    try:
        encrip = generate_password_hash(request.json['password'])
        cursor = db.connection.cursor()
        sql = """UPDATE user SET fullname = '{}' 
        WHERE username = '{}'""".format(request.json['fullname'], username)
        cursor.execute(sql)
        db.connection.commit()  
        return jsonify({'message': "user update.", 'exit': True})
        
    except Exception as ex:
        return jsonify({'message': "Error", 'exit': False})
    

@app.route('/API/<username>', methods=['DELETE'])
def delete_user(username):
    try:
       
        cursor = db.connection.cursor()
        sql = "DELETE FROM user WHERE username = '{}'".format(username)
        cursor.execute(sql)
        db.connection.commit()  # Confirm.
        return jsonify({'message': "user DELTE.", 'exit': True})
        
    except Exception as ex:
        return jsonify({'message': "Error", 'exit': False})



def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Pág not found</h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
