from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({"message":"welcome to PROFIT_EMPIRE auto trader"})
