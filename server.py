from flask import Flask, jsonify, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib, json, base64, os, shutil

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app) #Database classes = models
#Each class is its own table in the database

#@app.route("/")
#@cross_origin()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.id}', {self.username}', '{self.password}')"

class Concert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    shortTitle = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tag = db.Column(db.Text, nullable=False)

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}, 400)
    # A few lines here from chatgpt
    password = password.encode('utf-8', 'strict')
    hashedpw = hashlib.md5(password).hexdigest()

    # print("**********************")
    # print(data)
    # print(hashedpw)
    # print("**********************")
    # user = mycol.find_one({"username":username, "password" : hashedpw})

    admin1 = Admin.query.filter_by(username=username).first()
    print(admin1);
    if admin1 != None and admin1.password == hashedpw:
        return jsonify(Response=True)
    else:
        return jsonify(Response=False)

@app.route("/addconcert", methods=['POST'])
def addconcert():
    data = request.get_json()
    print("*****************************")
    print(f"{data['title']} - {data['shortTitle']} - {data['time']} - {data['location']} - {data['content']} - {data['tag']}")
    print("**********************")

    try:
        exists = Concert.query.filter_by(title=data['title']).first();
        if exists == None:
            # Add concert data to database
            instance = Concert(title=data['title'], shortTitle=data['shortTitle'], time=data['time'], location=data['location'], content=json.dumps(data['content']), tag=data['tag'])
            db.session.add(instance)
            db.session.commit();

            # Add the photos in
            os.makedirs(f"mysite/static/{instance.id}")
            print(f"mysite/static/{instance.id}")
            if len(data['base64']) > 0:
                print('we make it here?')
                for index, img in enumerate(data['base64']):
                    imgdata = base64.b64decode(img)
                    filename = f"mysite/static/{instance.id}/{index}.jpg"
                    print(filename)
                    with open(filename, 'wb') as f:
                        f.write(imgdata)
            # Add the poster in
            if len(data['base64Poster']) > 0:
                print('we got something');
                imgdata = base64.b64decode(data['base64Poster'][0])
                filename = f"mysite/static/Posters/{instance.id}.jpg"
                with open(filename, 'wb') as f:
                    f.write(imgdata)

            return jsonify(Response=True)
        else:
            return jsonify(Response='Concert Exists')
    except Exception as e:
        print(e);
        return jsonify(Response='Error with server')

    # if (Concert.query.filter_by(title=data['title']).first()):
    #     return jsonify(Response=False)
    # else:
    #     instance = Concert(title=data['title'], location=data['time'], country=data['location'], content=data['paragraphs'])
    #     db.session.add(instance)
    #     db.session.commit();
    #     return jsonify(Response=True)

# Update Concert
@app.route("/updateConcert", methods=['GET', 'POST'])
def updateConcert():
    data = request.get_json()
    print(data)
    try:
        concertToEdit = Concert.query.filter_by(id=data['concertID']).first();
        if concertToEdit != None:
            concertToEdit.title = data['title']
            concertToEdit.shortTitle = data['shortTitle']
            concertToEdit.time = data['time']
            concertToEdit.location = data['location']
            concertToEdit.content = json.dumps(data['content'])
            concertToEdit.tag = data['tag']
            db.session.commit()

            # Check poster & update it
            if len(data['base64Poster']) > 0:
                imgdata = base64.b64decode(data['base64Poster'][0])
                filename = f"mysite/static/Posters/{concertToEdit.id}.jpg"
                with open(filename, 'wb') as f:
                    f.write(imgdata)

            # Check concert images & update them
            if len(data['base64']) > 0:
                # Nuke the photos first
                try:
                    for file in os.listdir(f"mysite/static/{data['concertID']}"):
                        os.remove(f"mysite/static/{data['concertID']}/{file}")
                except Exception as e:
                    print(e)
                    return jsonify(Response='Error adding photos')

                # Add in the new photos
                try:
                    for index, img in enumerate(data['base64']):
                        imgdata = base64.b64decode(img)
                        filename = f"mysite/static/{concertToEdit.id}/{index}.jpg"
                        with open(filename, 'wb') as f:
                            f.write(imgdata)
                except Exception as e:
                    print(e)
                    return jsonify(Response='Error updating poster')

            return jsonify(Response=True)
        else:
            return jsonify(Response='Error')
    except Exception as e:
        print(e);
        return jsonify(Response='Error with server')

