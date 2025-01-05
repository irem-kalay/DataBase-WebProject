from flask import Flask, redirect, jsonify, url_for, request, render_template, Blueprint
from config import *
from utils.main_page_functions.actors_functions import *

# Create the Blueprint
actors_bp = Blueprint('actors', __name__)
# app.route demek yerine blueprint_name.bp olcak artik

# blueprint kullanimi:
# @blueprint_name.route('/route_name', methods=['POST or GET'])
# def fonksiyon():