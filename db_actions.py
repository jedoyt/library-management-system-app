import sqlite3, csv
from app.db import get_db
from pprint import pprint

# conn = sqlite3.connect('instance/app_db.sqlite')
# c = conn.cursor()

# # Bulk INSERT
# with open('library_catalogue.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print(row)

#         inserted_items = c.execute(
#             "INSERT INTO book (title, author, category, ean_isbn13,"
#             " upc_isbn10, book_desc, publisher, date_published, date_added, pages)"
#             " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
#             (row['title'], row['author'], row['category'], row['ean_isbn13'], 
#              row['upc_isbn10'], row['description'], row['publisher'], row['publish_date'], row['added'], row['length'])
#         ).fetchall()

#         print(inserted_items)
#         print(f"No. of rows inserted: {len(inserted_items)}")

c = sqlite3.connect(
            'instance/app_db.sqlite',
            # detect_types=sqlite3.PARSE_DECLTYPES
        )
c.row_factory = sqlite3.Row
# Other Queries
title = ''
author = ''
category = 'Commentaries'

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

query = '''
SELECT title, author, category FROM book WHERE book.id NOT IN (SELECT book_id FROM book_log)
AND title LIKE "%" || ? || "%" 
AND author LIKE "%" || ? || "%" 
AND category LIKE "%" || ? || "%"
'''

fetched_items = c.execute(
    query, 
    (title, author, category)
    )
all_items = fetched_items.fetchall()
for item in all_items:
    pprint([i for i in item])
# print(f"No. of rows: {len(all_items)}")

# conn.commit()

# conn.close()