
import unittest
import app


class TestLibrary(unittest.TestCase):
    def setUp(self):
        app.books.clear()
        app.next_id = 1

    def test_add_book(self):
        book = app.add_book("Python Basics", "John Smith")

        self.assertEqual(book["id"], 1)
        self.assertEqual(book["title"], "Python Basics")
        self.assertEqual(book["author"], "John Smith")
        self.assertTrue(book["available"])

    def test_view_available_books(self):
        app.add_book("Python Basics", "John Smith")
        app.add_book("Operating Systems", "Jane Doe")

        books = app.get_available_books()

        self.assertEqual(len(books), 2)
        self.assertEqual(books[0]["title"], "Python Basics")

    def test_unique_book_ids(self):
        first = app.add_book("Book One", "Author One")
        second = app.add_book("Book Two", "Author Two")

        self.assertNotEqual(first["id"], second["id"])

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValueError):
            app.add_book("", "John Smith")

    def test_empty_author_is_rejected(self):
        with self.assertRaises(ValueError):
            app.add_book("Python Basics", "")

    def test_issue_book(self):
        book = app.add_book("Python Basics", "John Smith")

        issued = app.issue_book(book["id"])

        self.assertFalse(issued["available"])
        self.assertEqual(len(app.get_available_books()), 0)

    def test_cannot_issue_book_twice(self):
        book = app.add_book("Python Basics", "John Smith")
        app.issue_book(book["id"])

        with self.assertRaises(ValueError):
            app.issue_book(book["id"])

    def test_return_book(self):
        book = app.add_book("Python Basics", "John Smith")
        app.issue_book(book["id"])

        returned = app.return_book(book["id"])

        self.assertTrue(returned["available"])
        self.assertEqual(len(app.get_available_books()), 1)

    def test_cannot_return_available_book(self):
        book = app.add_book("Python Basics", "John Smith")

        with self.assertRaises(ValueError):
            app.return_book(book["id"])

    def test_book_not_found(self):
        with self.assertRaises(ValueError):
            app.issue_book(999)

    def test_get_all_books_includes_issued_books(self):
        book = app.add_book("Python Basics", "John Smith")
        app.issue_book(book["id"])

        self.assertEqual(len(app.get_all_books()), 1)
        self.assertEqual(len(app.get_available_books()), 0)


if __name__ == "__main__":
    unittest.main()
