from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {
        "id": 0,
        "title": "A Fire Upon the Deep",
        "author": "Vernor Vinge",
        "first_sentence": "The coldsleep itself was dreamless.",
        "year_published": "1992"
    },
    {
        "id": 1,
        "title": "The Ones Who Walk Away From Omelas",
        "author": "Ursula K. Le Guin",
        "first_sentence": "With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.",
        "published": "1973"
    },
    {
        "id": 2,
        "title": "Dhalgren",
        "author": "Samuel R. Delany",
        "first_sentence": "to wound the autumnal city.",
        "published": "1975"
    }
]


# 1. Todos los libros
@app.route("/books", methods=["GET"])
def get_all_books():
    return jsonify(books)


# 2. Id como query param  →  GET /books/search?id=2
@app.route("/books/search", methods=["GET"])
def get_book_by_param():
    book_id = request.args.get("id", type=int)
    result = [b for b in books if b["id"] == book_id]
    return jsonify(result)


# 3. Title en la URL  →  GET /books/A Fire Upon the Deep
@app.route("/books/<string:title>", methods=["GET"])
def get_book_by_title(title):
    result = next((b for b in books if b["title"].lower() == title.lower()), None)
    if result is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(result)


# 4. Id en el body  →  GET /books/body  con JSON {"id": 2}
@app.route("/books/body", methods=["GET"])
def get_book_by_body():
    data = request.get_json()
    book_id = data.get("id")
    result = next((b for b in books if b["id"] == book_id), None)
    if result is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
