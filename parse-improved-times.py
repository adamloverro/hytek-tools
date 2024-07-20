import pandas as pd
import pdfplumber
import os
from datetime import datetime as dt

pdf_directory = './.data'
output_directory = './.output'

# This code defines the Swimmer class.

class Swimmer:
    """Represents a swimmer.

    Attributes:
        current_name (str): The name of the swimmer.
        current_age (int): The age of the swimmer.
        current_gender (str): The gender of the swimmer. must have one of the following values: ['M', 'F']
        improved_time_records (list): A list of ImprovedTimeRecord objects.
    """

    def __init__(self, current_name, current_age, current_gender, improved_time_records):
        self.current_name = current_name
        self.current_age = current_age
        self.current_gender = current_gender
        self.improved_time_records = improved_time_records

        # validate data types in the constructor according to the following rules:
        # current_name: str; Last, First separated by a comma
        # current_age: int; must be an integer
        # current_gender: str; must have one of the following values: ['M', 'F']
        # improved_time_records: list; can be an empty list, or a list of ImprovedTimeRecord objects

        try:
            current_name = str(current_name)
        except Exception as e:
            print(f"Warning: {e}")

        try:
            current_age = int(current_age)
        except Exception as e:
            print(f"Warning: {e}")

        try:
            current_gender = str(current_gender)
            assert current_gender in ['M', 'F'], f"Invalid gender value: {current_gender}"
        except Exception as e:
            print(f"Warning: {e}")

        try:
            improved_time_records = list(improved_time_records)
            for record in improved_time_records:
                assert isinstance(record, ImprovedTimeRecord), f"Invalid improved_time_records value: {record}"
        except Exception as e:
            print(f"Warning: {e}")


class ImprovedTimeRecord:
    """Represents an improved time record.

    Attributes:
        name (str): The name of the swimmer.
        age (int): The age of the swimmer.
        gender (str): The gender of the swimmer
        course (str): The course of the record.
        type_of_time (str): The type of time.
        distance (int): The distance of the record.
        stroke (str): The stroke of the record.
        date (str): The date of the record.
        meet (str): The meet of the record.
        time_dropped (datetime): The time dropped in the record.
        baseline_time (datetime): The baseline time in the record.
    """

    def __init__(self, name, age, gender, course, type_of_time, distance, stroke, date, meet, time_dropped, baseline_time):
        self.name = name
        self.age = age
        self.gender = gender
        self.course = course
        self.type_of_time = type_of_time
        self.distance = distance
        self.stroke = stroke
        self.date = date
        self.meet = meet
        self.time_dropped = time_dropped
        self.baseline_time = baseline_time

        

        try: 
            assert self.validate_input_data(), "Invalid input data for ImprovedTimeRecord"
        except Exception as e:
            print(f"Warning: {e}")
            print(f"Invalid input data for ImprovedTimeRecord: {self.name}, {self.age}, {self.gender}, {self.course}, {self.type_of_time}, {self.distance}, {self.stroke}, {self.date}, {self.meet}, {self.time_dropped}, {self.baseline_time}")    

    def validate_input_data(self):
        # Validate the input data for ImprovedTimeRecord attributes
        # Return True if all attributes are valid, otherwise return False

        try:
            self.name = str(self.name)
        except Exception as e:
            print(f"Warning: Name Conversion: {e}")
            return False

        try:
            self.age = int(self.age)
        except Exception as e:
            print(f"Warning: Age Conversion: {e}")
            return False

        try:
            self.gender = str(self.gender)
            assert self.gender in ['M', 'F'], f"Invalid gender value: {self.gender}"
        except Exception as e:
            print(f"Warning: Gender Conversion: {e}")
            return False

        try:
            self.course = str(self.course)
            assert self.course in ['S', 'Y', 'L'], f"Invalid course value: {self.course}"
        except Exception as e:
            print(f"Warning: Course Conversion: {e}")
            return False

        try:
            self.type_of_time = str(self.type_of_time)
            assert self.type_of_time in ['P', 'F', 'S'], f"Invalid type_of_time value: {self.type_of_time}"
        except Exception as e:
            print(f"Warning: Type of Time Conversion: {e}")
            return False

        try:
            self.distance = int(self.distance)
            assert self.distance % 25 == 0, f"Invalid distance value: {self.distance}"
        except Exception as e:
            print(f"Warning: Distance Conversion: {e}")
            return False

        try:
            self.stroke = str(self.stroke)
            assert self.stroke in ['Free', 'Back', 'Breast', 'Fly', 'IM'], f"Invalid stroke value: {self.stroke}"
        except Exception as e:
            print(f"Warning: Stroke Conversion: {e}")
            return False

        try:
            self.date = dt.strptime(self.date, '%m/%d/%Y').date()

        except Exception as e:
            print(f"Warning: Date Conversion: {e}")
            return False

        try:
            self.meet = str(self.meet)
        except Exception as e:
            print(f"Warning: Meet Conversion: {e}")
            return False

        try:
            self.time_dropped = float(self.time_dropped)
            
        except Exception as e:
            print(f"Warning: Time Dropped Conversion: {e}")
            return False

        try:
            tmp_baseline_time = dt.strptime(self.baseline_time, '%M:%S.%f').time()
        except ValueError:
            try:
                tmp_baseline_time = dt.strptime(self.baseline_time, '%S.%f').time()
            except Exception as e:
                print(f"Warning: Baseline Time Conversion: {e}")
                return False

        self.baseline_time = tmp_baseline_time.minute * 60 + tmp_baseline_time.second + tmp_baseline_time.microsecond / 1000000

        return True
    
    def __str__(self):
        """Returns a string representation of the ImprovedTimeRecord object."""
        return f"Course: {self.course}\nType of Time: {self.type_of_time}\nDistance: {self.distance}\nStroke: {self.stroke}\nDate: {self.date}\nMeet: {self.meet}\nTime Dropped: {self.time_dropped}\nBaseline Time: {self.baseline_time}"

    
    def export_properties(self):
        """Exports all the properties of the ImprovedTimeRecord class as a list."""
        properties = [self.name, self.age, self.gender, self.course, self.type_of_time, self.distance, self.stroke, self.date, self.meet, self.time_dropped, self.baseline_time]
        return properties
    


