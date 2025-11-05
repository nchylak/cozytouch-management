import os
import pandas as pd
import pyairbnb

from datetime import datetime
from dotenv import load_dotenv


load_dotenv()  # get secrets from .env file if present
airbnb_room_id = os.getenv("AIRBNB_ROOM_ID")

# get airbnb calendar & find tomorrow's occupancy
# note: occupancy needs to be checked a day in advance since same-day bookings for this room are
# disabled in Airbnb (i.e. today's date will always be shown as unavailable even if the room
# is effectively not booked for the night)
calendar_data = pyairbnb.get_calendar(room_id=airbnb_room_id)
for month in calendar_data[:2]:
    for day in month["days"]:
        tomorrow = datetime.now().date() + pd.Timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        if day["calendarDate"] == tomorrow_str:
            is_occupied = not day["available"]

# udate occupancy.csv
occupancy_df = pd.read_csv("occupancy.csv")
if tomorrow_str in occupancy_df["date"].values:
    occupancy_df.loc[occupancy_df["date"] == tomorrow_str, "is_occupied"] = is_occupied
else:
    new_row = pd.DataFrame({"date": [tomorrow_str], "is_occupied": [is_occupied]})
    occupancy_df = pd.concat([occupancy_df, new_row], ignore_index=True)
occupancy_df.to_csv("occupancy.csv", index=False)
