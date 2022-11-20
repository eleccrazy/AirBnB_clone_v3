#!/usr/bin/python3
"""This module initiates the api"""
from flask import Flask, make_response, jsonify
from models import storage
from api.v1.views import app_views
from os import getenv

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(app_views)


@app.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    d = error.description
    message = 'Not a Json' if d != "Missing name" else 'Missing name'
    return make_response(jsonify({'error': message}), 400)


@app.teardown_appcontext
def tear_down_db(execute):
    """Removes the current SQLAlchemy session after each request
    is completed"""
    storage.close()


if __name__ == "__main__":
    app.run(host=getenv('HBNB_API_HOST', '0.0.0.0'),
            port=getenv('HBNB_API_PORT', 5000),
            threaded=True, debug=True)
