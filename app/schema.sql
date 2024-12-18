DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS book_log;


CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    user_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    contact_number TEXT,
    library_staff BOOLEAN NOT NULL
);

CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT NOT NULL,
    ean_isbn13 TEXT,
    upc_isbn10 TEXT,
    book_desc TEXT,
    publisher TEXT,
    date_published DATE,
    date_added DATE,
    pages INTEGER
);

CREATE TABLE book_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime_log TIMESTAMP NOT NULL,
    remarks TEXT,
    book_status TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (book_id) REFERENCES book (id)
);