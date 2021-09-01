//Temp and Humd Sensor
#include <dht11.h>
dht11 DHT;
#define DHT11_PIN A8

//Rasp Pi to Arduino
int Function = '0';


//LCD
#include <LiquidCrystal.h>
const int rs = 13, en = 12, d4 = 8, d5 = 9, d6 = 10, d7 = 11;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


//Initialized Variables
const int WASHLED = A0;
const int DRYLED = A1;
const int SANITIZELED = A2;

const int fan_control_pin = A4;

int FLOATSW = 7; 
int PUMP = A3;
int LEDSTRIP = A5;

int WASH = 0;
int DRY = 0;
int SANITIZE = 0;

int Drain = 0;
int FINISHWASH = 0;
int FINISHDRY = 0;
int FINISHSAN = 0;
int STOP = 0;
int CAMERA_1 = 0;
int CAMERA_2 = 0;
int FLOATDETECT = 0;


//Timer
unsigned long startMillis;
unsigned long currentMillis;


//Stepper Motor
#include <Stepper.h>
// Define number of steps per rotation:
const int angle_control = (1024/3);     //60 degrees
const int dry_control = 2048;      //180 degrees


// Wiring:
// Pin 6 to IN1 on the ULN2003 driver
// Pin 5 to IN2 on the ULN2003 driver
// Pin 4 to IN3 on the ULN2003 driver
// Pin 3 to IN4 on the ULN2003 driver
// Create stepper object called 'myStepper', note the pin order:
Stepper myStepper = Stepper(angle_control, 6, 4, 5, 3);



//========================== VOID SETUP ===================================
void setup()
{
  //Initialize Serial
  Serial.begin(9600);

  //Set Row/Column For LCD
  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("TEAM 21");
  lcd.setCursor(0, 1);
  lcd.print("OIP PROJECT");

  //Set I/O for Buttons/LED
  pinMode(WASH, INPUT);
  pinMode(SANITIZE, INPUT);
  pinMode(WASHLED, OUTPUT);
  pinMode(DRYLED, OUTPUT);
  pinMode(SANITIZELED, OUTPUT);

  //Set I/O and status for Pump / LED Strip / USB Fan
  pinMode(PUMP, OUTPUT);
  digitalWrite(PUMP, LOW);
  pinMode(LEDSTRIP, OUTPUT);
  digitalWrite(LEDSTRIP, LOW);
  pinMode(fan_control_pin, OUTPUT);
  digitalWrite(fan_control_pin, LOW);
  pinMode(FLOATDETECT, INPUT);

  
  // Set the speed to 60 rpm (Stepper Motor)
  myStepper.setSpeed(60); 
}

//========================================================================



