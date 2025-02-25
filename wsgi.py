import click
import csv
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from tabulate import tabulate
from App import db, User, Pokemon, UserPokemon
from App import app, initialize_db

@app.cli.command("init", help="Creates and initializes the database")
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
    print("Database Initialized!")
  
@app.cli.command('create-user', help= 'adds user to the database')
@click.argument('username', default='rick')
@click.argument('email', default='rick@mail.com')
@click.argument('password', default='rickpass')
def create_User(username,email,password):
  newuser = User(username, email, password)
  try:
    
    db.session.add(newuser)
    db.session.commit()
  except IntegrityError as e:
    db.session.rollback()
    print("Username or email already taken!")

  print(f"User {username} created with ID {newuser.id}")



@app.cli.command('get-user', help= 'getsuser from database')
@click.argument('username', default='rick')
def get_user(username):
  user=User.query.filter_by(username=username).first()
  if not user:
     print(f"{username} not found")
     return
  print(user.username)

@app.cli.command("get-poks", help = "returns all the pokemons")
def get_poks():
  pok = Pokemon.query.all()
  pok_list = [pokemon.get_json() for pokemon in pok]
  print(pok_list)
  return pok

@app.cli.command("catch-pok", help = "lets the user catch there pokemons")
@click.argument('pokemonid', default=1)
@click.argument('name', default='rickyon')
def catch_pok(name, pokemonid):
  rick = getuser('henry')
  if not rick:
     print("does not exit")
     return
  rick.catch_pokemon(pokemonid,name)# type: ignore
  testing=UserPokemon.query.filter_by(userid=rick.id,pokemon_id=pokemonid).first()
  print(testing.name)# type: ignore

@app.cli.command("get-mypoks")
@click.argument('username', default='henry')
def get_my_poks(username):
  user=User.query.filter_by(username=username).first()
  mypoks = UserPokemon.query.filter_by(userid=user.id).all()# type: ignore
  pok_list = [pok.get_json() for pok in mypoks]
  print(pok_list)

 
@app.cli.command("get-users", help = "return all users")
def get_users():
  users = User.query.all()
  for user in users:
     print(user.id,user.username)
 

def getuser(username):
  user=User.query.filter_by(username=username).first()
  return user