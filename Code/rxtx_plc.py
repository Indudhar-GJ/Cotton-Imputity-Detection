import serial
import time

def main():
    # Configuration for the serial port
    serial_port = '/dev/ttyUSB0'  # Replace with the actual port (e.g., COM3 on Windows)
    baud_rate = 115200            # Set the baud rate of your device
    timeout = 1                  # Timeout in seconds

    try:
        # Open the serial connection with 8N1 settings
        with serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,  # 8 data bits
            parity=serial.PARITY_NONE,  # No parity
            stopbits=serial.STOPBITS_ONE,  # 1 stop bit
            timeout=timeout
        ) as ser:
            print(f"Connected to {serial_port} at {baud_rate} baud (8N1).")
            
            while True:
                # Take user input to send commands
                hex_input = input("Enter the hex value to send (or 'exit' to quit): ")
                
                if hex_input.lower() == 'exit':
                    print("Exiting...")
                    break
                
                try:
                    # Convert hex string to bytes
                    hex_bytes = bytes.fromhex(hex_input)
                    ser.write(hex_bytes)  # Send the bytes to the serial device
                    print(f"Sent: {hex_input}")
                    
                    # Read the response (if any)
                    time.sleep(0.1)  # Small delay for the device to respond
                    if ser.in_waiting > 0:
                        response = ser.read(ser.in_waiting).hex()  # Read response as hex
                        print(f"Received: {response}")
                    else:
                        print("No response received.")
                
                except ValueError:
                    print("Invalid hex input. Please enter a valid hex string (e.g., 'A1B2C3').")
    
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt.")

if __name__ == "__main__":
    main()

