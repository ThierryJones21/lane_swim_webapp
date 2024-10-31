import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Time, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

pool_names = {
    'bob-macquarrie-recreation-complex-orleans': "1490 Youville Drive, Ottawa, ON K1C 2X8, Canada",
    'brewer-pool-and-arena': "100 Brewer Way, Ottawa, ON K1S 5T1, Canada",
    'canterbury-recreation-complex': "2185 Arch Street, Ottawa, ON K1G 2H5, Canada",
    'cardelrec-recreation-complex-goulbourn': "1500 Shea Road, Ottawa, ON K2S 0B2, Canada",
    'champagne-fitness-centre': "321 King Edward Avenue, Ottawa, ON K1N 7M5, Canada",
    'deborah-anne-kirwan-pool': "1300 Kitchener Avenue, Ottawa, ON K1V 6W2, Canada",
    'francois-dupuis-recreation-centre': "2263 Portobello Boulevard, Ottawa, ON K4A 0X3, Canada",
    'jack-purcell-community-centre': "320 Jack Purcell Lane, Ottawa, ON K2P 2J5, Canada",
    'kanata-leisure-centre-and-wave-pool': "70 Aird Place, Ottawa, ON K2L 4C9, Canada",
    'lowertown-community-centre-and-pool': "40 Cobourg Street, Ottawa, ON K1N 8Z6, Canada",
    'minto-recreation-complex-barrhaven': "3500 Cambrian Road, Ottawa, ON K2J 0V1, Canada",
    'nepean-sportsplex': "1701 Woodroffe Avenue, Ottawa, ON K2G 1W2, Canada",
    'pinecrest-recreation-complex': "2250 Torquay Avenue, Ottawa, ON K2C 1J3, Canada",
    'plant-recreation-centre': "930 Somerset Street West, Ottawa, ON K1R 6R9, Canada",
    'ray-friel-recreation-complex': "1585 Tenth Line Road, Ottawa, ON K1E 3E8, Canada",
    'richcraft-recreation-complex-kanata': "4101 Innovation Drive, Ottawa, ON K2K 0J3, Canada",
    'sawmill-creek-community-centre-and-pool': "3380 D’Aoust Avenue, Ottawa, ON K1T 1R5, Canada",
    'splash-wave-pool': "2040 Ogilvie Road, Ottawa, ON K1J 7N8, Canada",
    'st-laurent-complex': "525 Côté Street, Ottawa, ON K1K 0Z8, Canada",
    'walter-baker-sports-centre': "100 Malvern Drive, Ottawa, ON K2J 2G5, Canada"
}

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

def parse_schedule_time(schedule_time):
    """Parse schedule times into start and end datetime objects."""
    # Replace non-breaking spaces, clean up format, and split by common delimiters like commas
    times = schedule_time.replace('\xa0', ' ').replace("\n", " ").replace("\t", " ").replace('–', '-').split(',')
    # print(times)
    time_ranges = []
    # Define possible formats
    formats = ["%I:%M %p", "%I %p", "%I:%M", "%I", "%I%p"]
    for time_range in times:
        print(f"\n timerange {time_range}")
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

def extract_lane_swim_rows(table, pool_name, address):
    lane_swim_schedules = []
    # Iterate through each row in the table body
    for row in table.find_all("tr"):
        header = row.find("th")  # Get the header cell
        if header and "Lane swim" in header.text:  # Check if "Lane swim" is in the header text
            swim_type = header.text.strip().replace('\xa0', ' ').replace("\n", " ").replace("\t", " ").replace('–', '-')  # Get the swim type
            cells = row.find_all("td")  # Get all the data cells in the row
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day, cell in zip(days, cells):
                schedule_time = cell.text.strip()
                if schedule_time and schedule_time.lower() != 'n/a':  # Only consider valid times
                    print(pool_name)
                    print(day)
                    start_end_times = parse_schedule_time(schedule_time)
                    for start_end in start_end_times:
                        print(start_end)
                        lane_swim_schedules.append({
                            'Pool': pool_name,
                            'Address': address, 
                            'Swim Type': swim_type,
                            'Day': day,
                            'Start Time': start_end[0],  # Start time from tuple
                            'End Time': start_end[1]     # End time from tuple
                        })
    return lane_swim_schedules

# List to hold all schedules
all_lane_swim_schedules = []
# Iterate through each pool name
for pool_name, address in pool_names.items():
    response = requests.get(url + pool_name)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table within the div with class "table-responsive"
        table_div = soup.find("div", class_="table-responsive")
        table = table_div.find("table") if table_div else None
        
        if table:
            lane_swim_schedules = extract_lane_swim_rows(table, pool_name.replace('-', ' ').title(), address)
            all_lane_swim_schedules.extend(lane_swim_schedules)  # Collect all schedules
        else:
            print(f"No schedule table found for {pool_name.replace('-', ' ').title()}.")
    else:
        print(f"Failed to retrieve data for {pool_name.replace('-', ' ').title()}. Status code: {response.status_code}")

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
session.close()

print("Data inserted into the database successfully.")