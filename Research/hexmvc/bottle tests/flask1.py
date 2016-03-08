#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!@!!! ok"

if __name__ == "__main__":
    app.run()
    