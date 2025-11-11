import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

import services.library_service as ls


class PaymentGateway:
	def process_payment(self, patron_id: str, amount: float, description: str):
		raise NotImplementedError
	def refund_payment(self, transaction_id: str, amount: float):
		raise NotImplementedError


def test_pay_late_fees_successful_payment(mocker):
	mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={
		"fee_amount": 6.5, "days_overdue": 3, "status": "Overdue"
	})
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 1, "title": "Clean Code"
	})
	gateway = Mock(spec=PaymentGateway)
	gateway.process_payment.return_value = (True, "txn_123", "Success")
	success, msg, txn = ls.pay_late_fees("123456", 1, payment_gateway=gateway)
	assert success is True
	assert "payment successful" in msg.lower()
	assert txn == "txn_123"
	gateway.process_payment.assert_called_once()
	gateway.process_payment.assert_called_with(
		patron_id="123456", amount=6.5, description="Late fees for 'Clean Code'"
	)


def test_pay_late_fees_payment_declined(mocker):
	mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={
		"fee_amount": 4.0, "days_overdue": 2, "status": "Overdue"
	})
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 2, "title": "Refactoring"
	})
	gateway = Mock(spec=PaymentGateway)
	gateway.process_payment.return_value = (False, None, "Card declined")
	success, msg, txn = ls.pay_late_fees("123456", 2, payment_gateway=gateway)
	assert success is False
	assert "payment failed" in msg.lower()
	assert txn is None
	gateway.process_payment.assert_called_once_with(
		patron_id="123456", amount=4.0, description="Late fees for 'Refactoring'"
	)


def test_pay_late_fees_invalid_patron_id_mock_not_called(mocker):
	mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={
		"fee_amount": 5.0, "days_overdue": 1, "status": "Overdue"
	})
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "X"})
	gateway = Mock(spec=PaymentGateway)
	success, msg, txn = ls.pay_late_fees("12345", 1, payment_gateway=gateway)
	assert success is False
	assert "invalid patron id" in msg.lower()
	assert txn is None
	gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_fees_mock_not_called(mocker):
	mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={
		"fee_amount": 0.0, "days_overdue": 0, "status": "Not overdue"
	})
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Y"})
	gateway = Mock(spec=PaymentGateway)
	success, msg, txn = ls.pay_late_fees("123456", 1, payment_gateway=gateway)
	assert success is False
	assert "no late fees" in msg.lower()
	assert txn is None
	gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error_exception_handling(mocker):
	mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={
		"fee_amount": 2.5, "days_overdue": 1, "status": "Overdue"
	})
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Z"})
	gateway = Mock(spec=PaymentGateway)
	gateway.process_payment.side_effect = RuntimeError("network error")
	success, msg, txn = ls.pay_late_fees("123456", 1, payment_gateway=gateway)
	assert success is False
	assert "payment processing error" in msg.lower()
	assert "network error" in msg.lower()
	assert txn is None
	gateway.process_payment.assert_called_once_with(
		patron_id="123456", amount=2.5, description="Late fees for 'Z'"
	)


def test_refund_successful_refund(mocker):
	gateway = Mock(spec=PaymentGateway)
	gateway.refund_payment.return_value = (True, "Refund successful")
	success, msg = ls.refund_late_fee_payment("txn_abc", 5.0, payment_gateway=gateway)
	assert success is True
	assert "refund successful" in msg.lower()
	gateway.refund_payment.assert_called_once_with("txn_abc", 5.0)


def test_refund_invalid_transaction_id_rejection(mocker):
	gateway = Mock(spec=PaymentGateway)
	success, msg = ls.refund_late_fee_payment("bad_id", 5.0, payment_gateway=gateway)
	assert success is False
	assert "invalid transaction id" in msg.lower()
	gateway.refund_payment.assert_not_called()


def test_refund_amount_zero_not_called(mocker):
	gateway = Mock(spec=PaymentGateway)
	success, msg = ls.refund_late_fee_payment("txn_123", 0, payment_gateway=gateway)
	assert success is False
	assert "greater than 0" in msg.lower()
	gateway.refund_payment.assert_not_called()


def test_refund_amount_negative_not_called(mocker):
	gateway = Mock(spec=PaymentGateway)
	success, msg = ls.refund_late_fee_payment("txn_123", -1.0, payment_gateway=gateway)
	assert success is False
	assert "greater than 0" in msg.lower()
	gateway.refund_payment.assert_not_called()


