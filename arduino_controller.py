import serial
import serial.tools.list_ports
import time

class ArduinoController:
    def __init__(self, baudrate=9600, handshake_msg="HANDSHAKE:PLATFORM_COM"):
        self.serial_connection = None
        self.baudrate = baudrate
        self.handshake_msg = handshake_msg

    def find_arduino_port(self):
        ports = [port.device for port in serial.tools.list_ports.comports() if 'ttyUSB' in port.device or 'ttyACM' in port.device]
        
        if not ports:
            print("No USB/ACM serial ports found.")
            return None

        for port in ports:
            try:
                print(f"Checking port {port}...")
                ser = serial.Serial(port, self.baudrate, timeout=2)
                time.sleep(2)  # Allow Arduino to initialize

                # Send handshake request and check response
                ser.write("HANDSHAKE_REQUEST\n".encode())
                time.sleep(0.5)

                if ser.in_waiting:
                    response = ser.readline().decode().strip()
                    if self.handshake_msg in response:
                        print(f"Handshake successful on port {port}")
                        ser.close()
                        return port

                ser.close()
            except Exception as e:
                print(f"Error checking port {port}: {e}")
        return None

    def connect(self):
        port = self.find_arduino_port()
        if port:
            self.serial_connection = serial.Serial(port, self.baudrate, timeout=1)
            print(f"Connected to Arduino on {port}")
        else:
            raise Exception("No Arduino device found with the correct handshake message.")

    def is_connected(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write("PING\n".encode())
                time.sleep(0.5)
                if self.serial_connection.in_waiting:
                    response = self.serial_connection.readline().decode().strip()
                    return response == "PONG"
            except Exception as e:
                print(f"Error during connection check: {e}")
        return False

    def ensure_connection(self):
        if not self.is_connected():
            print("Lost connection to Arduino. Attempting to reconnect...")
            
            # Close the current connection if open
            try:
                self.close()
            except Exception as e:
                print(f"Error closing port: {e}")

            # Small delay to let the OS release the port
            time.sleep(2)

            # Try to reconnect
            try:
                self.connect()
            except Exception as e:
                print(f"Reconnection failed: {e}")

    def send_command(self, command):
        self.ensure_connection()  # Ensure connection is active before sending
        try:
            self.serial_connection.write(f"{command}\n".encode())
            time.sleep(0.5)
            return self.serial_connection.readline().decode().strip()
        except Exception as e:
            print(f"Error sending command: {e}")
            self.ensure_connection()  # Attempt reconnection if there's an issue

    def close(self):
        if self.serial_connection:
            print("Closing serial connection.")
            self.serial_connection.close()
