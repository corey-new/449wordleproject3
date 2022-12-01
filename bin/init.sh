#!/bin/sh

echo "Initializing databases..."
sqlite3 ./var/users.db < ./share/users.sql
sqlite3 ./var/games.db < ./share/games.sql
echo "Successfully initialized database."
echo "Populating games database with words..."
python3 ./share/populate.py