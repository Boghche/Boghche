"""
Objects
=======

Object are json objects.

1. Permission
    :name: Name of the permission to display it.
    :code_name: the code for the permission.

2. Group
    :id: ID of the group in database.
    :name: Name of the group to display it.
    :permissions: List of permission object.

3. User
    :id: ID of the user in database.
    :first_name: First name of the user.
    :last_name: Last name of the user.
    :email: email of the user.


4. Access
    At login API, if the user is staffmember or admin we have such an object.

    :group: The group object which user is member of it.
    :is_admin: If the user is admin then its true.
    :is_staff: If the user is staffmember then its true.  
    

Errors
======

If a token needs to be refreshed:

:status_code: 401
:response:
    .. code-block:: json
        
        {"message": "Fresh token required"}

Invalid token:

:status_code: 422
:response:
    .. code-block:: json

        {"message": "reason"}

Expired token:

:status_code: 401
:response:
    .. code-block:: json

        {"message": "Token has expired"}

Revoked token:

:status_code: 401
:response:
    .. code-block:: json

        {"message":"Token has been revoked"}
"""


from sqlalchemy import or_
from flask import render_template, redirect, url_for, jsonify, request, make_response

from flask_restful import Api, abort, reqparse
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt, current_user,
    jwt_optional
)

from web.ext import jwt, db
from web.core.base import BaseResource

from . import mod
from .models import *


auth_api = Api(mod)

@mod.before_app_first_request
def create_permissions():
    setup_permissions()


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    auth_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class RegistrationApi(BaseResource):
    """
    :URL: ``/api/auth/register/``
    """
    endpoints = ['/register/']

    def already_exists(self):
        return {
            'message': 'A user with this email already exists.'
        }, 409

    def post(self):
        """
        :required arguments:
            * email
            * password
        :optional arguments:
            * first_name
            * last_name
        :response:
            .. code-block:: json

               {
                  "message":"Successfully registered",
                  "access_token":"access_token",
                  "refresh_token":"refresh_token"
               }

        :errors:
            if email or password does not provided:

            :status_code: 400
            :response:
                .. code-block:: json

                    {"message":"Unvalid form submitted"}

            If email already exists:

            :status_code: 409
            :response:
                .. code-block:: json

                    {"message": "A user with this email already exists."}
        """
        data = request.get_json()
        if not self.check_data(data, ['password', 'email']):
            return self.bad_request()

        password = data['password']
        email = data['email']
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if User.query.filter_by(email=email).first():
            return self.already_exists()

        u = User(password=password, email=email,
                 first_name=first_name, last_name=last_name)

        db.session.add(u)
        db.session.commit()
        access_token = create_access_token(identity=u.email)
        refresh_token = create_refresh_token(identity=u.email)
        return {
            'message':'Successfully registered',
            'access_token': access_token,
            'refresh_token': refresh_token
        }


@rest_resource
class LoginApi(BaseResource):
    """
    :URL: ``/api/auth/login/``
    """
    endpoints = ['/login/']
    def post(self):
        """
        :required arguments:
            * email
            * password
        :response:
            .. code-block:: python

               {
                  "message":"Successfully registered",
                  "access_token":"access_token",
                  "refresh_token":"refresh_token",
                  "access": AccessObject
               }

        :errors:
            if email or password does not provided:

            :status_code: 400
            :response:
                .. code-block:: json

                    {"message":"Unvalid form submitted"}

            If email or password is not correct:

            :status_code: 401
            :response:
                .. code-block:: json

                    {"message":"Username or password is not correct"}
        """
        data = request.get_json()
        if not self.check_data(data, ['email', 'password']):
            return self.bad_request()

        password = data['password']
        email = data['email']

        u = User.query.filter_by(email=email).scalar()
        if u and u.check_password(password):
            access_token = create_access_token(identity=u.email)
            refresh_token = create_refresh_token(identity=u.email)
            obj = {
                'message':'Successfully logined',
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
            access = u.access_dict()
            if access:
                obj['access'] = access
            return obj
        return {
            'message':'Username or password is not correct'
        }, 401


@rest_resource
class LogoutApi(BaseResource):
    """
    :URL: ``/api/auth/logout/``
    """
    endpoints = ['/logout/']
    method_decorators = [jwt_required]

    def post(self):
        """
        * Authorization header containing access token is required

        :status_code: 200
        :response:
            .. code-block:: json

                {
                    "message": "Access token has been revoked"
                }
        """
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        return {'message': 'Access token has been revoked'}


@rest_resource
class LogoutRefreshApi(BaseResource):
    """
    :URL: ``/api/auth/logout-refresh/``
    """
    endpoints = ['/logout-refresh/']
    method_decorators = [jwt_refresh_token_required]
    def post(self):
        """
        * Authorization header containing refresh token is required

        :status_code: 200
        :response:
            .. code-block:: json

                {
                    "message": "Refresh token has been revoked"
                }
        """
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        return {'message': 'Refresh token has been revoked'}


@rest_resource
class RefreshTokenApi(BaseResource):
    """
    :URL: ``/api/auth/refresh-token/``
    """
    endpoints = ['/refresh-token/']
    method_decorators = [jwt_refresh_token_required]
    def post(self):
        """
        * Authorization header containing refresh token is required

        :status_code: 200
        :response:
            .. code-block:: json

                {
                    "access_token": "access_token"
                }
        """
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


@rest_resource
class ProfileApi(BaseResource):
    """
    :URL: ``/api/auth/profile/``
    """
    endpoints = ['/profile/']
    method_decorators = {
        'get':[jwt_required],
        'put':[jwt_required]
    }

    def get(self):
        """
        * Authorization header containing access token is required

        :status_code: 200
        :response:
            .. code-block:: python

                {
                    "user": UserObject
                }
        """
        return {"user":current_user.dict()}

    def put(self):
        """
        * Authorization header containing refresh token is required

        :status_code: 200
        :response:
            .. code-block:: python

                {
                    "message": "Profile successfully updated"
                    "user": UserObject
                }
        """
        data = request.get_json()
        fields = {
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "email": data.get('email'),
            "password": data.get('password'),
        }
        for field in fields:
            if data.get(field):
                setattr(current_user, field, data[field])

        db.session.commit()
        return {"message":"Profile successfully updated",
                'user':current_user.dict()}