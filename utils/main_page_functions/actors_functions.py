from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")
# Load app configuration from config.py
app.config.from_object(Config)
# Initialize MySQL connection
mysql = MySQL(app)

def get_actors():
    return

