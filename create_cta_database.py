import sqlite3
import math

def create_database():
    # Connect to the SQLite database (this will create the database file)
    conn = sqlite3.connect('cta_database.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stations (
        Station_ID INTEGER PRIMARY KEY,
        Station_Name TEXT NOT NULL UNIQUE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stops (
        Stop_ID INTEGER PRIMARY KEY,
        Station_ID INTEGER,
        Stop_Name TEXT NOT NULL,
        Direction TEXT NOT NULL CHECK(Direction IN ('N', 'E', 'S', 'W')),
        ADA INTEGER CHECK(ADA IN (0, 1)),
        Latitude REAL,
        Longitude REAL,
        FOREIGN KEY (Station_ID) REFERENCES Stations(Station_ID)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Lines (
        Line_ID INTEGER PRIMARY KEY,
        Color TEXT NOT NULL UNIQUE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS StopDetails (
        StopDetail_ID INTEGER PRIMARY KEY,
        Stop_ID INTEGER,
        Line_ID INTEGER,
        FOREIGN KEY (Stop_ID) REFERENCES Stops(Stop_ID),
        FOREIGN KEY (Line_ID) REFERENCES Lines(Line_ID),
        UNIQUE (Stop_ID, Line_ID)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ridership (
        Ride_ID INTEGER PRIMARY KEY,
        Station_ID INTEGER,
        Ride_Date TEXT,
        Num_Riders INTEGER,
        Type_of_Day TEXT CHECK(Type_of_Day IN ('W', 'A', 'U')),
        FOREIGN KEY (Station_ID) REFERENCES Stations(Station_ID)
    );
    ''')

    # Insert sample data into Stations
    stations = [
        ('UIC-Halsted',),
        ('Clark/Lake',),
        ('Sheridan',),
        ('Union Station',)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO Stations (Station_Name) VALUES (?)", stations)

    # Insert sample data into Stops
    stops = [
        (1, 'Stop 1', 'N', 1, 41.8721, -87.6505),
        (1, 'Stop 2', 'S', 0, 41.8722, -87.6506),
        (2, 'Stop 3', 'E', 1, 41.8839, -87.6322),
        (2, 'Stop 4', 'W', 0, 41.8840, -87.6323),
        (3, 'Stop 5', 'N', 1, 41.9470, -87.6550),
        (4, 'Stop 6', 'E', 1, 41.8795, -87.6320)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO Stops (Station_ID, Stop_Name, Direction, ADA, Latitude, Longitude) VALUES (?, ?, ?, ?, ?, ?)", stops)

    # Insert sample data into Lines
    lines = [
        ('Red',),
        ('Blue',),
        ('Yellow',)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO Lines (Color) VALUES (?)", lines)

    # Insert sample data into StopDetails
    stop_details = [
        (1, 1), 
        (2, 1), 
        (3, 2), 
        (4, 3), 
        (5, 2), 
        (6, 1)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO StopDetails (Stop_ID, Line_ID) VALUES (?, ?)", stop_details)

    # Insert sample data into Ridership
    ridership_data = [
        (1, '2021-01-01', 1143302, 'W'),
        (1, '2021-01-02', 1350077, 'W'),
        (1, '2021-01-03', 1398751, 'W'),
        (1, '2021-01-04', 1364987, 'W'),
        (1, '2021-01-05', 1414985, 'W'),
        (1, '2021-01-06', 1417008, 'W'),
        (1, '2021-01-07', 1286209, 'W'),
        (1, '2021-01-08', 1406969, 'W'),
        (1, '2021-01-09', 1340464, 'W'),
        (1, '2021-01-10', 1461571, 'W'),
        (1, '2021-01-11', 1653511, 'W'),
        (1, '2021-01-12', 1726553, 'W'),
        (1, '2021-01-13', 1715302, 'W'),
        (1, '2021-01-14', 1695108, 'W'),
        (1, '2021-01-15', 1676810, 'W'),
        (1, '2021-01-16', 1725557, 'W'),
        (1, '2021-01-17', 1702964, 'W'),
        (1, '2021-01-18', 1722221, 'W'),
        (1, '2021-01-19', 1729039, 'W'),
        (1, '2021-01-20', 524093, 'W'),
        (1, '2021-01-21', 157614, 'W'),
        (1, '2022-01-01', 1650000, 'W'),  # Example year 2022
        (1, '2022-01-02', 1500000, 'W'),  # Example year 2022
        (1, '2022-01-03', 1600000, 'W'),  # Example year 2022
        (2, '2021-01-01', 800, 'W'),      # Additional station
        (3, '2021-01-02', 600, 'W'),      # Additional station
        (2, '2021-01-03', 1200, 'W')       # Additional station
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO Ridership (Station_ID, Ride_Date, Num_Riders, Type_of_Day) VALUES (?, ?, ?, ?)", ridership_data)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()

