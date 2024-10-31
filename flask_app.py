from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Time, Integer
from datetime import datetime, timedelta

Base = declarative_base()

class LaneSwimSchedule(Base):
    __tablename__ = 'lane_swim_schedules'
    
    id = Column(Integer, primary_key=True)
    pool = Column(String, nullable=False)
    address = Column(String, nullable=False)
    swim_type = Column(String, nullable=False)
    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

def parse_time(time_str):
    """Parse a time string into a time object, accommodating both 12-hour and 24-hour formats."""
    formats = ["%I:%M %p", "%I %p", "%H:%M", "%I:%M", "%I%p"]
    for fmt in formats:
        try:
            parsed_time = datetime.strptime(time_str.strip(), fmt).time()
            return parsed_time
        except ValueError:
            continue
    raise ValueError(f"Time data '{time_str}' does not match any expected formats.")

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

DATABASE_URL = 'sqlite:///lane_swim_database.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/pools', methods=['GET'])
def get_pools():
    session = Session()
    pools = session.query(LaneSwimSchedule.pool).distinct().all()
    session.close()

    # Extracting pool names from the query result
    pool_list = [pool[0] for pool in pools]
    
    return jsonify(pool_list)


@app.route('/schedules', methods=['GET'])
def get_schedules():
    session = Session()
    filters = request.args
    query = session.query(LaneSwimSchedule)

    # Apply filters
    if 'pool[]' in filters:
        # Get the list of pools and filter them
        pools = filters.getlist('pool[]')
        query = query.filter(LaneSwimSchedule.pool.in_(pools))
        
    if 'day' in filters:
        query = query.filter(LaneSwimSchedule.day.ilike(f"%{filters['day']}%"))
    if 'time' in filters:
        time = filters['time'].split('-')
        print(time)
        if len(time) == 2:
            start_time_str = time[0].strip() 
            end_time_str = time[1].strip() 
            try:
                start_time = parse_time(start_time_str)
                end_time = parse_time(end_time_str)
                
                # Update the query to check for overlapping times
                query = query.filter(
                    (LaneSwimSchedule.start_time >= start_time) & 
                    (LaneSwimSchedule.end_time <= end_time)
                )
            except ValueError as e:
                print(str(e))

    schedules = query.all()
    session.close()

    result = [{'id': sch.id,
               'pool': sch.pool,
               'address': sch.address,
               'swim_type': sch.swim_type,
               'day': sch.day,
               'start_time': str(sch.start_time),
               'end_time': str(sch.end_time)} for sch in schedules]
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
