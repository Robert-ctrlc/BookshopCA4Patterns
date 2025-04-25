from dao import UserDAO

class AdminAccessProxy:
    def __init__(self, conn):
        self.conn = conn

    def is_admin(self, user_id):
        user_dao = UserDAO(self.conn)
        user = user_dao.get_user_by_id(user_id)
        return user and user.is_admin