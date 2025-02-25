from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255),nullable = False,unique=True)
  email = db.Column(db.String(255),nullable = False,unique=True)
  password = db.Column(db.String(255),nullable = False,unique=True)
  pokemons = db.relationship('UserPokemon',  backref=db.backref('User', lazy='joined')) 
  
  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.set_password(password)

  def set_password(self, password):
    """Create hashed password."""
    self.password = generate_password_hash(password, method='scrypt')

  def check_password(self, password):
    """Check hashed password."""
    return check_password_hash(self.password, password)
  
  def catch_pokemon(self,pokemonid,Name):
   newuser = UserPokemon(userid=self.id,pokemon_id=pokemonid,name=Name)# type: ignore
   db.session.add(newuser)
   db.session.commit()

  def release_pokemon(self,pokemonid,Name):
   finder = UserPokemon.query.filter_by(userid=self.id,pokemon_id=pokemonid,name=Name).first()
   if finder:
    db.session.delete(finder)
    db.session.commit()
   else:
     print('could not be found in database')

  def rename_pokemon(self,pokemonid,Name):
   finder = UserPokemon.query.filter_by(userid=self.id,pokemon_id=pokemonid).first()
   if finder:
     finder.name=Name
     db.session.commit()
     print("pokemon name changed")
   pass  

class UserPokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=True)
  name = db.Column(db.String(255), nullable=True)

  def get_json(self):
        pok = Pokemon.query.filter_by(id=self.pokemon_id).first()
        species=pok.name# type: ignore
        return {
            "id": self.id,
            "species": species,
            "name": self.name,
        }
  pass

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    sp_attack = db.Column(db.Integer, nullable=False)
    sp_defense = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    type1 = db.Column(db.String(255), nullable=False)
    type2 = db.Column(db.String(255), nullable=False)
    users = db.relationship('UserPokemon', backref=db.backref('Pokemon', lazy='joined')) 
    def get_json(self):
        return {
            "pokemon_id": self.id,
            "name": self.name,
            "attack": self.attack,
            "defense": self.defense,
            "hp": self.hp,
            "height": self.height,
            "sp_attack": self.sp_attack,
            "sp_defense": self.sp_defense,
            "speed": self.speed,
            "type1": self.type1,
            "type2": self.type2,
            "weight": self.weight
        }
pass
