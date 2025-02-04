from flask import Flask, render_template, jsonify
from arduino_controller import ArduinoController
import threading
import time

def create_app():
    app = Flask(__name__)
    arduino = ArduinoController()

    def monitor_connection():
        """Periodically check if the Arduino is still connected and reconnect if needed."""
        while True:
            if not arduino.is_connected():
                print("Periodic check: Lost connection. Attempting to reconnect...")
                try:
                    arduino.connect()
                    print("Reconnected to Arduino successfully.")
                except Exception as e:
                    print(f"Reconnection attempt failed: {e}")
            time.sleep(5)  # Check every 5 seconds

    # Start background monitoring thread
    monitor_thread = threading.Thread(target=monitor_connection, daemon=True)
    monitor_thread.start()

    try:
        arduino.connect()  # Initial connection
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/check_connection', methods=['GET'])
    def check_connection():
        if arduino.is_connected():
            return jsonify({"status": "connected"})
        else:
            return jsonify({"status": "disconnected"})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
