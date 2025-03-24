#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
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
def home():
    return ''

# Route handlers


@app.route('/scientists', methods=['GET'])
def get_scientists():
    scientists = Scientist.query.all()
    return jsonify([{
        "id": scientist.id,
        "name": scientist.name,
        "field_of_study": scientist.field_of_study
    } for scientist in scientists])


@app.route('/scientists/<int:id>', methods=['GET'])
def get_scientist(id):
    scientist = Scientist.query.get(id)
    if scientist:
        return jsonify(scientist.to_dict())
    else:
        return jsonify({"error": "Scientist not found"}), 404


@app.route('/scientists', methods=['POST'])
def create_scientist():
    data = request.get_json()

    try:
        new_scientist = Scientist(
            name=data.get('name'),
            field_of_study=data.get('field_of_study')
        )
        db.session.add(new_scientist)
        db.session.commit()

        # Return the created scientist
        return jsonify(new_scientist.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        # Return exactly the error format expected by the test
        return jsonify({"errors": ["validation errors"]}), 400


@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):
    scientist = Scientist.query.get(id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    data = request.get_json()

    try:
        # Update only the fields that are provided
        if 'name' in data:
            scientist.name = data['name']
        if 'field_of_study' in data:
            scientist.field_of_study = data['field_of_study']

        db.session.commit()

        # Return the updated scientist with 202 status
        return jsonify(scientist.to_dict()), 202
    except Exception as e:
        db.session.rollback()
        # Return exactly the error format expected by the test
        return jsonify({"errors": ["validation errors"]}), 400


@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_scientist(id):
    scientist = Scientist.query.get(id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    try:
        # The cascade delete should handle deleting associated missions
        db.session.delete(scientist)
        db.session.commit()

        # Return an empty JSON response with 204 No Content
        # Make sure to use jsonify for the empty response
        return jsonify({}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/missions', methods=['POST'])
def create_mission():
    data = request.get_json()

    try:
        new_mission = Mission(
            name=data.get('name'),
            scientist_id=data.get('scientist_id'),
            planet_id=data.get('planet_id')
        )
        db.session.add(new_mission)
        db.session.commit()

        # Return the created mission with related scientist and planet
        return jsonify(new_mission.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        # Return exactly the error format expected by the test
        return jsonify({"errors": ["validation errors"]}), 400


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    # Return only the specified fields without nested data
    return jsonify([{
        "id": planet.id,
        "name": planet.name,
        "distance_from_earth": planet.distance_from_earth,
        "nearest_star": planet.nearest_star
    } for planet in planets])


if __name__ == '__main__':
    app.run(port=5555, debug=True)
