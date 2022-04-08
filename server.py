from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app) #Database classes = models
#Each class is its own table in the database

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin(''{self.id}', {self.username}', '{self.password}')"

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    password = data['password'].encode('utf-8', 'strict')
    hashedpw = hashlib.md5(password).hexdigest()

    print("**********************")
    print(data)
    print(hashedpw)
    print("**********************")
    # user = mycol.find_one({"username":username, "password" : hashedpw})

    admin = Admin.query.filter_by(username=data['username'])
    # admin.one().password = hashedpw
    # db.session.commit()
    print(admin.one());
    if admin.one() and admin.one().password == hashedpw:
        return jsonify(Response=True)
    else:
        return jsonify(Response=False)

if __name__ == "__main__":
    app.run()