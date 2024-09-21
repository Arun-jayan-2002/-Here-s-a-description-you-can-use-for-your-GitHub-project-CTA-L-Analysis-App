import sqlite3
import math
import matplotlib.pyplot as plt
import matplotlib

# Ensure the correct backend is used for plotting
matplotlib.use('TkAgg')

def connect_db():
    return sqlite3.connect('cta_database.db')

def display_statistics(cursor):
    cursor.execute("SELECT COUNT(DISTINCT Station_ID), COUNT(*), MIN(Ride_Date), MAX(Ride_Date) FROM Ridership")
    stats = cursor.fetchone()
    
    print("Welcome to CTA L analysis app")
    
    if stats:
        print(f"General Statistics: # of stations: {stats[0]} # of ride entries: {stats[1]} date range: {stats[2]} - {stats[3]}")

def find_stations(cursor, partial_name):
    cursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?", (partial_name,))
    results = cursor.fetchall()
    
    if results:
        for station in results:
            print(f"{station[0]} : {station[1]}")
    else:
        print("No stations found...")

def ridership_percentages(cursor, station_name):
    cursor.execute("SELECT SUM(Num_Riders), Type_of_Day FROM Ridership WHERE Station_ID IN (SELECT Station_ID FROM Stations WHERE Station_Name = ?) GROUP BY Type_of_Day", (station_name,))
    results = cursor.fetchall()
    
    total_riders = sum(count for count, _ in results)
    
    if total_riders == 0:
        print("No data found...")
        return
    
    percentages = {}
    for count, day_type in results:
        percentages[day_type] = (count, (count / total_riders) * 100)
    
    print(f"Percentage of ridership for the {station_name} station:")
    for day_type, (count, percentage) in percentages.items():
        print(f"{day_type} ridership: {count:,} ({percentage:.2f}%)")
    print(f"Total ridership: {total_riders:,}")

def weekday_ridership(cursor):
    cursor.execute("""SELECT s.Station_Name, SUM(r.Num_Riders) AS Total_Riders 
                      FROM Ridership r 
                      JOIN Stations s ON r.Station_ID = s.Station_ID 
                      WHERE r.Type_of_Day = 'W' 
                      GROUP BY s.Station_Name 
                      ORDER BY Total_Riders DESC""")
    
    results = cursor.fetchall()
    total_weekday_riders = sum(count for _, count in results)
    
    for station_name, count in results:
        percentage = (count / total_weekday_riders) * 100 if total_weekday_riders > 0 else 0
        print(f"{station_name} : {count:,} ({percentage:.2f}%)")

def stops_by_line_color(cursor, line_color, direction):
    # Check if the line color exists
    cursor.execute("SELECT COUNT(*) FROM Lines WHERE LOWER(Color) = LOWER(?)", (line_color,))
    line_count = cursor.fetchone()[0]
    
    if line_count == 0:
        print(f"**No such line '{line_color}'...")
        return
    
    # Get the stops for the specified line color and direction
    cursor.execute("""SELECT s.Stop_Name 
                      FROM Stops s 
                      JOIN StopDetails sd ON s.Stop_ID = sd.Stop_ID 
                      JOIN Lines l ON sd.Line_ID = l.Line_ID 
                      WHERE LOWER(l.Color) = LOWER(?) AND UPPER(s.Direction) = UPPER(?)
                      ORDER BY s.Stop_Name""", (line_color, direction))
    
    results = cursor.fetchall()
    
    if results:
        print(f"Stops for the {line_color} line going {direction}:")
        for stop in results:
            print(stop[0])
    else:
        print(f"No stops found for the {line_color} line going {direction}...")

