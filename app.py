# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
api.app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 4}

movies_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

app.app_context().push()

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

    def __repr__(self):
        return self.title

class MoviesSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorsSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenresSchema(Schema):
    id = fields.Int()
    name = fields.Str()

@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        movies = Movie.query

        if director_id:
            movies = movies.filter(Movie.director_id == director_id)
        if director_id:
            movies = movies.filter(Movie.genre_id == genre_id)
        movies = movies.all()
        return MoviesSchema(many=True).dump(movies), 200

    def post(self):
        data = request.get_json()
        movie = Movie.guery.filter(Movie.title == data['title'], Movie.genre_id == data['genre_id'])
        if len(movie) > 0:
            return 'Уже есть данный фильм', 400
        new_movie = Movie(**data)
        db.session.add(new_movie)
        db.session.commit()
        db.session.close()

        return '', 201

@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        return MoviesSchema().dump(movie), 200

    def put(self, mid):
        data = request.get_json()
        movie = Movie.query.get(mid)
        movie.id = data['id']
        movie.title = data['title']
        movie.description = data['description']
        movie.trailer = data['trailer']
        movie.year = data['year']
        movie.genre_id = data['genre_id']
        movie.director_id = data['director_id']

        db.session.add(movie)
        db.session.commit()
        db.session.close()

    def delete(self, mid):
        movie = Movie.query.get(mid)

        db.session.delete(movie)
        db.session.commit()
        db.session.close()



if __name__ == '__main__':
    app.run(debug=True)
