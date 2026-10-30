#include <Ethernet.h>
#include <Adafruit_ADS1X15.h>
#include <Wire.h>
#include <string.h>

#define OK    (0)
#define ERROR (-1)

#define ETH_OK    (1)
#define ETH_ERROR (0)

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

#define API_MAX_LEN      (50)
#define API_NULL_CHAR    ('\0')
#define API_START_CHAR   ('#')
#define API_STOP_CHAR    ('*')
#define API_SPACE_CHAR   (' ')
#define API_MIN_LEN      (6)
#define API_IDN_LEN      (6)
#define API_ACQUIRE_LEN  (9)
#define API_GETADC_LEN   (8)
#define API_GETGAIN_LEN  (9)
#define API_GETSHIFT_LEN (10)

Adafruit_ADS1015 g_adc;

int  g_eth_status;
byte g_eth_mac[] = {0x90, 0xA2, 0xDA, 0x10, 0xFB, 0xD0};
IPAddress g_eth_ip(192, 168, 150, 94);
EthernetServer g_eth_port(1666);

int  g_api_count;
char g_api[API_MAX_LEN];
static const unsigned long API_IDN          = 0;
static const unsigned long API_ACQUIRE      = 1;
static const unsigned long API_GETADC       = 100;
static const unsigned long API_GETGAIN      = 200;
static const unsigned long API_GETSHIFT     = 300;
static const unsigned int  API_FIRST_PARAM  = 1;
static const unsigned int  API_SECOND_PARAM = 10;

const byte ch1_pin = 0;
const byte ch2_pin = 1;
const byte ch3_pin = 7;

volatile unsigned long time1=0;
volatile unsigned long time2=0;
volatile unsigned long time3=0;
double current_value = 0;

void in1(){
  time1=micros();
}

void in2(){
  time2=micros();
}

void in3(){
  time3=micros();
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

  // Phase conversion assumes a 50 Hz line frequency.
  shift = ((time_difference*360.0)*50/1000000);
  interrupts();
  return(shift);
}

void setup(void)
{

  g_api_count = 0;
  memset(g_api, API_NULL_CHAR, API_MAX_LEN);
  g_eth_status = ETH_ERROR;

  myADC_init();

  pinMode(ch1_pin, INPUT);
  pinMode(ch2_pin, INPUT);
  pinMode(ch3_pin, INPUT);
  attachInterrupt(digitalPinToInterrupt(ch1_pin), in1, RISING);
  attachInterrupt(digitalPinToInterrupt(ch2_pin), in2, RISING);
  attachInterrupt(digitalPinToInterrupt(ch3_pin), in3, RISING);

}

void loop()
{

  unsigned int i;
  long ret;
  char eth_char;
  unsigned int adc_ch;
  unsigned int shift_code;

  float  g_adc_buffer_ch_0[ADC_BUF_LEN];
  float  g_adc_buffer_ch_1[ADC_BUF_LEN];
  float  g_adc_buffer_ch_2[ADC_BUF_LEN];

  if(g_eth_status == ETH_ERROR) {

    if(Ethernet.linkStatus() != LinkOFF) {

      Ethernet.begin(g_eth_mac, g_eth_ip);

      g_eth_port.begin();

      g_eth_status = ETH_OK;
    }
  }
  else {

    if(Ethernet.linkStatus() != LinkOFF) {

      EthernetClient eth_client = g_eth_port.available();
      if(eth_client) {

        while(eth_client.connected()) {

          if(Ethernet.linkStatus() != LinkOFF) {

            if(eth_client.available()) {

              eth_char = eth_client.read();

              if(eth_char == API_START_CHAR) {

                memset(g_api, API_NULL_CHAR, API_MAX_LEN);
                g_api_count = 0;
                g_api[g_api_count] = eth_char;
              }
              else {
                g_api_count++;
                g_api[g_api_count] = eth_char;
                if(eth_char == API_STOP_CHAR) {

                  ret = myAPI_parse(g_api, g_api_count + 1);

                  memset(g_api, API_NULL_CHAR, API_MAX_LEN);
                  g_api_count = 0;

                  if(ret == ERROR) {

                    eth_client.print("ERROR*");
                  }
                  else {

                    // The identification command has no response in this firmware.
                    if(ret == API_IDN) {

                    }
                    else {

                      if(ret == API_ACQUIRE) {

                        // Capture consecutive channel blocks, not simultaneous samples.
                        for(i=0; i<ADC_BUF_LEN; i++) {
                          g_adc_buffer_ch_0[i] = ads_read_volts(0);
                        }
                        for(i=0; i<ADC_BUF_LEN; i++) {
                          g_adc_buffer_ch_1[i] = ads_read_volts(1);
                        }
                        for(i=0; i<ADC_BUF_LEN; i++) {
                          g_adc_buffer_ch_2[i] = ads_read_volts(2);
                        }

                        eth_client.print("OK*");
                      }
                      else {

                        if((ret >= API_GETADC) && (ret < API_GETGAIN)) {

                          adc_ch = ret - API_GETADC;

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

                          if((ret >= API_GETGAIN) && (ret < API_GETSHIFT)) {

                            adc_ch = ret - API_GETGAIN;

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

                              shift_code = ret - API_GETSHIFT;
                                if(time2 > time1 && time3 > time2){
                                  current_value = read_shift(shift_code);
                                }
                                eth_client.print(current_value);
                                eth_client.print("*");
                              }
                            else{

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

            g_eth_status = ETH_ERROR;
            break;
          }
        }

        eth_client.stop();
      }
    }
    else {

      g_eth_status = ETH_ERROR;
    }
  }
}
