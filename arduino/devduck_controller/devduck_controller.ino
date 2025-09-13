#include <Servo.h>

Servo servoX;  // X-axis servo (side-to-side)
Servo servoY;  // Y-axis servo (up-down)

void setup() {
  servoX.attach(12);
  servoY.attach(13);

  servoX.write(60);  // neutral center position
  servoY.write(10);  // slight up
  Serial.begin(9600);

  Serial.println("Duck ready! Type commands: NOD, SHAKE, DANCE, DANCEAGAIN, LOOKUP, LOOKDOWN, LEFT, RIGHT, SURPRISE");
}

// --- Helper functions ---
void nod(int times = 2) {
  for (int i = 0; i < times; i++) {
    servoY.write(20); delay(300);
    servoY.write(0);  delay(300);
  }
}

void shake(int times = 3) {
  for (int i = 0; i < times; i++) {
    servoX.write(20);  delay(250);
    servoX.write(100); delay(250);
  }
  servoX.write(60); // reset center
}

void lookUp() {
  servoY.write(-50);   // head up
  delay(600);
  servoY.write(0);  // back to neutral
}

void lookDown() {
  servoY.write(40);  // head down
  delay(1500);
  servoY.write(10);  // back to neutral
}

void lookLeft() {
  servoX.write(0);
  delay(600);
  servoX.write(60);
}

void lookRight() {
  servoX.write(120);
  delay(600);
  servoX.write(60);
}

void dance() {
  // A little wiggle routine
  for (int i = 0; i < 2; i++) {
    servoX.write(20);  servoY.write(0);  delay(300);
    servoX.write(30); servoY.write(20); delay(300);
    servoX.write(40);  servoY.write(10); delay(300);
    servoX.write(50); servoY.write(20); delay(300);
    servoX.write(60);  servoY.write(10); delay(300);
    servoX.write(70); servoY.write(20); delay(300);
    servoX.write(80);  servoY.write(10); delay(300);
  }
  servoX.write(20); servoY.write(0);
}

void surprise() {
  // sudden head lift
  servoY.write(0); 
  delay(300);

  // frantic shakes
  for (int i = 0; i < 3; i++) {
    servoX.write(20); delay(150);
    servoX.write(100); delay(150);
  }

  // quick double-nod
  for (int i = 0; i < 2; i++) {
    servoY.write(25); delay(200);
    servoY.write(5);  delay(200);
  }

  // quick glance left-right like "what happened?!"
  servoX.write(20); delay(200);
  servoX.write(100); delay(200);
  servoX.write(60);  // back to center

  // settle back to neutral
  servoY.write(10);
}

void danceAgain() {
  // Shake left/right while nodding
  for (int i = 0; i < 3; i++) {
    servoX.write(20);  servoY.write(20); delay(250);  // left + down
    servoX.write(100); servoY.write(0);  delay(250);  // right + up
  }
  // return to neutral
  servoX.write(60);
  servoY.write(10);
}

// --- Main loop listens for serial commands ---
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();

    if (cmd == "NOD") nod();
    else if (cmd == "SHAKE") shake();
    else if (cmd == "DANCE") dance();
    else if (cmd == "LOOKUP") lookUp();
    else if (cmd == "LOOKDOWN") lookDown();
    else if (cmd == "LEFT") lookLeft();
    else if (cmd == "RIGHT") lookRight();
    else if (cmd == "SURPRISE") surprise();
    else if (cmd == "DANCEAGAIN") danceAgain();
    else Serial.println("Unknown command: " + cmd);
  }
}
