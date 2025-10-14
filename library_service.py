"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    get_patron_borrowed_books, get_patron_borrowing_history, insert_book, 
    insert_borrow_record, update_book_availability, update_borrow_record_return_date, get_all_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Implements R1: Book Catalog Management
    """
    if not title or not title.strip():
        return False, "Title is required"
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters"
    
    if not author or not author.strip():
        return False, "Author is required"
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters"
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits"
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer"
    
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists"
    
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'"{title.strip()}" has been successfully added to the catalog'
    else:
        return False, "error occurred while adding the book"

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Implements R3 as per requirements  
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits"
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found"
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available"
    
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books"
    
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record"
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability"
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Implements R4: Book Return Processing
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits"
    
    if not isinstance(book_id, int) or book_id <= 0:
        return False, "Invalid book ID"
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found"
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    book_borrowed = False
    borrow_record = None
    
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            book_borrowed = True
            borrow_record = borrowed_book
            break
    
    if not book_borrowed:
        return False, f"Book '{book['title']}' was not borrowed by this patron"
    
    return_date = datetime.now()
    return_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_success:
        return False, "Database error occurred while recording return date"
    
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability"
    
    due_date = borrow_record['due_date']
    days_overdue = 0
    late_fee = 0.0
    
    if return_date > due_date:
        days_overdue = (return_date - due_date).days
        
        if days_overdue <= 7:
            late_fee = days_overdue * 0.50
        else:
            late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
        
        late_fee = min(late_fee, 15.00)
    
    if late_fee > 0:
        message = f'Successfully returned "{book["title"]}". Late fee: ${late_fee:.2f} ({days_overdue} days overdue)'
    else:
        message = f'Successfully returned "{book["title"]}". No late fees'
    
    return True, message

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Implements R5: Late Fee Calculation API
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid patron ID'
        }
    
    if not isinstance(book_id, int) or book_id <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid book ID'
        }
    
    book = get_book_by_id(book_id)
    if not book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found'
        }
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    book_borrowed = False
    borrow_record = None
    
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            book_borrowed = True
            borrow_record = borrowed_book
            break
    
    if not book_borrowed:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not borrowed by this patron'
        }
    
    current_date = datetime.now()
    due_date = borrow_record['due_date']
    days_overdue = 0
    late_fee = 0.0
    
    if current_date > due_date:
        days_overdue = (current_date - due_date).days
        
        if days_overdue <= 7:
            late_fee = days_overdue * 0.50
        else:
            late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
        
        late_fee = min(late_fee, 15.00)
        
        return {
            'fee_amount': round(late_fee, 2),
            'days_overdue': days_overdue,
            'status': 'Overdue'
        }
    else:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Not overdue'
        }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Implements R6: Book Search Functionality
    """
    if not search_term or not search_term.strip():
        return []
    
    if search_type not in ['title', 'author', 'isbn']:
        return []
    
    all_books = get_all_books()
    search_term = search_term.strip().lower()
    results = []
    
    for book in all_books:
        match = False
        
        if search_type == 'title':
            if search_term in book['title'].lower():
                match = True
        elif search_type == 'author':
            if search_term in book['author'].lower():
                match = True
        elif search_type == 'isbn':
            if search_term == book['isbn']:
                match = True
        
        if match:
            results.append({
                'id': book['id'],
                'title': book['title'],
                'author': book['author'],
                'isbn': book['isbn'],
                'available_copies': book['available_copies'],
                'total_copies': book['total_copies']
            })
    
    return results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Implements R7: Patron Status Report
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'borrowed_books': [],
            'total_late_fees': 0.0,
            'borrowed_count': 0,
            'borrowing_history': [],
            'error': 'Invalid patron ID'
        }
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    borrowing_history = get_patron_borrowing_history(patron_id)
    
    total_late_fees = 0.0
    current_date = datetime.now()
    
    for book in borrowed_books:
        if book['is_overdue']:
            days_overdue = (current_date - book['due_date']).days
            if days_overdue <= 7:
                late_fee = days_overdue * 0.50
            else:
                late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
            late_fee = min(late_fee, 15.00)
            total_late_fees += late_fee
    
    return {
        'borrowed_books': borrowed_books,
        'total_late_fees': round(total_late_fees, 2),
        'borrowed_count': len(borrowed_books),
        'borrowing_history': borrowing_history
    }
