## Smesher (derived from mesh..?)

The purpose of this program is to land the Tesla internship by creating a script similar to the job description.
The scrypt relies on the premise that the user already has a solution file using Ansys Fluent. 
Automation features are being implemented, this is honestly fun learning about different features and how to integrate things
The job requires for a design of API system, will add that in in app.py, or create a new file. 
Probably will need to also outline how I did the simulation on Ansys Fluent, and why I did them. 

# Problem Statement:

Electronic chip can withstadn a maximum package temperature of 50 C.
Heat sink is attached to the top of the chip, airflow of 1 m/s will be supplied to the heat sink.
Will heat sink and airflow provide sufficient cooling for the chip?

Answered in: Max temperature, downstreap of air temperature
 
# app.py

Create api calls and visualize the csv data gained from data section
The visualization is the 'answer' to the problem.
Knows to decide which .csv file extracted from the solution folder is to be used, filtered through key syntaxes. 

# preprocess.py

Searches for dat.h5 file in data section (the premise is that the solution file from Ansys moved to the data folder),
coverts .h5 -> .csv
Data is stored under folder named exported_data
Folder contains A LOT of .csv files