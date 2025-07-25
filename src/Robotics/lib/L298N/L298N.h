#ifndef L298N_H
#define L298N_H

#include <Arduino.h>

class L298N {
  private:
    int enPin, in1, in2;

  public:
    L298N(int en, int i1, int i2);
    void setSpeed(int speed);
    void forward();
    void backward();
    void stop();
};

#endif
