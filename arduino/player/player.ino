#include <RF24.h>
#include <RF24Network.h>
#include <Adafruit_GPS.h>


#define CE_PIN   7
#define CSN_PIN 8

//We can now create our Software Serial object after including the library
SoftwareSerial mySerial(3, 2);

//And finally attach our Serial object pins to our GPS module
Adafruit_GPS GPS(&mySerial);

RF24 radio(CE_PIN, CSN_PIN); // Create a Radio
RF24Network network(radio);
const uint16_t nodeTX1 = 01;
const uint16_t nodeRX = 00;
  
const int id = 1;
String dataToSend = "";

void setup() 
{
  Serial.begin(115200);
  GPS.begin(9600); 
GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); //Sets output to only RMC and GGA sentences
GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); //Sets the output to 1/second. If you want you can go higher/lower
GPS.sendCommand(PGCMD_ANTENNA); //Can report if antenna is connected or not

  SPI.begin();
  radio.begin();
  network.begin(124, nodeTX1);
  radio.setDataRate(RF24_250KBPS);  
  radio.startListening();
}

//====================
bool flag = false;
void loop()
{
    GPS.parse(GPS.lastNMEA()); //This is going to parse the last NMEA sentence the Arduino has received, breaking it down into its constituent parts.
GPS.newNMEAreceived(); //This will return a boolean TRUE/FALSE depending on the case.

  if (GPS.fix) {
    dataToSend = id + " " + GPS.fix + String(" ") + GPS.lat + String(" ") + GPS.lon;
  } else {
    dataToSend = id + " " + GPS.fix + String(" none none");
  }
  network.update();
  
  sendData();
}

//====================

void sendData() {

  bool rslt;
  RF24NetworkHeader header(nodeRX); //(nodo destinatario)
  rslt = network.write(header, &dataToSend, sizeof(dataToSend));
  
  if (rslt) 
  {
    Serial.println("  Acknowledge received");
  }
  else
  {
    Serial.println("  Tx failed");
  }
}
