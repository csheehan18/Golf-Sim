# Golf Simulator Reservation API System
Hi!

This was all done in python using flask as the framework as well.

Libraries used
- Flask, jsonify, request
- os
- database.db import Base, engine
- sqlite3
- datetime import datetime, time, timedelta
- pytest
- sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String
- sqlalchemy.orm import declarative_base
- sqlalchemy import ForeignKey

# CALLS (Everything expects a string) <br>
POST
- /add_user (Expecting: username, name, email)
- /book (Expecting: username, date, timeslot, bay_name)

GET
- /get_daily (Expecting: date, bay_name)
- /get_monthly (Expecting: date) (I like the format 04/13/2026 so thats what it should be in)

DELETE
- /cancel_book (Expecting: username. date, timeslot)

# How to Run
- This should be as easy as running "python app.py"
- Also the to run the tests do "pytest test.py -v"
- make sure you have the proper libraries installed (I would've added the enviroment but the consensus is its bad to do that?)

# My Final Thoughts
Im overall very happy with the design of this and how functional it is. 
I started initially with the database to plan out how I wanted this all to look which was helpful. In hindsight with the database I didn't 
need the foreign key or UniqueConstraint's as I handled most of it anyway with the code checks. It is nice though if I missed something
code wise the database is smart enough to ignore me. I do think sqlalchemy is the best library for the job as it allows for 
a very pythonic way of creating schemas. I focused a good chunk of time on testing specifically making my own tests. That way since
I don't have a UI I could quickly check my work and also any future things I added. Its easy to setup and worth the effort. I was a little lite in testing
the reports but I don't see why they would fail. I had initially debated adding UI but decided against it as it would've taken significantly longer to finish.
This was a fun project and its actually similar to another project I did when I was younger for my dad where I automated his golf reservations using Selenium.
I love designing and creating software and I think thats where I thrive so hopefully this code is a good read. Thanks!
