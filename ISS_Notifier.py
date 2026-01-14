import requests
import datetime as dt
import smtplib
import time


while True:
    time.sleep(60)
    now = dt.datetime.now()
    current_hour= now.hour


    my_latitude=round(28.651939,0)
    my_longitude=round(77.268951,0)



    location= requests.get(url="http://api.open-notify.org/iss-now.json")
    location.raise_for_status()
    data= location.json()
    iss_longitude=float((data["iss_position"]["longitude"]))
    iss_latitude=float((data["iss_position"]["latitude"]))
    coordinates=(iss_longitude,iss_latitude)
    print(coordinates)



    parameters= {
        "lat": 28.651939,
        "lng": 77.268951,
        "formatted" : 0,
        "tzid": "Asia/Kolkata"
    }

    sun = requests.get("https://api.sunrise-sunset.org/json", parameters)
    sun.raise_for_status()
    data= sun.json()
    sunrise= int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset= int(data["results"]["sunset"].split("T")[1].split(":")[0])



    if 23 < iss_latitude < 33 and 72 < iss_longitude < 83 and (current_hour >= sunset or current_hour < sunrise):
        print("It's between 18:00 and 05:00")
        my_email = "rachit.malhotra.code@gmail.com"
        password = "tjglfxzuthdftsqb"
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email,
                                to_addrs= "merachitmalhotra@gmail.com",
                                msg="ISS is overhead AND it’s dark — look up!")
