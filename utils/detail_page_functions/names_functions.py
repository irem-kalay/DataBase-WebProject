from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py
import random

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)


def fetch_names_by_nconst(nconst):
    try:
        cursor = mysql.connection.cursor()
        
        # Fetch the name details (original and known name)
        query_name = """
        SELECT originalName, knownName, birthYear, deathYear, primaryProfession, nconst 
        FROM name_basics 
        WHERE nconst = %s;
        """
        cursor.execute(query_name, (nconst,))

        
        name_data = cursor.fetchone()
        
        if not name_data:
            cursor.close()
            return None
        
        # print(name_data)
        # {'originalName': 'Samantha Cook', 'knownName': 'Bryan Carey', 'birthYear': 2009, 'deathYear': 2014, 'primaryProfession': 'actor\r'}

        # Fetch movies where the person was an actor
        query_actor = """
        SELECT tb.title, tb.startYear, tb.tconst, tr.averageRating
        FROM title_cast tc
        JOIN title_basics tb ON tc.tconst = tb.tconst
        LEFT JOIN title_rating tr ON tb.tconst = tr.tconst
        WHERE tc.nconst = %s AND tc.category = 'main_character'
        """
        cursor.execute(query_actor, (nconst,))
        actor_movies = cursor.fetchall()
        # print(actor_movies)
        # ({'title': 'Short because.', 'startYear': 1915},)

        # Fetch movies where the person was a director
        query_director = """
        SELECT tb.title, tb.startYear, tb.tconst, tr.averageRating
        FROM title_crew tc
        JOIN title_basics tb ON tc.tconst = tb.tconst
        LEFT JOIN title_rating tr ON tb.tconst = tr.tconst
        WHERE tc.directorNconst = %s
        """
        cursor.execute(query_director, (nconst,))
        director_movies = cursor.fetchall()

        # print(director_movies)
        # ({'title': 'Rate throw.', 'startYear': 1951}, {'title': 'Mouth current story should.', 'startYear': 1936})


        # Fetch movies where the person was a writer
        query_writer = """
        SELECT tb.title, tb.startYear, tb.tconst, tr.averageRating
        FROM title_crew tc
        JOIN title_basics tb ON tc.tconst = tb.tconst
        LEFT JOIN title_rating tr ON tb.tconst = tr.tconst
        WHERE tc.writerNconst = %s
        """
        cursor.execute(query_writer, (nconst,))
        writer_movies = cursor.fetchall()

        # print(writer_movies)

        #({'title': 'Back society.', 'startYear': 2015}, {'title': 'Nor offer would.', 'startYear': 1907})


        # Fetch crew and cast that worked with this person
        query_collaborators = """
        -- fetch all tconsts where the nconst appears in cast or crew
        WITH relevant_tconsts AS (
            SELECT tconst, 'cast' AS role
            FROM title_cast
            WHERE nconst = %s

            UNION

            SELECT tconst, 'director' AS role
            FROM title_crew
            WHERE directorNconst = %s

            UNION

            SELECT tconst, 'writer' AS role
            FROM title_crew
            WHERE writerNconst = %s
        )

        -- fetch everyone for all tconsts found
        SELECT *
        FROM (
            SELECT 
                tc.tconst, 
                tb.title AS titleName,
                nb.nconst, 
                tc.category AS role, 
                tc.characterName, 
                nb.originalName AS personName
            FROM title_cast tc
            JOIN name_basics nb ON tc.nconst = nb.nconst
            JOIN title_basics tb ON tc.tconst = tb.tconst
            WHERE tc.tconst IN (SELECT tconst FROM relevant_tconsts)

            UNION

            -- Fetch directors
            SELECT 
                tc.tconst, 
                tb.title AS titleName,
                nb.nconst, 
                'director' AS role, 
                NULL AS characterName, 
                nb.originalName AS personName
            FROM title_crew tc
            JOIN name_basics nb ON tc.directorNconst = nb.nconst
            JOIN title_basics tb ON tc.tconst = tb.tconst
            WHERE tc.tconst IN (SELECT tconst FROM relevant_tconsts)

            UNION

            -- Fetch writers
            SELECT 
                tc.tconst, 
                tb.title AS titleName,
                nb.nconst, 
                'writer' AS role, 
                NULL AS characterName, 
                nb.originalName AS personName
            FROM title_crew tc
            JOIN name_basics nb ON tc.writerNconst = nb.nconst
            JOIN title_basics tb ON tc.tconst = tb.tconst
            WHERE tc.tconst IN (SELECT tconst FROM relevant_tconsts)
        ) AS combined_results
        ORDER BY tconst;
        """
        cursor.execute(query_collaborators, (nconst, nconst, nconst))
        collaborators = cursor.fetchall()

        # print(collaborators)

        # ({'knownName': 'Bryan Carey', 'directorNconst': 49851, 'writerNconst': 10517, 'tconst': 2480254}, {'knownName': 'Joseph Newman', 'directorNconst': 49851, 'writerNconst': 10517, 'tconst': 2480254}, {'knownName': 'Bryan Carey', 'directorNconst': 10517, 'writerNconst': 55702, 'tconst': 3622115}, {'knownName': 'Charles Henderson', 'directorNconst': 10517, 'writerNconst': 55702, 'tconst': 3622115}, {'knownName': 'Bryan Carey', 'directorNconst': 10517, 'writerNconst': 60015, 'tconst': 5250683}, {'knownName': 'Thomas Jones', 'directorNconst': 10517, 'writerNconst': 60015, 'tconst': 5250683}, {'knownName': 'Bryan Carey', 'directorNconst': 84335, 'writerNconst': 10517, 'tconst': 7365954}, {'knownName': 'Sherry West', 'directorNconst': 84335, 'writerNconst': 10517, 'tconst': 7365954})

        # Randomly generate some other people for "People Also Search For"
        other_people_query = """
        SELECT nconst, knownName 
        FROM name_basics 
        WHERE nconst != %s 
        ORDER BY RAND() 
        LIMIT 5
        """
        cursor.execute(other_people_query, (nconst,))
        other_people = cursor.fetchall()

        # print(other_people)
        # ({'nconst': 96090, 'knownName': 'Stephen Johnson'}, {'nconst': 82907, 'knownName': 'Randy Garcia'}, {'nconst': 65963, 'knownName': 'Kerri Contreras'}, {'nconst': 88681, 'knownName': 'Shannon Carter'}, {'nconst': 48003, 'knownName': 'Brian Mora'})


        best_media_query = """
            SELECT DISTINCT title_basics.tconst, 
                            title_basics.startYear, 
                            title_rating.averageRating, 
                            title_basics.title AS originalTitle
            FROM title_basics
            JOIN title_rating ON title_basics.tconst = title_rating.tconst
            LEFT JOIN title_cast ON title_basics.tconst = title_cast.tconst
            LEFT JOIN title_crew ON title_basics.tconst = title_crew.tconst
            WHERE title_cast.nconst = %s OR title_crew.directorNconst = %s OR title_crew.writerNconst = %s
            ORDER BY title_rating.averageRating DESC
            LIMIT 4;
        """
        cursor.execute(best_media_query, (nconst, nconst, nconst))
        best_media = cursor.fetchall()


        cursor.close()

        # Prepare the result data
        # Combine all data into a single dictionary
        data = {
            "name_data": name_data,
            "best_movies": best_media,
            "actor_movies": actor_movies,
            "director_movies": director_movies,
            "writer_movies": writer_movies,
            "collaborators": collaborators,
            "other_people": other_people
        }

        print (data)
        return data

    except Exception as e:
        print(f"Error fetching name with nconst {nconst}: {e}")
        return None
    

