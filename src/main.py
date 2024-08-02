import logging
import json
import time
import os
from signalrcore.hub_connection_builder import HubConnectionBuilder
from dotenv import load_dotenv
import requests
import psycopg2

load_dotenv()


class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10
        self.db_connection = self.init_db_connection()

        # To be configured by your team
        self.HOST = os.getenv("HOST")  # Utiliser les variables d'environnement
        self.TOKEN = os.getenv("TOKEN")
        self.T_MAX = os.getenv("T_MAX")
        self.T_MIN = os.getenv("T_MIN")
        self.DATABASE_URL = os.getenv("DATABASE_URL")

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_temperature_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX) + 10:
            print("turnOnAC")
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            print("TurnOnHeater")
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(
            f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}", timeout=10
        )
        json.loads(r.text)
        self.save_event_to_database(action)

    def init_db_connection(self):
        try:
            connection = psycopg2.connect(
                user="user01eq9",
                password="Nenm1rpZpqHNRUyw",
                host="157.230.69.113",
                database="db01eq9",
            )
            return connection
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            return None

    def save_temperature_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            # To implement
            cursor = self.db_connection.cursor()
            insert_query = (
                'INSERT INTO sensor_data ("Timestamp", "Temperature") VALUES (%s, %s)'
            )
            cursor.execute(insert_query, (timestamp, temperature))
            self.db_connection.commit()
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into table", error)

    def save_event_to_database(self, event):
        """Save sensor data into database."""
        try:
            cursor = self.db_connection.cursor()
            insert_query = (
                'INSERT INTO sensor_event ("Timestamp", "Event") VALUES (NOW(), %s)'
            )
            cursor.execute(insert_query, (event,))
            self.db_connection.commit()
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into table", error)


if __name__ == "__main__":
    app = App()
    app.start()
