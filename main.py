
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

#-------------------------------Clase Libro-----------------------------------------------------------------------------

class Libro:
    def __init__(self, nombre):
        self.nombre = nombre

#--------------------------------clase sistema experto------------------------------------------------------------------
class SistemaExperto:
    def __init__(self):
        # Base del conocimiento
        self.usuario = var()
        self.libro = var()
        self.libro_goodread = var()
        self.autores = var()
        self.titulo_libro = var()
        self.tag = var()
        self.tag_nombre = var()
        self.rating_rating = var()

        self.Book = Relation()
        self.BookTags = Relation()
        self.Tags = Relation()
        self.Ratings = Relation()

        for i in range(len(book_id_book)):
            fact(self.Book, book_id_book[i], title_book[i], goodreads_book_id_book[i])

        for i in range(len(goodreads_book_id_book_tags)):
            fact(self.BookTags, goodreads_book_id_book_tags[i], tag_id_book_tags[i])

        for i in range(len(tag_id_tags)):
            fact(self.Tags, tag_id_tags[i], tag_name[i])

        for i in range(len(rating)):
            fact(self.Ratings, user_id[i], book_id_rating[i], rating[i])

    #
    def leyoEstosLibro(self, x, y):
        return conde((self.Ratings(x, self.libro, self.rating_rating), self.Book(self.libro, self.titulo_libro, y)))

    # Igual que el de arriba solo que devolvera el titulo
    def leyoEstosLibrosTitulo(self, x, y):
        return conde((self.Ratings(x, self.libro, self.rating_rating), self.Book(self.libro, y, self.libro_goodread)))

    def esteLibroTieneEstosTags(self, x, y):
        return conde((self.Book(self.libro, self.titulo_libro, x), self.BookTags(x, y)))

    def estosTagsEstanPresentesEnEstosLibros(self, x, y):
        return conde((self.BookTags(self.libro_goodread, y), self.Book(self.libro, x, self.libro_goodread)))

    def recomendar_lista_libros(self, usuarioID):
        resultado_libros_usuario = run(0, self.libro_goodread, self.leyoEstosLibro(usuarioID, self.libro_goodread))

        resultado_libros_usuario_nombre = run(0, self.titulo_libro, self.leyoEstosLibrosTitulo(usuarioID, self.titulo_libro))

        # BookTags(libro_goodread, tag)
        resultado_tags_usuario = ()

        for x in resultado_libros_usuario:
            resultado_tags_usuario = resultado_tags_usuario + run(0, self.tag, self.esteLibroTieneEstosTags(x, self.tag))

        # eliminacion de duplicados
        lista_tags = list(resultado_tags_usuario)
        lista_tags = list(dict.fromkeys(lista_tags))

        resultado = ()

        if len(lista_tags) < 10:
            for y in lista_tags:
                resultado = resultado + run(0, self.titulo_libro, self.estosTagsEstanPresentesEnEstosLibros(self.titulo_libro, y))
        else:
            for i in range(10):
                resultado = resultado + run(0, self.titulo_libro, self.estosTagsEstanPresentesEnEstosLibros(self.titulo_libro, lista_tags[i]))

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

    def retornar_libros_leidos(self, usuarioID):
        resultado_libros_usuario_nombre = run(0, self.titulo_libro, self.leyoEstosLibrosTitulo(usuarioID, self.titulo_libro))

        lst_leidos = []

        for i in range(len(resultado_libros_usuario_nombre)):
            lst_leidos.append(Libro(resultado_libros_usuario_nombre[i]))

        #lst_leidos = list(resultado_libros_usuario_nombre)
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

        se = SistemaExperto()

        lista_recomendados = se.recomendar_lista_libros(int(userID))

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

        se = SistemaExperto()

        lista_leidos = se.retornar_libros_leidos(int(userID))

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