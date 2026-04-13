from flask import Flask, jsonify, request
import os
from database.db import Base, engine
import pandas as pd
import sqlite3
from datetime import datetime, time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

Base.metadata.create_all(engine)

db = sqlite3.connect("golf-sim.db", check_same_thread=False)
db.row_factory = sqlite3.Row
cursor = db.cursor()

# Creating 4 bays to start
bays = [("Bay A",), ("Bay B",), ("Bay C",), ("Bay D",)]
cursor.executemany("INSERT OR IGNORE INTO bays (name) VALUES (?)", bays)
db.commit()

def check_user(type, username):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE {type} = ?)", (username,))
    return cursor.fetchone()

def check_reservation(id, date, timeslot):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM reservations WHERE user_id = ? AND date = ? AND timeslot = ?)", (id, date, timeslot))
    return cursor.fetchone()

def get_user(username):
    # now get real user
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

@app.route("/")
def index():
    return jsonify({"message": "Golf Simulator Reservation API"})

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    username = data["username"]
    name = data["name"]
    email = data["email"]
    name_accepted = check_user("username", username)
    email_accepted = check_user("email", email)

    if name_accepted[0] == 1:
        return jsonify({"message": "Username already exists, please try a different one"}), 403
    elif email_accepted[0] == 1:
        return jsonify({"message": "Email already exists, please use that account"}), 403
    
    cursor.execute("INSERT INTO users (username, name, email) VALUES (?, ?, ?)", (username, name, email))
    db.commit()

    return jsonify({"message": f"User {username} has successfully been created"}), 200

@app.route("/book", methods=["POST"])
def book_reservation():
    data = request.get_json()
    username = data["username"]
    date = data["date"]
    timeslot = data["timeslot"]
    bayname = data["bay"]

    # check to see if valid timeslot
    potential_time = datetime.strptime(timeslot, "%H:%M").time()
    if potential_time < time(6, 0) or potential_time > time(18, 0):
        return jsonify({"message": "Please select a time within our operations"}), 403

    # check user first to see if they exist
    if check_user("username", username)[0] == 0:
        return jsonify({"message": "User does not exist, please create a user first"}), 403

    cursor.execute("SELECT id FROM bays WHERE name = ?", (bayname,))
    bay = cursor.fetchone()
    if bay is None:
        return jsonify({"message": "Bay does not exist"}), 403
    
    # now get real user
    user = get_user(username)
    
    # now check if this person is already in this timeslot
    book_reserv = check_reservation(user["id"], date, timeslot)
    if book_reserv[0] == 1:
        return jsonify({"message": f"User has another reservation already booked with same timeslot on Date: {date}"}), 403

    # now check if two users are already booked into that slot
    cursor.execute("SELECT COUNT(*) FROM reservations WHERE bay_id = ? AND date = ? AND timeslot = ? ", (bay["id"], date, timeslot))
    count = cursor.fetchone()[0]
    if count == 2:
        return jsonify({"message": "Reservation is full at that time"}), 403
    
    cursor.execute("INSERT INTO reservations (user_id, date, timeslot, bay_id) VALUES (?, ?, ?, ?)", (user["id"], date, timeslot, bay["id"]))
    db.commit()

    return jsonify({"message": f"User {username} has successfully book reservation for {date} at {timeslot}"}), 200

@app.route("/cancel_book", methods=["DELETE"])
def cancel_reservation():
    data = request.get_json()
    username = data["username"]
    date = data["date"]
    timeslot = data["timeslot"]

    # check user first to see if they exist
    if check_user("username", username)[0] == 0:
        return jsonify({"message": "User does not exist, nothing has been done"}), 403
    
    user = get_user(username)
    book_reserv = check_reservation(user["id"], date, timeslot)
    if book_reserv[0] == 0:
        return jsonify({"message": "No reservation exists"}), 403
    
    cursor.execute("SELECT id FROM reservations WHERE user_id = ? AND date = ? AND timeslot = ?", (user["id"], date, timeslot))
    reservation = cursor.fetchone()

    cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation["id"],))
    db.commit()

    return jsonify({"message": "Successfully removed reservation"}), 200


if __name__ == "__main__":
    app.run(debug=True)