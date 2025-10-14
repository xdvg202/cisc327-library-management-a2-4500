import pytest
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)
from database import(
    get_all_books
)
#r1
def test_add_book_valid_input():
    success, message = add_book_to_catalog("test", "test", "1234567890123", 5)
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_rejects_blank_title():
    success, message = add_book_to_catalog("", "test", "1145618123332", 1)
    assert success == False
    assert "title" in message.lower()

def test_add_book_invalid_isbn_too_short():
    success, message = add_book_to_catalog("test", "test", "123456789", 5)
    assert success == False
    assert "isbn" in message.lower()

def test_add_book_no_input():
    success, message = add_book_to_catalog("", "", "", "")
    assert success == False
    assert any(c in message.lower() for c in ["input", "invalid", "title", "isbn", "author"])
    
    
#r2
def test_display_catalog_with_books():
    add_book_to_catalog("book 1", "author 1", "1234567890123", 5)
    add_book_to_catalog("book 2", "author 2", "9876543210123", 3)
    books = get_all_books()
    assert len(books) >= 2, "catalog should display at least two books"
    assert books[-2]['title'] == "book 1"
    assert books[-1]['title'] == "book 2"

def test_display_catalog_empty():
    books = get_all_books()
    assert len(books) == 0, "catalog should be empty when no books are added"

def test_display_catalog_order():
    add_book_to_catalog("zebra Book", "Author Z", "9999999999999", 2)
    add_book_to_catalog("apple Book", "Author A", "1111111111111", 3)
    books = get_all_books()
    assert books[0]['title'] == "apple Book"
    assert books[1]['title'] == "zebra Book"

def test_display_catalog_with_duplicates():
    add_book_to_catalog("duplicate book", "author 1", "2222222222222", 1)
    add_book_to_catalog("duplicate book", "author 1", "2222222222222", 1)
    books = get_all_books()
    duplicate_books = [book for book in books if book['title'] == "duplicate book"]
    assert len(duplicate_books) == 2
    assert duplicate_books[0]['author'] == "author 1"
    assert duplicate_books[1]['author'] == "author 2"

#r3
def test_borrow_book_valid():
    add_book_to_catalog("test book", "test author", "1234567890123", 2)
    books = get_all_books()
    book_id = books[-1]['id']
    success, message = borrow_book_by_patron("654321", book_id)
    assert success is True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_invalid_patron():
    add_book_to_catalog("invalid patron pest", "author", "9876543210123", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    success, message = borrow_book_by_patron("12345", book_id)
    assert success is False
    assert "invalid patron" in message.lower()

def test_borrow_book_unavailable():
    add_book_to_catalog("unavailable book", "author", "1111111111111", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    success, message = borrow_book_by_patron("123456", book_id)
    assert success is False
    assert "no available copies" in message.lower()

#r4
def test_return_book_valid():
    add_book_to_catalog("return test book", "author", "2222222222222", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    success, message = return_book_by_patron("654321", book_id)
    assert success is True
    assert "successfully returned" in message.lower()

def test_return_book_not_borrowed():
    add_book_to_catalog("not borrowed book", "author", "4444444444444", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    success, message = return_book_by_patron("654321", book_id)
    assert success is False
    assert "not borrowed" in message.lower()

def test_return_book_invalid_patron():
    add_book_to_catalog("invalid patron return", "author", "5555555555555", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    success, message = return_book_by_patron("12345", book_id)
    assert success is False
    assert "invalid patron" in message.lower()

def test_return_book_late_fee():
    add_book_to_catalog("late fee book", "author", "6666666666666", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    success, message = return_book_by_patron("654321", book_id)
    assert success is True
    assert "late fee" in message.lower()

#r5
def test_calculate_late_fee_no_fee():
    add_book_to_catalog("on time book", "author", "7777777777777", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    success = return_book_by_patron("654321", book_id)
    assert success is True
    
    fee_info = calculate_late_fee_for_book("654321", book_id)
    assert fee_info['fee_amount'] == 0.00
    assert fee_info['days_overdue'] == 0

def test_calculate_late_fee_latest():
    add_book_to_catalog("max fee book", "author", "9999999999999", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    fee_info = calculate_late_fee_for_book("654321", book_id)
    assert fee_info['fee_amount'] == 15.00  

def test_calculate_late_fee_no_borrow_record():
    add_book_to_catalog("no borrow record book", "author", "1010101010101", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    fee_info = calculate_late_fee_for_book("654321", book_id)
    assert fee_info['fee_amount'] == 0.00
    assert fee_info['days_overdue'] == 0
#r6
def test_search_books_by_title_partial():
    add_book_to_catalog("searchable Book", "author", "1111111111111", 1)
    add_book_to_catalog("another Book", "author", "2222222222222", 1)
    results = search_books_in_catalog("search", "title")
    assert len(results) == 1
    assert results[0]['title'] == "searchable book"

def test_search_books_by_author_partial():
    add_book_to_catalog("book 1", "unique Author", "3333333333333", 1)
    add_book_to_catalog("book 2", "common Author", "4444444444444", 1)
    results = search_books_in_catalog("unique", "author")
    assert len(results) == 1
    assert results[0]['author'] == "unique author"

def test_search_books_by_isbn_exact():
    add_book_to_catalog("book 1", "author", "5555555555555", 1)
    add_book_to_catalog("book 2", "author", "6666666666666", 1)
    results = search_books_in_catalog("5555555555555", "isbn")
    assert len(results) == 1
    assert results[0]['isbn'] == "5555555555555"

def test_search_books_no_results():
    add_book_to_catalog("book 1", "author", "7777777777777", 1)
    results = search_books_in_catalog("non existent", "title")
    assert len(results) == 0


#r7
def test_patron_status_with_borrowed_books():
    add_book_to_catalog("borrowed book", "author", "1111111111111", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    status = get_patron_status_report("654321")
    assert len(status['borrowed_books']) == 1
    assert status['borrowed_books'][0]['title'] == "borrowed book"

def test_patron_status_with_late_fees():
    add_book_to_catalog("late fee book", "author", "2222222222222", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    status = get_patron_status_report("654321")
    assert status['total_late_fees'] > 0

def test_patron_status_with_no_borrowed_books():
    status = get_patron_status_report("654321")
    assert len(status['borrowed_books']) == 0
    assert status['total_late_fees'] == 0

def test_patron_status_with_borrowing_history():
    add_book_to_catalog("history book", "author", "3333333333333", 1)
    books = get_all_books()
    book_id = books[-1]['id']
    borrow_book_by_patron("654321", book_id)
    return_book_by_patron("654321", book_id)
    status = get_patron_status_report("654321")
    assert len(status['borrowing_history']) > 0
    assert status['borrowing_history'][0]['title'] == "history book"