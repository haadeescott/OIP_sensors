#include <dht11.h>
dht11 DHT;
#define DHT11_PIN 13

void setup(){
  Serial.begin(9600);
  Serial.println("DHT TEST PROGRAM ");
  Serial.print("LIBRARY VERSION: ");
  Serial.println(DHT11LIB_VERSION);
  Serial.println();
  Serial.println("Type,\tstatus,\tHumidity (%),\tTemperature (C)");
}

void loop(){
  int chk;
  Serial.print("DHT11, \t");
  chk = DHT.read(DHT11_PIN);    // READ DATA
  switch (chk){
    case DHTLIB_OK:
                Serial.println("OK,\t");
                break;
    case DHTLIB_ERROR_CHECKSUM:
                Serial.println("Checksum error,\t");
                break;
    case DHTLIB_ERROR_TIMEOUT:
                Serial.println("Time out error,\t");
                break;
    default:
                Serial.println("Unknown error,\t");
                break;
  }
 // DISPLAT DATA
  Serial.print(DHT.humidity,1);
  Serial.print(",\t");
  Serial.println(DHT.temperature,1);

  delay(2000);
}
