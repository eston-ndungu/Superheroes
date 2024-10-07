#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def heroes():

    heroes = []  
    for hero in Hero.query.all():
        hero_dict = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
        }
        heroes.append(hero_dict)  

    response = make_response(
        jsonify(heroes),
        200
    )
    return response

@app.route('/heroes/<int:id>')
def hero_by_id(id):
    hero = Hero.query.filter(Hero.id == id).first()

    if hero is None:
        response = make_response(
        jsonify({"error": "Hero not found"}),
            404
        )
        return response

    hero_dict = hero.to_dict()

    response = make_response(
        hero_dict,
        200
    )
    return response

@app.route('/powers')
def powers():

    powers = []
    for power in Power.query.all():
        power_dict = {
            "description": power.description,
            "id": power.id,
            "name": power.name,
        }
        powers.append(power_dict)

        response = make_response(
            jsonify(powers),
            200
        )

    return response

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_by_id(id):
    power = Power.query.filter(Power.id == id).first()
    
    # Power does not exist
    if power is None:
        response_body = {
            "error": "Power not found"
        }
        return make_response(response_body, 404)

    if request.method == 'GET':
        power_dict = {
            "description": power.description,
            "id": power.id,
            "name": power.name,
        }
        return make_response(power_dict, 200)

    elif request.method == 'PATCH':
        data = request.get_json()

        # Check if description is in the request data
        if 'description' not in data:
            response_body = {
                "errors": ["description is required"]
            }
            return make_response(response_body, 400)

        description = data['description']
        
        # Validate the description
        if not isinstance(description, str) or len(description) < 20:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

        # Update the description 
        power.description = description
        db.session.commit()

        power_dict = {
            "description": power.description,
            "id": power.id,
            "name": power.name,
        }
        return make_response(power_dict, 200)
    

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Validate the  new data
    if 'strength' not in data or 'power_id' not in data or 'hero_id' not in data:
        return make_response({"errors": ["strength, power_id, and hero_id are required"]}, 400)

    strength = data['strength']
    power_id = data['power_id']
    hero_id = data['hero_id']

    # Check if the Power and Hero exist
    power = Power.query.filter(Power.id == power_id).first()
    hero = Hero.query.filter(Hero.id == hero_id).first()

    if not power or not hero:
        return make_response({"errors": ["Power or Hero not found"]}, 404)

    # Validate strength value
    valid_strengths = {"Average", "Strong", "Weak"}
    if strength not in valid_strengths:
        return make_response({"errors": ["validation errors"]}, 400)

    # Create the new HeroPower instance
    new_hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)

    # Add to the session and commit
    db.session.add(new_hero_power)
    db.session.commit()

    # response data
    response_data = {
        "id": new_hero_power.id,
        "hero_id": hero_id,
        "power_id": power_id,
        "strength": strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }

    return make_response(response_data, 200)


    



if __name__ == '__main__':
    app.run(port=5555, debug=True)
