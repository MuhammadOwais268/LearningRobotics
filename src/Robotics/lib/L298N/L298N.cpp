#include "L298N.h"

L298N::L298N(int en, int i1, int i2) {
  enPin = en;
  in1 = i1;
  in2 = i2;

  pinMode(enPin, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
}

void L298N::setSpeed(int speed) {
  analogWrite(enPin, constrain(speed, 0, 255));
}

void L298N::forward() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
}

void L298N::backward() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
}

void L298N::stop() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
}
