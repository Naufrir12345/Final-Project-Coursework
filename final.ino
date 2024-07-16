#include <Arduino.h>
#include <ESP32CAN.h>
#include <CAN_config.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ir_Panasonic.h>
#include <LiquidCrystal_I2C.h>

// #define IR_LED_PIN GPIO_NUM_2
const uint16_t kIrLed = 19; //D2 - GPIO4
const uint16_t indicatorLed = 18;
int temp = 16;

CAN_device_t CAN_cfg;

IRPanasonicAc ac(kIrLed);  
IRsend irsend(kIrLed);
LiquidCrystal_I2C lcd(0x27,16, 2);
// IRsend irsend(IR_LED_PIN);

void setup() {
    ac.begin();
    irsend.begin();
    Serial.begin(115200);
    Serial.println("iotsharing.com CAN demo");
    
    //FOR SETUP IR LED 
    irsend.begin();
    pinMode(indicatorLed, OUTPUT);
    // pinMode(IR_LED_PIN, OUTPUT);
    // digitalWrite(IR_LED_PIN, LOW); // Ensure the IR LED is off initially
    
    //FOR SETUP CAN
    CAN_cfg.speed=CAN_SPEED_250KBPS;
    CAN_cfg.tx_pin_id = GPIO_NUM_5;
    CAN_cfg.rx_pin_id = GPIO_NUM_4;
    CAN_cfg.rx_queue = xQueueCreate(10,sizeof(CAN_frame_t));

    //start CAN Module
    ESP32Can.CANInit();
    lcd.init(); // inialisasi LCD
  //Print a message to the LCD.
    lcd.backlight();
    lcd.print("Welcome to AC System");
}

