int i = 0, j = 0;
float time1[3] = {0,0};
float time2[3] = {0,0};

float freq1 = 0, freq2 = 0;
float period1 = 0, period2 = 0;
float ps = 0;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println();
  pinMode(3, INPUT);
  pinMode(0, INPUT);
  noInterrupts();
  attachInterrupt(digitalPinToInterrupt(3), in1, RISING);
  attachInterrupt(digitalPinToInterrupt(0), in2, RISING);
  interrupts();
}

void in1() {
  switch (i) {
  case 0:
    time1[i] = micros();
    i++;
    break;
  case 1:
    if (j == 1) {
      time1[i] = micros();
      i++;
      break;
    }
  }
}
void in2() {
  switch (j) {
  case 0:
    if (i == 1) {
      time2[j] = micros();
      j++;
      break;
    }
  case 1:
    if (i == 2) {
      time2[j] = micros();
      j++;
      break;
    }
  }
  if (j == 2) {
    period1 = (time1[1] - time1[0]);
    period2 = (time2[1] - time2[0]);
    freq1 = 1000.0 / period1;
    freq2 = 1000.0 / period2;
    ps = (((time2[1] - time1[1]) * 360.0)/ period1);
      i = 0;
      j = 0;
  }
}

void loop() {
  if (freq1 == freq2) {
      Serial.println("");
      Serial.print("TIME1[0] = ");
      Serial.print(time1[0], 6);
      Serial.print("\t TIME1[1] = ");
      Serial.print(time1[1], 6);
      Serial.print("\t DEL1 = ");
      Serial.println(time1[1] - time1[0], 6);
      Serial.print("TIME2[0] = ");
      Serial.print(time2[0], 6);
      Serial.print("\t TIME2[1] = ");
      Serial.print(time2[1], 6);
      Serial.print("\t DEL2 = ");
      Serial.println(time2[1] - time2[0], 6);
      Serial.print("x = ");
      Serial.print(time2[0] - time1[0], 6);
      Serial.print("\t \t period1(ms) = ");
      Serial.print(period1, 6);
      Serial.print("\t period2(ms) = ");
      Serial.println(period2, 6);
      Serial.print("freq1 = ");
      Serial.print(freq1, 6);
      Serial.print("\t freq2 = ");
      Serial.print(freq2, 6);
      Serial.print("\t Phase Shift = ");
      Serial.println(ps, 6);
    }
  delay(100);
}
