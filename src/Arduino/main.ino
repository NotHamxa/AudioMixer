const int sensorNum = 4;
int sensors[sensorNum] = {A0,A1,A2,A3};
int sensorVals[sensorNum];

void setup() {
  // put your setup code here, to run once:
  for(int i=0;i<sensorNum;i++){
    pinMode(sensors[i],INPUT);
  }
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:

  readPots();
  String serialOut = "";
  serialOut+="(";
  for(int i=0;i<sensorNum-1;i++){
    serialOut+=String(sensorVals[i]);
    serialOut+="-";
  }
  serialOut+=String(sensorVals[sensorNum-1]);
  serialOut+=")";
  Serial.println(serialOut);
  delay(30);
}
void readPots(){
    for(int i=0;i<sensorNum;i++){
    sensorVals[i] = map(analogRead(sensors[i]),0,1024,0,100);

  }

}