import os
from time import time

from flask import Flask, send_file, request

from novel import Novel

app = Flask(__name__)

DATA = "data"


@app.route("/ping")
def ping():
    return "Ok"


@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        url = request.json["url"]
    except KeyError:
        return "Missing url in request", 400

    try:
        d = f"{DATA}/{time()}"
        os.mkdir(d)
        fname = Novel(url).collect(d)
        return send_file(os.path.join(d, fname))
    except Exception as e:
        print(e)
        return "Failed to scrape book", 400


if __name__ == "__main__":
    app.run(host='0.0.0.0')
