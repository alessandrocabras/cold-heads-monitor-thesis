    volatile unsigned long time1=0;
    volatile unsigned long time2=0;
    volatile unsigned long time3=0;
    
    void setup(){
      Serial.begin(115200);
      pinMode(1,INPUT);   
      pinMode(2,INPUT);
      pinMode(3,INPUT);  
      attachInterrupt(digitalPinToInterrupt(1),in1,RISING);     //enable ISR1 for voltage signal at rising from zero crossing 
      attachInterrupt(digitalPinToInterrupt(2),in2,RISING);     //enable ISR2 for current signal at rising from zero crossing
      attachInterrupt(digitalPinToInterrupt(3),in3,RISING);
    }

    void in1(){
      time1=micros();    //measure time in micro second for first zero crossing ISR1
    }

    void in2(){
      time2=micros();    //measure time in micro second for first zero crossing ISR2
    }

    void in3(){
      time3=micros();    //measure time in micro second for first zero crossing ISR2
    }
           
    void loop(){
      unsigned long time21; 
      unsigned long time31;
      double ps21;
      double ps31;
      if (time2 > time1 && time3 > time2){
        noInterrupts();
        time21=time2-time1;
        ps21 = ((time21*360.0)*50/1000000); //calculate the phase shift from measured time difference
        time31=time3-time1;
        ps31 = ((time31*360.0)*50/1000000); //calculate the phase shift from measured time difference
        interrupts();
        Serial.print("Phase Shift 2-1 = ");
        Serial.println(ps21,2);
        Serial.print("degree\n\n");
        Serial.print("Phase Shift 3-1 = ");
        Serial.println(ps31,2);
        Serial.print("degree\n\n");
      }
    }