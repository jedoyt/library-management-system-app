# from flask import request

# # Form dictionaries for adding/editing of books
# required_dict = {
#             'Title': request.form['book_title'],
#             'Category': request.form['book_category'],
#         }

# nullables_dict = {
#             'Author': request.form['book_author'],
#             'EAN_ISBN13': request.form['ean_isbn13'],
#             'UPC_ISBN10': request.form['upc_isbn10'],
#             'Book_Desc': request.form['book_desc'],
#             'Publisher': request.form['publisher'],
#             'Date_Published': request.form['date_published'],
#             'Date_Added': request.form['date_added'],
#             'Pages': request.form['pages']
#         }

# Book Categories
categories = [
        "Apologetics", "Bibles", "Biblical Theology", "Biographies", "Christian Classics", 
        "Christian Living", "Church History", "Church Ministry", "Collected Works", "Commentaries", 
        "Creeds and Confessions", "Devotionals", "Dictionaries, Concordance, etc.", "IX 9 Marks Series", 
        "Liturgy Worship", "New Testament Studies", "Old Testament Studies", "Pastoral Ministry", 
        "Puritan Works", "Study Bibles", "Systematic Theology", "The 5 Solas Series", "Theology",
        "Uncategorized"
    ]

# Color theme dictionary for status badges on book logs
badge = {
        'Available': 'success',
        'Borrowed': 'warning',
        'Returned': 'info',
        'Damaged': 'secondary',
        'Lost': 'dark',
        'Unavailable': 'light'
    }