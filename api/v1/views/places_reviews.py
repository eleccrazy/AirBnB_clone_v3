#!/usr/bin/python3
"""Python file that works with api calls on Reviews objects"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.state import State
from models.city import City
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'])
def place_review_without_id(place_id=None):
    """Handles http request for reviews route with no id provided"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if request.method == 'GET':
        objs = storage.all('Place')
        obj_list = [obj.to_dict() for obj in objs.values()
                    if obj.place_id == place_id]
        return jsonify(obj_list)

    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            abort(400, "Not a Json")
        if data.get("name") is None:
            abort(400, "Missing name")
        if data.get("user_id") is None:
            abort(400, "Missing user_id")
        user = storage.get(User, data.get("user_id"))
        if user is None:
            abort(404)
        if data.get("text") is None:
            abort(400, "Missing text")
        data['place_id'] = place_id
        obj = Review(**data)
        obj.save()
        return jsonify(obj.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'])
def state_city_with_id(review_id=None):
    """Handles http request for reviews route with id"""
    obj = storage.get(Review, review_id)
    if obj is None:
        abort(404, "Not found")
    if request.method == 'GET':
        return jsonify(obj.to_dict())

    if request.method == 'DELETE':
        obj.delete()
        del obj
        return jsonify({}), 200

    if request.method == 'PUT':
        data = request.get_json()
        if data is None:
            abort(400)
        IGNORE = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
        d = {k: v for k, v in data.items() if k not in IGNORE}
        for k, v in d.items():
            setattr(obj, k, v)
        obj.save()
        return jsonify(obj.to_dict()), 200
