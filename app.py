# __init__.py

from flask import Flask, config, redirect
from flask.json import jsonify
import os
from src.compute import sim
from src.findfit import fit

from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR




def create_app(test_config=None):

    app = Flask(__name__)

    app.register_blueprint(sim)
    app.register_blueprint(fit)


  
    

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app
