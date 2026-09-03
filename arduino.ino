#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <EEPROM.h> 

LiquidCrystal_I2C lcd(0x27, 16, 2); 

#define DHT_TYPE DHT11
const int dhtVccPin = A0;
const int dhtDataPin = A1;
const int dhtGndPin = A2;
DHT dht(dhtDataPin, DHT_TYPE);

const int shockPin = 2;
const int shockVccPin = 3;
const int shockGndPin = 4;

const int buzzerPin = 5;

const int trigPin = 6;
const int echoPin = 7;

const int ALERT_DISTANCE_CM = 5; 

const int reedPin = 8;
const bool REED_ACTIVE_LOW = true; 
long pulseCount = 0;
int reedLastState = HIGH;
unsigned long reedLastDebounceTime = 0;
const unsigned long reedDebounceDelay = 50;

unsigned long lastMeasureTime = 0;
const unsigned long measureInterval = 120;

unsigned long lastDhtReadTime = 0;
const unsigned long dhtReadInterval = 2000; 
float lastTemp = NAN;
float lastHumidity = NAN;

unsigned long lastDataPrintTime = 0;
const unsigned long dataPrintInterval = 1000; 

long lastDistance = 999;
bool lastShockDetected = false;


const int DIST_WINDOW_SIZE = 5;
long distBuffer[DIST_WINDOW_SIZE];
int distIndex = 0;

void setup() {
  pinMode(shockVccPin, OUTPUT);
  pinMode(shockGndPin, OUTPUT);
  pinMode(shockPin, INPUT_PULLUP);
  digitalWrite(shockVccPin, HIGH);
  digitalWrite(shockGndPin, LOW);

  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  digitalWrite(trigPin, LOW);

  pinMode(dhtVccPin, OUTPUT);
  pinMode(dhtGndPin, OUTPUT);
  digitalWrite(dhtVccPin, HIGH);
  digitalWrite(dhtGndPin, LOW);
  dht.begin();

  pinMode(reedPin, INPUT_PULLUP);
  reedLastState = digitalRead(reedPin);


  for (int i = 0; i < DIST_WINDOW_SIZE; i++) {
    distBuffer[i] = 999;
  }


  EEPROM.get(0, pulseCount);
  if (pulseCount < 0) pulseCount = 0; 

  Serial.begin(9600);
  Serial.print("COUNT,");
  Serial.println(pulseCount);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Starting...");
}

void loop() {
  if (millis() - lastDhtReadTime >= dhtReadInterval) {
    lastDhtReadTime = millis();
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t)) lastTemp = t;
    if (!isnan(h)) lastHumidity = h;
  }

  if (millis() - lastMeasureTime >= measureInterval) {
    lastMeasureTime = millis();

    
    lastDistance = getFilteredDistance();
    lastShockDetected = (digitalRead(shockPin) == HIGH); 
    bool alert = lastShockDetected || (lastDistance <= ALERT_DISTANCE_CM);

    digitalWrite(buzzerPin, alert ? HIGH : LOW);
    updateLcd(lastDistance, lastShockDetected, alert);
  }

  if (millis() - lastDataPrintTime >= dataPrintInterval) {
    lastDataPrintTime = millis();

    if (!isnan(lastTemp) && !isnan(lastHumidity)) {
      Serial.print("DATA,");
      Serial.print(lastDistance);
      Serial.print(",");
      Serial.print(lastShockDetected ? 1 : 0);
      Serial.print(",");
      Serial.print(lastTemp, 1);
      Serial.print(",");
      Serial.println(lastHumidity, 1);
    }
  }

  int reedCurrentState = digitalRead(reedPin);
  if (reedCurrentState != reedLastState) {
    if (millis() - reedLastDebounceTime > reedDebounceDelay) {
      reedLastDebounceTime = millis();
      bool isActivated = REED_ACTIVE_LOW ? (reedCurrentState == LOW) : (reedCurrentState == HIGH);
      if (isActivated) {
        pulseCount++;
        EEPROM.put(0, pulseCount); 
        Serial.print("COUNT,");
        Serial.println(pulseCount);
      }
      reedLastState = reedCurrentState;
    }
  }

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "RESET") {
      pulseCount = 0;
      EEPROM.put(0, pulseCount); 
      reedLastState = digitalRead(reedPin);
      Serial.println("COUNT,0");
    }
  }
}


long getFilteredDistance() {
  long rawDist = measureDistanceCm();
  distBuffer[distIndex] = rawDist;
  distIndex = (distIndex + 1) % DIST_WINDOW_SIZE;

  long sum = 0;
  for (int i = 0; i < DIST_WINDOW_SIZE; i++) {
    sum += distBuffer[i];
  }
  return sum / DIST_WINDOW_SIZE;
}

long measureDistanceCm() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000); 
  if (duration == 0) return 999; 

  return duration * 0.0343 / 2; 
}

void updateLcd(long distance, bool shockDetected, bool alert) {
  char line1[17];
  char line2[17];

  snprintf(line1, sizeof(line1), "Dist:%3ldcm S:%s", distance, shockDetected ? "ON " : "OFF");

  if (alert) {
    snprintf(line2, sizeof(line2), "%-16s", "*** ALERT!! ***");
  } else if (isnan(lastTemp) || isnan(lastHumidity)) {
    snprintf(line2, sizeof(line2), "%-16s", "DHT read error");
  } else {
    char temp[17];
    snprintf(temp, sizeof(temp), "T:%2.0fC H:%2.0f%% OK", lastTemp, lastHumidity);
    snprintf(line2, sizeof(line2), "%-16s", temp);
  }

  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}
