Name: Victor Poltavski
Student ID: 20414500
Group: #3

| Function Name               | Implementation Status | What is Missing                                                |
| --------------------------- | --------------------- | -------------------------------------------------------------- |
| add_book_to_catalog         | partial               | non-numerical chars can be added to the ISBN code of a book    |
| get_all_books               | complete              |
| borrow_book_by_patron       | partial               | user can take out more than 5 books (6)                        |
| return_book_by_patron       | partial               | Feature is not yet implemented by dev team                     |
| calculate_late_fee_for_book | partial               | feature can't be tested due to incomplete book return function |
| search_books_in_catalog     | partial               | feature can't be tested due to incomplete book return function |
| get_patron_status_report    | partial               | feature can't be tested due to incomplete book return function |

=======================================================================================================================

PART 3:
R1 Tests:

- testing if books can be added to added to the DB
- testing if invalid books can be added to the DB
- testing if invalid book ISBN can be added to the DB
- testing if null book can be added

R2 Tests:

- testing if the catalogue displays added books in catalog
- testing if the catalogue can show empty
- testing if the catalogue displays order of added books correctly
- testing if the catalogue displays duplicated books

R3 Tests:

- testing if a book can be borrowed
- testing if a book can be borrowed with an invalid patron
- testing if an unavailable book can be borrowed

R4 Tests:

- testing if a borrowed book can be returned
- testing if a not borrowed book can be returned
- testing if a book can be returned with an invalid patron
- testing if a returned book has a late fee

R5 Tests:

- testing if the calculated late fee is correct
- testing the max possible late fee
- testing the late fee with no borrowing record

R6 Tests:

- testing the search algo with a partial title
- testing the search algo with a partial author name
- testing the search algo with the exact ISBN
- testing the search algo with a non existent book

R7 Tests:

- testing the status of a patron with borrowed books
- testing the status of a patron with late fees
- testing the status of a ptron with no borrowed books
- testing the patron status with a borrowing history