def test_refund_amount_exceeds_max_not_called(mocker):
	gateway = Mock(spec=PaymentGateway)
	success, msg = ls.refund_late_fee_payment("txn_123", 20.0, payment_gateway=gateway)
	assert success is False
	assert "exceeds maximum late fee" in msg.lower()
	gateway.refund_payment.assert_not_called()


def test_borrow_book_book_not_found(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value=None)
	success, msg = ls.borrow_book_by_patron("123456", 1)
	assert success is False
	assert "book not found" in msg.lower()


def test_borrow_book_no_available_copies(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 1, "title": "X", "available_copies": 0
	})
	success, msg = ls.borrow_book_by_patron("123456", 1)
	assert success is False
	assert "not available" in msg.lower()


def test_borrow_book_max_limit_exceeded(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 1, "title": "X", "available_copies": 2
	})
	mocker.patch('services.library_service.get_patron_borrow_count', return_value=6)
	success, msg = ls.borrow_book_by_patron("123456", 1)
	assert success is False
	assert "maximum borrowing limit" in msg.lower()


def test_borrow_book_insert_record_failure(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 1, "title": "X", "available_copies": 2
	})
	mocker.patch('services.library_service.get_patron_borrow_count', return_value=0)
	mocker.patch('services.library_service.insert_borrow_record', return_value=False)
	success, msg = ls.borrow_book_by_patron("123456", 1)
	assert success is False
	assert "creating borrow record" in msg.lower()


def test_borrow_book_update_availability_failure(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 1, "title": "X", "available_copies": 2
	})
	mocker.patch('services.library_service.get_patron_borrow_count', return_value=0)
	mocker.patch('services.library_service.insert_borrow_record', return_value=True)
	mocker.patch('services.library_service.update_book_availability', return_value=False)
	success, msg = ls.borrow_book_by_patron("123456", 1)
	assert success is False
	assert "updating book availability" in msg.lower()


def test_return_book_invalid_book_id():
	success, msg = ls.return_book_by_patron("123456", 0)
	assert success is False
	assert "invalid book id" in msg.lower()


def test_return_book_book_not_found(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value=None)
	success, msg = ls.return_book_by_patron("123456", 1)
	assert success is False
	assert "book not found" in msg.lower()


def test_return_book_not_borrowed_by_patron(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "X"})
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[])
	success, msg = ls.return_book_by_patron("123456", 1)
	assert success is False
	assert "was not borrowed" in msg.lower()


def test_return_book_update_return_date_failure(mocker):
	borrow_record = {
		"book_id": 1,
		"due_date": datetime.now() + timedelta(days=1)
	}
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Y"})
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[borrow_record])
	mocker.patch('services.library_service.update_borrow_record_return_date', return_value=False)
	success, msg = ls.return_book_by_patron("123456", 1)
	assert success is False
	assert "recording return date" in msg.lower()


def test_return_book_update_availability_failure(mocker):
	borrow_record = {
		"book_id": 1,
		"due_date": datetime.now() + timedelta(days=1)
	}
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Z"})
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[borrow_record])
	mocker.patch('services.library_service.update_borrow_record_return_date', return_value=True)
	mocker.patch('services.library_service.update_book_availability', return_value=False)
	success, msg = ls.return_book_by_patron("123456", 1)
	assert success is False
	assert "updating book availability" in msg.lower()


def test_calc_fee_invalid_patron():
	info = ls.calculate_late_fee_for_book("abc", 1)
	assert info['status'].lower().startswith("invalid patron id")
	assert info['fee_amount'] == 0.0


def test_calc_fee_invalid_book_id():
	info = ls.calculate_late_fee_for_book("123456", 0)
	assert info['status'].lower().startswith("invalid book id")
	assert info['fee_amount'] == 0.0


def test_calc_fee_book_not_found(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value=None)
	info = ls.calculate_late_fee_for_book("123456", 1)
	assert info['status'].lower() == "book not found"
	assert info['fee_amount'] == 0.0


def test_calc_fee_not_borrowed(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1})
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[])
	info = ls.calculate_late_fee_for_book("123456", 1)
	assert info['status'].lower().startswith("book not borrowed")
	assert info['fee_amount'] == 0.0


