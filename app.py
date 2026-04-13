from flask import Flask, jsonify, request
import os
from database.db import Base, engine
import sqlite3
from datetime import datetime, time, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

Base.metadata.create_all(engine)

db = sqlite3.connect("golf-sim.db", check_same_thread=False)
db.row_factory = sqlite3.Row
cursor = db.cursor()

# operating hours
start_time = time(6, 0)
end_time = time(18, 0)

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

def check_bay(bay_name):
    cursor.execute("SELECT id FROM bays WHERE name = ?", (bay_name,))
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
    bay_name = data["bay"]

    # check to see if valid timeslot
    potential_time = datetime.strptime(timeslot, "%H:%M").time()
    if potential_time < start_time or potential_time > end_time or potential_time.minute != 0:
        return jsonify({"message": "Please select a time within our operations"}), 403

    # check user first to see if they exist
    if check_user("username", username)[0] == 0:
        return jsonify({"message": "User does not exist, please create a user first"}), 403

    bay = check_bay(bay_name)
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

@app.route("/get_daily", methods=["GET"])
def get_daily_report():
    data = request.get_json()
    date = data["date"]
    bay_name = data["bay"]

    bay = check_bay(bay_name)
    if bay is None:
        return jsonify({"message": "Bay does not exist"}), 403
    
    time_index = datetime.combine(datetime.today(), time(6, 0))
    end_index = datetime.combine(datetime.today(), time(18, 0))
    daily_reservations = []

    while time_index <= end_index:
        timeslot = time_index.strftime("%H:%M")
        # got from claude, im not this good at sql
        cursor.execute("SELECT u.username FROM reservations r JOIN users u ON r.user_id = u.id WHERE r.bay_id = ? AND r.date = ? AND r.timeslot = ?", (bay["id"], date, timeslot))
        reservations = cursor.fetchall()
        daily_reservations.append({
            "timeslot": timeslot,
            "users": [user["username"] for user in reservations],
            "capacity": 2 - len(reservations)
        })
        time_index += timedelta(hours=1)
    
    return jsonify({"date": date, "bay": bay_name, "reservations": daily_reservations}), 200

@app.route("/get_monthly", methods=["GET"])
def get_monthly_report():
    data = request.get_json()
    date = data["date"]
    converted = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m")

    cursor.execute("""
        SELECT u.username, COUNT(*) as total_reservations
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        WHERE strftime('%Y-%m', substr(r.date, 7, 4) || '-' || substr(r.date, 1, 2) || '-' || substr(r.date, 4, 2)) = ?
        GROUP BY u.username
    """, (converted,)) # got from claude, im not this good at sql
    rows = cursor.fetchall()
    
    report = []
    for row in rows:
        report.append({
        "username": row["username"],
        "total_reservations": row["total_reservations"],
        "total_hours": row["total_reservations"]
    })

    return jsonify({"month": date, "report": report}), 200

if __name__ == "__main__":
    app.run(debug=True)