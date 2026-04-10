from flask import Flask, jsonify, request
import os
from database.db import Base, engine

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

Base.metadata.create_all(engine)

@app.route("/")
def index():
    return jsonify({"message": "Golf Simulator Reservation API"})

if __name__ == "__main__":
    app.run(debug=True)