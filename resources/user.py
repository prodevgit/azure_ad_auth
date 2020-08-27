from flask import jsonify, request , session, url_for, redirect
from flask_restful import Resource
from model import db, User, UserSchema
import uuid
import msal
import app_config
from flask.blueprints import Blueprint
from functools import wraps
# from custom_decorator import token_required
import json
import datetime

users_schema = UserSchema(many=True)
user_schema = UserSchema()

# AUTH DECORATOR
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = _get_token_from_cache(app_config.SCOPE)
        status = False
        if not token:
            return redirect(url_for("api.login"))        
        return f(*args, **kwargs)
    return decorated


#LOGINs
class Login(Resource):
    def get(self):
        session["state"] = str(uuid.uuid4())
        auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
        return {"status":"success", "data":auth_url}, 200
    
class Logout(Resource):
    def get(self):
        current_user = User.query.filter_by(email = session["user"]['preferred_username']).first()
        current_user.access_token = None
        current_user.refresh_token = None
        db.session.commit()
        session.clear()
          # Wipe out user and its token cache from session
        return redirect(  # Also logout from your tenant's web session
            app_config.AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("api.home", _external=True))

#EXECUTE AFTER AUTHORIZING
class Authorized(Resource):
    def get(self):
        if request.args.get('state') != session.get("state"):
            print("FAIL")
            return redirect(url_for("api.home"))  # No-OP. Goes back to Index page
        if "error" in request.args:  # Authentication/Authorization failure
            return {"status":"error", "result":request.args}
        if request.args.get('code'):
            cache = _load_cache()
            result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
                request.args['code'],
                scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
                redirect_uri=url_for("api.authorized", _external=True))
            id_token = result['id_token_claims']
            current_user = User.query.filter_by(email = id_token['preferred_username']).first()
            if current_user:
                currentuser.last_login = datetime.timestamp(datetime.now())
                current_user.access_token = result['access_token']
                current_user.refresh_token = result['access_token']
                current_user.id_token = result['access_token']
            else:
                current_user = User(id_token['name'],id_token['preferred_username'],result['access_token'],result['refresh_token'],result['id_token'])
                db.session.add(current_user)
            db.session.commit()
            if "error" in result:
                return {"status":"error_result", "result":result}
            session["user"] = result.get("id_token_claims")
            _save_cache(cache)
        print("ABC")
        data = {'message':'success','data':{'token':result['access_token']}}
        return redirect(url_for("api.home",data=data))

#GO TO THIS PAGE AFTER LOGIN
class Home(Resource):
    def get(self):
        #Access Token
        return request.args.get('data')

#GET USEREMAIL FROM API
class UserEmail(Resource):
    method_decorators = [token_required]
    def get(self):
        token = _get_token_from_cache(app_config.SCOPE)
        current_user = User.query.filter_by(email=session['user']['preferred_username']).first()
        return {'email':current_user.email}

#MSAI FUNCTIONS
def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_url(authority=None, scopes=None, state=None):
    print("URL")
    print(url_for("api.authorized", _external=True))
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("api.authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])   #Automatically acquire or refreshes token
        _save_cache(cache)
        return result