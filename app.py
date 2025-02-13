import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Konfigurasi Aplikasi dari .env
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi Database & API
db = SQLAlchemy(app)
api = Api(app)

# Model Database
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}

with app.app_context():
    db.create_all()

# API Resource (CRUD)
class BookResource(Resource):
    def get(self, book_id=None):
        if book_id:
            book = Book.query.get(book_id)
            if book:
                return jsonify(book.to_dict())
            return {"message": "Book not found"}, 404
        books = Book.query.all()
        return jsonify([book.to_dict() for book in books])

    def post(self):
        data = request.get_json()
        new_book = Book(title=data['title'], author=data['author'])
        db.session.add(new_book)
        db.session.commit()
        return jsonify(new_book.to_dict())

    def put(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        data = request.get_json()
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        db.session.commit()
        return jsonify(book.to_dict())

    def delete(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted successfully"}

api.add_resource(BookResource, "/books", "/books/<int:book_id>")

if __name__ == "__main__":
    app.run(debug=True)
