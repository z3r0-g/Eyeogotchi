#web/__init__.py
import os
from flask import Blueprint, render_template

ui_bp = Blueprint(
    "ui",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@ui_bp.get("/")
def index():
    return render_template("eyeogotchi.html")
