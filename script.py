from ipview.models import db, User


def create_db():
    db.create_all()

    user = User()
    user.username = 'admin'
    user.password = 'ipview'
    user.role = 50
    user.email = 'admin@ipview.loal'

    user.save()

