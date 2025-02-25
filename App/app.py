import os, csv
from flask import Flask, json, jsonify, request
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from .models import db, User, UserPokemon, Pokemon

# Configure Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
# app.config['JWT_HEADER_TYPE'] = ""
app.config['JWT_HEADER_NAME'] = "Cookie"


# Initialize App 
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)

# Initializer Function to be used in both init command and /init route
def initialize_db():
  db.drop_all()
  db.create_all()

# ********** Routes **************
@app.route('/')
def index():
  return '<h1>Poke API v1.0</h1>'

@app.route('/init',methods=['GET'])
def initialize():
  initialize_db()
  db.drop_all()
  db.create_all()
  with open('pokemon.csv') as file:
      reader = csv.DictReader(file)
      for row in reader:
            
          new_pokemon = Pokemon(
            name=row['name'], # type: ignore
            attack=int(row['attack']),# type: ignore
            defense=int(row['defense']),# type: ignore
            hp=int(row['hp']),# type: ignore
            height=float(row['height_m']) if row['height_m'] and row['height_m'].replace('.', '', 1).isdigit() else 0,# type: ignore
            weight=float(row['weight_kg']) if row['weight_kg'] and row['weight_kg'].replace('.', '', 1).isdigit() else 0,# type: ignore
            sp_attack=int(row['sp_attack']),# type: ignore
            sp_defense=int(row['sp_defense']),# type: ignore
            speed=int(row['speed']),# type: ignore
            type1=row['type1'],# type: ignore
            type2=row['type2']# type: ignore
               )
          db.session.add(new_pokemon)
  db.session.commit()
  return jsonify(message= "Database Initialized!"), 200
   
@app.route('/pokemon',methods=['GET'])
def list_pokemon():
    pok = Pokemon.query.all()
    pok_list = [pokemon.get_json() for pokemon in pok]
    return jsonify(pok_list), 200

@app.route('/signup', methods=['POST'])
def signup_user_view():
  data = request.json
  try:
    new_user = User(data['username'], data['email'], data['password']) # type: ignore
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message=f'{new_user.username} created'), 201
  except IntegrityError:
    db.session.rollback()
    return jsonify(error='username or email already exists'), 400
  

def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=username)
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response
  return jsonify(error='bad username/password given'), 401

@app.route('/login', methods=['POST'])
def user_login_view():
  data = request.json
  response = login_user(data['username'], data['password'])# type: ignore
  if not response:
    return jsonify(error='bad username/password given'), 403
  return response


@app.route('/mypokemon',methods=['POST'])
@jwt_required()
def save_pokemon():
    username= get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    data = request.json
    name = data['name']# type: ignore
    pokemonid=data['pokemon_id']# type: ignore
    poky=Pokemon.query.filter_by(id=pokemonid)
    if not poky:
       return jsonify(error =f'Id {pokemonid} is not a valid pokemon id'), 400
    user.catch_pokemon(pokemonid,name)# type: ignore
    testing=UserPokemon.query.filter_by(userid=user.id,pokemon_id=pokemonid).first()# type: ignore
    return jsonify(message=f'{name} captured with id: {testing.id}'), 201# type: ignore

@app.route('/mypokemon',methods=['GET'])
@jwt_required()
def get_mypokemon():
    username= get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    mypoks = UserPokemon.query.filter_by(userid=user.id).all()# type: ignore
    pok_list = [pok.get_json() for pok in mypoks]
    return jsonify(pok_list), 201

@app.route('//mypokemon/<int:id>', methods=['PUT'])
@jwt_required()
def update_pokemon(id):
  data = request.json
  username= get_jwt_identity()
  user = User.query.filter_by(username=username).first()  
  mypok = UserPokemon.query.filter_by(id=id,userid=user.id).first()# type: ignore
  if not mypok:
      return jsonify(error =f'Id {id} is invalid or does not belong to {username}'), 401
  oldname = mypok.name
  mypok.name=data['name']# type: ignore
  db.session.commit()
  return jsonify(f'{oldname} renamed to {mypok.name}' ), 201

@app.route('//mypokemon/<int:id>', methods=['DELETE'])
@jwt_required()
def del_pokemon(id):
  username= get_jwt_identity()
  user = User.query.filter_by(username=username).first()  
  mypok = UserPokemon.query.filter_by(id=id,userid=user.id).first()# type: ignore
  if not mypok:
      return jsonify(error =f'Id {id} is invalid or does not belong to {username}'), 401
  oldname = mypok.name
  db.session.delete(mypok)
  db.session.commit()
  return jsonify(f'{oldname} released' ), 200

@app.route('//mypokemon/<int:id>', methods=['GET'])
@jwt_required()
def get_pokemon(id):
  username= get_jwt_identity()
  user = User.query.filter_by(username=username).first()  
  mypok = UserPokemon.query.filter_by(id=id,userid=user.id).first()# type: ignore
  if not mypok:
      return jsonify(error =f'Id {id} is invalid or does not belong to {username}'), 401
  return jsonify(mypok.get_json()), 201


@app.route('/identify')
@jwt_required()
def identify_view():
  username = get_jwt_identity()
  user = User.query.filter_by(username=username).first()
  if user:
    return jsonify(user.get_json())
  return jsonify(message='Invalid user'), 403

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)


