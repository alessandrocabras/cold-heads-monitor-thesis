#include <string.h>
#include <ctype.h>

#define API_IDN_STR "#IDN?*"
#define API_ACQUIRE_STR "#ACQUIRE*"
#define API_GETADC_STR "#GETADC "
#define API_GETGAIN_STR "#GETGAIN "
#define API_GETSHIFT_STR "#GETSHIFT "

/**
 * myAPI_check
 * Function that checks if a string contains a valid API string.
 * 
 * @param  *api is the source string
 * @param  len is length of the source string
 * @return The corresponding API defined constant
 */
long myAPI_check(char *api, int len)
{
  // Utility vars
  int  ret;

  // Source string length checking
  if(len < API_MIN_LEN) {
    return ERROR;
  }
  else {
    // API #IDN?*

    if(strcmp(api, API_IDN_STR) == 0) {
      return API_IDN;
    }
    else {
      // API #ACQUIRE*

      if(strcmp(api, API_ACQUIRE_STR) == 0) {
        return API_ACQUIRE;
      }
      else {
        // API #GETADC adc_ch*

        if(strncmp(api, API_GETADC_STR, API_GETADC_LEN) == 0) {
          // Looking for a single numeric argument in the source string and a stop char
          ret = myAPI_check_single_numeric_argument(api, API_GETADC_LEN);
          if(ret == OK) {
            return API_GETADC;
          }
          else {
            return ERROR;
          }
        }
        else {
          // API #GETGAIN adc_ch*

          if(strncmp(api, API_GETGAIN_STR, API_GETGAIN_LEN) == 0) {
            // Looking for a single numeric argument in the source string and a stop char
            ret = myAPI_check_single_numeric_argument(api, API_GETGAIN_LEN);
            if(ret == OK) {
              return API_GETGAIN;
            }
            else {
              return ERROR;
            }
          }
          else {
            // API #GETSHIFT shift_code*

            if(strncmp(api, API_GETSHIFT_STR, API_GETSHIFT_LEN) == 0) {
              // Looking for a single numeric argument in the source string and a stop char
              ret = myAPI_check_single_numeric_argument(api, API_GETSHIFT_LEN);
              if(ret == OK) {
                return API_GETSHIFT;
              }
              else {
                return ERROR;
              }
            }
            else {
              // API UNKNOWN

              return ERROR;
            }
          }
        }
      }
    }
  }
}

/**
 * myAPI_check_single_numeric_argument
 * Function that checks if a candidate API string has a single numeric argument and a stop char.
 * 
 * @param  *api is the source string
 * @param  offset is the index value for the starting point to perform the checking task in the source string
 * @return The check task result
 */
int myAPI_check_single_numeric_argument(char *api, unsigned int offset)
{
  // Utility vars
  int  i;
  int  counter_a;
  
  // Looking for a single numeric argument in the source string and a stop char
  // Index and counter vars initialization
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

  // Index and counter values checking
  if((i == 0) || (counter_a == 0)) {
    return ERROR;
  }
  else {
    return OK;
  }  
}

/**
 * myAPI_check_couple_numeric_argument
 * Function that checks if a candidate API string has a couple of numeric argument and a stop char.
 * 
 * @param  *api is the source string
 * @param  offset is the index value for the starting point to perform the checking task in the source string
 * @return The check task result
 */
int myAPI_check_couple_numeric_argument(char *api, unsigned int offset)
{
  // Utility vars
  int  i;
  int  counter_a;
  int  counter_b;
  int  counter_s;

  // Looking for a couple of numeric argument in the source string and a stop char
  // Index and counters vars initialization
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

  // Index and counters values checking
  if((i == 0) || (counter_s != 1) || (counter_a == 0) || (counter_b == 0)) {
    return ERROR;
  }
  else {
    return OK;
  }
}
     
/**
 * myAPI_parse
 * Function that parses a valid API string.
 * 
 * @param  *api is the source string
 * @param  len is lenght of the source string
 * @return The corresponding codified API constant
 */
long myAPI_parse(char *api, int len)
{
  // Utility vars
  unsigned int adc_ch;
  unsigned int shift_code;

  switch(myAPI_check(api, len)) {

    // API #IDN?*
    case API_IDN:
      return API_IDN;
    break;

    // API #ACQUIRE*
    case API_ACQUIRE:
      return API_ACQUIRE;
    break;

    // API #GETADC adc_ch*
    case API_GETADC:
      // Getting the single numeric argument from the source string
      adc_ch = myAPI_parse_first_numeric_argument(api, API_GETADC_LEN);

      // Numeric argument value checking
      if(adc_ch >= ADC_CHS) {
        return ERROR;
      }
      else {
        return (API_GETADC + adc_ch);
      }
    break;

    // API #GETGAIN adc_ch*
    case API_GETGAIN:
      // Getting the single numeric argument from the source string
      adc_ch = myAPI_parse_first_numeric_argument(api, API_GETGAIN_LEN);

      // Numeric argument value checking
      if(adc_ch >= ADC_CHS) {
        return ERROR;
      }
      else {
        return (API_GETGAIN + adc_ch);
      }
    break;

    // API #GETGAIN adc_ch*
    case API_GETSHIFT:
      // Getting the single numeric argument from the source string
      shift_code = myAPI_parse_first_numeric_argument(api, API_GETSHIFT_LEN);

      // Numeric argument value checking

      return (API_GETSHIFT + shift_code);
    break;

    // API UNKNOWN
    default:
      return ERROR;
    break;
  }
}

/**
 * myAPI_parse_first_numeric_argument
 * Function that parses the first numeric argument of a valid API string.
 * 
 * @param  *api is the source string
 * @param  offset is the index value for the starting point to perform the parsing task in the source string
 * @return The first numeric argument
 */
unsigned int myAPI_parse_first_numeric_argument(char *api, unsigned int offset)
{
  // Utility vars
  unsigned int i;
  char dummy_api[API_MAX_LEN];

  // Parsing the first (or unique) numeric argument from the source string
  // Index var initialization
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

  // Returning the first (or unique) numeric argument from the source string
  return (unsigned int)(atoi(dummy_api));
}

/**
 * myAPI_parse_second_numeric_argument
 * Function that parses the second numeric argument of a valid API string.
 * 
 * @param  *api is the source string
 * @param  offset is the index value for the starting point to perform the parsing task in the source string
 * @return The second numeric argument
 */
unsigned int myAPI_parse_second_numeric_argument(char *api, unsigned int offset)
{
  // Utility vars
  unsigned int i;
  char dummy_api[API_MAX_LEN];
  
  // Skipping the first numeric argument from the source string
  // Index var initialization
  i = 0;
  while(api[offset + i] != API_SPACE_CHAR) {
    i++;
  }
  offset = offset + i + 1;

  // Parsing the second numeric argument from the source string
  // Index var initialization
  i = 0;
  memset(dummy_api, API_NULL_CHAR, API_MAX_LEN);
  while(api[offset + i] != API_STOP_CHAR) {
    dummy_api[i] = api[offset + i];
    i++;
  }

  // Returning the second numeric argument from the source string
  return (unsigned int)(atoi(dummy_api));
}