void loop() {
    CAN_frame_t rx_frame;
    digitalWrite(kIrLed, LOW);
    //receive next CAN frame from queue
    if(xQueueReceive(CAN_cfg.rx_queue,&rx_frame, 3*portTICK_PERIOD_MS)==pdTRUE){

      //do stuff!
      if(rx_frame.FIR.B.FF==CAN_frame_std)
        printf("New standard frame");
      else
        printf("New extended frame");

      if(rx_frame.FIR.B.RTR==CAN_RTR)
        printf(" RTR from 0x%08x, DLC %d\r\n",rx_frame.MsgID,  rx_frame.FIR.B.DLC);
      else {
        Serial.printf("From 0x%08x, DLC %d\n", rx_frame.MsgID, rx_frame.FIR.B.DLC);
        char receivedData[9]; // Create a buffer to store the received data
        for (int i = 0; i < 8; i++) {
            receivedData[i] = (char)rx_frame.data.u8[i];
            Serial.printf("%c", receivedData[i]);
        }
        receivedData[8] = '\0'; // Null-terminate the string
        Serial.println();
        // Check the received data and control the IR LED
        if (strcmp(receivedData, "NAIK") == 0) {
          Serial.println("Received NAIK");
          // Increase the temperature
          temp++;
          if (temp > 30) {
            temp = 30;
          }
          ac.send();
          Serial.println("Suhu Naik: ");
          Serial.print(temp);
          lcd.setCursor(0,1);
          lcd.print("Suhu Naik: ");
          lcd.print(temp);
          Serial.print(" derajat Celsius");
          Serial.println();
          // lcd.setCursor(1,1);
          // lcd.print("derajat Celcius");
          Serial.println("Temperature increased");
            // Activate the IR LED for NAIK
            // digitalWrite(IR_LED_PIN, HIGH);
            // irsend.sendRaw(rawDataNAIK, RAW_DATA_LEN, 38);
            
        } else if (strcmp(receivedData, "TURUN") == 0) {
          Serial.println("Received TURUN");
          temp--;
          if (temp < 16) {
            temp = 16;
          }
          ac.send();
          Serial.println("Suhu Turun: ");
          Serial.print(temp);
          Serial.print(" derajat Celsius");
          lcd.setCursor(0,0);
          lcd.print("Kondisi AC");
          lcd.setCursor(0,1);
          lcd.print("Suhu Turun: ");
          lcd.print(temp);
          Serial.println();
          Serial.println("Temperature decreased");
            // Activate the IR LED for TURUN
            // digitalWrite(IR_LED_PIN, HIGH);
            // irsend.sendRaw(rawDataTURUN, RAW_DATA_LEN, 38);
        } else if (strcmp(receivedData, "NYALA") == 0) {
            Serial.println("Received NYALA");
            // Activate the IR LED for ON
            // digitalWrite(IR_LED_PIN, HIGH);
            // irsend.sendRaw(rawDataON, 263, 38);
            ac.on();
            ac.setTemp(temp);
            lcd.setCursor(0,0);
            lcd.print("Kondisi AC");
            lcd.setCursor(0,1);
            lcd.print("AC Nyala");
            ac.send();
        } else if (strcmp(receivedData, "MATI") == 0) {
            Serial.println("Received MATI");
            // Deactivate the IR LED for OFF
            // digitalWrite(kIrLed, HIGH);
            // irsend.sendRaw(rawDataOFF, 439, 38);
            // irsend.sendPanasonicAC(state, 27, 38);
            ac.off();
            ac.setTemp(temp);
            lcd.setCursor(0,0);
            lcd.print("Kondisi AC");
            lcd.setCursor(0,1);
            lcd.print("AC Mati");
            ac.send();
            Serial.println("IR signal sent for OFF");  // Menambahkan pesan ke serial monitor
    
            // Mengaktifkan LED indikator sebagai tanda bahwa sinyal telah dikirim
            // digitalWrite(indicatorLed, HIGH);
            // delay(1000);  // LED menyala selama 500 ms
            // digitalWrite(indicatorLed, LOW);
        } else {
            // If the received data is not recognized, turn off the IR LED
            digitalWrite(kIrLed, LOW);
            Serial.println("signal not sent");
        }
      }

      // else{
      //   printf(" from 0x%08x, DLC %d\n",rx_frame.MsgID,  rx_frame.FIR.B.DLC);
      //   for(int i = 0; i < 8; i++){
      //     printf("%c\t", (char)rx_frame.data.u8[i]);
      //   }
      //   printf("\n");
      // }
    }
    else
    {
      rx_frame.FIR.B.FF = CAN_frame_std;
      rx_frame.MsgID = 1;
      rx_frame.FIR.B.DLC = 8;
      rx_frame.data.u8[0] = 0xAA;
      rx_frame.data.u8[1] = 0x00;
      rx_frame.data.u8[2] = 0xBB;
      rx_frame.data.u8[3] = 0x00;
      rx_frame.data.u8[4] = 0xCC;
      rx_frame.data.u8[5] = 0x00;
      rx_frame.data.u8[6] = 0xDD;
      rx_frame.data.u8[7] = 0x00;

      
      ESP32Can.CANWriteFrame(&rx_frame);
    }
}

// #define BLYNK_TEMPLATE_ID "TMPL6voATjUfO"
// #define BLYNK_TEMPLATE_NAME "PanasonicACiot"
// #define BLYNK_AUTH_TOKEN "qKIEu9mEev5cQt3FEUzW1waMPmINTLwh"

// #include <Arduino.h>
// #include <IRremoteESP8266.h>
// #include <IRsend.h> //Jika protocol tidak terdeteksi
// #include <ir_Panasonic.h> //Protocol Panasonic (lihat library untuk protocol remote lain)
// #include <WiFi.h>
// #include <BlynkSimpleEsp32.h>


// char ssid[] = "vivo 1938";       
// char pass[] = "katasandi";

// //Pin IRLed TX
// const uint16_t kIrLed = 19; //D2 - GPIO4

// int pushMode = 0;
// int pushFan = 0;
// int pushSwing = 0;

// int togglePower = 0;
// int toggleMode = 0;
// int toggleFan = 0;
// int toggleSwing = 0;
// int toggleECO = 0;

// int temp = 16;

// int notifMode,notifFan,notifSwing,notifECO;

// // Set the GPIO used for sending messages.
// IRPanasonicAc ac(kIrLed);  
// IRsend irsend(kIrLed);

// WidgetLCD lcd(V7);

