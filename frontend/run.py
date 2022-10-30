from flask import Flask, render_template, request, redirect, url_for
import sys


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        query = request.form['query']
        topk = request.form['topk']
        #resultado = result(query,topk)
        #print(resultado)
        
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)