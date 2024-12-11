import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Time, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
from fuzzywuzzy import fuzz


pool_name_url = "https://ottawa.ca/en/recreation-and-parks/facilities/place-listing?place_facets%5B0%5D=place_type%3A4285"
url = "https://ottawa.ca/en/recreation-and-parks/facilities/place-listing/"

# Define the base class for SQLAlchemy
Base = declarative_base()

# Define the LaneSwimSchedule model
class LaneSwimSchedule(Base):
    __tablename__ = 'lane_swim_schedules'
    
    id = Column(Integer, primary_key=True)
    pool = Column(String, nullable=False)
    address = Column(String, nullable=False) 
    swim_type = Column(String, nullable=False)
    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

# Define a new model to log script execution
class ScriptLog(Base):
    __tablename__ = 'script_log'
    
    id = Column(Integer, primary_key=True)
    script_name = Column(String, nullable=False)
    last_run_time = Column(String, nullable=False)

    
def get_pools():
    pool_data = {}
    response = requests.get(pool_name_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table within the div with class "table-responsive"
        table_div = soup.find("div", class_="table-responsive")
        table = table_div.find("table") if table_div else None
        
        if table:
            for row in table.find_all('tr'):
                if row.find('td'):
                    # Find the pool name link and address container
                    name_tag = row.find('td', class_='views-field views-field-title').find('a')
                    address_tag = row.find('td', class_='views-field views-field-field-address').find('p', class_='address')

                    if name_tag and address_tag:
                        # Get pool name
                        pool_url = name_tag['href']
                        pool_name = pool_url.split('/')[-1]
                        
                        # Get address details
                        address_line = address_tag.find('span', class_='address-line1').get_text(strip=True)
                        locality = address_tag.find('span', class_='locality').get_text(strip=True)
                        admin_area = address_tag.find('span', class_='administrative-area').get_text(strip=True)
                        postal_code = address_tag.find('span', class_='postal-code').get_text(strip=True)
                        
                        # Combine address components into a single string
                        full_address = f"{address_line}, {locality}, {admin_area} {postal_code}, Canada"
                        
                        # Add to dictionary
                        pool_data[pool_name] = full_address
    return pool_data

def parse_schedule_time(schedule_time):
    """Parse schedule times into start and end datetime objects."""
    # Replace non-breaking spaces, clean up format, and split by common delimiters like commas
    times = schedule_time.replace('\xa0', ' ').replace("\n", " ").replace("\t", " ").replace('–', '-').split(',')
    # print(times)
    time_ranges = []
    # Define possible formats
    formats = ["%I:%M %p", "%I %p", "%I:%M", "%I", "%I%p"]
    for time_range in times:
        # print(f"\n timerange {time_range}")
        # Split the time range by the dash for start and end times
        start_end = time_range.strip().split('-')
        # Ensure there are exactly two elements: start and end
        if len(start_end) == 2:
            start_time_str = start_end[0].strip().lower()
            end_time_str = start_end[1].strip().lower()
            # Handle 'noon' as a special case
            if start_time_str == "noon":
                start_time_str = "12:00 pm"
            if end_time_str == "noon":
                end_time_str = "12:00 pm"
            # Parse the start time with multiple format attempts
            start_time = None
            for fmt in formats:
                try:
                    start_time = datetime.strptime(start_time_str, fmt)
                    break  # Stop if successful
                except ValueError:
                    continue
            if not start_time:
                print(f"Failed to parse start time: {start_time_str}")
                continue  # Skip if start time fails
            # Parse the end time with multiple format attempts
            end_time = None
            for fmt in formats:
                try:
                    end_time = datetime.strptime(end_time_str, fmt)
                    break  # Stop if successful
                except ValueError:
                    continue
            if not end_time:
                print(f"Failed to parse end time: {end_time_str}")
                continue  # Skip if end time fails
            # Adjust the end time to 24-hour format
            if end_time_str.endswith("pm") and not start_time_str.endswith("am") and start_time.hour < 12:
                start_time = start_time.replace(hour=start_time.hour + 12)
            # Append the parsed start and end time as a tuple to the time_ranges list
            time_ranges.append((start_time, end_time))
    return time_ranges

def parse_date(date_str, default_year):
    """
    Parse the date string and return a datetime object.
    If only month and day are provided, use the default_year.
    """
    try:
        return datetime.strptime(f"{date_str}, {default_year}", "%B %d, %Y")
    except ValueError:
        return None

def validate_table_date_range(table):
    """
    Validate table data with caption date range when comparing it to today's date.
    """
    today = datetime.now()
    
    # Updated regex to handle both full dates and day ranges
    date_pattern = r"([a-z]+ \d{1,2})(?:, \d{4})?\s*to\s*([a-z]+ \d{1,2})(?:, \d{4})?"

    caption = table.find("caption")
    if caption:
        caption = caption.text.encode("utf-8", "ignore").decode("utf-8")
        caption = caption.replace("\u202f", " ").replace("\xa0", " ").lower()
        # print(f"Caption: {caption}")
        
        matches = re.findall(date_pattern, caption)
        
        if matches:
            for match in matches:
                # print(f"Found match: {match}")
                try:
                    start_date_str, end_date_str = match
                    
                    # Use the current year if no year is provided
                    if ',' in start_date_str:
                        start_date = parse_date(start_date_str, today.year)
                    else:
                        start_date = parse_date(start_date_str, today.year)
                    
                    if ',' in end_date_str:
                        end_date = parse_date(end_date_str, today.year)
                    else:
                        end_date = parse_date(end_date_str, today.year)

                    # Adjust if end date is earlier than start date (e.g., for New Year's crossing)
                    if start_date > end_date:
                        end_date = end_date.replace(year=start_date.year + 1)
                    
                    # Check if today's date is within the range
                    if start_date <= today <= end_date:
                        print(f"Today's date {today} is within the range.")
                        return True
                    else:
                        print(f"Today's date {today} is NOT within the range.")
                
                except ValueError as e:
                    print(f"Error parsing dates: {e}")
    return False
    

def extract_lane_swim_rows(table, pool_name, address, existing_types):
    lane_swim_schedules = []
    
    if validate_table_date_range(table):
        # Iterate through each row in the table body 
        # debug statement to print only tables that have valid date ranges   
        # print(table.find("caption"))
        for row in table.find_all("tr"):
            header = row.find("th")  # Get the header cell 
            if header:
                # If &nbsp; or any other unrecognized characters \u202f in cell to write new line in html clean out
                header = header.text.encode("utf-8", "ignore").decode("utf-8")
                header = header.replace("\u202f", " ").replace("\xa0", " ") 
                # if "lane swim" in header.lower():  # Check if "Lane swim" is in the header text any type convert to lower 
                print(f"Activity Type: {header.lower()}")
                type_of_activity = header.strip().replace("\n", " ").replace("\t", " ").replace('–', '-')
                
                # Compare with existing types to see if it's similar
                matched_type = None
                for existing_type in existing_types:
                    # Use fuzzy matching to check similarity (you can adjust the threshold)
                    if fuzz.partial_ratio(type_of_activity.lower(), existing_type.lower()) > 90:  # 80% similarity
                        matched_type = existing_type
                        break
                
                if matched_type:
                    type_of_activity = matched_type 
                    
                cells = row.find_all("td")  # Get all the data cells in the row
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']      
                # print(header.lower())          
                for day, cell in zip(days, cells):
                    schedule_time = cell.text.encode("utf-8", "ignore").decode("utf-8")
                    schedule_time = schedule_time.replace("\u202f", " ").replace("\xa0", " ") 
                    if schedule_time and schedule_time.lower() != 'n/a':  # Only consider valid times
                        start_end_times = parse_schedule_time(schedule_time)
                        # debug 
                        # print(start_end_times)
                        for start_end in start_end_times:
                            # print(start_end)
                            lane_swim_schedules.append({
                                'Pool': pool_name,
                                'Address': address, 
                                'Swim Type': type_of_activity,
                                'Day': day,
                                'Start Time': start_end[0],  # Start time from tuple
                                'End Time': start_end[1]     # End time from tuple
                            })
                if type_of_activity not in existing_types:
                    existing_types.append(type_of_activity)
            else:
                print("Header not found in row header")
    else:
        print(f"table data range invalid: {table.find('caption')}")
                        
    return lane_swim_schedules

import requests
from bs4 import BeautifulSoup

def main():
    # List to hold all schedules
    all_lane_swim_schedules = []
    
    existing_types = [] 
    
    # Dynamically web scrape pool names and url links to each one
    pool_names = get_pools()
    
    # Iterate through each pool name
    for pool_name, address in pool_names.items():
        response = requests.get(url + pool_name)
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables within the page (not just the first one inside "table-responsive")
            tables = soup.find_all("table")
            
            if tables:
                for table in tables:
                    # If the table is part of the desired schedule, process it
                    lane_swim_schedules = extract_lane_swim_rows(table, pool_name.replace('-', ' ').title(), address, existing_types)
                    all_lane_swim_schedules.extend(lane_swim_schedules)  # Collect all schedules
            else:
                print(f"No schedule tables found for {pool_name.replace('-', ' ').title()}.")
        else:
            print(f"Failed to retrieve data for {pool_name.replace('-', ' ').title()}. Status code: {response.status_code}")
    
    # Optionally, print or process all collected schedules
    print(f"Total schedules collected: {len(all_lane_swim_schedules)}")

    # If any table are found
    if all_lane_swim_schedules:
        df = pd.DataFrame(all_lane_swim_schedules)
        df['Start Time'] = pd.to_datetime(df['Start Time'], format='%I:%M %p', errors='coerce').dt.time
        df['End Time'] = pd.to_datetime(df['End Time'], format='%I:%M %p', errors='coerce').dt.time
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df['Day'] = pd.Categorical(df['Day'], categories=day_order, ordered=True)
        df.sort_values(by=['Day', 'Pool', 'Start Time'], inplace=True)

        # Display the sorted DataFrame without index
        print(df.to_string(index=False))


        """Push df to sqllite database"""
        engine = create_engine('sqlite:///lane_swim_database.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # overwrite previous data
        session.query(LaneSwimSchedule).delete()
        session.commit()

        for index, row in df.iterrows():
            swim_schedule = LaneSwimSchedule(
                pool=row['Pool'],
                address=row['Address'],
                swim_type=row['Swim Type'],
                day=row['Day'],
                start_time=row['Start Time'],
                end_time=row['End Time']
            )
            session.add(swim_schedule)
        session.commit()
        
        # Log the script execution time
        script_log = ScriptLog(
            script_name="Ottawa Activities Scraper",
            last_run_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        session.add(script_log)
        session.commit()
        
        session.close()

        print("Data inserted into the database successfully.")
    else:
        print("No tables found in any url")
    
main()
# get_pools()