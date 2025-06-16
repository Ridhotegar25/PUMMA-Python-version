#!/home/pi/code/envPumma/bin/python3

import json
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt

from alert import process_and_forecast, process_alert_log
from mb import connect_serial, read_sensor_once, save_sensor_data
#from jsnA import measure_distance #for jsn but caused delay on send mqtt 

# MQTT Configuration
MQTT_BROKER = ""
MQTT_PORT = 1883
MQTT_TOPIC = ""
MQTT_USERNAME = ""
MQTT_PASSWORD = ""

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "" # Ganti dengan Bot Token Yang sudah dibuat 
TELEGRAM_CHAT_ID = "-1002374272293"

# Data logger path
DATA_LOGGER_PATH = "/home/pi/Data/Pumma_MB"
LOG_FOLDER = "/home/pi/Data/Log_maxbo"

os.makedirs(DATA_LOGGER_PATH, exist_ok=True)

# MQTT Setup
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def get_maxbo_value(ser):
    result = read_sensor_once(ser)
    if result:
        save_sensor_data(LOG_FOLDER, result["timestamp"], result["value"])
        return result
    return None

def write_to_logger(data_dict):
    now = datetime.now()
    filename = f"Pumma_MB_{now.strftime('%d-%m-%Y')}.csv"
    file_path = os.path.join(DATA_LOGGER_PATH, filename)
    header = [
        "timestamp", "maxbo_value", "forecast_30", "forecast_300",
        "alert_signal", "rms_alert_signal", "threshold", "alert_level"
    ]
    is_new = not os.path.exists(file_path)

    with open(file_path, "a") as f:
        if is_new:
            f.write(",".join(header) + "\n")
        f.write(",".join([str(data_dict.get(h, "")) for h in header]) + "\n")

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram alert sent successfully")
        else:
            print(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")        

def main_loop():
    ser = connect_serial()
    if not ser:
        print("Tidak bisa konek ke sensor. Keluar.")
        return

    while True:
        try:
            maxbo_data = get_maxbo_value(ser)
            if maxbo_data is None:
                print("Gagal ambil data sensor.")
                time.sleep(1)
                continue
            #jsn_distance0 = measure_distance()
            #jsn_distance1 = 2.198 - jsn_distance0/100
            #jsn_distance = round((1 + jsn_distance1),2)
            forecast_30, forecast_300, alert_signal = process_and_forecast()
            rms_alert_signal, threshold, alert_level = process_alert_log()

            payload = {
                "timestamp": maxbo_data["timestamp"],
                "Maxbotic": maxbo_data["value"],
                #"JSN_Data" : jsn_distance,
                "forecast_30": forecast_30,
                "forecast_300": forecast_300,
                "alert_signal": alert_signal,
                "rms_alert_signal": rms_alert_signal,
                "threshold": threshold,
                "alert_level": alert_level
            }

            # Kirim ke MQTT
            client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)

            # Simpan ke file logger
            write_to_logger(payload)

            # Send alert if necessary
            if alert_level > 0:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = (
                    f"⚠️ PUMMA ** ⚠️ \n" #Ganti dengan Nama yang sesuai 
                    f"Timestamp: {timestamp}\n"
                    f"Water Level: {payload['Maxbotic']}\n"
                    f"Alert Signal: {payload['Alert_Signal']}\n"
                    f"RMS: {payload['rms']}\n"
                    f"Threshold: {payload['Threshold']}\n"
                    f"Alert Level: {payload['Alert_Level']}"
                )
                send_telegram_alert(message)

            print(f"Sent and logged: {payload}")

        except Exception as e:
            print("Main loop error:", e)

        time.sleep(1)

if __name__ == "__main__":
    main_loop()