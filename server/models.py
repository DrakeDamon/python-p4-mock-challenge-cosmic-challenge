from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    # Add relationship
    missions = db.relationship(
        'Mission', back_populates='scientist', cascade='all, delete-orphan')

    # Add serialization rules
    serialize_rules = ('-missions.scientist',)

    # Add validation
    @validates('name', 'field_of_study')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f"{key} must not be empty")
        return value


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship(
        'Mission', back_populates='planet', cascade='all, delete-orphan')

    # Add serialization rules
    serialize_rules = ('-missions.planet',)


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # Foreign keys
    scientist_id = db.Column(db.Integer, db.ForeignKey(
        'scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey(
        'planets.id'), nullable=False)

    # Relationships
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    # Serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions')

    # Add validation
    @validates('name', 'scientist_id', 'planet_id')
    def validate_fields(self, key, value):
        if not value and value != 0:
            raise ValueError(f"{key} must not be empty")
        return value

# add any models you may need.
