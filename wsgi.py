import click
import csv
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
              name=row['name'],
              attack=int(row['attack']),
              defense=int(row['defense']),
              hp=int(row['hp']),
              height=float(row['height_m']) if row['height_m'].isdigit() else 0,
              sp_attack=int(row['sp_attack']),
              sp_defense=int(row['sp_defense']),
              speed=int(row['speed']),
              type1=row['type1'],
              type2=row['type2']
                )
            db.session.add(new_pokemon)
    db.session.commit()
    print("Database Initialized!")
  