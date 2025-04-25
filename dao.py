from factories import BookFactory, UserFactory

class BookDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_all_books(self, search='', author='', category='', publisher='', sort_strategy=None):
        query = 'SELECT * FROM books WHERE 1=1'
        params = []

        if search:
            query += ' AND title LIKE ?'
            params.append(f'%{search}%')
        if author:
            query += ' AND author LIKE ?'
            params.append(f'%{author}%')
        if category:
            query += ' AND category LIKE ?'
            params.append(f'%{category}%')
        if publisher:
            query += ' AND publisher LIKE ?'
            params.append(f'%{publisher}%')

        if sort_strategy:
            query += f' {sort_strategy.sort_query()}'

        rows = self.conn.execute(query, params).fetchall()
        return [BookFactory.create_book_from_row(row) for row in rows]

    def get_categories(self):
        rows = self.conn.execute('SELECT DISTINCT category FROM books').fetchall()
        return [row['category'] for row in rows]

class UserDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_user_by_id(self, user_id):
        row = self.conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return UserFactory.create_user_from_row(row) if row else None

    def get_user_by_credentials(self, username, password):
        row = self.conn.execute('SELECT * FROM users WHERE name = ? AND password = ?', (username, password)).fetchone()
        return UserFactory.create_user_from_row(row) if row else None
