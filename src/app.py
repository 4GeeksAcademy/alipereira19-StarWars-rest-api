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
from models import Planet, db, User, People, Favorite
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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    return jsonify({"msg": "Person not found"}), 404

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"msg": "Planet not found. Try again."}), 404
    
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
      user_id = request.args.get('user_id', type=int)  
      if not user_id:
        return jsonify({"msg": "ID is required."}), 400

      favorite = Favorite.query.filter_by(user_id = user_id).all()
      return jsonify([fav.serialize() for fav in favorite]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()  
    user_id = data.get('user_id')  
    planet_id = data.get('planet_id')
    if not user_id or not planet_id:
        return jsonify({"msg": "user.id and planet.id required."}), 404
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    
    favorite = Favorite(user_id = user_id, planet_id = planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()  
    user_id = data.get('user_id')  
    people_id = data.get('people_id')
    if not people_id:
        return jsonify({"msg": "Person not found"}), 404
    
    favorite = Favorite(user_id = user_id, people_id = people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
   data = request.get_json() 
   user_id = data.get('user_id')  
   planet_id = data.get('planet_id')
   if not user_id or not planet_id:
       return jsonify({"msg": "user_id and planet_id required."}), 404
   
   favorite = Favorite.query.filter_by(user_id = user_id, planet_id = planet_id).first()
   if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404
   
   db.session.delete(favorite)
   db.session.commit()
   return jsonify({"msg": "Planet deleted"}), 200    

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
   data = request.get_json()  
   user_id = data.get('user_id')  
   people_id = data.get('people_id')
   if not user_id or not people_id:
       return jsonify({"msg": "user_id and people_id required"}), 404

   favorite = Favorite.query.filter_by(user_id = user_id, people_id = people_id).first()
   if not favorite:
       return jsonify({"msg": "Favorite not found"}), 404
   
   db.session.delete(favorite)
   db.session.commit()
   return jsonify({"msg": "Person deleted from favorites"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
