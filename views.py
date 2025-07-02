from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user, fresh_login_required
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)




