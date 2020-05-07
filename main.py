
from flask import Flask, request
from flask_restful import Api, Resource
from flask import jsonify
from flask_restful.utils import cors
import json
from flask_cors import CORS
from kanren import *
import pandas as pd

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

#-----------------------------------LOGICA FIRST ORDER------------------------------------------------------------------

class Libro:
    def __init__(self, nombre):
        self.nombre = nombre

archBooks = pd.read_csv('books.csv')
archBooks_tags = pd.read_csv('book_tags.csv')

# seleccionar el rating mayor que 3
archRatings = pd.read_csv('ratings.csv')
archRatings.where(archRatings['rating'] > 3, inplace=True)


archTags = pd.read_csv('tags.csv')
#archToRead = pd.read_excel('to_read.xlsx')

#Columnas de books
book_id_book = archBooks['book_id'].values
title_book = archBooks['title'].values
goodreads_book_id_book = archBooks['goodreads_book_id'].values


#columnas Book Tags
goodreads_book_id_book_tags = archBooks_tags['goodreads_book_id'].values
tag_id_book_tags = archBooks_tags['tag_id'].values

#Columnas Tags
tag_id_tags = archTags['tag_id'].values
tag_name = archTags['tag_name'].values

#Columnas Rating
user_id = archRatings['user_id'].values
book_id_rating = archRatings['book_id'].values
rating = archRatings['rating'].values



#Base del conocimiento chidori

usuario = var()
libro = var()
libro_goodread = var()
autores = var()
titulo_libro = var()
tag = var()
tag_nombre = var()
rating_rating = var()

Book = Relation()
BookTags = Relation()
Tags = Relation()
Ratings = Relation()

for i in range(len(book_id_book)):
    fact(Book, book_id_book[i], title_book[i], goodreads_book_id_book[i])

for i in range(len(goodreads_book_id_book_tags)):
    fact(BookTags, goodreads_book_id_book_tags[i], tag_id_book_tags[i])

for i in range(len(tag_id_tags)):
    fact(Tags, tag_id_tags[i], tag_name[i])

for i in range(len(rating)):
    fact(Ratings, user_id[i], book_id_rating[i], rating[i])


def recomendar_lista_libros(usuarioID):
    resultado_libros_usuario = run(0, (libro_goodread), Ratings(usuarioID, libro, rating_rating),
                                   Book(libro, titulo_libro, libro_goodread))

    resultado_libros_usuario_nombre = run(0, (titulo_libro), Ratings(usuarioID, libro, rating_rating),
                                          Book(libro, titulo_libro, libro_goodread))

    # BookTags(libro_goodread, tag)
    resultado_tags_usuario = ()

    for x in resultado_libros_usuario:
        resultado_tags_usuario = resultado_tags_usuario + run(0, (tag), Book(libro, titulo_libro, x), BookTags(x, tag))

    # eliminacion de duplicados
    lista_tags = list(resultado_tags_usuario)
    lista_tags = list(dict.fromkeys(lista_tags))

    resultado = ()

    if (len(lista_tags) < 10):
        for y in lista_tags:
            resultado = resultado + run(0, (titulo_libro), BookTags(libro_goodread, y),
                                        Book(libro, titulo_libro, libro_goodread))

    else:
        for i in range(10):
            resultado = resultado + run(0, (titulo_libro), BookTags(libro_goodread, lista_tags[i]),
                                        Book(libro, titulo_libro, libro_goodread))

    # eliminacion de duplicados
    lst1 = list(resultado)
    lst1 = list(dict.fromkeys(lst1))

    # eliminacion de ya leidos
    for i in range(len(resultado_libros_usuario_nombre)):
        if resultado_libros_usuario_nombre[i] in lst1:
            lst1.remove(resultado_libros_usuario_nombre[i])

    lst_final = []

    for i in range(len(lst1)):
        lst_final.append(Libro(lst1[i]))

    return lst_final

def libros_leidos(usuarioID):
    resultado_libros_usuario_nombre = run(0, (titulo_libro), Ratings(usuarioID, libro, rating_rating), Book(libro, titulo_libro, libro_goodread))
    lista_leidos = list(resultado_libros_usuario_nombre)

    lst_leidos = []

    for i in range(len(lista_leidos)):
        lst_leidos.append(Libro(lista_leidos[i]))

    return lst_leidos

#-----------------------------------API FLASK---------------------------------------------------------------------------
def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

lst = []

lst2 = []

class UserResource(Resource):
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def post(self):
        userID = request.json['userID']

        lista_recomendados = recomendar_lista_libros(int(userID))

        lst.clear()

        lst.extend(lista_recomendados)

        return jsonify(to_dict(lst))
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def get(self):
        return jsonify(to_dict(lst))


class LibrosleidosResource(Resource):
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def post(self):
        userID = request.json['userID']

        lista_leidos = libros_leidos(int(userID))

        lst2.clear()

        lst2.extend(lista_leidos)

        return jsonify(to_dict(lst2))
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def get(self):
        return jsonify(to_dict(lst2))




api.add_resource(UserResource, '/user')
api.add_resource(LibrosleidosResource, '/libros')



if __name__ == '__main__':
    app.run(debug=True)