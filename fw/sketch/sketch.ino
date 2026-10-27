#include <Ethernet.h>
#include <Adafruit_ADS1X15.h>
#include <Wire.h>
#include <string.h>

/*
 * Constants definition section
 */

// Return codes
#define OK    (0)  // Constant for the ret variable from function calling
#define ERROR (-1) // Constant for the ret variable from function calling

// ETH constants
#define ETH_OK    (1) // Constant for the global g_eth_status variable
#define ETH_ERROR (0) // Constant for the global g_eth_status variable

// ADC constants
#define ADC_BUF_LEN (128)
#define ADC_CH_0    (0)
#define ADC_CH_1    (1)
#define ADC_CH_2    (2)
#define ADC_CHS     (3)
#define SHIFT_12     (12)
#define SHIFT_21     (21)
#define SHIFT_23     (23)
#define SHIFT_32     (32)
#define SHIFT_13     (13)
#define SHIFT_31     (31)


// API constants
#define API_MAX_LEN      (50)   // API_MAX_LEN is the constant containing the maximum API string length
#define API_NULL_CHAR    ('\0') // API_NULL_CHAR is the constant containing the API string null char
#define API_START_CHAR   ('#')  // API_START_CHAR is the constant containing the API string start char
#define API_STOP_CHAR    ('*')  // API_STOP_CHAR is the constant containing the API string stop char
#define API_SPACE_CHAR   (' ')  // API_SPACE_CHAR is the constant containing the API string space char
#define API_MIN_LEN      (6)    // API_MIN_LEN is the constant containing the minimum API string length
#define API_IDN_LEN      (6)    // API_IDN_LEN is the constant containing the minimum API string length
#define API_ACQUIRE_LEN  (9)    // API_ACQUIRE_LEN is the constant containing the "#ACQUIRE*" API string length
#define API_GETADC_LEN   (8)    // API_GETADC_LEN is the constant containing the "#GETADC " API string length
#define API_GETGAIN_LEN  (9)    // API_GETGAIN_LEN is the constant containing the "#GETGAIN " API string length
#define API_GETSHIFT_LEN (10)   // API_GETSHIFT_LEN is the constant containing the "#GETSHIFT " API string length

/*
 * Global vars declaration section
 */

// ADC vars
Adafruit_ADS1015 g_adc;

// ETH vars
int  g_eth_status;                                         // Ethernet status var
byte g_eth_mac[] = {0x90, 0xA2, 0xDA, 0x10, 0xFB, 0xD0};  // Ethernet mac address var
IPAddress g_eth_ip(192, 168, 150, 94);                   // Ethernet ip address var
EthernetServer g_eth_port(1666);                        // Ethernet TCP port number var

// API vars
int  g_api_count;        // API string counter
char g_api[API_MAX_LEN]; // API string
static const unsigned long API_IDN          = 0;   // API constant for "#IDN?*"
static const unsigned long API_ACQUIRE      = 1;   // API constant for "#ACQUIRE*"
static const unsigned long API_GETADC       = 100; // API constant for "#GETADC "
static const unsigned long API_GETGAIN      = 200; // API constant for "#GETGAIN "
static const unsigned long API_GETSHIFT     = 300; // API constant for "#GETSHIFT "
static const unsigned int  API_FIRST_PARAM  = 1;   // Constant for coding the first parameter in the API constant
static const unsigned int  API_SECOND_PARAM = 10;  // Constant for coding the second parameter in the API constant

//Interrupts vars
const byte ch1_pin = 0;
const byte ch2_pin = 1;
const byte ch3_pin = 7;

volatile unsigned long time1=0;
volatile unsigned long time2=0;
volatile unsigned long time3=0;
double current_value = 0;

void in1(){
  time1=micros();    //measure time in micro second for first zero crossing ISR1
}

void in2(){
  time2=micros();    //measure time in micro second for first zero crossing ISR2
}

void in3(){
  time3=micros();    //measure time in micro second for first zero crossing ISR2
}

double read_shift(int code_shift){
  unsigned long time_difference; 
  double shift;
  noInterrupts();
  switch(code_shift){
    case SHIFT_12:
      time_difference = time1 - time2;
      break;
    case SHIFT_21:
      time_difference = time2 - time1;
      break;
    case SHIFT_23:
      time_difference = time2 - time3;
      break;
    case SHIFT_32:
      time_difference = time3 - time2;
      break;
    case SHIFT_13:
      time_difference = time1 - time3;
      break;
    case SHIFT_31:
      time_difference = time3 - time1;
      break;
    default:
      break;
  }

  shift = ((time_difference*360.0)*50/1000000); //calculate the phase shift from measured time difference
  interrupts();
  return(shift);
}

void setup(void)
{
  // Global vars initialization
  g_api_count = 0;
  memset(g_api, API_NULL_CHAR, API_MAX_LEN);
  g_eth_status = ETH_ERROR;

  // External ADC initialization function calling
  myADC_init();

  //Interrupt initialization
  pinMode(ch1_pin, INPUT);
  pinMode(ch2_pin, INPUT);
  pinMode(ch3_pin, INPUT);
  attachInterrupt(digitalPinToInterrupt(ch1_pin), in1, RISING); //Channel 1
  attachInterrupt(digitalPinToInterrupt(ch2_pin), in2, RISING); //Channel 2
  attachInterrupt(digitalPinToInterrupt(ch3_pin), in3, RISING); //Channel 3

  // DEBUG
  //#Serial.begin(115200);
}
  