def test_calc_fee_overdue_under_7(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1})
	borrow_record = {
		"book_id": 1,
		"due_date": datetime.now() - timedelta(days=5)
	}
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[borrow_record])
	info = ls.calculate_late_fee_for_book("123456", 1)
	assert info['status'] == "Overdue"
	assert info['fee_amount'] == 2.5
	assert info['days_overdue'] == 5


def test_calc_fee_overdue_cap_at_15(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1})
	borrow_record = {
		"book_id": 1,
		"due_date": datetime.now() - timedelta(days=40)
	}
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[borrow_record])
	info = ls.calculate_late_fee_for_book("123456", 1)
	assert info['status'] == "Overdue"
	assert info['fee_amount'] == 15.0
	assert info['days_overdue'] >= 8


def test_search_invalid_inputs():
	assert ls.search_books_in_catalog("", "title") == []
	assert ls.search_books_in_catalog("x", "bad_type") == []


def test_search_match_paths(mocker):
	mocker.patch('services.library_service.get_all_books', return_value=[
		{"id": 1, "title": "Alpha", "author": "A", "isbn": "111", "available_copies": 1, "total_copies": 1},
		{"id": 2, "title": "Beta", "author": "Bee", "isbn": "444", "available_copies": 1, "total_copies": 1},
	])
	out = ls.search_books_in_catalog("alp", "title")
	assert len(out) == 1 and out[0]['title'] == "Alpha"
	out = ls.search_books_in_catalog("bee", "author")
	assert len(out) == 1 and out[0]['author'] == "Bee"
	out = ls.search_books_in_catalog("444", "isbn")
	assert len(out) == 1 and out[0]['isbn'] == "444"


def test_patron_status_invalid_id():
	status = ls.get_patron_status_report("abc")
	assert status['borrowed_books'] == []
	assert status['total_late_fees'] == 0.0
	assert 'error' in status


def test_patron_status_fee_calculation(mocker):
	now = datetime.now()
	borrowed = [
		{"book_id": 1, "is_overdue": True, "due_date": now - timedelta(days=10)},
		{"book_id": 2, "is_overdue": False, "due_date": now + timedelta(days=1)},
	]
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=borrowed)
	mocker.patch('services.library_service.get_patron_borrowing_history', return_value=[])
	status = ls.get_patron_status_report("123456")
	assert status['total_late_fees'] == 6.5
	assert status['borrowed_count'] == 2


def test_add_book_success(mocker):
	mocker.patch('services.library_service.get_book_by_isbn', return_value=None)
	mocker.patch('services.library_service.insert_book', return_value=True)
	ok, msg = ls.add_book_to_catalog("Title", "Author", "1234567890123", 2)
	assert ok is True
	assert "successfully added" in msg.lower()


def test_add_book_duplicate_isbn(mocker):
	mocker.patch('services.library_service.get_book_by_isbn', return_value={"id": 1})
	ok, msg = ls.add_book_to_catalog("Title", "Author", "1234567890123", 2)
	assert ok is False
	assert "already exists" in msg.lower()


def test_borrow_book_success(mocker):
	mocker.patch('services.library_service.get_book_by_id', return_value={
		"id": 1, "title": "Some Book", "available_copies": 1
	})
	mocker.patch('services.library_service.get_patron_borrow_count', return_value=0)
	mocker.patch('services.library_service.insert_borrow_record', return_value=True)
	mocker.patch('services.library_service.update_book_availability', return_value=True)
	ok, msg = ls.borrow_book_by_patron("123456", 1)
	assert ok is True
	assert "successfully borrowed" in msg.lower()


def test_return_book_success_with_late_fee(mocker):
	borrow_record = {
		"book_id": 1,
		"due_date": datetime.now() - timedelta(days=3)
	}
	mocker.patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Late Book"})
	mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[borrow_record])
	mocker.patch('services.library_service.update_borrow_record_return_date', return_value=True)
	mocker.patch('services.library_service.update_book_availability', return_value=True)
	ok, msg = ls.return_book_by_patron("123456", 1)
	assert ok is True
	assert "late fee" in msg.lower()


def test_pay_late_fees_unable_to_calculate(mocker):
	mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={})
	ok, msg, txn = ls.pay_late_fees("123456", 1, payment_gateway=None)
	assert ok is False
	assert "unable to calculate late fees" in msg.lower()
	assert txn is None