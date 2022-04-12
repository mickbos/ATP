#include <Arduino.h>

extern "C" {
    void serialBegin()
    {
        Serial.begin(9600);
    }

    void println(int i)
    {
        Serial.println(i);
    }

    bool odd(int i);
    bool even(int i);
    int sommig(int i);
    int add(int a, int b);
    int subtract(int a, int b);
}

void setup(){
    serialBegin();
}

void loop(){
    sommig(83);
    Wait(500);
}