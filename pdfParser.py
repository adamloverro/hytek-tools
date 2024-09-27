import PyPDF2
import pprint
import re
import pandas as pd
from datetime import datetime as dt

class Person:
    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender
        self.times = []  # Array to hold time details

    def add_time(self, date, meet_name, time, event_name, change_in_time):
        self.times.append({
            "date": date,
            "meet_name": meet_name,
            "time": time,
            "event_name": event_name,
            "change_in_time": change_in_time
        })

    def __repr__(self):
        times_str = pprint.pformat(self.times, indent=4)
        return f"Name={self.name}, age={self.age}, gender={self.gender}, \ntimes={times_str})\n\n"


def parse_person(line):
    # Assuming a specific format for the line, use regex or string manipulation to extract details
    # This is a placeholder pattern and should be replaced with the actual pattern of the lines
    #print(line)
    pattern = r"(?P<name>[A-Za-z ,]+?)\s+\((?P<age>\d+)\)\s+(?P<gender>[MF])"
    match = re.match(pattern, line)
    if match:
        return match.groupdict()
    else:
        return None

def parse_times(line):
    # Assuming a specific format for the line, use regex or string manipulation to extract details
    # This is a placeholder pattern and should be replaced with the actual pattern of the lines
    #print(line)
    pattern = r"(?P<date>\d+/\d+/\d+)\s+(?P<meet_name>[A-Za-z @\-\d]+)\s*\sx*(?P<time>[\d.:]+)\s*S\s(?P<event_name>[A-Za-z\d]+)\sF(?P<change_in_time>[-\d]+.\d+)"
    match = re.match(pattern, line)
    if match:
        return match.groupdict()
    else:
        return None

def parse_pdf(file_path):
    people = []  # Step 1: Initialize an empty list

    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        person = None
        skip_lines = 5

        for page_num in range(num_pages):  # Step 2: Iterate through each page
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            lines = text.split('\n')  # Step 4: Split the text into lines
            for line in lines[skip_lines:]:
                skip_lines = 4
                line = line.replace("ϐ", "f")
                parsed_line = parse_person(line)
                #print(parsed_line)
                if parsed_line:
                    # Assuming the person's name uniquely identifies them
                    person = next((p for p in people if p.name == parsed_line['name']), None)
                    if not person:
                        person = Person(parsed_line['name'], parsed_line['age'], parsed_line['gender'])
                        people.append(person)
                else:
                    parsed_line = parse_times(line)
                    #print(parsed_line)
                    if parsed_line:
                        person.add_time(parsed_line['date'], parsed_line['meet_name'], parsed_line['time'], parsed_line['event_name'], parsed_line['change_in_time'])

    return people

def person_to_dict(person, time):
    """Convert a Person object to a dictionary suitable for a DataFrame row."""
    # Flatten the times into a string or a more complex structure as needed
    if(time['time'].find(':') == -1):
        tmp_time = dt.strptime(time['time'], '%S.%f').time()
    else:
        tmp_time = dt.strptime(time['time'], '%M:%S.%f').time()
    
    return {
        "Name": person.name,
        "Age": person.age,
        "Gender": person.gender,
        "Date": dt.strptime(time['date'], '%m/%d/%Y').date(),
        "Meet Name": time['meet_name'],
        "Time": tmp_time.minute * 60 + tmp_time.second + tmp_time.microsecond / 1000000,
        "Event Name": time['event_name'],
        "Change in Time": float(time['change_in_time'])
    }

def calculate_most_improved_per_swimmer(df):
    grouped_df = df.groupby('Name')
    swimmers = []

    for name, group in grouped_df:
        age = group['Age'].iloc[0]
        gender = group['Gender'].iloc[0]
        total_time_dropped = group['Change in Time'].sum()
        fastest_time_dropped = group['Change in Time'].min()
        average_time_dropped = (group['Change in Time'] / group['Time']).mean() * 100
        total_percent_time_dropped = (group['Change in Time'] / group['Time']).sum() * 100 / 5

        swimmer = {
            'Name': name,
            'Age': age,
            'Gender': gender,
            'Total Time Dropped': total_time_dropped,
            'Fastest Time Dropped': fastest_time_dropped,
            'Average Time Dropped': average_time_dropped,
            'Total Percent Time Dropped (Divided by 5)': total_percent_time_dropped
        }

        swimmers.append(swimmer)

    return pd.DataFrame(swimmers)


# Usage example
file_path = '/Users/Charlie.Ruhs/Projects/MostImproved/most-improved-team-manager-20240717.pdf'
people = parse_pdf(file_path)
people_dict = []
for person in people:
    for time in person.times:
        people_dict.append(person_to_dict(person, time))

df = pd.DataFrame(people_dict)
improved_df = calculate_most_improved_per_swimmer(df)

# Specify the Excel writer and file name
writer = pd.ExcelWriter('/Users/Charlie.Ruhs/Projects/MostImproved/MostImproved.xlsx', engine='openpyxl')

# Write the DataFrame to an Excel file
df.to_excel(writer, index=False, sheet_name='Raw Data')
improved_df.to_excel(writer, index=False, sheet_name='Most Improved')

# Save the Excel file
writer.close()

print("Excel file created successfully.")