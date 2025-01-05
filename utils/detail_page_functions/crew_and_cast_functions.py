from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)

def fetch_crew_and_cast_by_nconst(nconst):
    try:
        cursor = mysql.connection.cursor()
        query = """
SELECT 
    tb.title AS movieTitle,
    nb_cast.knownName AS castName,
    tc_cast.category AS role,
    nb_writer.knownName AS writerName
FROM 
    title_crew tc
JOIN 
    title_basics tb ON tc.tconst = tb.tconst
JOIN 
    title_cast tc_cast ON tc_cast.tconst = tb.tconst
JOIN 
    name_basics nb_cast ON tc_cast.nconst = nb_cast.nconst
LEFT JOIN 
    title_crew tc_writer ON tc_writer.tconst = tb.tconst
LEFT JOIN 
    name_basics nb_writer ON tc_writer.writerNconst = nb_writer.nconst
WHERE 
    tc.directorNconst = %s
ORDER BY 
    tb.title, nb_cast.knownName;
                """
        cursor.execute(query, (nconst,))
        data = cursor.fetchall()
        print(data)
        cursor.close()
        return data  # Return raw data
    except Exception as e:
        print(f"Error fetching TV series: {e}")
        return None
