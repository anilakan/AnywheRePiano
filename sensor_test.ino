//#include <ArduinoBLE.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(A1, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  int sensorValue = analogRead(A1);
  // print out the value you read:
  float volts = sensorValue * 5.0 / 1024.0;
  //Serial.println(sensorValue);
  Serial.println(volts);
  //Serial.println("----");
  // Serial.println("hello world");
  delay(100);
  if (volts > 0 && volts < 1) {
    digitalWrite(2, HIGH);
    digitalWrite(3, LOW);
    digitalWrite(4, LOW);
    //Serial.println("low volume");
  }
  else if (volts >= 1 && volts < 1.7) {
    digitalWrite(2, LOW);
    digitalWrite(3, HIGH);
    digitalWrite(4, LOW);
    //Serial.println("medium volume");
  }
  else if (volts >= 1.7) {
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(4, HIGH);
    //Serial.println("high volume");
  }
  else {
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(4, LOW);
   // Serial.println("no volume");
  }
}