def stops_count_by_color(cursor):
    cursor.execute("""SELECT l.Color, s.Direction, COUNT(s.Stop_ID) AS Stop_Count 
                      FROM Stops s 
                      JOIN StopDetails sd ON s.Stop_ID = sd.Stop_ID 
                      JOIN Lines l ON sd.Line_ID = l.Line_ID 
                      GROUP BY l.Color, s.Direction 
                      ORDER BY l.Color, s.Direction""")
    
    results = cursor.fetchall()
    total_stops = sum(count for _, _, count in results)
    
    for color, direction, count in results:
        percentage = (count / total_stops) * 100 if total_stops > 0 else 0
        print(f"{color} going {direction} : {count} ({percentage:.2f}%)")

def yearly_ridership(cursor, station_name):
    cursor.execute("""SELECT strftime('%Y', Ride_Date), SUM(Num_Riders) 
                      FROM Ridership 
                      WHERE Station_ID IN (SELECT Station_ID FROM Stations WHERE Station_Name LIKE ?) 
                      GROUP BY strftime('%Y', Ride_Date)
                      ORDER BY strftime('%Y', Ride_Date)""", (station_name,))
    
    results = cursor.fetchall()
    
    if not results:
        print("**No station found...")
        return
    
    print(f"Yearly Ridership at {station_name}:")
    for year, total in results:
        print(f"{year} : {total:,}")

    # Prepare for plotting
    years, totals = zip(*results)

    # Prompt to plot data
    plot_option = input("Plot? (y/n): ")
    if plot_option.lower() == 'y':
        plt.figure(figsize=(10, 5))
        plt.plot(years, totals, marker='o', label='Total Ridership')
        plt.xlabel('Year')
        plt.ylabel('Total Ridership')
        plt.title(f'Yearly Ridership at {station_name}')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

