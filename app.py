from flask import Blueprint
from flask_restful import Api
from resources.user import *
from model import User
import app_config

api_bp = Blueprint('api', __name__)
api = Api(api_bp)
# Route
api.add_resource(Login,'/auth/login')
api.add_resource(UserEmail,'/getemail')
api.add_resource(Home,'/index')
api.add_resource(Authorized,'/auth/validate')
api.add_resource(Logout,'/auth/logout')
