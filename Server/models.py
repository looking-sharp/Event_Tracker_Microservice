#region imports
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, JSON, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime, timezone
#endregion 

# ------------------------
#   DB TABLE DEFINITIONS
# ------------------------

Base = declarative_base()

utcnow = lambda: datetime.now(timezone.utc)  

class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(String(12), primary_key=True)
    user_id = Column(Text, nullable=False)
    event_name = Column(String(255), nullable=False)
    event_date = Column(Date, nullable=False)
    created_on = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    start_time = Column(Time(timezone=True))
    end_time = Column(Time(timezone=True))
    tz_str = Column(String(50), default='utc')
    public = Column(Boolean, default=True)
    event_location = Column(String(255))
    event_description = Column(Text)
    rsvps = Column(MutableList.as_mutable(JSON), default=list)
    age_restriction = Column(Integer, default=None)
    attendence_restriction = Column(Text, default=None)

    check_in_token = Column(Text)
    cover_photo_url_id = Column(String(12))
    




