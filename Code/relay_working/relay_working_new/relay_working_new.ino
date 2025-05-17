const int controlPin[16] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}; // define pins
const int triggerType = LOW; // your relay type
int suctionTime = 250; // delay in loop

void setup() {
  for (int i = 0; i < 16; i++) {
    pinMode(controlPin[i], OUTPUT); // set pin as output
    if (triggerType == LOW) {
      digitalWrite(controlPin[i], HIGH); // set initial state OFF for low trigger relay
    } else {
      digitalWrite(controlPin[i], LOW); // set initial state OFF for high trigger relay     
    }
  }
  Serial.begin(9600);
  Serial1.begin(115200);
}

void loop() {
  if (Serial1.available() > 0) {
    String receivedData = Serial1.readString(); // Read data until newline

    if (receivedData.length() > 0) {
      // Parse the received data and control the relays
      controlRelays(receivedData);
    }
  }
}

void controlRelays(String data) {
  int commaIndex;
  int relayNumbers[16]; // Array to hold relay numbers to activate
  int relayCount = 0;

  // Parse the received data and store relay numbers
  while (data.length() > 0) {
    commaIndex = data.indexOf(',');
    int relayNumber;

    if (commaIndex == -1) {
      relayNumber = data.toInt(); // Last or single number in the data
      data = "";
    } else {
      relayNumber = data.substring(0, commaIndex).toInt(); // Extract the number
      data = data.substring(commaIndex + 1); // Update the string
    }

    relayNumbers[relayCount++] = relayNumber; // Store relay number
  }

  // Activate relays simultaneously
  for (int i = 0; i < relayCount; i++) {
    int relayNumber = relayNumbers[i];
    if (relayNumber >= 1 && relayNumber <= 17) {
      int pinIndex = relayNumber - 1; // Calculate the index for controlPin array
      digitalWrite(controlPin[pinIndex], triggerType); // Turn the relay ON
    }
  }

  delay(suctionTime); // Wait for a specified time

  // Turn off all relays simultaneously
  for (int i = 0; i < relayCount; i++) {
    int relayNumber = relayNumbers[i];
    if (relayNumber >= 1 && relayNumber <= 17) {
      int pinIndex = relayNumber - 1; // Calculate the index for controlPin array
      digitalWrite(controlPin[pinIndex], !triggerType); // Turn the relay OFF
    }
  }
}
