"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user/<int:user_id>', methods=['GET'])
def handle_hello(user_id):
    # Getting all users
    users = User.query.all() #Retrieve all users
    single_user = User.query.get(user_id) # Retrieve single user
    filter_users = User.query.filter_by(is_active = True)
    # print(type(filter_users))
    # print(filter_users)
    filter_users_serialized = list(map(lambda x : x.serialize(), filter_users))
    print(filter_users_serialized)

    
    # Return single-user to front-end
    if single_user is None:
        #return jsonify({"msg": f"User with ID {user_id} not found."}), 400
        #APIException also returns msg and bad request code
        raise APIException(f"User with ID {user_id} not found.", status_code=400) 

    #print(single_user)
    users_serialized = list(map(lambda x : x.serialize(), users))
    #print(users_serialized)
    #print(users)
    # Pass user id as parameter and show it in message
    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "users": users_serialized,
        "user_id": user_id,
        "user_info": single_user.serialize() #serialize user info as json format
    }

    return jsonify(response_body), 200

# ADDING NEW USERS WITH POST MEHTOD
@app.route('/user', methods=['POST'])
def post_user():
    body = request.get_json(silent = True)
    if body is None:
        raise APIException("Must give user's information (in body)", status_code=400)
    if "email" not in body:
        raise APIException("Email address is rquired", status_code=400)
    if "password" not in body:
        raise APIException("Must set a password", status_code=400)
    new_user = User(email = body['email'], password = body['password'], is_active = True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Completed", "new_user_info": new_user.serialize()})
    
    
        



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