void loop()
{
  // Utility vars
  unsigned int i;
  long ret;
  char eth_char;
  unsigned int adc_ch;
  unsigned int shift_code;

  float  g_adc_buffer_ch_0[ADC_BUF_LEN];
  float  g_adc_buffer_ch_1[ADC_BUF_LEN];
  float  g_adc_buffer_ch_2[ADC_BUF_LEN];
  
  // Ethernet status variable checking
  if(g_eth_status == ETH_ERROR) {

    // Ethernet physical link checking
    if(Ethernet.linkStatus() != LinkOFF) {

      // Starting the ethernet connection
      Ethernet.begin(g_eth_mac, g_eth_ip);

      // Starting the TCP server
      g_eth_port.begin();

      // Ethernet status variable updating
      g_eth_status = ETH_OK;
    }
  }
  else {

    // Ethernet physical link checking
    if(Ethernet.linkStatus() != LinkOFF) {

      // Listening for TCP clients
      EthernetClient eth_client = g_eth_port.available();
      if(eth_client) {

        // TCP client connection checking
        while(eth_client.connected()) {

          // Ethernet physical link checking
          if(Ethernet.linkStatus() != LinkOFF) {

            // TCP client connection checking
            if(eth_client.available()) {

              // Reading a char from TCP client connection
              eth_char = eth_client.read();

              // Checking the red char from the TCP client connection
              if(eth_char == API_START_CHAR) {
                // Starting API char found!

                // API string and char counter initialization
                memset(g_api, API_NULL_CHAR, API_MAX_LEN);
                g_api_count = 0;
                g_api[g_api_count] = eth_char;
              }
              else {
                g_api_count++;
                g_api[g_api_count] = eth_char;
                if(eth_char == API_STOP_CHAR) {
                  // Ending API char found!

                  // Parsing API string
                  ret = myAPI_parse(g_api, g_api_count + 1);

                  // API string and char counter initialization
                  memset(g_api, API_NULL_CHAR, API_MAX_LEN);
                  g_api_count = 0;

                  // Execution phase after API string parsing
                  if(ret == ERROR) {
                    // API string not valid!

                    // Sending TCP response to client
                    eth_client.print("ERROR*");
                  }
                  else {

                    // API #IDN?* - Looking for the corresponding codified API constant
                    if(ret == API_IDN) {
                      // "#IDN?*" codified API constant found!
                      // Sending TCP response to client
                      //eth_client.print("bau*");
                    }
                    else {
                      // API #ACQUIRE* - Looking for the corresponding codified API constant
                      if(ret == API_ACQUIRE) {
                        
                        // "#ACQUIRE*" codified API constant found!
                        // Execution of API meaning
                        for(i=0; i<ADC_BUF_LEN; i++) {
                          g_adc_buffer_ch_0[i] = ads_read_volts(0);
                        }
                        for(i=0; i<ADC_BUF_LEN; i++) {
                          g_adc_buffer_ch_1[i] = ads_read_volts(1);
                        }
                        for(i=0; i<ADC_BUF_LEN; i++) {
                          g_adc_buffer_ch_2[i] = ads_read_volts(2);
                        }
                        // Sending TCP response to client
                        eth_client.print("OK*");
                      }
                      else {

                        // API #GETADC adc_ch* - Looking for the corresponding codified API constant
                        if((ret >= API_GETADC) && (ret < API_GETGAIN)) {
                          // "#GETADC " codified API constant found!

                          // Getting execution values
                          adc_ch = ret - API_GETADC;

                          // Sending TCP response to client
                          switch(adc_ch) {
                            case ADC_CH_0:
                              for(i=0; i<ADC_BUF_LEN; i++) {
                                eth_client.print(g_adc_buffer_ch_0[i]);
                                if(i < (ADC_BUF_LEN - 1)) {
                                  eth_client.print(" ");
                                }
                              }
                            break;
                            case ADC_CH_1:
                              for(i=0; i<ADC_BUF_LEN; i++) {
                                eth_client.print(g_adc_buffer_ch_1[i]);
                                if(i < (ADC_BUF_LEN - 1)) {
                                  eth_client.print(" ");
                                }
                              }
                            break;
                            case ADC_CH_2:
                              for(i=0; i<ADC_BUF_LEN; i++) {
                                eth_client.print(g_adc_buffer_ch_2[i]);
                                if(i < (ADC_BUF_LEN - 1)) {
                                  eth_client.print(" ");
                                }
                              }
                            break;
                            default:
                            break;
                          }
                          eth_client.print("*");
                        }
                        else {

                          // API #GETGAIN adc_ch* - Looking for the corresponding codified API constant
                          if((ret >= API_GETGAIN) && (ret < API_GETSHIFT)) {
                            // "#GETGAIN " codified API constant found!

                            // Getting execution values
                            adc_ch = ret - API_GETGAIN;

                            // Sending TCP response to client
                            switch(adc_ch) {
                              case ADC_CH_0:
                                eth_client.print(g_adc.getGain());
                              break;
                              case ADC_CH_1:
                                eth_client.print(g_adc.getGain());
                              break;
                              case ADC_CH_2:
                                eth_client.print(g_adc.getGain());
                              break;
                              default:
                              break;
                            }
                            eth_client.print("*");
                          }
                          else {
                            if(ret >= API_GETSHIFT) {
                              // "#ACQUIRE*" codified API constant found!
                              // Getting execution values
                              shift_code = ret - API_GETSHIFT;
                                if(time2 > time1 && time3 > time2){
                                  current_value = read_shift(shift_code);
                                } 
                                eth_client.print(current_value);
                                eth_client.print("*");
                              }
                            else{

                              // Codified API constant NOT found!

                              // Sending TCP response to client
                              eth_client.print("ERROR*");
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
          else {
            // Ethernet status variable updating
            g_eth_status = ETH_ERROR;
            break;
          }
        }
        // Closing the ethernet connection 
        eth_client.stop();
      }
    }
    else {
      // Ethernet status variable updating
      g_eth_status = ETH_ERROR;
    }
  }
}
