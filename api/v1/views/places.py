#!/usr/bin/python3
"""Python file that works with api calls on Place objects"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.user import User
from os import getenv


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
        abort(404)
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


@app_views.route('/places_search', methods=['POST'])
def search_place():
    """Handles http POST request for searching places depending on some data"""
    all_places = [p for p in storage.all('Place').values()]
    data = request.get_json()
    if data is None:
        abort(400)
    states = data.get('states')
    if states and len(states) > 0:
        all_cities = storage.all('City')
        state_cities = set([city.id for city in all_cities.values()
                            if city.state_id in states])
    else:
        state_cities = set()
    cities = data.get('cities')
    if cities and len(cities) > 0:
        cities = set([
            c_id for c_id in cities if storage.get(City, c_id)])
        state_cities = state_cities.union(cities)
    amenities = data.get('amenities')
    if len(state_cities) > 0:
        all_places = [p for p in all_places if p.city_id in state_cities]
    elif amenities is None or len(amenities) == 0:
        result = [place.to_dict() for place in all_places]
        return jsonify(result)
    places_amenities = []
    if amenities and len(amenities) > 0:
        amenities = set([
            a_id for a_id in amenities if storage.get(Amenity, a_id)])
        for p in all_places:
            p_amenities = None
            if STORAGE_TYPE == 'db' and p.amenities:
                p_amenities = [a.id for a in p.amenities]
            elif len(p.amenities) > 0:
                p_amenities = p.amenities
            if p_amenities and all([a in p_amenities for a in amenities]):
                places_amenities.append(p)
    else:
        places_amenities = all_places
    result = [place.to_dict() for place in places_amenities]
    return jsonify(result)
