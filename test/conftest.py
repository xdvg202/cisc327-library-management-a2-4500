import os
import sys
import pytest
import sqlite3

# Ensure project root on sys.path so `services` can be imported from /test
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure tests run against the project-local SQLite file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'library.db')


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the SQLite DB before each test to ensure isolation."""
    # Drop and recreate tables to provide a clean slate for each test
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS borrow_records')
    cur.execute('DROP TABLE IF EXISTS books')

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
        '''
    )

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patron_id TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
        '''
    )

    conn.commit()
    conn.close()

    yield


