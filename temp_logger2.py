#!/usr/bin/env python3
import serial
import time
import csv
import re
import argparse
from datetime import datetime

# Expected sensor names (to ensure consistent ordering)
EXPECTED_SENSORS = [
    "qfe_wtr_pa0", "qfe_wtr_pa1", "qfe_wtr_pa2", "qfe_wtr_pa3",
    "aoss0-usr", "mdm-q6-usr", "ipa-usr", "cpu0-a7-usr",
    "mdm-5g-usr", "mdm-vpe-usr", "mdm-core-usr",
    "xo-therm-usr", "sdx-case-therm-usr"
]

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Log AT+QTEMP temperature data to a CSV file.")
    parser.add_argument("--csv", type=str, default="temperature_log.csv", help="CSV output filename (default: temperature_log.csv)")
    return parser.parse_args()

def initialize_csv(filename):
    """Create and initialize the CSV file with headers if it doesn't exist."""
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp"] + EXPECTED_SENSORS)  # Header row
    except Exception as e:
        print(f"Error initializing CSV file: {e}")

def extract_temperatures(response_lines):
    """Extract sensor names and temperature values from modem response."""
    temp_data = {sensor: None for sensor in EXPECTED_SENSORS}  # Initialize all sensors with None

    for line in response_lines:
        match = re.match(r'QTEMP:"([^"]+)",\s*"?(\d+)"?', line)
        if match:
            sensor_name, temperature = match.groups()
            if sensor_name in temp_data:
                temp_data[sensor_name] = temperature  # Store parsed value

    return temp_data  # Returns dictionary {sensor_name: temperature_value}

def log_to_csv(filename, timestamp, temperature_data):
    """Append a new entry to the CSV file."""
    try:
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            row = [timestamp] + [temperature_data[sensor] for sensor in EXPECTED_SENSORS]  # Keep column order
            writer.writerow(row)
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def main():
    # Parse command-line arguments
    args = parse_arguments()
    csv_filename = args.csv  # Get CSV filename from argument

    # Serial port configuration
    serial_port = '/dev/ttyUSB2'  # Adjust as needed
    baud_rate = 115200
    timeout = 1  # Read timeout in seconds

    # Initialize CSV file
    initialize_csv(csv_filename)

    try:
        # Open the serial port
        with serial.Serial(serial_port, baud_rate, timeout=timeout) as ser:
            print(f"Connected to {serial_port} at {baud_rate} baud.")
            print(f"Logging AT+QTEMP responses to {csv_filename}. Press Ctrl+C to stop.")

            while True:
                # Send the AT+QTEMP command
                command = "AT+QTEMP\r"
                ser.write(command.encode('utf-8'))

                # Allow the modem time to process and respond
                time.sleep(0.2)

                response_lines = []
                while ser.in_waiting:
                    try:
                        response_line = ser.readline().decode('utf-8', errors='replace').strip()
                        if response_line and "QTEMP" in response_line:  # Filter out only temperature responses
                            response_lines.append(response_line)
                    except Exception as read_error:
                        print(f"Error reading line: {read_error}")

                if response_lines:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Millisecond precision
                    temperature_data = extract_temperatures(response_lines)

                    print(f"[{timestamp}] {temperature_data}")  # Print structured data to terminal
                    log_to_csv(csv_filename, timestamp, temperature_data)  # Log to specified CSV file

                # Wait 1 second before sending the next command
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nPolling stopped by user.")

    except serial.SerialException as serial_err:
        print(f"Serial error: {serial_err}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
