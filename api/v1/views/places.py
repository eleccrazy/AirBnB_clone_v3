#!/usr/bin/python3
"""Python file that works with api calls on Place objects"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.city import City
from models.place import Place


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'])
def city_place_without_id(city_id=None):
    """Handles http request for places route with no id provided"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if request.method == 'GET':
        objs = storage.all('Place')
        obj_list = [obj.to_dict() for obj in objs.values()
                    if obj.city_id == city_id]
        return jsonify(obj_list)

    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            abort(400, "Not a Json")
        if data.get("user_id") is None:
            abort(400, "Missing user_id")
        user = storage.get(User, data.get("user_id"))
        if user is None:
            abort(404)
        if data.get("name") is None:
            abort(400, "Missing name")
        data['city_id'] = city_id
        obj = Place(**data)
        obj.save()
        return jsonify(obj.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['GET', 'DELETE', 'PUT'])
def city_place_with_id(place_id=None):
    """Handles http request for places route with id"""
    obj = storage.get(Place, place_id)
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
        IGNORE = ['id', 'created_at', 'updated_at', 'city_id', 'user_id']
        d = {k: v for k, v in data.items() if k not in IGNORE}
        for k, v in d.items():
            setattr(obj, k, v)
        obj.save()
        return jsonify(obj.to_dict()), 200
