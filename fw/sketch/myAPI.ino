#include <string.h>
#include <ctype.h>

#define API_IDN_STR "#IDN?*"
#define API_ACQUIRE_STR "#ACQUIRE*"
#define API_GETADC_STR "#GETADC "
#define API_GETGAIN_STR "#GETGAIN "
#define API_GETSHIFT_STR "#GETSHIFT "

long myAPI_check(char *api, int len)
{

  int  ret;

  if(len < API_MIN_LEN) {
    return ERROR;
  }
  else {

    if(strcmp(api, API_IDN_STR) == 0) {
      return API_IDN;
    }
    else {

      if(strcmp(api, API_ACQUIRE_STR) == 0) {
        return API_ACQUIRE;
      }
      else {

        if(strncmp(api, API_GETADC_STR, API_GETADC_LEN) == 0) {

          ret = myAPI_check_single_numeric_argument(api, API_GETADC_LEN);
          if(ret == OK) {
            return API_GETADC;
          }
          else {
            return ERROR;
          }
        }
        else {

          if(strncmp(api, API_GETGAIN_STR, API_GETGAIN_LEN) == 0) {

            ret = myAPI_check_single_numeric_argument(api, API_GETGAIN_LEN);
            if(ret == OK) {
              return API_GETGAIN;
            }
            else {
              return ERROR;
            }
          }
          else {

            if(strncmp(api, API_GETSHIFT_STR, API_GETSHIFT_LEN) == 0) {

              ret = myAPI_check_single_numeric_argument(api, API_GETSHIFT_LEN);
              if(ret == OK) {
                return API_GETSHIFT;
              }
              else {
                return ERROR;
              }
            }
            else {

              return ERROR;
            }
          }
        }
      }
    }
  }
}

int myAPI_check_single_numeric_argument(char *api, unsigned int offset)
{

  int  i;
  int  counter_a;

  i = 0;
  counter_a = 0;
  while(api[offset + i] != API_STOP_CHAR) {
    if (!isdigit((unsigned char)api[offset + i])) {
    return ERROR;
    }
    else {
      counter_a++;
    }
    i++;
  }

  if((i == 0) || (counter_a == 0)) {
    return ERROR;
  }
  else {
    return OK;
  }
}

int myAPI_check_couple_numeric_argument(char *api, unsigned int offset)
{

  int  i;
  int  counter_a;
  int  counter_b;
  int  counter_s;

  i = 0;
  counter_s = 0;
  counter_a = 0;
  counter_b = 0;
  while(api[offset + i] != API_STOP_CHAR) {
    if(api[offset + i] == API_SPACE_CHAR) {
      counter_s++;
    }
    else {
      if (!isdigit((unsigned char)api[offset + i])) {
      return ERROR;
      }
      else {
        if(counter_s == 0) {
          counter_a++;
        }
        else {
          counter_b++;
        }
      }
    }
    i++;
  }

  if((i == 0) || (counter_s != 1) || (counter_a == 0) || (counter_b == 0)) {
    return ERROR;
  }
  else {
    return OK;
  }
}

long myAPI_parse(char *api, int len)
{

  unsigned int adc_ch;
  unsigned int shift_code;

  switch(myAPI_check(api, len)) {

    case API_IDN:
      return API_IDN;
    break;

    case API_ACQUIRE:
      return API_ACQUIRE;
    break;

    case API_GETADC:

      adc_ch = myAPI_parse_first_numeric_argument(api, API_GETADC_LEN);

      if(adc_ch >= ADC_CHS) {
        return ERROR;
      }
      else {
        return (API_GETADC + adc_ch);
      }
    break;

    case API_GETGAIN:

      adc_ch = myAPI_parse_first_numeric_argument(api, API_GETGAIN_LEN);

      if(adc_ch >= ADC_CHS) {
        return ERROR;
      }
      else {
        return (API_GETGAIN + adc_ch);
      }
    break;

    case API_GETSHIFT:

      shift_code = myAPI_parse_first_numeric_argument(api, API_GETSHIFT_LEN);

      return (API_GETSHIFT + shift_code);
    break;

    default:
      return ERROR;
    break;
  }
}

unsigned int myAPI_parse_first_numeric_argument(char *api, unsigned int offset)
{

  unsigned int i;
  char dummy_api[API_MAX_LEN];

  i = 0;
  memset(dummy_api, API_NULL_CHAR, API_MAX_LEN);
  while(api[offset + i] != API_STOP_CHAR) {
    if(api[offset + i] == API_SPACE_CHAR) {
      return (unsigned int)(atoi(dummy_api));
    }
    else {
      dummy_api[i] = api[offset + i];
      i++;
    }
  }

  return (unsigned int)(atoi(dummy_api));
}

unsigned int myAPI_parse_second_numeric_argument(char *api, unsigned int offset)
{

  unsigned int i;
  char dummy_api[API_MAX_LEN];

  i = 0;
  while(api[offset + i] != API_SPACE_CHAR) {
    i++;
  }
  offset = offset + i + 1;

  i = 0;
  memset(dummy_api, API_NULL_CHAR, API_MAX_LEN);
  while(api[offset + i] != API_STOP_CHAR) {
    dummy_api[i] = api[offset + i];
    i++;
  }

  return (unsigned int)(atoi(dummy_api));
}