// //ECO SMART ON
// uint16_t rawEcoOff[439] = {3574, 1648,  486, 380,  514, 1218,  488, 380,  514, 352,  516, 350,  514, 352,  518, 348,  518, 350,  512, 354,  514, 352,  512, 382,  512, 352,  512, 356,  512, 1220,  484, 384,  512, 352,  512, 354,  512, 354,  514, 352,  516, 350,  512, 354,  512, 1222,  508, 1222,  484, 1252,  510, 354,  512, 382,  510, 1224,  482, 382,  512, 356,  508, 358,  510, 354,  512, 356,  508, 356,  512, 354,  510, 356,  508, 358,  510, 356,  512, 354,  510, 358,  506, 358,  510, 382,  508, 358,  508, 358,  510, 358,  508, 358,  508, 358,  506, 360,  506, 358,  508, 360,  508, 358,  506, 358,  508, 358,  508, 356,  508, 358,  494, 400,  482, 384,  482, 382,  484, 1248,  484, 1250,  482, 384,  484, 382,  510, 356,  504, 362,  482, 384,  480, 9948,  3556, 1672,  466, 400,  482, 1248,  510, 384,  482, 384,  482, 384,  480, 386,  480, 384,  484, 384,  480, 384,  482, 386,  482, 384,  482, 382,  482, 384,  480, 1254,  466, 400,  482, 382,  494, 398,  482, 384,  482, 384,  482, 384,  480, 384,  484, 1252,  464, 1266,  470, 1262,  468, 398,  480, 388,  480, 1252,  480, 386,  482, 384,  480, 386,  480, 388,  458, 406,  520, 374,  460, 406,  462, 404,  458, 410,  456, 406,  462, 406,  460, 406,  462, 402,  464, 404,  496, 370,  520, 346,  522, 1210,  522, 1212,  524, 1208,  524, 344,  486, 406,  526, 342,  522, 342,  524, 1210,  520, 344,  518, 1214,  518, 1220,  486, 376,  488, 376,  486, 380,  486, 382,  486, 378,  484, 382,  484, 384,  484, 382,  512, 380,  484, 1250,  482, 1248,  484, 382,  482, 384,  484, 382,  484, 384,  480, 1252,  482, 384,  482, 1250,  482, 384,  482, 386,  480, 384,  480, 386,  480, 388,  508, 382,  482, 386,  478, 388,  480, 386,  482, 384,  480, 390,  476, 390,  476, 386,  480, 388,  478, 386,  480, 408,  456, 410,  458, 1276,  456, 1278,  454, 1278,  482, 410,  454, 412,  456, 412,  454, 410,  456, 410,  454, 412,  454, 412,  452, 414,  454, 412,  452, 1280,  454, 1282,  450, 1280,  450, 420,  446, 416,  448, 418,  472, 420,  446, 422,  444, 422,  446, 418,  446, 422,  446, 420,  444, 422,  444, 420,  446, 422,  444, 420,  446, 420,  444, 422,  446, 420,  444, 1288,  472, 420,  444, 420,  446, 1290,  446, 420,  444, 422,  446, 420,  446, 1290,  442, 422,  444, 422,  444, 422,  444, 420,  446, 422,  444, 424,  444, 422,  446, 420,  470, 424,  444, 424,  442, 424,  442, 444,  420, 422,  444, 420,  446, 444,  420, 446,  420, 446,  420, 1312,  420, 446,  420, 1312,  420, 422,  446, 444,  420, 444,  448, 444,  420};
// //ECO SMART OFF
// uint16_t rawEcoOn[439] = {3544, 1680,  584, 280,  558, 1176,  586, 278,  584, 282,  586, 280,  592, 272,  592, 276,  586, 280,  586, 278,  586, 280,  514, 380,  558, 310,  588, 276,  588, 1148,  582, 280,  556, 310,  586, 282,  586, 278,  592, 272,  562, 306,  586, 278,  590, 1144,  590, 1142,  590, 1146,  584, 280,  514, 378,  588, 1146,  586, 278,  590, 278,  584, 280,  584, 282,  586, 282,  556, 308,  590, 276,  588, 278,  586, 280,  586, 280,  584, 280,  586, 280,  588, 278,  516, 378,  588, 278,  586, 280,  588, 278,  586, 278,  594, 272,  588, 280,  582, 282,  584, 282,  558, 310,  558, 308,  584, 284,  586, 278,  586, 280,  544, 352,  556, 310,  580, 284,  582, 1154,  552, 1180,  584, 280,  584, 284,  556, 312,  552, 312,  554, 312,  582, 9848,  3642, 1586,  552, 314,  548, 1184,  570, 322,  558, 310,  548, 318,  546, 318,  544, 322,  544, 320,  548, 320,  542, 322,  542, 324,  542, 322,  542, 324,  542, 1192,  516, 348,  542, 324,  568, 326,  538, 326,  516, 352,  514, 352,  512, 352,  516, 1216,  490, 1242,  516, 1218,  512, 352,  490, 374,  492, 1242,  490, 376,  490, 374,  492, 376,  490, 374,  516, 352,  510, 382,  516, 354,  512, 348,  492, 374,  514, 354,  512, 354,  512, 352,  486, 380,  486, 1248,  484, 380,  484, 382,  484, 1248,  484, 1248,  484, 1250,  482, 382,  512, 382,  486, 382,  482, 384,  484, 1248,  482, 384,  484, 1248,  484, 1252,  482, 382,  482, 384,  482, 382,  482, 384,  482, 384,  484, 382,  482, 384,  482, 386,  508, 384,  480, 1274,  460, 1274,  458, 388,  478, 386,  478, 410,  456, 388,  478, 1274,  458, 410,  456, 1276,  456, 412,  454, 410,  456, 410,  454, 412,  454, 412,  480, 414,  454, 410,  454, 414,  452, 414,  450, 414,  452, 414,  454, 414,  452, 414,  450, 414,  450, 416,  450, 416,  448, 418,  446, 1288,  444, 1288,  444, 1288,  470, 422,  444, 424,  442, 422,  446, 422,  442, 424,  442, 446,  420, 420,  444, 422,  444, 446,  420, 1312,  420, 1312,  420, 1314,  422, 420,  442, 446,  420, 448,  446, 446,  420, 446,  418, 446,  420, 446,  422, 446,  418, 446,  420, 448,  420, 446,  418, 444,  420, 446,  420, 448,  418, 446,  420, 446,  420, 1312,  420, 446,  446, 446,  420, 1312,  420, 446,  420, 446,  420, 446,  420, 1316,  420, 444,  420, 444,  422, 446,  418, 448,  418, 446,  420, 448,  418, 450,  418, 446,  448, 446,  420, 446,  420, 448,  418, 446,  420, 448,  420, 446,  418, 446,  420, 446,  420, 1312,  420, 1314,  418, 446,  420, 1314,  418, 446,  420, 446,  420, 446,  446, 448,  418};
// void setup() 
// {
//   ac.begin();
//   irsend.begin();
//   Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
//   Serial.begin(115200);
//   lcdState();
//   Blynk.virtualWrite(V8, temp);
// }
 
