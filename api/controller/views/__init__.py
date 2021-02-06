#!/usr/bin/python3

from flask import Blueprint

controller = Blueprint('controller', __name__, url_prefix='/api/')

from api.controller.views.register import *
from api.controller.views.login import *
from api.controller.views.auth_required import *
