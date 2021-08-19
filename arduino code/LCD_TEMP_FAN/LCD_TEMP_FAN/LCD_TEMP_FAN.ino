//TEMP_HUMD
#include <dht11.h>
dht11 DHT;
#define DHT11_PIN 10

//LCD
#include <LiquidCrystal.h>
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

//FAN CONTROL
const int fan_control_pin = 9;



void setup(){

  // Setup Fan I/O
  pinMode(fan_control_pin, OUTPUT);
  digitalWrite(fan_control_pin, LOW);

  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);

  //TEMP_HUMD
  Serial.begin(9600);
  Serial.println("DHT TEST PROGRAM ");
  Serial.print("LIBRARY VERSION: ");
  Serial.println(DHT11LIB_VERSION);
  Serial.println();
  Serial.println("Type,\tstatus,\tHumidity (%),\tTemperature (C)");
}



void loop(){

//===========================       TEMP HUMD        ==========================================
  int chk;
  Serial.print("DHT11, \t");
  chk = DHT.read(DHT11_PIN);    // READ DATA
  switch (chk){
    case DHTLIB_OK:
                Serial.print("OK,\t");
                break;
    case DHTLIB_ERROR_CHECKSUM:
                Serial.print("Checksum error,\t");
                break;
    case DHTLIB_ERROR_TIMEOUT:
                Serial.print("Time out error,\t");
                break;
    default:
                Serial.print("Unknown error,\t");
                break;
  }
  
 // DISPLAT DATA ON SERIAL MONITOR
  Serial.print(DHT.humidity,1);
  Serial.print(",\t");
  Serial.println(DHT.temperature,1);
  
  float temp = (DHT.temperature);
  Serial.println(temp);
  
//===========================================================================================


//=============================       DISPLAY TEMP_HUMD ON LCD      =========================
  
  // set the cursor to column 0, line 0
  lcd.setCursor(0, 0);
  lcd.print("Temp:");
  // set the cursor to column 0, line 6
  lcd.setCursor(6, 0);
  lcd.print(DHT.temperature,1);

  lcd.setCursor(0, 1);
  lcd.print("Humd:");
  lcd.setCursor(6,1);
  lcd.print(DHT.humidity,1);
  
//=========================================================================================


//=========================     FAN CONTROL     ===========================================
 
 if (temp > 25.3){
  
  digitalWrite(fan_control_pin, HIGH);
  Serial.println("??");
 }
 else{
  digitalWrite(fan_control_pin, LOW);
 }

//=========================================================================================
 
  //10 seconds delay update
  delay(5000);
  
}
