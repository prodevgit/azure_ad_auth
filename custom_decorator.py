from functools import wraps
from flask import request
from model import User
from flask_restful import abort

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        status = False
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            abort(401,description="Token Missing")
        
        # try:
        current_user = User.query.filter_by(access_token = token).first()
        print(current_user)
        # CHECK TOKEN EXPIRY
        # if current_user:
        #     status = True
        if current_user:
            print("TOKEN MATCH")
        else:
            # return {'message':'Invalid Token'}
            abort(401,description="Invalid Token")
        
        return f(*args, **kwargs)
    return decorated