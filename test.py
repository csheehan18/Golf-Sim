import pytest
from app import app
from app import db


username = "csheehan"
date = "4/13/2026"
timeslot = "12:30"
bay = "Bay A"

@pytest.fixture(autouse=True)
def clean_db():
    cursor = db.cursor()
    cursor.execute("DELETE FROM reservations")
    cursor.execute("DELETE FROM users")
    db.commit()
    yield

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    res = client.get("/")
    assert res.json["message"] == "Golf Simulator Reservation API"
    assert res.status_code == 200

def test_user_does_not_exist(client):
    res = client.post("/book", json={"username": username, "date": date, "timeslot": timeslot, "bay" : bay})
    assert res.json["message"] == "User does not exist, please create a user first"
    assert res.status_code == 403

def test_add_user(client):
    res = client.post("/add_user", json={"username": username, "email" : "csheehan118@gmail.com", "name" : "Conner Sheehan"})
    assert res.json["message"] == "User csheehan has successfully been created"
    assert res.status_code == 200

def add_user(client):
    client.post("/add_user", json={"username": username, "email" : "csheehan118@gmail.com", "name" : "Conner Sheehan"})

def add_reservation(client):
    client.post("/book", json={"username": username, "date": date, "timeslot": timeslot, "bay": bay})

def test_book_reservation(client):
    add_user(client)
    res = client.post("/book", json={"username": username, "date": date, "timeslot": timeslot, "bay": bay})
    assert res.json["message"] == f"User {username} has successfully book reservation for {date} at {timeslot}"
    assert res.status_code == 200

def test_book_reservation_at_same_time(client):
    add_user(client)
    add_reservation(client)
    res = client.post("/book", json={"username": username, "date": date, "timeslot": timeslot, "bay": bay})
    assert res.json["message"] == f"User has another reservation already booked with same timeslot on Date: {date}"
    assert res.status_code == 403

def test_bad_reservation_time(client):
    add_user(client)
    res = client.post("/book", json={"username": username, "date": date, "timeslot": "01:00", "bay": bay})
    assert res.json["message"] == "Please select a time within our operations"
    assert res.status_code == 403

def test_bad__bay_reservation(client):
    add_user(client)
    res = client.post("/book", json={"username": username, "date": date, "timeslot": timeslot, "bay": "Bay G"})
    assert res.json["message"] == "Bay does not exist"
    assert res.status_code == 403

def test_reservation_deletion(client):
    add_user(client)
    add_reservation(client)
    res = client.delete("/cancel_book", json={"username": username, "date": date, "timeslot": timeslot})
    assert res.json["message"] == "Successfully removed reservation"
    assert res.status_code == 200

def test_no_reservation_delete(client):
    add_user(client)
    res = client.delete("/cancel_book", json={"username": username, "date": date, "timeslot": timeslot})
    assert res.json["message"] == "No reservation exists"
    assert res.status_code == 403

def test_no_user_reservation_delete(client):
    res = client.delete("/cancel_book", json={"username": username, "date": date, "timeslot": timeslot})
    assert res.json["message"] == "User does not exist, nothing has been done"
    assert res.status_code == 403
