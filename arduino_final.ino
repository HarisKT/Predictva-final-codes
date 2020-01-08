 #include <Wire.h>
#include <DHT.h>
#include <DHT_U.h>
#include <DHT.h>
#define serialPi Serial
#define SLAVE_ADDRESS 0x08
#define DHTPIN 13
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
const int voltageSensor = A0;
float vOUT = 0.0;
float vIN = 0.0;
float R1 = 30000.0;
float R2 = 7500.0;
int value = 0;
const int currentPin = A1;
int sensitivity = 66;
int adcValue= 0;
int offsetVoltage = 2500;
double adcVoltage = 0;
double currentValue = 0;
//float temp;
String rqst,temp,a,b,c;
int req;
int led = 12;
int vs =9;
String s1;
String s2;
void setup() {
  Wire.begin(SLAVE_ADDRESS);
  pinMode(vs, INPUT);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  //Serial.println("Ready!");
  dht.begin();
  while(!serialPi);
  Serial.begin(9600);
}

void loop() {
  temp= dht.readTemperature();
  value = analogRead(voltageSensor);
  vOUT = (value * 5.0) / 1024.0;
  vIN = vOUT / (R2/(R1+R2));
  adcValue = analogRead(currentPin);
  adcVoltage = (adcValue / 1024.0) * 5000;
  currentValue = ((adcVoltage - offsetVoltage) / sensitivity);
  long measurement =vibration();
  delay(150);
  if (measurement > 50){
    digitalWrite(led, HIGH);
  }
  else{
    digitalWrite(led, LOW);
  }
  a= String(vIN);
  b= String(currentValue);
  c= String(measurement);
  serialPi.print("<");
  serialPi.print(" Temprature: ");
  serialPi.print(temp);
  serialPi.print(",");
  serialPi.print("Voltage :");
  serialPi.print(a);
  serialPi.print(">");
  serialPi.print(",");
  serialPi.print("Current :");
  serialPi.print(b);
  serialPi.print("@");
  serialPi.print(",");
  serialPi.print("vibration :");
  serialPi.print(c);
  serialPi.println("$");
  delay(1000);
}

long vibration(){
  long measurement=pulseIn (vs, HIGH);  //wait for the pin to get HIGH and returns measurement
  return measurement;
  }

void receiveData(int howMany) {
  while (Wire.available()) { // loop through all but the last
       rqst+=char(Wire.read());
  }
}    

void sendData(){
  if(rqst=="1"){
    //Serial.print("rEQUEST:");
    //Serial.println(rqst);
   // Serial.println(   temp);
    char md[6];
    temp.toCharArray(md,6);  
    Wire.write(md);
    }
    else if(rqst=="2"){
//    Serial.print("rEQUEST:");
//    Serial.println(rqst);
   // Serial.println(   vIN);
       
  char sd[5];
  a.toCharArray(sd,5);  
  Wire.write(sd);
    }

    else if(rqst=="3"){
//    Serial.print("rEQUEST:");
//    Serial.println(rqst);
   // Serial.println(   vIN);
       
  char qd[6];
  b.toCharArray(qd,6);  
  Wire.write(qd);
    }

    else{if(rqst=="4"){
//    Serial.print("rEQUEST:");
//    Serial.println(rqst);
   // Serial.println(   vIN);
       
  char rd[6];
  c.toCharArray(rd,6);  
  Wire.write(rd);
    }}
    req="";
   rqst="";
}
