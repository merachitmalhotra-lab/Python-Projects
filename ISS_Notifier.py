import os
import time
import smtplib
import requests
import datetime as dt
from zoneinfo import ZoneInfo

MY_LAT = 28.651939
MY_LNG = 77.268951
TZ = ZoneInfo("Asia/Kolkata")

SENDER_EMAIL = os.getenv("ISS_EMAIL")          # set in env
SENDER_PASSWORD = os.getenv("ISS_APP_PASSWORD")# set in env (Gmail App Password)
RECEIVER_EMAIL = os.getenv("ISS_TO_EMAIL")     # set in env

last_sent = None
COOLDOWN_SECONDS = 30 * 60


while True:
    time.sleep(60)

    now = dt.datetime.now(TZ)

    # ISS location
    location = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
    location.raise_for_status()
    data = location.json()
    iss_longitude = float(data["iss_position"]["longitude"])
    iss_latitude = float(data["iss_position"]["latitude"])
    print((iss_longitude, iss_latitude))

    # Sunrise/Sunset (API returns UTC timestamps)
    parameters = {"lat": MY_LAT, "lng": MY_LNG, "formatted": 0}
    sun = requests.get("https://api.sunrise-sunset.org/json", params=parameters, timeout=10)
    sun.raise_for_status()
    data = sun.json()["results"]

    sunrise_utc = dt.datetime.fromisoformat(data["sunrise"]).replace(tzinfo=dt.timezone.utc)
    sunset_utc = dt.datetime.fromisoformat(data["sunset"]).replace(tzinfo=dt.timezone.utc)

    sunrise_local = sunrise_utc.astimezone(TZ)
    sunset_local = sunset_utc.astimezone(TZ)

    is_dark = now >= sunset_local or now <= sunrise_local
    is_overhead = (23 < iss_latitude < 33) and (72 < iss_longitude < 83)

    can_send = (last_sent is None) or ((now - last_sent).total_seconds() >= COOLDOWN_SECONDS)

    if is_overhead and is_dark and can_send:
        if not (SENDER_EMAIL and SENDER_PASSWORD and RECEIVER_EMAIL):
            raise RuntimeError("Set ISS_EMAIL, ISS_APP_PASSWORD, ISS_TO_EMAIL in environment variables.")

        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
            connection.sendmail(
                from_addr=SENDER_EMAIL,
                to_addrs=RECEIVER_EMAIL,
                msg="Subject: ISS Overhead!\n\nISS is overhead AND it’s dark — look up!"
            )

        last_sent = now
        print("Email sent ✅")
