#include "DHT.h"
#include <Servo.h>

/* ---------- CONFIGURATION ---------- */
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int powerPin  = 7;  
const int sensorPin = A1; 
const int dryValue = 0;
const int wetValue = 531;

Servo myServo;
int posClosed = 20;     
int posOpen = 180;    
bool atClosedPosition = true;

/* ---------- TIMING ---------- */
unsigned long lastRead = 0;
const unsigned long interval = 10000; // Read sensors every 10 Seconds
String inputString = "";

void setup() {
  Serial.begin(9600); // Bluetooth on Pins 0 & 1

  myServo.attach(9);
  myServo.write(posClosed); 

  pinMode(powerPin, OUTPUT);
  digitalWrite(powerPin, LOW);

  dht.begin();
  delay(1000); 

  Serial.println("System Ready.");
}

void loop() {
  /* 1. CHECK COMMANDS */
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      inputString.trim();
      if (inputString.equalsIgnoreCase("go")) {
        // Reset timer so sensors don't activate during the heavy movement
        lastRead = millis(); 
        toggleServoFullSpeed();
      }
      inputString = "";
    } else {
      inputString += c;
    }
  }

  /* 2. READ SENSORS (Only if 10s passed) */
  if (millis() - lastRead >= interval) {
    lastRead = millis();
    readSensors();
  }
}

/* --- FULL SPEED SERVO MOVEMENT --- */
void toggleServoFullSpeed() {
  if (atClosedPosition) {
    // Snap directly to OPEN
    myServo.write(posOpen);
    Serial.println("Servo: OPEN");
  } else {
    // Snap directly to CLOSED
    myServo.write(posClosed);
    Serial.println("Servo: CLOSED");
  }
  
  atClosedPosition = !atClosedPosition;
  
  // CRITICAL: Longer pause (1 sec) to let Capacitor recharge 
  // and battery recover after the big jump.
  delay(1000); 
}

void readSensors() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  delay(50); 

  digitalWrite(powerPin, HIGH);
  delay(50);
  int raw = analogRead(sensorPin);
  digitalWrite(powerPin, LOW);
  
  int soil = map(raw, dryValue, wetValue, 0, 100);
  soil = constrain(soil, 0, 100);
  delay(50); 

  // --- SEND DATA ---
  Serial.println("--------------------");
  Serial.print("Temp: "); Serial.print(t); Serial.println(" C");
  Serial.print("Humi: "); Serial.print(h); Serial.println(" %");
  Serial.print("Soil: "); Serial.print(soil); Serial.println(" %");
}