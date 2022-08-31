from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps 

import psycopg2
# get db config
from config import config

# set connection params
dbparams = config()
# create a new connection
conn = psycopg2.connect(**dbparams)
# create cursor
cursor = conn.cursor()



# User and token handling

# flask and SQLAlchemy setup 

app = Flask(__name__)

# set user connection params
udbparams = config(section="postgresql_usr")
# set uri for PostgreSQL
pg_uri = "postgresql://" + udbparams["user"] + ":" + udbparams["password"] + "@" + udbparams["host"] + ":5432/" + udbparams["database"]

app.config['SECRET_KEY']='Fart5inCart5'
#app.config['SQLALCHEMY_DATABASE_URI']='sqlite://///Users/edricbrown/Documents/DataSchool/Project/wine_test_db'
app.config['SQLALCHEMY_DATABASE_URI']=pg_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

adb = SQLAlchemy(app)
class users(adb.Model):
     u_id = adb.Column(adb.Integer, primary_key=True)
     public_id = adb.Column(adb.Integer)
     u_name = adb.Column(adb.String(50))
     u_password = adb.Column(adb.String(50))
     u_admin = adb.Column(adb.Boolean)

# token bit - checking token from headers

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid '})
        
        return f(current_user, *args, **kwargs)
    return decorator


# user register route 

@app.route('/register', methods=['GET', 'POST'])
def signup_user():  
    data = request.get_json()  

    hashed_password = generate_password_hash(data['password'], method='sha256')
 
    new_user = users(public_id=str(uuid.uuid4()), u_name=data['name'], u_password=hashed_password, u_admin=False) 
    adb.session.add(new_user)  
    adb.session.commit()    

    return jsonify({'message': 'registered successfully'})


# login (generate token)

@app.route('/login', methods=['GET', 'POST'])  
def login_user(): 
 
    auth = request.authorization   

    if not auth or not auth.username or not auth.password:  
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

    user = users.query.filter_by(u_name=auth.username).first()   
     
    if check_password_hash(user.u_password, auth.password):  
        token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],algorithm="HS256")  
        #return jsonify({'token' : token.decode('UTF-8')})
        return jsonify({'token' : token})

    return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})





