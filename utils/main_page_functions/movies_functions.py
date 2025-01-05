from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)

def get_movies(sort_by=None, sort_order='ASC', filter_by=None, filter_value=None):
    try:
        cursor = mysql.connection.cursor()
       
        # Base query
        query = """
                SELECT 
                    tb.tconst, 
                    tb.title, 
                    tb.startYear AS year, 
                    tr.averageRating AS rating,
                    tb.genre
                FROM 
                    title_basics tb
                LEFT JOIN 
                    title_rating tr ON tb.tconst = tr.tconst
                WHERE 
                    tb.titleType = 'movie'
                """

        # Apply filtering if filter_value is provided and valid
        if filter_value and filter_value != 'None':  # Avoid using 'None' as a string or invalid input
            if filter_by == 'tb.year':
                query += f" AND tb.startYear = {filter_value}"
            elif filter_by:  # Ensure filter_by is provided to apply the LIKE filter
                query += f" AND {filter_by} LIKE %s"
                filter_value = f"%{filter_value}%"

        # Sorting logic with sort_order
        if sort_by == 'tb.title':
            sort_clause = f"ORDER BY tb.title {sort_order}"
        elif sort_by == 'tb.year':
            sort_clause = f"ORDER BY tb.startYear {sort_order}"
        elif sort_by == 'tb.rating':
            sort_clause = f"ORDER BY tr.averageRating {sort_order}"
        else:
            sort_clause = f"ORDER BY tr.averageRating DESC"  # Default sorting by rating DESC
        
        query = query + " " + sort_clause

        # Execute query with or without filter
        if filter_value and filter_value != 'None':  # If a valid filter_value exists
            cursor.execute(query, (filter_value,))
        else:
            cursor.execute(query)

        data = cursor.fetchall()
        return data  

    except Exception as e:
        print(f"Error fetching movies: {e}")
        return None