// void loop() 
// {
//    Blynk.run();
// }

// //Widget Power Button(Switch)
// BLYNK_WRITE(V0)
// {
//   togglePower = param.asInt();
//   if(togglePower==1)
//   {
//     ac.on();
//     ac.setSwingVertical(true);
//     ac.setSwingHorizontal(false);
//     ac.setTemp(temp);
//     Blynk.virtualWrite(V8, temp);
    
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif 
//     delay(2000);   
//   }
//   else
//   {
//     ac.off();
 
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif 
//     delay(2000);   
//   }
  
// }

// //Widget Button ECO SMART(Switch)
// BLYNK_WRITE(V1)
// {
//   toggleECO = param.asInt();
//   if(toggleECO == 1)
//   {
//     #if SEND_RAW
//      irsend.sendRaw(rawEcoOn, 263, 38);  // Send a raw data capture at 38kHz.
//     #endif  //SEND_RAW
//     lcd.print(11,0, "E-ON ");
//     delay(2000);  
//   }
//   else
//   {
//     #if SEND_RAW
//      irsend.sendRaw(rawEcoOff, 263, 38);  // Send a raw data capture at 38kHz.
//     #endif  // SEND_RAW
//     lcd.print(11,0, "E-OFF");
//     delay(2000);     
//   }
// }

