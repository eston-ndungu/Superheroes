from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship

    # Relationship mapping the hero to related hero powers
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade= 'all, delete-orphan')

    # add serialization rules
    serialize_rules = ('-hero_powers.hero',)

    # Association proxy to get powers for this hero through hero powers
    powers = association_proxy('hero_powers', 'power', creator=lambda power_obj: HeroPower(power=power_obj))

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship

    #Relationship mapping the power to related hero powers
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

    # add serialization rules
    serialize_rules = ('-hero_powers.power',)

    # Association proxy to get heroes for this power through hero powers
    heroes = association_proxy('hero_powers', 'hero', creator=lambda hero_obj: HeroPower(hero=hero_obj))

    # add validation
    @validates('description')
    def validate_description(self, key, description):
        if not description:
            raise ValueError('No description provided')
        if len(description) < 20 :
            raise ValueError('Description must be at least 20 characters')
        return description

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    #Foreign key to store the hero id
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))

    #Foreign key to store the power id
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # add relationships

    #Relationship mapping the hero power to hero
    hero = db.relationship('Hero', back_populates='hero_powers')

    #Relationship mapping the hero power to related power
    power = db.relationship('Power', back_populates='hero_powers')

    # add serialization rules
    serialize_rules = ('-power.hero_powers', '-hero.hero_powers',)

    # add validation
    @validates('strength')
    def validate_strength(self, key, strength):
        possible_strengths = {'Strong', 'Weak', 'Average'}
        if strength not in possible_strengths:
            raise ValueError(f'Strength must be one of {possible_strengths}')
        return strength


    def __repr__(self):
        return f'<HeroPower {self.id}>'
