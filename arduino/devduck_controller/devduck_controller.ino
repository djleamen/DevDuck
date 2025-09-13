#include <Servo.h>

Servo neck_side;
Servo neck_up;
Servo left_wing;
Servo right_wing;

// Servo pins
int side = 9;
int up = 10;
int left = 11;
int right = 13;

String inputString = "";  // store incoming serial text
bool stringComplete = false;

void setup() {
  Serial.begin(9600);

  neck_side.attach(side);
  neck_up.attach(up);
  left_wing.attach(left);
  right_wing.attach(right);

  // Start all servos at 90 (neutral position)
  neck_side.write(90);
  neck_up.write(90);
  left_wing.write(90);
  right_wing.write(90);

  Serial.println("Ready for commands: yes, no, flap, reset...");
}

void loop() {
  // Check if a full command was received
  if (stringComplete) {
    inputString.trim();  // remove whitespace/newlines
    handleCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

// Function to handle commands
void handleCommand(String cmd) {
  if (cmd.equalsIgnoreCase("yes")) {
    Serial.println("Nodding Yes");
    for (int i = 0; i < 2; i++) {
      neck_up.write(60);  // down
      delay(300);
      neck_up.write(120); // up
      delay(300);
    }
    neck_up.write(90); // back to neutral
  } 
  else if (cmd.equalsIgnoreCase("no")) {
    Serial.println("Shaking No");
    for (int i = 0; i < 2; i++) {
      neck_side.write(60);  // left
      delay(300);
      neck_side.write(120); // right
      delay(300);
    }
    neck_side.write(90); // neutral
  } 
  else if (cmd.equalsIgnoreCase("flap")) {
    Serial.println("Flapping Wings");
    for (int i = 0; i < 3; i++) {
      left_wing.write(30);
      right_wing.write(150);
      delay(300);
      left_wing.write(150);
      right_wing.write(30);
      delay(300);
    }
    left_wing.write(90);
    right_wing.write(90);
  }
  else if (cmd.equalsIgnoreCase("reset")) {
    Serial.println("Resetting to neutral");
    neck_side.write(90);
    neck_up.write(90);
    left_wing.write(90);
    right_wing.write(90);
  }
  else {
    Serial.print("Unknown command: ");
    Serial.println(cmd);
  }
}

// SerialEvent occurs whenever new data comes in
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {   // command ends when newline is received
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}
