from machine import ADC, Pin
from time import sleep

# Opsætning af ADC på Pin 36
adc = ADC(Pin(36))  
adc.atten(ADC.ATTN_11DB)  # Tillader måling op til 3.3V

# Konstanter
U_min = 3.0  # Minimum batterispænding
U_max = 4.2  # Maksimum batterispænding
battery_capacity = 1800  # Batterikapacitet i mAh

def batt_voltage(adc_val):
    """ Konverterer ADC-værdi til batterispænding """
    U_adc = (adc_val / 4095) * 3.3  # Konverterer ADC-værdi (0-4095) til volt (0-3.3V)
    return U_adc * 2  # Ganger med 2 pga. spændingsdeler (10kΩ/10kΩ)

def batt_percentage(voltage):
    """ Beregner batteriprocent baseret på 3.0V - 4.2V interval """
    percentage = ((voltage - U_min) / (U_max - U_min)) * 100
    return max(0, min(100, percentage))  # Begrænser værdien    til 0-100%

while True:
    adc_val = adc.read()  # Læs ADC-værdi (0-4095)
    voltage = batt_voltage(adc_val)  # Konverter til volt
    battery_percent = batt_percentage(voltage)  # Beregn batteriprocent

    # Beregn resterende kapacitet og tid tilbage
    remaining_capacity = (battery_percent / 100) * battery_capacity
    current_consumption = 200  # Antaget strømforbrug på 200mA
    remaining_time = remaining_capacity / current_consumption if current_consumption else 0

    # Udskriv til terminalen
    print(f"Voltage: {voltage:.2f}V, Battery: {battery_percent:.1f}%, Time Left: {remaining_time:.1f}h")

    sleep(0.5)  # Opdatering hver 0.5 sekunder
