import serial
import firebase

ser = serial.Serial('COM8', 9600)

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip().split(',')
            print(data)
            if (data[0] == "MIC"):
                data[0] = 'sound'
                firebase.store_anomalie(data)
            elif (data[0] == "CARDIO"):
                data[0] = 'heart_rate'
                firebase.store_anomalie(data)
            elif (data[0] == "GPS"):
                print(data)
                firebase.store_coordinate(data)
except KeyboardInterrupt:
    print("Terminato dalla tastiera")
finally:
    ser.close()

