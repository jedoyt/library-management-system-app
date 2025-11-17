import sqlite3
import csv
from datetime import datetime
from pprint import pprint
from app.book_log import convert_current_utc_dt


# c = sqlite3.connect(
#             'instance/app_db.sqlite',
#             # detect_types=sqlite3.PARSE_DECLTYPES
#         )
# c.row_factory = sqlite3.Row

# # BULK INSERT ON book_log TABLE (INITIAL LOGS)
# for i in range(1,513):
#     # Convert from UTC to UTC+8:00
#     datetime_log = convert_current_utc_dt(delta_hour=8)
#     c.execute(
#         'INSERT INTO book_log (datetime_log, remarks, book_status, user_id, book_id)'
#         ' VALUES (?, ?, ?, ?, ?);',
#         (datetime_log, "Newly added to database", "Available", 1, i)
#         )

# # OTHER QUERIES
# title = ''
# author = ''
# category = 'Commentaries'

# query = """
# SELECT * from user;
# """

# query = '''
# SELECT * FROM book 
# WHERE title LIKE "%" || ? || "%" 
# AND author LIKE "%" || ? || "%" 
# AND category LIKE "%" || ? || "%"
# '''

# query = '''
# SELECT book_log.id, MAX(datetime_log), book_status, user_id, book_id, full_name, title, author, category 
# FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id
# WHERE title LIKE "%" || ? || "%"
# AND author LIKE "%" || ? || "%"
# AND category LIKE "%" || ? || "%"
# GROUP BY book_id
# ORDER BY MAX(datetime_log) DESC
# '''

# query = '''
# SELECT title, author, category FROM book WHERE book.id NOT IN (SELECT book_id FROM book_log)
# AND title LIKE "%" || ? || "%" 
# AND author LIKE "%" || ? || "%" 
# AND category LIKE "%" || ? || "%"
# '''

# query = '''
# SELECT MAX(book_log.id), book_status, datetime_log, book_id, title, author, category, user_id, full_name, email, contact_number
# FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id
# WHERE book_status = ?
# GROUP BY book_id
# ORDER BY MAX(book_log.id) ASC
# '''

# Set first registered user libarry_staff to True
# query = '''
# UPDATE user SET library_staff = 1 WHERE id = 1;
# '''

# fetched_items = c.execute(
#     "SELECT * from user;"
#     )
# all_items = fetched_items.fetchall()
# # print(all_items)
# for item in all_items:
#     pprint([i for i in item])

# c.commit()
# c.close()


# Bulk insertion of books from initial catalogue in csv file
def bulk_insert_books(db_path='instance/app_db.sqlite', csv_path='library_catalogue.csv'):
    c = sqlite3.connect(
            db_path,
            # detect_types=sqlite3.PARSE_DECLTYPES
        )
    c.row_factory = sqlite3.Row
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(row)
            inserted_items = c.execute(
                "INSERT INTO book (title, author, category, ean_isbn13,"
                " upc_isbn10, book_desc, publisher, date_published, date_added, pages)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (row['title'], row['author'], row['category'], row['ean_isbn13'], 
                row['upc_isbn10'], row['description'], row['publisher'], row['publish_date'], row['added'], row['length'])
            ).fetchall()

            # print(inserted_items)
            # print(f"No. of rows inserted: {len(inserted_items)}")
    c.commit()
    c.close()


# DATABASE INITIALIZATION FUNCTION
def init_database():
    """
    Initialize the database by creating tables from schema.sql
    This function creates a fresh database with all necessary tables.
    """
    db_path = 'instance/app_db.sqlite'
    
    # Connect to database
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    
    try:
        # Read and execute schema.sql
        with open('app/schema.sql', 'r') as schema_file:
            schema_script = schema_file.read()
            conn.executescript(schema_script)
        
        conn.commit()
        print(f"✓ Database initialized successfully at {db_path}")
        print("✓ Tables created: user, book, book_log")
        
    except FileNotFoundError:
        print("✗ Error: schema.sql file not found at app/schema.sql")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
    # bulk_insert_books()