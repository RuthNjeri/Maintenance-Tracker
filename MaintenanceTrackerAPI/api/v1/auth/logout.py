import datetime

from flask_jwt_extended import jwt_required, get_raw_jwt, current_user
from flask_restplus import Resource
from flask_restplus.namespace import Namespace

from MaintenanceTrackerAPI.api.v1.boilerplate import generate_auth_output
from MaintenanceTrackerAPI.api.v1.database import Database

auth_ns = Namespace('auth')
db = Database()


class Logout(Resource):
    @jwt_required
    @auth_ns.response(200, 'user logged out successfully')
    @auth_ns.response(400, 'bad request')
    @auth_ns.response(401, 'error with token')
    def post(self):
        """
        User Logout

        Makes use of Flask-JWT-Extended

        The token in the headers is revoked by being added to the tokens
        blacklist table

        """
        jti = get_raw_jwt()['jti']
        expires = datetime.datetime.utcfromtimestamp(get_raw_jwt()['exp'])
        sql = 'insert into tokens(jti, expires) values (%s, %s)'
        data = (jti, expires)
        db.cur = db.conn.cursor()
        db.cur.execute(sql, data)
        db.conn.commit()
        output = generate_auth_output(self, current_user)
        response = self.api.make_response(output, 200)
        return response
