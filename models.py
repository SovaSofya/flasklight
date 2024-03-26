from flask_sqlalchemy import SQLAlchemy
import gensim
# from sqlalchemy import ForeignKey, PrimaryKeyConstraint
# from sqlalchemy.orm import relationship
# import sys
# import os
# import wget
import re
from ufal.udpipe import Model, Pipeline
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pymorphy3 import MorphAnalyzer
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'  # имя таблицы
    id = db.Column(db.Integer, primary_key=True)  # имя колонки = специальный тип (тип данных, первичный ключ)
    ask = db.Column(db.Text)
    vector = db.Column(db.Text)
    theme_user = db.Column(db.Integer, db.ForeignKey("themes.id"))
    answer_id = db.Column(db.Integer, db.ForeignKey("poems.id"))


class Poems(db.Model):
    __tablename__ = 'poems'  # имя таблицы
    id = db.Column(db.Integer, primary_key=True)  # имя колонки = специальный тип (тип данных, первичный ключ)
    poem = db.Column(db.Text)
    theme_id = db.Column(db.Integer, db.ForeignKey("themes.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    vector = db.Column(db.Text)
    popularity = db.Column(db.Integer)
    users_poem = db.relationship("User", backref="poem", lazy="dynamic")


class Themes(db.Model):
    __tablename__ = 'themes'  # имя таблицы
    id = db.Column(db.Integer, primary_key=True)  # имя колонки = специальный тип (тип данных, первичный ключ)
    theme = db.Column(db.Text)
    vector_theme = db.Column(db.Text)
    poems_theme = db.relationship("Poems", backref="themeofpoem", uselist=False)
    users_theme = db.relationship("User", backref="themeofuser", uselist=False)


class Authors(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    born = db.Column(db.Integer)
    died = db.Column(db.Integer)



def cos_comparison(uservector, df):
    c = 0.0
    for x in df:
        compare = np.asarray(list((map(float, x.split(" ")))))
        if cosine_similarity(uservector.reshape(1, -1), compare.reshape(1, -1))[0][0] >= c:
            c = cosine_similarity(uservector.reshape(1, -1), compare.reshape(1, -1))[0][0]
            ans = x
    return ans



morph = MorphAnalyzer()
from wordcloud import WordCloud
def lemmatize(x):
    stops = set(stopwords.words('russian') + ['это', 'весь', 'который', 'мочь', 'свой'])
    if type(x) != str:
        return ""
    text = wordpunct_tokenize(x)
    result = []
    for word in text:
        if word.isalpha():
            nf = morph.parse(word)[0].normal_form
            if nf not in stops:
                result.append(nf)
    return " ".join(result)