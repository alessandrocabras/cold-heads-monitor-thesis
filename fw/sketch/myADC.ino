void myADC_init(void)
{
  g_adc.begin();

  // The gain setting does not extend physical ADC input limits.
  g_adc.setGain(GAIN_TWOTHIRDS);
  g_adc.setDataRate(RATE_ADS1015_3300SPS);
  Wire.setClock(400000);
}

float ads_read_volts(int ch)
{
  int16_t adc;
  if(ch == 0){
    // Historical channel-0 amplitude and offset correction.
    adc = (g_adc.readADC_SingleEnded(0)*2)-512;
  }
  else{
    adc = g_adc.readADC_SingleEnded(ch);
  }

  return g_adc.computeVolts(adc);
}
