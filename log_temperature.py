#!/usr/bin/env python3
import serial
import time

def main():
    # Change these parameters as necessary for your setup
    serial_port = '/dev/ttyUSB0'  # Example port (adjust for your system)
    baud_rate = 115200            # Adjust baud rate if needed
    timeout = 1                   # Read timeout in seconds

    try:
        # Open the serial port
        with serial.Serial(serial_port, baud_rate, timeout=timeout) as ser:
            print(f"Connected to {serial_port} at {baud_rate} baud.")
            print("Polling AT+QTEMP. Press Ctrl+C to stop.")

            while True:
                # Send the AT+QTEMP command with the proper termination (usually \r or \r\n)
                command = "AT+QTEMP\r"
                ser.write(command.encode('utf-8'))

                # Allow a short time for the modem to process the command and reply
                time.sleep(0.2)

                # Read and display all available response lines
                while ser.in_waiting:
                    try:
                        response_line = ser.readline().decode('utf-8', errors='replace').strip()
                        if response_line:
                            print(response_line)
                    except Exception as read_error:
                        print(f"Error reading line: {read_error}")

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
