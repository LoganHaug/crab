#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>

#include <BluetoothSerial.h>

const char* device_name = "cr4b-brain";

// Check if Bluetooth is available
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

// Check Serial Port Profile
#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Port Profile for Bluetooth is not available or not enabled. It is only available for the ESP32 chip.
#endif

BluetoothSerial SerialBT;

#define SERVOMIN  150 // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // This is the 'maximum' pulse length count (out of 4096)
#define USMIN  600 // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX  2400 // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(); // PCA9685

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  delay(100);
  pwm.begin();
  pwm.setOscillatorFrequency(26500000);  // chip dependent, test for pwm hz
  pwm.setPWMFreq(50); // PWM Freq of rc electric parts classic esc 30A
  Wire.setClock(100000); // Normal clock hz
  delay(100); // allow i2c device to initialize
  Serial.println("test");

  // begin bluetooth connection
  SerialBT.begin(device_name);
  delay(500); // bluetooth amirite haha
}

void setAng(int servonum, int ang) {
  pwm.setPWM(servonum, 0, floor(map(ang, 0, 180, SERVOMIN, SERVOMAX)));
}

void loop() {
  // Drive each servo one at a time using setPWM()
  Serial.println("serv 0");
  for (int i = 0; i < 60; i += 5) {
    setAng(0,  30+i);
    delay(100);
  }
  Serial.println("serv 1");
  for (int i = 0; i < 60; i += 5) {
    setAng(1,  90+i);
    delay(100);
  }
  Serial.println("serv 2");
  for (int i = 0; i < 60; i += 5) {
    setAng(2,  40+i); 
    delay(100);
  }
}
