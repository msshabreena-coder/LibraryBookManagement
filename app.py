
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

        rows = ""
        for book in get_available_books():
            rows += (
                "<tr>"
                f"<td>{book['id']}</td>"
                f"<td>{escape(book['title'])}</td>"
                f"<td>{escape(book['author'])}</td>"
                "<td>Available</td>"
                "</tr>"
            )

        if not rows:
            rows = '<tr><td colspan="4">No available books.</td></tr>'

        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Library Book Management</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 850px;
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
    </style>
</head>
<body>
    <h1>Library Book Management</h1>
    <p>Push 1: Add and view available books</p>

    <section class="panel">
        <h2>Menu</h2>
        <p>1. Add Book</p>
        <p>2. View Available Books</p>
        <form action="/books" method="post">
            <h2>Add a Book</h2>
            <input name="title" placeholder="Book title" required>
            <br>
            <input name="author" placeholder="Author name" required>
            <br>
            <button type="submit">Add Book</button>
        </form>
    </section>

    <section>
        <h2>Available Books</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Status</th>
            </tr>
            {rows}
        </table>
        <p><a href="/">Refresh book list</a></p>
    </section>
</body>
</html>"""

        self.respond(200, page)

    def do_POST(self):
        if self.path != "/books":
            self.respond(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 10000:
                self.respond(413, "Form submission too large.")
                return

            form_data = self.rfile.read(length).decode("utf-8")
            form = parse_qs(form_data)

            title = form.get("title", [""])[0]
            author = form.get("author", [""])[0]

            add_book(title, author)

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        except (ValueError, UnicodeDecodeError):
            self.respond(400, "Invalid book details.")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), LibraryHandler)
    print("Library Book Management running on port 8080", flush=True)
    server.serve_forever()
