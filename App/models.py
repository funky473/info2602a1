from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class UserPokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
  name = db.Column(db.String(255), nullable=False)

  #user = db.relationship("User", back_populates="pokemons")
  #pokemon = db.relationship("Pokemon", back_populates="owners")
  pass

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255),nullable = False,unique=True)
  email = db.Column(db.String(255),nullable = False,unique=True)
  password = db.Column(db.String(255),nullable = False,unique=True)

  #pokemons = db.relationship("UserPokemon", back_populates="user", cascade="all, delete-orphan")
  
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
  pass

class Pokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False,unique=True)
  attack = db.Column(db.Integer, nullable=False)
  defense = db.Column(db.Integer, nullable=False)
  hp = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Float, nullable=True)
  sp_attack = db.Column(db.Integer, nullable=False)
  sp_defense = db.Column(db.Integer, nullable=False)
  speed = db.Column(db.Integer, nullable=False)
  type1 = db.Column(db.String(255), nullable=False)
  type2 = db.Column(db.String(255), nullable=False)

  #Trainers = db.relationship("UserPokemon", back_populates="pokemon", cascade="all, delete-orphan")
  pass