def parse_swim_pdf_corrected(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        data = []
        swimmers = []
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            current_name = None
            current_age = None
            current_gender = None
            for line in lines:
                current_improved_time_record = None

                # Skip unnecessary lines
                if not line.strip() or "Page" in line or "Licensed To:" in line or "Individual Top Times" in line:
                    continue
                
                # Identify new swimmer with checks for comma and gender
                if '(' in line and ')' in line and ',' in line and ('M' in line or 'F' in line):
                    parts = line.split()
                    current_name = " ".join(parts[:-2])
                    current_age = parts[-2][1:-1]
                    current_gender = parts[-1]

                    swimmers.append(current_name)
                    continue

                # Process swimmer's event data
                if current_name and current_age and current_gender:
                    columns = line.split()
                    if len(columns) < 8:
                        continue
                    # Column index should only have one character in it; if not, split it into two columns
                    if len(columns[2]) > 1:
                        columns.insert(3, columns[2][1:])
                        columns[2] = columns[2][0]

                    baseline_time = columns[0]
                    # If the baseline time field begins with an x, remove the x
                    if baseline_time[0] == 'x':
                        baseline_time = baseline_time[1:]
                    

                    course = columns[1]
                    type_of_time = columns[2]
                    time_dropped = columns[3]
                    distance = columns[4]
                    stroke = columns[5]

                    date = columns[6]
                    meet = " ".join(columns[7:])

                    current_improved_time_record = ImprovedTimeRecord(current_name, current_age, current_gender, course, type_of_time, distance, stroke, date, meet, time_dropped, baseline_time)

                    data.append(current_improved_time_record.export_properties())
        
        df = pd.DataFrame(data, columns=['Name', 'Age', 'Gender', 'Course', 'Type of Time', 'Distance','Stroke', 'Date', 'Meet', 'Time Dropped','Baseline Time'])
        print(f"Processed a total of {len(swimmers)} swimmers")
        return df



def generate_improved_time_report(parsed_df): 
    # Process parsed_df in the following way
    # 1. Produce a report for every unique swimmer in the dataset
    # 2. For each swimmer, calculate the following statistics:
    #       a. total time dropped across all records
    #       b. fastest time dropped
    #       c. The average percentage time dropped  across all records where the percentage time dropped is calculated as (time dropped / baseline time) * 100
    #       d. The total percentage time dropped  across all records, divided by 5, where the percentage time dropped is calculated as (time dropped / baseline time) * 100

    # Group the records by swimmer
    grouped_df = parsed_df.groupby('Name')

    # Initialize an empty list to store the reports
    reports = []

    # Iterate over each swimmer group
    for name, group in grouped_df:
        # Age
        age = group['Age'].iloc[0]

        # Gender
        gender = group['Gender'].iloc[0]

        # Calculate the total time dropped
        total_time_dropped = group['Time Dropped'].sum()

        # Calculate the fastest time dropped
        fastest_time_dropped = group['Time Dropped'].min()

        # Calculate the average percentage time dropped
        average_percentage_time_dropped = (group['Time Dropped'] / group['Baseline Time']).mean() * 100

        # Calculate the total percentage time dropped divided by 5
        total_percentage_time_dropped = (group['Time Dropped'] / group['Baseline Time']).sum() * 100 / 5

        # Create the report dictionary
        report = {
            'Name': name,
            'Age': age,
            'Gender': gender,
            'Total Time Dropped': total_time_dropped,
            'Fastest Time Dropped': fastest_time_dropped,
            'Average Percentage Time Dropped': average_percentage_time_dropped,
            'Total Percentage Time Dropped (Divided by 5)': total_percentage_time_dropped
        }

        # Append the report to the list of reports
        reports.append(report)

    # Convert the list of reports to a DataFrame
    reports_df = pd.DataFrame(reports)

    # Print the reports DataFrame
    #print(reports_df)
    return reports_df

# Path to the input PDF and output CSV
pdf_files = []

for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_files.append(os.path.join(pdf_directory, filename))

for pdf_path in pdf_files:
    output_csv_path = os.path.join(output_directory, os.path.basename(os.path.splitext(pdf_path)[0]) + '_raw.csv')
    output_report_path = os.path.join(output_directory, os.path.basename(os.path.splitext(pdf_path)[0]) + '_report.csv')
    parsed_df = parse_swim_pdf_corrected(pdf_path)

    # Remove duplicate improvement records based on the following criteria:
    # 1. The records have the same name, age, gender, stroke, distance, and baseline_time
    parsed_df.drop_duplicates(subset=['Name', 'Age', 'Gender', 'Stroke', 'Distance', 'Baseline Time'], inplace=True)
    


    report_df = generate_improved_time_report(parsed_df)

    parsed_df.to_csv(output_csv_path, index=False)
    report_df.to_csv(output_report_path, index=False)




