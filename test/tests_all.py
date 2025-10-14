import pytest
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
)
from database import get_all_books


# R1: Add Book
def test_r1_add_book_valid():
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 2)
    assert success is True
    assert "successfully" in msg.lower()


def test_r1_add_book_validation():
    assert add_book_to_catalog("", "A", "1234567890123", 1)[0] is False
    assert add_book_to_catalog("T", "", "1234567890123", 1)[0] is False
    assert add_book_to_catalog("T", "A", "short", 1)[0] is False
    assert add_book_to_catalog("T" * 201, "A", "1234567890123", 1)[0] is False
    assert add_book_to_catalog("T", "A" * 101, "1234567890123", 1)[0] is False
    assert add_book_to_catalog("T", "A", "1234567890123", 0)[0] is False


# R2: Catalog Display
def test_r2_catalog_lists_books_and_order():
    add_book_to_catalog("Zebra", "Auth", "9999999999999", 1)
    add_book_to_catalog("Apple", "Auth", "1111111111111", 1)
    books = get_all_books()
    assert len(books) >= 2
    # get_all_books orders by title
    assert books[0]["title"].lower() <= books[1]["title"].lower()


# R3: Borrow Book
def test_r3_borrow_happy_path_and_limits():
    add_book_to_catalog("B", "A", "1234567890123", 2)
    book_id = get_all_books()[-1]["id"]
    ok, _ = borrow_book_by_patron("123456", book_id)
    assert ok is True

    # Borrow 5 books total for the same patron
    for i in range(4):
        add_book_to_catalog(f"B{i}", "A", f"12345678901{i}0", 1)
        bid = get_all_books()[-1]["id"]
        borrow_book_by_patron("123456", bid)

    # Sixth should fail
    add_book_to_catalog("Full", "A", "3333333333333", 1)
    bid = get_all_books()[-1]["id"]
    ok, msg = borrow_book_by_patron("123456", bid)
    assert ok is False
    assert "maximum" in msg.lower()


def test_r3_borrow_validations():
    add_book_to_catalog("Once", "A", "7777777777777", 1)
    book_id = get_all_books()[-1]["id"]
    ok, msg = borrow_book_by_patron("12345", book_id)
    assert ok is False and "invalid patron" in msg.lower()


# R4: Return Book
def test_r4_return_happy_path():
    add_book_to_catalog("R", "A", "2222222222222", 1)
    book_id = get_all_books()[-1]["id"]
    borrow_book_by_patron("123456", book_id)
    ok, msg = return_book_by_patron("123456", book_id)
    assert ok is True
    assert "returned" in msg.lower()


def test_r4_return_not_borrowed():
    add_book_to_catalog("NB", "A", "4444444444444", 1)
    book_id = get_all_books()[-1]["id"]
    ok, msg = return_book_by_patron("123456", book_id)
    assert ok is False
    assert "not borrowed" in msg.lower()


# R5: Late Fee Calculation
def test_r5_late_fee_shapes():
    add_book_to_catalog("L", "A", "5555555555555", 1)
    book_id = get_all_books()[-1]["id"]
    borrow_book_by_patron("123456", book_id)
    info = calculate_late_fee_for_book("123456", book_id)
    assert set(info.keys()) == {"fee_amount", "days_overdue", "status"}


# R6: Search
def test_r6_search_variants():
    add_book_to_catalog("Searchable Book", "Author", "1010101010101", 1)
    add_book_to_catalog("Another", "Someone", "2020202020202", 1)

    res = search_books_in_catalog("search", "title")
    assert len(res) == 1

    res = search_books_in_catalog("author", "author")
    assert len(res) >= 1

    res = search_books_in_catalog("1010101010101", "isbn")
    assert len(res) == 1


# R7: Patron Status
def test_r7_patron_status_fields_and_counts():
    add_book_to_catalog("S1", "A", "3030303030303", 1)
    bid = get_all_books()[-1]["id"]
    borrow_book_by_patron("123456", bid)

    status = get_patron_status_report("123456")
    assert {"borrowed_books", "total_late_fees", "borrowed_count", "borrowing_history"} <= set(status.keys())
    assert status["borrowed_count"] == len(status["borrowed_books"]) 