def monthly_ridership(cursor):
    station_name = input("Enter a station name (wildcards _ and %): ")
    year = input("Enter a year: ")

    # Query to find distinct stations matching the provided name
    cursor.execute("""
        SELECT DISTINCT s.Station_ID, s.Station_Name
        FROM Stations s
        JOIN Ridership r ON s.Station_ID = r.Station_ID
        WHERE s.Station_Name LIKE ?
        """, (station_name,))
    
    matching_stations = cursor.fetchall()

    # Handle cases where no station is found or multiple stations are found
    if len(matching_stations) == 0:
        print("**No station found...")
        return
    elif len(matching_stations) > 1:
        print("**Multiple stations found...")
        for idx, station in enumerate(matching_stations, start=1):
            print(f"{idx}: {station[1]}")
        
        choice = input("Choose a station number: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(matching_stations):
            print("Invalid choice. Exiting...")
            return

        station_id = matching_stations[int(choice) - 1][0]
        station_full_name = matching_stations[int(choice) - 1][1]
    else:
        station_id = matching_stations[0][0]
        station_full_name = matching_stations[0][1]

    print(f"\nMonthly Ridership at {station_full_name} for {year}")

    # Fetch monthly ridership data for the selected station and year
    cursor.execute("""
        SELECT strftime('%m', Ride_Date) AS Month, SUM(Num_Riders) AS Total_Riders
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Month
        ORDER BY Month
    """, (station_id, year))

    results = cursor.fetchall()

    # Prepare data for all months (filling missing months with zeroes)
    months = [f"{i:02d}/{year}" for i in range(1, 13)]  # Generate list of months 01/202X - 12/202X
    totals = {f"{i:02d}": 0 for i in range(1, 13)}  # Initialize totals dictionary with zeroes

    # Update totals with actual ridership data
    for month, total in results:
        totals[month] = total

    # Print the results for each month
    for month in months:
        print(f"{month} : {totals[month[:2]]:,}")  # Use the first two characters for the month key

    # Ask the user if they want to plot the results
    plot_response = input("Plot? (y/n): ")
    if plot_response.lower() == 'y':
        # Plotting the data as a simple line chart
        plt.figure(figsize=(8, 6))  # Set figure size for better readability
        plt.plot(months, [totals[month[:2]] for month in months], marker='o', linestyle='-', color='b', label='Ridership')  # Draw the line with markers
        plt.xlabel('Month')
        plt.ylabel('Total Ridership')
        plt.title(f'Monthly Ridership at {station_full_name} for {year}')
        plt.xticks(rotation=45)
        plt.legend()  # Add a legend to the plot
        plt.grid(True)  # Add grid lines for clarity
        plt.tight_layout()  # Ensure everything fits within the plot
        plt.show()  # Display the plot
    else:
        print(f"No data found for {station_full_name} in {year}.")


def daily_ridership_comparison(cursor):
    year = input("Year to compare against? ")
    station_1_name = input("Enter station 1 (wildcards _ and %): ")
    station_2_name = input("Enter station 2 (wildcards _ and %): ")

    # Query to find distinct stations matching station 1
    cursor.execute("""
        SELECT DISTINCT s.Station_ID, s.Station_Name
        FROM Stations s
        JOIN Ridership r ON s.Station_ID = r.Station_ID
        WHERE s.Station_Name LIKE ?
    """, (station_1_name,))
    station_1_matches = cursor.fetchall()

    if len(station_1_matches) == 0:
        print(f"**No station found for {station_1_name}")
        return
    elif len(station_1_matches) > 1:
        print("**Multiple stations found for station 1...")
        for idx, station in enumerate(station_1_matches, start=1):
            print(f"{idx}: {station[1]}")
        choice = input("Choose a station number for station 1: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(station_1_matches):
            print("Invalid choice. Exiting...")
            return
        station_1_id = station_1_matches[int(choice) - 1][0]
        station_1_full_name = station_1_matches[int(choice) - 1][1]
    else:
        station_1_id = station_1_matches[0][0]
        station_1_full_name = station_1_matches[0][1]

    # Query to find distinct stations matching station 2
    cursor.execute("""
        SELECT DISTINCT s.Station_ID, s.Station_Name
        FROM Stations s
        JOIN Ridership r ON s.Station_ID = r.Station_ID
        WHERE s.Station_Name LIKE ?
    """, (station_2_name,))
    station_2_matches = cursor.fetchall()

    if len(station_2_matches) == 0:
        print(f"**No station found for {station_2_name}")
        return
    elif len(station_2_matches) > 1:
        print("**Multiple stations found for station 2...")
        for idx, station in enumerate(station_2_matches, start=1):
            print(f"{idx}: {station[1]}")
        choice = input("Choose a station number for station 2: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(station_2_matches):
            print("Invalid choice. Exiting...")
            return
        station_2_id = station_2_matches[int(choice) - 1][0]
        station_2_full_name = station_2_matches[int(choice) - 1][1]
    else:
        station_2_id = station_2_matches[0][0]
        station_2_full_name = station_2_matches[0][1]

    # Fetch daily ridership data for both stations
    cursor.execute("""
        SELECT Ride_Date, SUM(Num_Riders) AS Total_Riders
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date
    """, (station_1_id, year))
    station_1_data = cursor.fetchall()

    cursor.execute("""
        SELECT Ride_Date, SUM(Num_Riders) AS Total_Riders
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date
    """, (station_2_id, year))
    station_2_data = cursor.fetchall()

    # Print first 5 and last 5 records for each station
    print(f"Station 1: {station_1_id} {station_1_full_name}")
    if station_1_data:
        for entry in station_1_data[:5]:  # First 5 days
            print(f"{entry[0]} {entry[1]:,}")
        for entry in station_1_data[-5:]:  # Last 5 days
            print(f"{entry[0]} {entry[1]:,}")
    else:
        print(f"No data found for {station_1_full_name} in {year}.")

    print(f"\nStation 2: {station_2_id} {station_2_full_name}")
    if station_2_data:
        for entry in station_2_data[:5]:  # First 5 days
            print(f"{entry[0]} {entry[1]:,}")
        for entry in station_2_data[-5:]:  # Last 5 days
            print(f"{entry[0]} {entry[1]:,}")
    else:
        print(f"No data found for {station_2_full_name} in {year}.")

    # Ask if the user wants to plot the results
    plot_response = input("Plot? (y/n): ")
    if plot_response.lower() == 'y':
        # Extract dates and ridership numbers
        station_1_dates = [entry[0] for entry in station_1_data]
        station_1_ridership = [entry[1] for entry in station_1_data]

        station_2_dates = [entry[0] for entry in station_2_data]
        station_2_ridership = [entry[1] for entry in station_2_data]

        # Plot the data
        plt.figure(figsize=(10, 6))  # Adjust the figure size
        plt.plot(station_1_dates, station_1_ridership, label=station_1_full_name, marker='o')
        plt.plot(station_2_dates, station_2_ridership, label=station_2_full_name, marker='x')

        # Customize the plot
        plt.xlabel('Date')
        plt.ylabel('Ridership')
        plt.title(f'Daily Ridership Comparison for {year}')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Function to check bounds and find stations within a mile



def get_stations_within_mile(cursor, latitude, longitude):
    # Calculate the latitude and longitude boundaries for 1 mile
    radius = 1  # 1 mile
    min_latitude = latitude - (radius / 69)
    max_latitude = latitude + (radius / 69)
    min_longitude = longitude - (radius / (69 * math.cos(math.radians(latitude))))
    max_longitude = longitude + (radius / (69 * math.cos(math.radians(latitude))))

    # Query to select stops (or stations) within the specified boundaries
    query = """
    SELECT Stop_Name, latitude, longitude FROM Stops
    WHERE latitude BETWEEN ? AND ?
    AND longitude BETWEEN ? AND ?
    """
    
    cursor.execute(query, (min_latitude, max_latitude, min_longitude, max_longitude))
    
    # Fetching results
    rows = cursor.fetchall()
    
    if rows:
        print("List of Stations Within a Mile:")
        x = []
        y = []
        for row in rows:
            print(f"{row[0]} : ({row[1]}, {row[2]})")
            x.append(row[2])  # longitude
            y.append(row[1])  # latitude

        # Plot option
        plot_choice = input("Plot? (y/n) ")
        if plot_choice.lower() == 'y':
            plot_stations_on_map(x, y)
    else:
        print("No stops found within the specified area.")

def plot_stations_on_map(x, y):
    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  # area covered by the map
    plt.imshow(image, extent=xydims)
    plt.title("Stations within a Mile")
    plt.plot(x, y, 'ro')  # 'ro' for red points
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    
    # Annotate each point with station name
    for (longitude, latitude) in zip(x, y):
        plt.annotate(f"({latitude}, {longitude})", (longitude, latitude))

    plt.show()


def main():
    conn = connect_db()
    cursor = conn.cursor()

   

    # Display general statistics
    display_statistics(cursor)

    while True:
        command = input("Please enter a command (1-9,x to exit): ")
        
        if command == "1":
            partial_name = input("Enter partial station name (wildcards _ and %): ")
            find_stations(cursor, partial_name)
        
        elif command == "2":
            station_name = input("Enter the name of the station you would like to analyze: ")
            ridership_percentages(cursor, station_name)
        
        elif command == "3":
            weekday_ridership(cursor)
        
        elif command == "4":
            line_color = input("Enter a line color (e.g. Red or Yellow): ")
            direction = input("Enter a direction (N/S/W/E): ")
            stops_by_line_color(cursor, line_color, direction)
        
        elif command == "5":
            stops_count_by_color(cursor)
        
        elif command == "6":
            station_name = input("Enter a station name (wildcards _ and %): ")
            yearly_ridership(cursor, station_name)
        
        elif command == "7":  # Monthly ridership
            monthly_ridership(cursor)

        elif command == "8":  # Daily ridership comparison
            daily_ridership_comparison(cursor)

        elif command == '9':
            latitude = float(input("Enter a latitude: "))
            longitude = float(input("Enter a longitude: "))
            get_stations_within_mile(cursor, latitude, longitude)

        elif command.lower() == 'x':
            break

    cursor.close()  # Close the cursor
    conn.close()    # Close the database connection

if __name__ == "__main__":
    main()


