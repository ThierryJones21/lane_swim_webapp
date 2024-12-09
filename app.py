from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Time, Integer
from datetime import datetime, timedelta
from sqlalchemy import desc


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

class ScriptLog(Base):
    __tablename__ = 'script_log'
    
    id = Column(Integer, primary_key=True)
    script_name = Column(String, nullable=False)
    last_run_time = Column(String, nullable=False)

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
        
    if 'start_time' in filters:
        try:
            start_time = parse_time(filters['start_time'])
            query = query.filter(LaneSwimSchedule.start_time >= start_time)
        except ValueError as e:
            print(f"Invalid start time: {e}")

    if 'end_time' in filters:
        try:
            end_time = parse_time(filters['end_time'])
            query = query.filter(LaneSwimSchedule.end_time <= end_time)
        except ValueError as e:
            print(f"Invalid end time: {e}")

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

@app.route('/script-log', methods=['GET'])
def get_script_log():
    session = Session()
    # Query the most recent script log entry
    latest_log = session.query(ScriptLog).order_by(desc(ScriptLog.last_run_time)).first()
    session.close()

    if latest_log:
        result = {
            'script_name': latest_log.script_name,
            'last_run_time': latest_log.last_run_time
        }
    else:
        result = {
            'message': "No script logs found."
        }
    return jsonify(result)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host='0.0.0.0', port=4000)
