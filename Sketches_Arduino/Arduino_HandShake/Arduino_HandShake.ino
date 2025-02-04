void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    if (command == "HANDSHAKE_REQUEST") {
      Serial.println("HANDSHAKE:PLATFORM_COM");
    } else if (command == "PING") {
      Serial.println("PONG");
    }
  }
}
