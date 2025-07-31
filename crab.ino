#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>
#include <BluetoothSerial.h>
#include <string.h>

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

void setAng(int servonum, int ang) {
  if ((servonum >= 0) && (servonum < 12)) {
    if ((ang >= SERVOMIN) && (ang <= SERVOMAX)) {
      pwm.setPWM(servonum, 0, ang);
    }
  }
}

int ang;
int readAng() {
  ang = SerialBT.read() << 8;
  return ang + SerialBT.read();
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  delay(100);
  pwm.begin();
  pwm.setOscillatorFrequency(26500000);  // chip dependent, test for pwm hz
  pwm.setPWMFreq(50); // PWM Freq of rc electric parts classic esc 30A
  Wire.setClock(100000); // Normal clock hz
  delay(100); // allow i2c device to initialize

  // begin bluetooth connection
  SerialBT.begin(device_name);
  delay(500); // bluetooth amirite haha
}

// "#" -> start byte
#define MSG_START '#'
#define MSG_DELIN '+'
#define MSG_END '$'
// "$" -> end byte
// example packet with each byte in brackets: <start><char servo><delin><int ang><end>
int serv;
int start;
void loop() {
  while (SerialBT.available()) {
    start = SerialBT.read();
    if (start == MSG_START) {
      serv = SerialBT.read();
      } if (SerialBT.read() == MSG_DELIN) {
        ang = readAng();
      }
      if (SerialBT.read() == MSG_END) {
        setAng(serv, ang);
      }
    }
  delay(20); // 50 hz = 20ms period
}

