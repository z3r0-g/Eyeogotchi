from flask import Blueprint, jsonify

bp = Blueprint("example_api", __name__)

@bp.get("/ping")
def ping():
    return jsonify({"example": "pong"})
