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
    ean_isbn13 TEXT,
    upc_isbn10 TEXT,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT NOT NULL,
    publisher TEXT,
    date_added DATE,
    date_added DATE,
    book_desc TEXT
);

CREATE TABLE book_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime_log TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    book_status TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (book_id) REFERENCES book (id)
);