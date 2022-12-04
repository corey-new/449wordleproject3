#!/bin/sh

echo "Initializing databases..."
sqlite3 ./var/users.db < ./share/users.sql
sqlite3 ./var/primary/mount/games.db < ./share/games.sql
echo "Successfully initialized database."

echo "Populating valid words..."
python3 ./share/populate.py
echo "Successfully populated valid words."