from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)

def get_directors(sort_by=None, filter_by=None, filter_value=None, rating=None, rating_condition=None, year=None, year_condition=None):
    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT 
            nb.originalName AS directorName,
            tb.title,
            tb.tconst,
            nb.nconst AS directorNconst,
            tr.averageRating AS rating,          -- Ratings of the title
            wb.originalName AS writerName,          -- Writer's name
            wb.nconst AS writerNconst,
            tb.startYear AS yearDirected         -- Year the title was directed
        FROM 
            title_crew tc
        LEFT JOIN 
            name_basics nb ON tc.directorNconst = nb.nconst
        LEFT JOIN 
            title_basics tb ON tc.tconst = tb.tconst
        LEFT JOIN 
            title_rating tr ON tb.tconst = tr.tconst  -- Join with title_ratings for rating
        LEFT JOIN 
            title_crew twc ON tb.tconst = twc.tconst  -- Join for writers
        LEFT JOIN 
            name_basics wb ON twc.writerNconst = wb.nconst  -- Join to get writer's name
        WHERE 1=1
        """

        params = []

        # Apply filter by the selected option
        if filter_by and filter_value:
            if filter_by in ['tb.title', 'nb.originalName', 'wb.originalName']:
                query += f" AND {filter_by} LIKE %s"
                params.append(f"%{filter_value}%")
            elif filter_by == 'tb.tconst':
                query += " AND tb.tconst = %s"
                params.append(filter_value)
            elif filter_by == 'nb.nconst':
                query += " AND nb.nconst = %s"
                params.append(filter_value)
            elif filter_by == 'wb.nconst':
                query += " AND wb.nconst = %s"
                params.append(filter_value)

        # Apply rating filter if provided
        if rating and rating_condition and rating_condition != 'none':
            if rating_condition == 'greater':
                query += " AND tr.averageRating > %s"
            elif rating_condition == 'less':
                query += " AND tr.averageRating < %s"
            else:  # default is 'equal'
                query += " AND tr.averageRating = %s"
            params.append(rating)

        # Apply year filter if provided
        if year and year_condition and year_condition != 'none':
            if year_condition == 'greater':
                query += " AND tb.startYear > %s"
            elif year_condition == 'less':
                query += " AND tb.startYear < %s"
            else:  # default is 'equal'
                query += " AND tb.startYear = %s"
            params.append(year)

        # Apply sorting if provided
        if sort_by:
            query += f" ORDER BY {sort_by}"

        # Execute the query
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()

        return data
    except Exception as e:
        print(f"Error fetching directors: {e}")
        return None
    
def delete_selected_directors(selected_directors):
    try:
        if not selected_directors:
            raise ValueError("No directors selected for deletion.")

        # Extract tconst and directorNconst from the selected values
        for director in selected_directors:
            tconst, directorNconst = director.split('|')
            delete_director(tconst, directorNconst)  # Call the delete function for each director

    except Exception as e:
        raise e

def delete_director(tconst, directorNconst):
    try:
        cursor = mysql.connection.cursor()
        query = """
        DELETE FROM title_crew WHERE tconst = %s AND directorNconst = %s;
        """
        cursor.execute(query, (tconst, directorNconst))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error deleting director {directorNconst}: {e}")
        raise e  # Reraise the exception if necessary for error handling in the route

def update_director_helper(productionTitle, directorName, writerName, yearDirected, rating, tconst, directorNconst, writerNconst):
    # Check if the required fields are present
    if not all([productionTitle, directorName, writerName, yearDirected, rating, tconst, writerNconst, writerNconst]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        cursor = mysql.connection.cursor()

        print("Fetch current directorNconst and writerNconst from title_crew") 
        cursor.execute(
            """
            SELECT directorNconst, writerNconst 
            FROM title_crew 
            WHERE tconst = %s
            """,
            (tconst,)
        )
        current_crew = cursor.fetchone()

        if not current_crew:
            return jsonify({"success": False, "message": "No such tconst found in title_crew."}), 404

        current_director_nconst = current_crew['directorNconst']
        current_writer_nconst = current_crew['writerNconst']

        print("Check if directorNconst has changed")

        directorNconst = int(directorNconst)
        writerNconst = int(writerNconst)

        if directorNconst != current_director_nconst:
            cursor.execute("SELECT nconst FROM name_basics WHERE nconst = %s", (directorNconst,))
            
            if not cursor.fetchall():
                return jsonify({"success": False, "message": "Invalid directorNconst. Add it from the main page."}), 400
            cursor.execute(
                """
                UPDATE title_crew 
                SET directorNconst = %s 
                WHERE tconst = %s
                """,
                (directorNconst, tconst)
            )
        else:
            print("# Update name_basics for director name if directorNconst hasn't changed")
            cursor.execute(
                """
                UPDATE name_basics 
                SET originalName = %s 
                WHERE nconst = %s
                """,
                (directorName, current_director_nconst)
            )

        print("Check if writerNconst has changed")
        if writerNconst != current_writer_nconst:
            cursor.execute("SELECT nconst FROM name_basics WHERE nconst = %s", (writerNconst,))
            if not cursor.fetchone():
                return jsonify({"success": False, "message": "Invalid writerNconst. Add it from the main page."}), 400
            cursor.execute(
                """
                UPDATE title_crew 
                SET writerNconst = %s 
                WHERE tconst = %s
                """,
                (writerNconst, tconst)
            )
        else:
            print("# Update name_basics for writer name if writerNconst hasn't changed")
            cursor.execute(
                """
                UPDATE name_basics 
                SET originalName = %s 
                WHERE nconst = %s
                """,
                (writerName, current_writer_nconst)
            )

        print("Update title_basics table for production title and year")
        cursor.execute(
            """
            UPDATE title_basics 
            SET title = %s, startYear = %s 
            WHERE tconst = %s
            """,
            (productionTitle, yearDirected, tconst)
        )

        # Update title_rating table for rating
        cursor.execute(
            """
            UPDATE title_rating 
            SET averageRating = %s 
            WHERE tconst = %s
            """,
            (rating, tconst)
        )



        # Commit the transaction
        mysql.connection.commit()

        # Return success message
        return jsonify({"success": True, "message": "Data updated successfully"})

    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        # Return error message
        return jsonify({'success': False, 'error': str(e)}), 500

def add_director_writer_relation_helper(tconst, director_nconst, writer_nconst):
    try:
        print("here")
        # Create a cursor for interacting with the database
        cursor = mysql.connection.cursor()

        # Insert a new row into the title_crew table (director and writer relationship)
        cursor.execute(
            """
            INSERT INTO title_crew (tconst, directorNconst, writerNconst)
            VALUES (%s, %s, %s)
            """,
            (tconst, director_nconst, writer_nconst)
        )

        # Commit the transaction
        mysql.connection.commit()

        # Return success message
        return jsonify({"success": True, "message": "Director-Writer relation added successfully"})

    except Exception as e:
        # In case of an error, return the error message
        return jsonify({'success': False, 'error': str(e)}), 500
    

# Helper function for inserting data into the name_basics table
def add_name_basics_helper(nconst, originalName, birthYear, deathYear, knownName, primaryProfession):
    try:
        print("Inserting data into name_basics")
        # Create a cursor for interacting with the database
        cursor = mysql.connection.cursor()

        if deathYear == '':
            deathYear = None
        if primaryProfession == '':
            primaryProfession = None

        print("""
            INSERT INTO name_basics (nconst, originalName, birthYear, deathYear, knownName, primaryProfession)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nconst, originalName, birthYear, deathYear, knownName, primaryProfession))
        
        # Insert a new row into the name_basics table
        cursor.execute(
            """
            INSERT INTO name_basics (nconst, originalName, birthYear, deathYear, knownName, primaryProfession)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nconst, originalName, birthYear, deathYear, knownName, primaryProfession)
        )

        # Commit the transaction
        mysql.connection.commit()

        # Return success message
        return jsonify({"success": True, "message": "Name Basics added successfully"})

    except Exception as e:
        # In case of an error, return the error message
        return jsonify({'success': False, 'error': str(e)}), 500