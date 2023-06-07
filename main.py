from spacy.lang.en import English
import numpy
from flask import Flask, render_template, request
import json
import pickle
import os
import time
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers

nlp = English()
tokenizer = nlp.tokenizer

PAD_Token = 0

app = Flask(__name__)

class voc:
    def __init__(self):
        self.num_words = 1  # 0 is reserved for padding
        self.num_tags = 0
        self.tags = {}
        self.index2tags = {}
        self.questions = {}
        self.word2index = {}
        self.response = {}

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.num_words
            self.num_words += 1

    def addTags(self, tag):
        if tag not in self.tags:
            self.tags[tag] = self.num_tags
            self.index2tags[self.num_tags] = tag
            self.num_tags += 1

    def addQuestion(self, question, answer):
        self.questions[question] = answer
        words = self.tokenization(question)
        for wrd in words:
            self.addWord(wrd)

    def tokenization(self, ques):
        tokens = tokenizer(ques)
        token_list = []
        for token in tokens:
            token_list.append(token.lemma_)
        return token_list

    def getIndexOfWord(self, word):
        return self.word2index[word]

    def getQuestionInNum(self, ques):
        words = self.tokenization(ques)
        tmp = [0 for i in range(self.num_words)]
        for wrds in words:
            tmp[self.getIndexOfWord(wrds)] = 1
        return tmp

    def getTag(self, tag):
        tmp = [0.0 for i in range(self.num_tags)]
        tmp[self.tags[tag]] = 1.0
        return tmp

    def getVocabSize(self):
        return self.num_words

    def getTagSize(self):
        return self.num_tags

    def addResponse(self, tag, responses):
        self.response[tag] = responses


def predict(ques):
    ques = data.getQuestionInNum(ques)
    ques = numpy.array(ques)
    # ques=ques/255
    ques = numpy.expand_dims(ques, axis=0)
    y_pred = model.predict(ques)
    res = numpy.argmax(y_pred, axis=1)
    return res


def getresponse(results):
    tag = data.index2tags[int(results)]
    response = data.response[tag]
    return response


def chat(inp):
    while True:
        inp_x = inp.lower()
        results = predict(inp_x)
        response = getresponse(results)
        return random.choice(response)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(chat(userText))


if __name__ == "__main__":
    model = models.load_model('mymodel.h5')

    with open("mydata.pickle", "rb") as f:
        data = pickle.load(f)

    app.run(port=5003, debug=True)
