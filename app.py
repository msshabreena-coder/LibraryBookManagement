
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
from html import escape
import json

books = []
next_id = 1


def add_book(title, author):
    global next_id

    title = title.strip()
    author = author.strip()

    if not title or not author:
        raise ValueError("Title and author are required.")

    book = {
        "id": next_id,
        "title": title,
        "author": author,
        "available": True,
    }

    books.append(book)
    next_id += 1
    return book


def get_available_books():
    return [book for book in books if book["available"]]


def get_all_books():
    return list(books)


def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    raise ValueError("Book not found.")


def issue_book(book_id):
    book = find_book(book_id)

    if not book["available"]:
        raise ValueError("This book is already issued.")

    book["available"] = False
    return book


def return_book(book_id):
    book = find_book(book_id)

    if book["available"]:
        raise ValueError("This book has not been issued.")

    book["available"] = True
    return book


class LibraryHandler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.respond(
                200,
                json.dumps({"status": "ok"}),
                "application/json",
            )
            return

        if self.path == "/api/books":
            self.respond(
                200,
                json.dumps(get_available_books()),
                "application/json",
            )
            return

        if self.path == "/api/books/all":
            self.respond(
                200,
                json.dumps(get_all_books()),
                "application/json",
            )
            return

        rows = ""

        for book in get_all_books():
            book_id = book["id"]
            title = escape(book["title"])
            author = escape(book["author"])

            if book["available"]:
                status = "Available"
                action = f"""
                    <form action="/books/{book_id}/issue" method="post">
                        <button type="submit">Issue Book</button>
                    </form>
                """
            else:
                status = "Issued"
                action = f"""
                    <form action="/books/{book_id}/return" method="post">
                        <button type="submit">Return Book</button>
                    </form>
                """

            rows += f"""
                <tr>
                    <td>{book_id}</td>
                    <td>{title}</td>
                    <td>{author}</td>
                    <td>{status}</td>
                    <td>{action}</td>
                </tr>
            """

        if not rows:
            rows = '<tr><td colspan="5">No books in the library.</td></tr>'

        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Library Book Management</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 16px;
            background: #f5f7fb;
        }}
        h1, h2 {{ color: #23395d; }}
        form, .panel {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        input, button {{
            padding: 10px;
            margin: 5px 0;
        }}
        input {{ width: min(90%, 300px); }}
        button {{
            background: #23395d;
            color: white;
            border: 0;
            border-radius: 4px;
            cursor: pointer;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{ background: #e7edf7; }}
        td form {{
            padding: 0;
            margin: 0;
        }}
    </style>
</head>
<body>
    <h1>Library Book Management</h1>
    <p>Push 2: Book issue, return, and availability management</p>

    <section class="panel">
        <h2>Add a Book</h2>
        <form action="/books" method="post">
            <input name="title" placeholder="Book title" required>
            <br>
            <input name="author" placeholder="Author name" required>
            <br>
            <button type="submit">Add Book</button>
        </form>
    </section>

    <section>
        <h2>Book Inventory</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
            {rows}
        </table>
        <p><a href="/">Refresh book list</a></p>
    </section>
</body>
</html>"""

        self.respond(200, page)

    def do_POST(self):
        try:
            if self.path == "/books":
                length = int(self.headers.get("Content-Length", "0"))

                if length > 10000:
                    self.respond(413, "Form submission too large.")
                    return

                form_data = self.rfile.read(length).decode("utf-8")
                form = parse_qs(form_data)

                title = form.get("title", [""])[0]
                author = form.get("author", [""])[0]

                add_book(title, author)

            else:
                parts = self.path.strip("/").split("/")

                if (
                    len(parts) != 3
                    or parts[0] != "books"
                    or parts[2] not in ("issue", "return")
                ):
                    self.respond(404, "Not found")
                    return

                book_id = int(parts[1])

                if parts[2] == "issue":
                    issue_book(book_id)
                else:
                    return_book(book_id)

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        except (ValueError, UnicodeDecodeError):
            self.respond(400, "Invalid request or book operation.")

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), LibraryHandler)
    print("Library Book Management running on port 8080", flush=True)
    server.serve_forever()