def update_name_helper(name, knownName, birthYear, deathYear, profession, nconst):
    try:
        # Create a cursor to interact with the database
        cursor = mysql.connection.cursor()

        # Prepare the SQL query to update the row in the name_basics table
        cursor.execute("""
            UPDATE name_basics
            SET originalName = %s, knownName = %s, birthYear = %s, deathYear = %s, primaryProfession = %s
            WHERE nconst = %s
        """, (name, knownName, birthYear, deathYear, profession, nconst))

        # Commit the changes to the database
        mysql.connection.commit()

        # Return success message
        return jsonify({"success": True, "message": "Data updated successfully"})

    except Exception as e:
        # In case of an error, log it and return a failure message
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
def delete_name_helper(nconst):
    try:
        # Create a cursor to interact with the database
        cursor = mysql.connection.cursor()

        # Prepare the SQL query to update the row in the name_basics table
        cursor.execute("""
            DELETE FROM name_basics
            WHERE nconst = %s;
        """, (nconst,))

        # Commit the changes to the database
        mysql.connection.commit()
        print("commit mi sorun")
        # Return success message
        return jsonify({"success": True, "message": "Data updated successfully"})

    except Exception as e:
        # In case of an error, log it and return a failure message
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    

# OLD ONE HERE: 
# def fetch_names_by_nconst(nconst):
#     try:
#         cursor = mysql.connection.cursor()
        
#         # Query to fetch the director's known and original name based on nconst
#         query = """
#         SELECT originalName, knownName 
#         FROM name_basics 
#         WHERE nconst = %s;
#         """
        
#         cursor.execute(query, (nconst,))

#         data = cursor.fetchone()
#         cursor.close()

#         print (data)

#         # Check if result is found and return as a dictionary, else None
#         if data:
#             return data
#         else:
#             return None  # Return None if not found

#     except Exception as e:
#         print(f"Error fetching name with nconst {nconst}: {e}")
#         return None