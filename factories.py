class Book:
    def __init__(self, id, title, author, publisher, price, category, isbn, stock, image_url):
        self.id = id
        self.title = title
        self.author = author
        self.publisher = publisher
        self.price = price
        self.category = category
        self.isbn = isbn
        self.stock = stock
        self.image_url = image_url

class User:
    def __init__(self, id, name, is_admin, address, payment_method):
        self.id = id
        self.name = name
        self.is_admin = is_admin
        self.address = address
        self.payment_method = payment_method

class BookFactory:
    @staticmethod
    def create_book_from_row(row):
        return Book(
            id=row['id'],
            title=row['title'],
            author=row['author'],
            publisher=row['publisher'],
            price=row['price'],
            category=row['category'],
            isbn=row['isbn'],
            stock=row['stock'],
            image_url=row['image_url']
        )

class UserFactory:
    @staticmethod
    def create_user_from_row(row):
        return User(
            id=row['id'],
            name=row['name'],
            is_admin=row['is_admin'],
            address=row['address'],
            payment_method=row['payment_method']
        )
