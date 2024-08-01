## <center>Audio Mixer</center> 
###### <center>-NotHamxa</center>

Audio mixer application controlled using an arduino and potentiometers

### Requirements
`Arduino Uno`<br>
`1-4 10k potentiometers`<br>
Load the following script onto the arduino

```c++
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
    sensorVals[i] =map(analogRead(sensors[i]),0,1024,0,100);

  }

}
```

#### If directly running the python scripts
```pycon
pip install customtkinter
pip install PySerial
pip install pydantic
```

### Setup
Run the application and click on the menu icon "☰" in the top left corner<br>
Select the COM Port on which the arduino is running. If you do not see the COM Port in the dropdown try reconnecting the arduino and click on refresh COM Ports.<br>
Enter the baud rate set in the arduino script<br>
Click on Confirm Config<br>
The program will automatically detect the number of potentiometers used<br>
A prompt will appear to confirm the settings. 
> <font color="red">WARNING</font><br> Once confirmed the previous configuration will be overwritten including application prefrences 


### Debugging
If the correct COM port is selected but the board is still not connected, crosscheck if the correct baud rate is entered, the correct COM port is selected or close any other programs using the serial port.<br>
<br>
If the number of potentiometers is changed, it will require te user to reconfigure the board using the steps mentioned under Setup<br>
if 
