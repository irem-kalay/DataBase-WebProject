from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)

def fetch_episodes_by_tconst(parentTconst):
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT te.tconst, te.seasonNumber, te.episodeNumber, tb.title AS episodeTitle
            FROM title_episode te
            JOIN title_basics tb ON te.tconst = tb.tconst
            WHERE te.parentTconst = %s
            ORDER BY te.seasonNumber, te.episodeNumber
        """
        cursor.execute(query, (parentTconst,))
        data = cursor.fetchall()
        cursor.close()

        # Transform the data into a list of dictionaries, including episode titles
        results = [
            {
                "tconst": row["tconst"],
                "seasonNumber": row["seasonNumber"] or "N/A",  # Handle NULL values
                "episodeNumber": row["episodeNumber"] or "N/A",
                "episodeTitle": row["episodeTitle"],  # Include the episode title
            }
            for row in data
        ]

        return results
    except Exception as e:
        print(f"Error fetching episodes for parentTconst {parentTconst}: {e}")
        return []
