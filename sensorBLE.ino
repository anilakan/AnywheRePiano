/*
  Arduino Nano 33 BLE Getting Started
  BLE peripheral with a simple Hello World greeting service that can be viewed
  on a mobile phone
  Adapted from Arduino BatteryMonitor example
*/

#include <ArduinoBLE.h>

//static const char* greeting = "It's me World!";

int greeting = 1;
double sensorValue = 00000;

//BLEService greetingService("180C");  // User defined service

BLEService pressureService("180C"); 

BLEIntCharacteristic pressureCharacteristic("2A56",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will only be able to read this
// 

void setup() {
  Serial.begin(9600);    // initialize serial communication

  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin
  pinMode(A0, INPUT); // good
  pinMode(A1, INPUT); // good
  pinMode(A2, INPUT);
  pinMode(A3, INPUT); // being replaced
  pinMode(A4, INPUT); // turn around

  if (!BLE.begin()) {   // initialize BLE
    Serial.println("starting BLE failed!");
    while (1);
  }
  BLE.setLocalName("ThisIsNish");  // Set name for connection
  BLE.setDeviceName("NishBLE!"); // this is what i will actually search for 
  BLE.setAdvertisedService(pressureService); // Advertise service
  // BLE.setAdvertisedService(pressureService)
  pressureService.addCharacteristic(pressureCharacteristic); // Add characteristic to service
  BLE.addService(pressureService); // Add service
  pressureCharacteristic.setValue(sensorValue); // Set greeting string

  BLE.advertise();  // Start advertising
  Serial.print("Peripheral device MAC: ");
  Serial.println(BLE.address());
  Serial.println("Waiting for connections...");
}

// 0 - off, 1 - low... etc 
// __ __ __ __ __ 5 bytes sent in characteristic (LP, LR, LM, LI, LT) --> time? 
// __ __ __ __ __ (RT, RI, RM, RR, RP)


// send every 10 ms

unsigned long start_time;
void loop() {
  BLEDevice central = BLE.central();  // Wait for a BLE central to connect

  // if a central is connected to the peripheral:
  if (central) {
    Serial.print("Connected to central MAC: ");
    // print the central's BT address:
    start_time = millis();
    Serial.println(central.address());
    // turn on the LED to indicate the connection:
    // digitalWrite(LED_BUILTIN, HIGH);

    while (central.connected()){
      if (millis() - start_time > 10) {
        start_time = millis();
        int sensor1 = analogRead(A0);
        int sensor2 = analogRead(A1);
        int sensor3 = analogRead(A2);
        int sensor4 = analogRead(A3);
        int sensor5 = analogRead(A4);
        // print out the value you read:
        float volts1 = sensor1 * 5.0 / 1024.0;
        float volts2 = sensor2 * 5.0 / 1024.0;
        float volts3 = sensor3 * 5.0 / 1024.0;
        float volts4 = sensor4 * 5.0 / 1024.0;
        float volts5 = sensor5 * 5.0 / 1024.0;
        Serial.println(volts1);
        // Serial.println(volts2);
        // Serial.println(volts3);
        // Serial.println(volts4);
        // Serial.println(volts5);
        Serial.println("------");
        char value1 = 0;
        byte value2 = 0;
        byte value3 = 0;
        byte value4 = 0;
        byte value5 = 0;
        if (volts1 > 0.5 && volts1 < 1.25) {
          value1 = 1;
        }
        else if (volts1 >= 1.25 && volts1 < 2) {
          value1 = 2;
        }
        else if (volts1 >= 2) {
          value1 = 3;
        }
        if (volts2 > 0.3 && volts2 < 1) {
          value2 = 1;
        }
        else if (volts2 >= 1 && volts2 < 2) {
          value2 = 2;
        }
        else if (volts2 >= 2) {
          value2 = 3;
        }
        if (volts3 > 0.1 && volts3 < 1) {
          value3 = 1;
        }
        else if (volts3 >= 1 && volts3 < 2) {
          value3 = 2;
        }
        else if (volts3 >= 2) {
          value3 = 3;
        }
        if (volts4 > 0.5 && volts4 < 1.25) {
          value4 = 1;
        }
        else if (volts4 >= 1.25 && volts4 < 2) {
          value4 = 2;
        }
        else if (volts4 >= 2) {
          value4 = 3;
        }
        if (volts5 > 0.1 && volts5 < 0.75) {
          value5 = 1;
        }
        else if (volts5 >= 0.75 && volts5 < 1.5) {
          value5 = 2;
        }
        else if (volts5 >= 1.5) {
          value5 = 3;
        }
        // sensorValue = value1+(65535*value1) + value2+(4095*value2) + value3+(255*value3) + value4+(15*value4) + value5+(0*value5);
        sensorValue = value1+(1048575*value1) + value2+(65535*value2) + value3+(4095*value3) + value4+(255*value4) + value5+(15*value5);
        // value1+(ffff-1 * value1) + value2+(fff-1 * value2) + value3+(ff-1 * value3) + value4+(f-1 * value4) + value5
        // 
        // Serial.println(sensorValue);
        pressureCharacteristic.setValue(sensorValue);
      }
      //delay(2000);  
      //greetingCharacteristic.setValue(greeting); // Set greeting string


    } // keep looping while connected
    
    // when the central disconnects, turn off the LED:
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print("Disconnected from central MAC: ");
    Serial.println(central.address());
  }
}