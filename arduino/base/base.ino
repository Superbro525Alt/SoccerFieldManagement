#include <SPI.h>
#include <RF24.h>
#include <RF24Network.h>
#include "StringSplitter.h"

#define CE_PIN   7
#define CSN_PIN 8

RF24 radio(CE_PIN, CSN_PIN);
RF24Network network(radio);
const uint16_t nodeRX = 00;


int dataReceived; // this must match dataToSend in the TX
//invio un int così dal numero so chi lo ha inviato
bool newData = false;

//===========

void setup()
{
  Serial.begin(9600);
  Serial.println("SimpleRx Starting");

  SPI.begin();
  radio.begin();
  network.begin(124, nodeRX);  //canale, indirizzo nodo
  radio.setDataRate(RF24_250KBPS);
  radio.startListening();
}

//=============

void loop()
{
  network.update();
  while (network.available()) //Non vi entra se non vi sono dati
  {
    RF24NetworkHeader header;
    network.read(header, &dataReceived, sizeof(dataReceived));
    StringSplitter *splitter = new StringSplitter(dataReceived, ' ', 1);
    Serial.println(dataReceived); 
    switch (splitter->getItemAtIndex(0).toInt())
    {
      case 1: Serial.println("From TX1");
        break;
      case 2: Serial.println("From TX2");
        break;
      case 3: Serial.println("From TX3");
        break;
      default: Serial.println("Error: ");
        break;
    }
  }
}
