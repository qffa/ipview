from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask import flash


db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("DB operation failed on '{}'".format(self.__tablename__), "danger")
            return False
        else:
            return True

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("DB operation failed on '{}'".format(self.__tablename__), "danger")
            return False
        else:
            return True


    def log_event(self, content):
        event = Event(
            user=current_user.username,
            content=content
            )

        return event.save()




class Site(Base):
    __tablename__ = 'site'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<site: {}>'.format(self.name)


class Network(Base):
    __tablename__ = 'network'


    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64), nullable=False, unique=True)
    address_pack = db.Column(db.Float())
    description = db.Column(db.String(256), nullable=False)

    __mapper_args__ = {
        "order_by": address_pack
    }

    def __repr__(self):
        return '<Network: {}>'.format(self.address)


class Subnet(Base):
    __tablename__ = 'subnet'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(64), nullable=False, unique=True)
    address_pack = db.Column(db.Float())
    mask = db.Column(db.String(64))
    gateway = db.Column(db.String(64))
    dns1 = db.Column(db.String(64))
    dns2 = db.Column(db.String(64))
    description = db.Column(db.String(256), nullable=False)
    vlan = db.Column(db.SmallInteger, default=0)    # 0 means not a VLAN
    network_id = db.Column(db.Integer, db.ForeignKey('network.id'), nullable=False)
    network = db.relationship('Network', uselist=False, backref=db.backref('subnets'))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    site = db.relationship('Site', uselist=False, backref=db.backref('subnets'))


    __mapper_args__ = {
        "order_by": address_pack
    }
    def __repr__(self):
        return '<subnet: {}({})>'.format(self.name, self.address)


class IP(Base):
    __tablename__ = 'ip'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64), nullable=False, unique=True)
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'), nullable=False)
    subnet = db.relationship('Subnet', uselist=False, backref=db.backref('ips'))
    is_inuse = db.Column(db.Boolean, default=False)
    is_online = db.Column(db.Boolean, default=False)
    last_ping_time = db.Column(db.DateTime)
    host = db.relationship("Host", uselist=False)

    def __repr__(self):
        return '<ip: {}>'.format(self.address)


class Host(Base):
    __tablename__ = 'host'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    mac_address = db.Column(db.String(32), nullable=False, unique=True)
    description = db.Column(db.String(256), nullable=False)
    owner = db.Column(db.String(32), nullable=False)
    owner_email = db.Column(db.String(64), nullable=False)
    ip_id = db.Column(db.Integer, db.ForeignKey("ip.id"))
    ip = db.relationship('IP', uselist=False)

    def __repr__(self):
        return '<Host: {}>'.format(self.name)


class User(Base, UserMixin):
    __tablename__ = 'user'

    ROLE_USER = 10
    ROLE_ADMIN = 50

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    is_disable = db.Column(db.Boolean, default=False)
    remark = db.Column(db.String(128))

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN




class Request(Base):
    __tablename__ = "request"

    STATUS_REQUESTING = 10
    STATUS_APPROVED = 20
    STATUS_REJECTED = 30

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)             # username of requester
    status = db.Column(db.SmallInteger, default=STATUS_REQUESTING)
    host = db.Column(db.Integer, db.ForeignKey("host.id"))
    subnet = db.Column(db.Integer, db.ForeignKey("subnet.id"))


    def __repr__(self):
        return '<request: {}>'.format(self.host.name)



class Event(Base):
    __tableanme__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(32), nullable=False)
    content = db.Column(db.String(1024), nullable=False)






