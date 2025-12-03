import pytest
import threading
import time
import os
import sqlite3
from app import create_app

# Get the project root directory (one level up from the test folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="session")
def test_database():
    test_db_path = os.path.join(PROJECT_ROOT, 'library_test_e2e.db')
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    import database
    original_db = database.DATABASE
    database.DATABASE = test_db_path
    
    database.init_database()
    
    yield test_db_path
    database.DATABASE = original_db
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(scope="session")
def flask_app(test_database):
    """Create the Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope="session")
def flask_server(flask_app):
    def run_server():
        flask_app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    time.sleep(2)
    yield "http://127.0.0.1:5001"


@pytest.fixture(autouse=True)
def reset_database(test_database):
    import database
    
    database.DATABASE = test_database
    
    conn = sqlite3.connect(test_database)
    cur = conn.cursor()
    cur.execute('DELETE FROM borrow_records')
    cur.execute('DELETE FROM books')
    conn.commit()
    conn.close()
    
    yield

@pytest.fixture
def page(playwright, flask_server):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    yield page
    
    context.close()
    browser.close()


def test_add_book_and_verify_in_catalog(page, flask_server):
    page.goto(f"{flask_server}/catalog")
    page.wait_for_load_state("networkidle") 
    
    assert "Book Catalog" in page.inner_text("h2")
    
    page.click("a:has-text('➕ Add New Book')")
    page.wait_for_load_state("networkidle")
    
    assert "Add New Book" in page.inner_text("h2")
    
    page.fill('input[name="title"]', "E2E Test Book")
    page.fill('input[name="author"]', "Test Author")
    page.fill('input[name="isbn"]', "1234567890123")
    page.fill('input[name="total_copies"]', "5")
    
    page.click('button:has-text("Add Book to Catalog")')
    page.wait_for_load_state("networkidle")
    
    flash_message = page.locator(".flash-success")
    assert flash_message.is_visible()
    assert "successfully" in flash_message.inner_text().lower()
    
    assert "Book Catalog" in page.inner_text("h2")
    
    assert "E2E Test Book" in page.inner_text("table")
    assert "Test Author" in page.inner_text("table")
    assert "1234567890123" in page.inner_text("table")


def test_borrow_book_and_verify_confirmation(page, flask_server):
    page.goto(f"{flask_server}/catalog")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('➕ Add New Book')")
    page.wait_for_load_state("networkidle")
    
    page.fill('input[name="title"]', "Borrowable Book")
    page.fill('input[name="author"]', "Test Author")
    page.fill('input[name="isbn"]', "9876543210123")
    page.fill('input[name="total_copies"]', "3")
    page.click('button:has-text("Add Book to Catalog")')
    page.wait_for_load_state("networkidle")
    
    assert "Borrowable Book" in page.inner_text("table")
    
    book_row = page.locator("tr:has-text('Borrowable Book')")
    
    patron_input = book_row.locator('input[name="patron_id"]')
    
    patron_input.fill("654321")
    
    borrow_button = book_row.locator('button:has-text("Borrow")')
    borrow_button.click()
    page.wait_for_load_state("networkidle")
    
    flash_message = page.locator(".flash-success")
    assert flash_message.is_visible()
    message_text = flash_message.inner_text().lower()
    assert "successfully" in message_text or "borrowed" in message_text
    
    assert "Book Catalog" in page.inner_text("h2")
