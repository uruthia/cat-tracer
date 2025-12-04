# Cat Tracer 🐈📍

**Cat Tracer** is an IoT solution designed to monitor the location and well-being of a pet cat in real-time. The system utilizes LoRaWAN for long-range communication to transmit GPS coordinates and sensor data (environmental noise and heart rate) to a central dashboard.

## 🚀 Project Overview

The system consists of three main components:
1.  **IoT Wearable (Arduino + LoRa):** A device worn by the cat that collects data via sensors and transmits it over LoRaWAN.
2.  **Data Receiver (Python):** A script that listens to the LoRa receiver via Serial (USB), parses the packets, and uploads them to Google Firebase.
3.  **Web Dashboard (Flask):** A web application that visualizes the cat's path on a map, displays real-time alerts for anomalies, and provides historical statistics.

## ✨ Features

*   **Real-Time Tracking:** Live map updates showing the cat's current position using Leaflet and Socket.IO.
*   **Anomaly Detection:**
    *   **Sound:** Detects loud environmental noises (Microphone sensor).
    *   **Heart Rate:** Monitors for heart rate spikes (Cardio sensor).
*   **Dashboard Analytics:**
    *   Daily movement history.
    *   Speed and Altitude graphs.
    *   Statistical breakdown of anomalies per hour.
    *   Calculation of Max/Avg Speed and Altitude.

## 🛠️ Hardware Architecture

*   **Microcontroller:** Arduino (equipped with LoRaWAN capabilities).
*   **Communication:** LoRaWAN (Long Range Wide Area Network).
*   **Sensors:**
    *   **GPS Module:** For latitude, longitude, altitude, and speed.
    *   **Microphone (MIC):** For detecting sound levels.
    *   **Heart Rate Sensor (CARDIO):** For monitoring pulse.

## 📂 Project Structure

```text
├── data-reader/           # Handles serial communication with the LoRa receiver
│   ├── cat_tracer_receiver.py  # Main script to read Serial and push to Firebase
│   └── firebase.py             # Database helper functions
├── web-app/               # The Flask Web Application
│   ├── app.py                  # Main application entry point
│   ├── templates/              # HTML files (Dashboard, Live Map)
│   ├── static/                 # CSS, Images, and JS assets
│   └── data_formatter.py       # Pandas utilities for data processing
└── requirements.txt       # Python dependencies