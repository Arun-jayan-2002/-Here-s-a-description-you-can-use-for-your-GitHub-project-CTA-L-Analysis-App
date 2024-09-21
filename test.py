import sqlite3

# Connect to the database
conn = sqlite3.connect('cta_database.db')
cursor = conn.cursor()

# Query data from the Stations table
cursor.execute("SELECT * FROM Stations")
stations = cursor.fetchall()
print("Stations:", stations)

# Query data from the Stops table
cursor.execute("SELECT * FROM Stops")
stops = cursor.fetchall()
print("Stops:", stops)

# Query data from the Ridership table
cursor.execute("SELECT * FROM Ridership")
ridership = cursor.fetchall()
print("Ridership:", ridership)

cursor.execute("SELECT Station_ID, Station_Name FROM Stations")
stations = cursor.fetchall()
print("Stations in the database:", stations)


# Close connection
conn.close()
