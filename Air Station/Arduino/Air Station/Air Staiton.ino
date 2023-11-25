// Derining libraries
#include <WiFi.h>
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>
#include "ACROBOTIC_SSD1306.h"

#define DHTPIN 11
#define DHTTYPE DHT11
#define BUZZER 20
#define RGB_PIN 6
#define NUMPIXELS 1

Adafruit_NeoPixel pixels(NUMPIXELS, RGB_PIN, NEO_GRB + NEO_KHZ800);

DHT dht(DHTPIN, DHTTYPE);

// Replace with your Thingspeak API key
char* thingSpeakApiKey = "EGAZB630GY1CKAHJ";

// Replace with your WiFi credentials
char* ssid = "meow";
char* password = "880ba0ed2335";

float humidity;
float temperature;

WiFiClient espClient;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  // OLED screen setup
  oled.init();
  oled.clearDisplay();

  // RGB setup
  pixels.begin();
  pixels.clear();

  // setting buzzer as output
  pinMode(BUZZER, OUTPUT);

  // start WiFi connection
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Waiting for WiFi connection...");
    oled.setTextXY(0, 3);
    oled.putString("Power on");
    oled.setTextXY(3, 2);
    oled.putString("Waiting for");
    oled.setTextXY(4, 2);
    oled.putString("Connection");
  }

  Serial.println("WiFi connection successful!");
  oled.clearDisplay();
  oled.setTextXY(4, 2);
  oled.putString("Connected");
}

void loop() {
  // Read data from the DHT11 sensor
  
  temperature = dht.readTemperature();

  Serial.println("Temperature: ");
  Serial.println(temperature);
  delay(1000);
  oled.setTextXY(0, 1);
  oled.putString(String(temperature));

  humidity = dht.readHumidity();

  Serial.println("Humidity: ");
  Serial.println(humidity);
  oled.setTextXY(0, 3);
  oled.putString(String(humidity));
  sendToThingSpeak(temperature, humidity);

  if (temperature >= 25) {
    pixels.setPixelColor(0, pixels.Color(255, 0, 0));
    pixels.show();
  }
  if (temperature > 10 && temperature < 25) {
    pixels.setPixelColor(0, pixels.Color(255, 255, 0));
    pixels.show();
  }
  if (temperature <= 10) {
    pixels.setPixelColor(0, pixels.Color(0, 0, 255));
    pixels.show();
  }
  if (temperature < 4) {
    oled.setTextXY(0, 5);
    oled.putString("There is a danger of icing");
    for (int i = 0; i < 4 ; i++) {
      tone(BUZZER, 831);
      delay(500);
      noTone(BUZZER);
    }
  }

  delay(2000);
}

void sendToThingSpeak(float value1, float value2) {
  // ThingSpeak API address
  String apiUrl = "http://api.thingspeak.com/update?api_key=" + String(thingSpeakApiKey) + "&field1=" + String(value1) + "&field2=" + String(value2);

  // Sending HTTP GET request
  WiFiClient client;
  if (client.connect("api.thingspeak.com", 80)) {
    client.println("GET " + apiUrl + " HTTP/1.1");
    client.println("Host: api.thingspeak.com");
    client.println("Connection: close");
    client.println();
    delay(1000); // Short wait for data sending
    client.stop();
  } else {
    Serial.println("Error connecting to ThingSpeak.");
  }
}
