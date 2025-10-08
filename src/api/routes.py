"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }
    return jsonify(response_body), 200


@api.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        body = request.get_json()
        
        # Validate required fields
        if not body.get('email') or not body.get('password'):
            return jsonify({"msg": "Email and password are required"}), 400
        
        # Check if user already exists
        user_exists = User.query.filter_by(email=body['email']).first()
        if user_exists:
            return jsonify({"msg": "User already exists"}), 400
        
        # Create new user
        new_user = User(
            email=body['email'],
            is_active=True
        )
        new_user.set_password(body['password'])
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "msg": "User created successfully",
            "user": new_user.serialize()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error creating user", "error": str(e)}), 500


@api.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        body = request.get_json()
        
        # Validate required fields
        if not body.get('email') or not body.get('password'):
            return jsonify({"msg": "Email and password are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=body['email']).first()
        
        # Validate user exists and password is correct
        if not user or not user.check_password(body['password']):
            return jsonify({"msg": "Invalid email or password"}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "token": access_token,
            "user": user.serialize()
        }), 200
        
    except Exception as e:
        return jsonify({"msg": "Error logging in", "error": str(e)}), 500


@api.route('/token/validate', methods=['GET'])
@jwt_required()
def validate_token():
    """Validate if the JWT token is valid and return current user"""
    try:
        # Get user id from token
        current_user_id = get_jwt_identity()
        
        # Find user in database
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        return jsonify({
            "valid": True,
            "user": user.serialize()
        }), 200
        
    except Exception as e:
        return jsonify({"msg": "Invalid token", "error": str(e)}), 401


@api.route('/private', methods=['GET'])
@jwt_required()
def private():
    """Protected endpoint - requires valid JWT token"""
    try:
        # Get user id from token
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return jsonify({
            "msg": "Welcome to the private area!",
            "user": user.serialize()
        }), 200
        
    except Exception as e:
        return jsonify({"msg": "Error accessing private area", "error": str(e)}), 500