// //Widget Button MODE(Push)
// BLYNK_WRITE(V2)
// {
//   toggleMode = param.asInt();
//   if(toggleMode == 1)
//   {
//     pushMode++;
//     delay(200);
//     if (pushMode>2)
//     {
//       pushMode=0;
//     }
//     if(pushMode==1)
//     {
//       notifMode=0; //Mode Auto
//       lcd.print(5, 0, "AUTO");
//       //ac.setMode(0);
//     }
//     else if(pushMode==2)
//     {
//       notifMode=2; //Mode Dry
//       lcd.print(5, 0, "DRY ");
//       //ac.setMode(2);
//     }
//     else
//     {
//       notifMode=3; //Mode Cool
//       lcd.print(5, 0, "COOL");
//       //ac.setMode(3);
//     }
//     ac.setMode(notifMode);
   
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif  
//   }
// }

// //Widget Button Fan Speed(Push)
// BLYNK_WRITE(V3)
// {
//   toggleFan = param.asInt();
//   if(toggleFan == 1)
//   {
//     pushFan++;
//     delay(200);
//     if (pushFan>3)
//     {
//       pushFan=0;
//     }
//     if(pushFan==1)
//     {
//       notifFan=0; //Quiet
//       lcd.print(4, 1, "-   ");
//       //ac.setFan(0);
//     }
//     else if(pushFan==2)
//     {
//       notifFan=2; //Medium
//       lcd.print(4, 1, "--  ");
//       //ac.setFan(2);
//     }
//     else if(pushFan==3)
//     {
//       notifFan=3; //Max
//       lcd.print(4, 1, "--- ");
//       //ac.setFan(3);
//     }
//     else
//     {
//       notifFan=7; //Auto
//       lcd.print(4, 1, "AUTO");
//       //ac.setFan(7);
//     }
//     ac.setFan(notifFan);
 
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif  
//   }
// }

// //Widget Button AirSwingV(Push)
// BLYNK_WRITE(V4)
// {
//   toggleSwing = param.asInt();
//   if(toggleSwing == 1)
//   {
//     pushSwing++;
//     delay(200);
//     if (pushSwing>5)
//     {
//       pushSwing=0;
//     }
//     if(pushSwing==1)
//     {
//       notifSwing=1; //Highest
//       lcd.print(9,1, "Highest");
//     }
//     else if(pushSwing==2)
//     {
//       notifSwing=2; //High
//       lcd.print(9,1, "   High");
//     }
//     else if(pushSwing==3)
//     {
//       notifSwing=3; //Midle
//       lcd.print(9,1, "  Midle");
//     }
//     else if(pushSwing==4)
//     {
//       notifSwing=4; //Low
//       lcd.print(9,1, "    Low");
//     }
//     else if(pushSwing==5)
//     {
//       notifSwing=5; //Lowest
//       lcd.print(9,1, " Lowest");
//     }
//     else
//     {
//       notifSwing=15; //Auto
//       lcd.print(9,1, "  AUTO ");
//     }
//     ac.setSwingVertical(notifSwing);
 
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif  
//   }
// }

// //Widget Button TempUp(Push)
// BLYNK_WRITE(V5)
// {
//   int tempUp = param.asInt();
//   if(tempUp==1)
//   {
//     temp++;
//     delay(200);
//     if(temp>30)
//     {
//       temp=30;
//     }
    
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif 
//     Blynk.virtualWrite(V8, temp);
//   }
  
// }

// //Widget Button TempDown(Push)
// BLYNK_WRITE(V6)
// {
//   int tempDown = param.asInt();
//   if(tempDown==1)
//   {
//     temp--;
//     delay(200);
//     if(temp<16)
//     {
//       temp=16;
//     }
    
//     // Now send the IR signal.
//     #if SEND_PANASONIC_AC
//       ac.send();
//     #endif 
//     Blynk.virtualWrite(V8, temp);
//   }  
// }

// //Widget LCD Display
// void lcdState() 
// {
//   lcd.clear();
//   lcd.print(0, 0, "Mode:");
//   lcd.print(5, 0, "COOL");
//   lcd.print(11,0, "E-OFF");
//   lcd.print(0, 1, "Fan:");
//   lcd.print(4, 1, "AUTO");
//   lcd.print(9, 1, "AUTO  ");  
// }
