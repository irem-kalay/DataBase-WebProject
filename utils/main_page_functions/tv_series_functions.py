from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)

def get_tv_series(search_query='', order='ASC'):
    try:
        cursor = mysql.connection.cursor()
        query = """
SELECT 
    tb.tconst, tb.title, tb.startYear, tb.endYear,
    ta.title AS akaTitle, ta.country, 
    tr.averageRating, tr.numVotes
FROM 
    title_basics tb
LEFT JOIN 
    title_akas ta ON tb.tconst = ta.tconst
LEFT JOIN 
    title_rating tr ON tb.tconst = tr.tconst
WHERE 
    tb.titleType = 'tv_series'
"""

        # Arama sorgusu varsa, ekleyelim
        if search_query:
            query += " AND LOWER(tb.title) LIKE %s"
            search_query = f"%{search_query.lower()}%"  # LIKE için %

        # Rating'e göre sıralama
        query += f" ORDER BY tr.averageRating {order}"

        cursor.execute(query, (search_query,) if search_query else ())
        data = cursor.fetchall()
        cursor.close()
        return data  # Return raw data
    except Exception as e:
        print(f"Error fetching TV series: {e}")
        return None


def get_tv_series2():
    try:
        cursor = mysql.connection.cursor()
        query = """
SELECT 
    tb.tconst, tb.title, tb.startYear, 
    ta.title AS akaTitle, ta.country, 
    tr.averageRating, tr.numVotes
FROM 
    title_basics tb
LEFT JOIN 
    title_akas ta ON tb.tconst = ta.tconst
LEFT JOIN 
    title_rating tr ON tb.tconst = tr.tconst
WHERE 
    tb.titleType = 'tv_series' 
    AND tb.startYear = '2022'
ORDER BY 
    tr.averageRating DESC;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data  # Return sorted data based on rating
    except Exception as e:
        print(f"Error fetching TV series: {e}")
        return None

def delete_tv_series(tconst):
    try:
        cursor = mysql.connection.cursor()

        #title_rating ve title_akas tablo relation siliniyo
        query_rating = "DELETE FROM title_rating WHERE tconst = %s"
        cursor.execute(query_rating, (tconst,))
        mysql.connection.commit()

        query_akas = "DELETE FROM title_akas WHERE tconst = %s"
        cursor.execute(query_akas, (tconst,))
        mysql.connection.commit()

        #title_basics tablosundan tv_series siliniyor
        query_basics = "DELETE FROM title_basics WHERE tconst = %s"
        cursor.execute(query_basics, (tconst,))
        mysql.connection.commit()

        cursor.close()
        return True  

    except Exception as e:
        print(f"Error deleting TV series: {e}")
        return False  #silinemezse false

def get_best_year_series(year=None):
    if not year:
        return None  # Eğer yıl verilmemişse, None döner

    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT 
            tb.tconst, tb.title, tb.startYear, tb.endYear,
            ta.title AS akaTitle, ta.country, 
            tr.averageRating, tr.numVotes
        FROM 
            title_basics tb
        LEFT JOIN 
            title_akas ta ON tb.tconst = ta.tconst
        LEFT JOIN 
            title_rating tr ON tb.tconst = tr.tconst
        WHERE 
            tb.titleType = 'tv_series' AND tb.startYear = %s
        ORDER BY tr.averageRating DESC
        LIMIT 10
        """

        cursor.execute(query, (year,))
        data = cursor.fetchall()
        cursor.close()
        return data
    except Exception as e:
        print(f"Error fetching best TV series for the year {year}: {e}")
        return None

