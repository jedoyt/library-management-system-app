import sqlite3, csv
from app.db import get_db

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
query = """
SELECT book_id FROM book_log;
"""

fetched_items = c.execute(query)
all_items = fetched_items.fetchall()
for item in all_items:
    print(item['book_id'])
# print(f"No. of rows: {len(all_items)}")

# conn.commit()

# conn.close()