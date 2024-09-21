CTA L Analysis App

 This project is a command-line application built with Python and SQLite to analyze ridership data from the CTA (Chicago Transit Authority) L train system. It offers various tools and functionalities for querying, analyzing, and visualizing the ridership patterns across different train stations, lines, and days. The app provides a user-friendly interface to retrieve statistics and detailed data for specific stations or lines, and even compares ridership across multiple stations.
 
Key Features:
1. General Statistics: Displays an overview of the total number of stations, entries in the ridership dataset, and the date range of the data.
2. Station Search: Allows users to search for stations by a partial name.
3. Ridership Percentages: Analyzes and displays the ridership percentage based on the type of day (weekday, weekend, holiday) for a specific station.
4. Top Weekday Ridership: Shows stations with the highest ridership during weekdays.
5. Stops by Line Color and Direction: Lists stops on a specific line (by color) and in a chosen direction (N/S/W/E).
6. Stop Count by Color: Displays the number of stops for each line color, categorized by direction.
7. Yearly and Monthly Ridership: Allows users to view and visualize ridership data for a specific station by year or month, with an option to plot the data.
8. Daily Ridership Comparison: Compares daily ridership between two stations over a specified year.
9. Stations Within a Mile: Finds and plots stations within a 1-mile radius of a given latitude and longitude, with the option to plot them on a map.
10. Visualization: Integrated with matplotlib for graphical representations of ridership data, with options to plot yearly and monthly trends, as well as map station locations.

Technology Stack:
* Python 3
* SQLite3 for database handling
* Matplotlib for data visualization
* DB Browser for SQLite for database inspection (optional)