# Remove concert
@app.route("/removeConcert", methods=['GET', 'POST'])
def removeConcert():
    try:
        data = request.get_json()
        print(data['target'])
        concert = Concert.query.filter_by(id=data['target']).first();
        if concert == None:
            print('Concert not found')
            return jsonify(Response='No concert found')
        else:
            Concert.query.filter_by(id=data['target']).delete()
            db.session.commit()
            print('Concert successfully removed')

            # Remove poster if it exists
            for file in os.listdir(f"mysite/static/Posters"):
                if file == f"{data['target']}.jpg":
                    os.remove(f"mysite/static/Posters/{data['target']}.jpg")

            # Remove concert image folder
            shutil.rmtree(f"mysite/static/{data['target']}", ignore_errors=True)

            return jsonify(Response='Success')

    except Exception as e:
        print(e)
        return jsonify(Response='Error removing concert')

# Get concert list for the navbar
@app.route("/getConcertList", methods=['GET'])
def getConcertList():
    try:
        allConcerts = Concert.query.all()
        reversed = allConcerts[::-1]
        res = []
        for c in reversed:
            temp = [c.id, c.shortTitle, c.title]
            res.append(temp)
        return jsonify(Response=res)
    except:
        return jsonify(Response='Error with server')

# Given a concert id, get the concert data
@app.route("/getConcert", methods=['GET', 'POST'])
def getconcert():
    try:
        data = request.get_json()
        concert = Concert.query.filter_by(id=data['concertID']).first();
        img_names = []

        # for file in os.listdir(concert.shortTitle):
        #     with open(os.path.join(concert.shortTitle, file), 'rb') as f:
        #         base64_file = base64.b64encode(f.read())
        #         img_base64.append(base64_file.decode())
                #img_base64.append(f.read().decode())

        # print(img_base64)

        for file in os.listdir(f"mysite/static/{data['concertID']}"):
            img_names.append(f"{data['concertID']}/{file}")

        response = [['title', concert.title], ['time', concert.time], ['location', concert.location], ['content', concert.content], ['images', img_names], ['shortTitle', concert.shortTitle]]
        return jsonify(Response=response)
    except Exception as e:
        print(e)
        return jsonify(Response='Error with server')

# Hosting images
@app.route("/mysite/static/<concertID>/<filename>", methods=['GET'])
def display_image(concertID, filename):
    #return redirect(url_for('static', filename=f"{concertTitle}/{filename}"))
    #return f"static/{concertTitle}/{filename}"
    return send_from_directory('mysite/static', f"{concertID}/{filename}")

# Get all concerts in the format: [[concert id, concert name], [concert id, concert name]]
@app.route("/getConcertOfType", methods=['GET', 'POST'])
def getConcertOfType():
    try:
        sydneyContainer = []
        masterclassContainer = []
        studentContainer = []
        otherContainer = []

        allConcerts = Concert.query.all()
        reversed = allConcerts[::-1]
        for c in reversed:
            match c.tag:
                case 'Sydney Opera House':
                    sydneyContainer.append([c.id, c.shortTitle])
                case 'Masterclass Workshops':
                    masterclassContainer.append([c.id, c.shortTitle])
                case 'Student Recitals':
                    studentContainer.append([c.id, c.shortTitle])
                case 'Other':
                    otherContainer.append([c.id, c.shortTitle])
        container = [sydneyContainer, masterclassContainer, studentContainer, otherContainer]
        return jsonify(Response=container)
    except Exception as e:
        print(e)
        return jsonify(Response='Error with server')

if __name__ == "__main__":
    app.run(debug=True, port=8534)