//========================== VOID LOOP ===================================
void loop()
{
  
 
  
  if (Serial.available() > 0) {
     

//=============================== Function 1 =============================

    
    Function = (Serial.read());
    if (Function == '1') {

      
      Serial.println("Camera Detection");
      while(CAMERA_1 <5){

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Detecting");
        delay(500);
 
        
        Function = (Serial.read()); 
        if (Function == 'a') {
          CAMERA_1 += 1;
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Rotating Rack...");
          
          myStepper.step(angle_control);
          Serial.println("Next Angle");
          
        }

        Function = (Serial.read()); 
        if (Function == '0') {
 
          Serial.println("STOP"); 
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Detecting Stop");
          break;  
        }
      }

      
      myStepper.step(angle_control);
      delay(2000);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Pump on,");
      lcd.setCursor(0, 1);
      lcd.print("Filling Water");
      
      digitalWrite(PUMP, HIGH);
      delay(2000);

    
      while(1){ 

        //STOP FILLING WATER
        Function = (Serial.read()); 
        
        if (Function == '0') {
          
          STOP = 1;
          Drain = 0;
          DRY = 0;
          FINISHDRY = 0;
          
          Serial.println("STOP"); 
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Process Stop");
          lcd.setCursor(0, 1);
          lcd.print("Draining Water");
          digitalWrite(PUMP, LOW);
          
          delay(2000);

          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("TEAM 21");
          lcd.setCursor(0, 1);
          lcd.print("OIP PROJECT");
          
          break;
          
            }


      //CHECK WATER LEVEL
        FLOATDETECT = digitalRead(FLOATSW);
          
          if (FLOATDETECT == HIGH){
            
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Tank Filled");
          lcd.setCursor(0, 1);
          lcd.print("Pump off");
    
          
          digitalWrite(PUMP, LOW);
          delay(5000);
          

          
           startMillis = millis()/1000;  // Start Washing time


            //WASHING
            while(1){

            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Washing...");
            
            currentMillis = millis()/1000;


            
          
            if (currentMillis - startMillis >= 10 ){  //Checking for Elaspe time.
                Drain = 1;
                break;
              }

            // STOP WASHING
            Function = (Serial.read()); 
            if (Function == '0') {
            
              STOP = 1;
              Drain = 0;
              DRY = 0;
              FINISHDRY = 0;
              
              Serial.println("STOP"); 
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Washing Stop");
              lcd.setCursor(0, 1);
              lcd.print("Draining Water");
              digitalWrite(PUMP, LOW);
              
              break;
              //Drain Water
               
            }

            //MOTOR LEFT RIGHT MOTION
            //Serial.println(currentMillis - startMillis); //print Time
            myStepper.step(angle_control);
            myStepper.step(-angle_control);
        }


      //DRAINING OF WATER
      if (Drain == 1){
  
        delay(2000);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Draining");
        lcd.setCursor(0, 1);
        lcd.print("Water");
        
        delay(1000);
    
      startMillis = millis()/1000;  // Start Draining Time

      
      while(1){
      
        currentMillis = millis()/1000;

       
        
        if (currentMillis - startMillis >= 10 ){  //Checking for Elapse time
  
        delay(1000);
        
        digitalWrite(WASHLED, HIGH);
        Drain = 0;
        DRY = 1;
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Wash Completed");
        
        delay(2000);
        break;
        
        }

        //STOP PROCESS, CONTINUE DRAINING
        Function = (Serial.read()); 
        if (Function == '0') {
 
          STOP = 1;
          Drain = 0;
          DRY = 0;
          FINISHDRY = 0;
          Serial.println("STOP"); 
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Process Stop");
          lcd.setCursor(0, 1);
          lcd.print("Draining Water");
          digitalWrite(PUMP, LOW);
          break;
          //Drain Water
          
        }
        
        }
    }


    //DRYING PROCESS
    if (DRY == 1){

      myStepper.setSpeed(15); 
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Drying system");
      lcd.setCursor(0, 1);
      lcd.print("commencing");
      delay(3000);

      digitalWrite(WASHLED, LOW);
      digitalWrite(fan_control_pin, HIGH);
      
      
  
      startMillis = millis()/1000;  // Start Drying Time

        
      while(1){


        int chk;
        chk = DHT.read(DHT11_PIN);    // READ DATA
        
        lcd.clear();
        //Set Readings to LCD
        lcd.setCursor(0, 0);
        lcd.print("Temp:");
        // set the cursor to column 0, line 6
        lcd.setCursor(6, 0);
        lcd.print(DHT.temperature,1);
      
        lcd.setCursor(0, 1);
        lcd.print("Humd:");
        lcd.setCursor(6,1);
        lcd.print(DHT.humidity,1);
  
        currentMillis = millis()/1000;
        myStepper.step(dry_control);
        myStepper.step(-dry_control);

        
        
        if (currentMillis - startMillis >= 15 )  //Checking for Elaspe time.
        {
          myStepper.setSpeed(60); 
          digitalWrite(fan_control_pin, LOW);
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Checking of");
          lcd.setCursor(0, 1);
          lcd.print("Syringes");


          Serial.println("Camera Detection");
          
          //Checking of Syringes / Turn 60 Degrees

          while(CAMERA_2 <5){

            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Classifying");
            delay(500);
 
             
            Function = (Serial.read()); 
            if (Function == 'a') {
              CAMERA_2 += 1;
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Rotating Rack...");
              
              myStepper.step(angle_control);
              Serial.println("Next Angle");
            }

            Function = (Serial.read()); 
            if (Function == '0') {
 
              Serial.println("STOP"); 
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Classifying Stop");
              break;  
        }
          }
         
          myStepper.step(angle_control);
          FINISHDRY = 1;
          DRY = 0;
          digitalWrite(DRYLED, HIGH);
          break;
    }

          //STOP DRYING PROCESS  
          Function = (Serial.read()); 
          if (Function == '0') {
 
            STOP = 1;
            Drain = 0;
            DRY = 0;
            FINISHDRY = 0;
            Serial.println("STOP"); 
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Drying Stop");
            lcd.setCursor(0, 1);
            lcd.print("Fan off");
            digitalWrite(fan_control_pin, LOW);
            break;
            
          }
    
    }  
    } 


    if (FINISHDRY == 1){
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Sanitizing system");
      lcd.setCursor(0, 1);
      lcd.print("commencing");
      delay(3000);
      
      digitalWrite(DRYLED, LOW);
      digitalWrite(LEDSTRIP, HIGH);
  
      startMillis = millis()/1000;  // Start Drying Time

        
      while(1){
        
        int chk;
        chk = DHT.read(DHT11_PIN);    // READ DATA
  
        lcd.clear();
        //Set Readings to LCD
        lcd.setCursor(0, 0);
        lcd.print("Temp:");
        // set the cursor to column 0, line 6
        lcd.setCursor(6, 0);
        lcd.print(DHT.temperature,1);
      
        lcd.setCursor(0, 1);
        lcd.print("Humd:");
        lcd.setCursor(6,1);
        lcd.print(DHT.humidity,1);
  
        currentMillis = millis()/1000;

        
        
        if (currentMillis - startMillis >= 20 )  //Checking for Elaspe time.
        {
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Sanitising");
          lcd.setCursor(0, 1);
          lcd.print("Finished");
          digitalWrite(LEDSTRIP, LOW);
          digitalWrite(SANITIZELED, HIGH);
          delay(2000);
          digitalWrite(SANITIZELED, LOW);
          FINISHSAN = 1;
          Serial.println("Finish Sanitising");

          //Reset LCD
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("TEAM 21");
          lcd.setCursor(0, 1);
          lcd.print("OIP PROJECT");
          break;
    }

        //STOP SANITISING 
        Function = (Serial.read()); 
        if (Function == '0') {
        
          STOP = 1;
          Drain = 0;
          DRY = 0;
          FINISHDRY = 0;
          Serial.println("STOP"); 
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Sanitizing ");
          lcd.setCursor(0, 1);
          lcd.print("Stop");
          digitalWrite(LEDSTRIP, LOW);
          delay(2000);
          break;
          }
          
    }
    }
    if(FINISHSAN == 1){
      break; //break out of first system
    }

    if(STOP == 1){
      STOP = 0;
      Drain = 0;
      DRY = 0;
      FINISHDRY = 0;
      delay(2000);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("TEAM 21");
      lcd.setCursor(0, 1);
      lcd.print("OIP PROJECT");
      break;
    }
    }
    }
  }
  



    
//===================== SANITIZE FUNCTION =======================  



  if (Function == '2') {

    Serial.println("Sanitise System");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sanitizing system");
    lcd.setCursor(0, 1);
    lcd.print("commencing");
    delay(2000);
    
    digitalWrite(LEDSTRIP, HIGH);

    startMillis = millis()/1000;  // Start Drying Time
      
    while(1){
      
      int chk;
      chk = DHT.read(DHT11_PIN);    // READ DATA

      lcd.clear();
      //Set Readings to LCD
      lcd.setCursor(0, 0);
      lcd.print("Temp:");
      // set the cursor to column 0, line 6
      lcd.setCursor(6, 0);
      lcd.print(DHT.temperature,1);
    
      lcd.setCursor(0, 1);
      lcd.print("Humd:");
      lcd.setCursor(6,1);
      lcd.print(DHT.humidity,1);

      currentMillis = millis()/1000;
      
      if (currentMillis - startMillis >= 20 )  //Checking for Elaspe time.
      {
        digitalWrite(LEDSTRIP, LOW);
        digitalWrite(SANITIZELED, HIGH);
        delay(2000);
        digitalWrite(SANITIZELED, LOW);
        //Reset LCD
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("TEAM 21");
        lcd.setCursor(0, 1);
        lcd.print("OIP PROJECT");

        break;

      
      }

      Function = (Serial.read()); 
      if (Function == '0') {
        Serial.println("STOP"); 
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Sanitising");
        lcd.setCursor(0, 1);
        lcd.print("Stop");
        digitalWrite(LEDSTRIP, LOW);
        break; 
          }
       
    
  }
    
   
  } 

  }
}

  




 
