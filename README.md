## <center>Audio Mixer</center> 
###### <center>-NotHamxa</center>

Audio mixer application controlled using an arduino and potentiometers

### Requirements
`Arduino Uno`<br>
`1-4 10k potentiometers`<br>
Load the following script onto the arduino

```c++
void
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
