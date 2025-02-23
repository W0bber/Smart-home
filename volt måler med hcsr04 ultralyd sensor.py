# Smart Home sensor program
# MicroPython and ESP32
import network
import espnow
from machine import ADC, Pin
import time
from hcsr04 import HCSR04  # HC-SR04 ultralydssensor

########################################
# CONFIGURATION
dashboard_mac_address = b'\xB0\xA7\x32\xDD\x6F\x0C'  # MAC address of dashboard (Educaboard) som byte string

# Sensor
sensor_id = "Ultrasound"  # Sensor ID
pin_us_trigger = 32  # HC-SR04 trigger pin
pin_us_echo = 33  # HC-SR04 echo pin

# Battery
pin_battery = 36  # Battery voltage measurement pin

########################################
# OBJECTS
# ESP-NOW
sta = network.WLAN(network.STA_IF)  # Initialiser ESP-NOW
sta.active(True)

en = espnow.ESPNow()
en.active(True)

# Sensor objekt
sensor = HCSR04(pin_us_trigger, pin_us_echo, 10000)  # Timeout: 10 ms

# Battery ADC setup
adc = ADC(Pin(pin_battery))
adc.atten(ADC.ATTN_11DB)  # Måler op til 3.3V

########################################
# KONSTANTER
U_min = 3.0  # Minimum batterispænding (fladt batteri)
U_max = 4.2  # Maksimum batterispænding (fuldt opladet)
battery_capacity = 1800  # Batterikapacitet i mAh

# Tilføj dashboard som ESP-NOW peer
en.add_peer(dashboard_mac_address)

########################################
# FUNKTIONER

def batt_voltage(adc_val):
    """ Konverterer ADC-værdi til batterispænding """
    U_adc = (adc_val / 4095) * 3.3  # ADC skala (0-4095 til 0-3.3V)
    return U_adc * 2  # Ganger med 2 pga. spændingsdeler (10kΩ/10kΩ)

def batt_percentage(voltage):
    """ Beregner batteriprocent baseret på 3.0V - 4.2V """
    percentage = ((voltage - U_min) / (U_max - U_min)) * 100
    return max(0, min(100, percentage))  # Sikrer værdien er mellem 0-100%

########################################
# VARIABLER
prev_sensor_value = -999  # Forrige afstandsmåling
prev_bat_pct = -1  # Forrige batteriprocent

# INITIALISERING
en.send(dashboard_mac_address, sensor_id + " ready", False)
print(sensor_id + " ready")

########################################
# MAIN LOOP
while True:
    # Læs batterispænding
    adc_val = adc.read()
    voltage = batt_voltage(adc_val)
    bat_pct = batt_percentage(voltage)

    # Læs ultralydssensorens afstand
    sensor_value = sensor.distance_cm()

    # Send kun data, hvis der er ændringer
    if bat_pct != prev_bat_pct or sensor_value != prev_sensor_value:
        data_string = f"{time.ticks_ms()}|{bat_pct}|{sensor_value}"
        print("Sending:", data_string)

        try:
            en.send(dashboard_mac_address, data_string, False)
        except ValueError as e:
            print("Error sending message:", e)

        # Opdater tidligere værdier
        prev_bat_pct = bat_pct
        prev_sensor_value = sensor_value

    time.sleep_ms(500)  # Undgår støj i målinger
