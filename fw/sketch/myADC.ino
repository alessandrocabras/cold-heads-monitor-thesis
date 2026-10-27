/**
 * myADC_init
 * Function that initializes ADCs.
 * 
 * @param  None
 * @return None
 */
void myADC_init(void)
{ 
  g_adc.begin();
  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  g_adc.setGain(GAIN_TWOTHIRDS); // 2/3x gain +/- 6.144V  1 bit = 3mV
  g_adc.setDataRate(RATE_ADS1015_3300SPS); // 860SPS, 475SPS, 250SPS, 128SPS, 64SPS, 32SPS, 16SPS, 8SPS
  Wire.setClock(400000); //400kHz I2C clock 
}  

/**
 * myExternalADC_analog_read
 * Function that initializes external ADC.
 * 
 * @param  ch is the analog channel to digital convert
 * @param  samples is the number of conversion to perform
 * @return The A/D conversion result
 */
float ads_read_volts(int ch)
{
  int16_t adc;
  if(ch == 0){
    adc = (g_adc.readADC_SingleEnded(0)*2)-512; //viene riportata in linea con le altre sinusoidi
  }
  else{
    adc = g_adc.readADC_SingleEnded(ch);
  }
  
  return g_adc.computeVolts(adc);
}
