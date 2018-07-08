# City name sanitizer
This script automatically sanitize Spanish city names which are truncated and with typos using the Levanshtein distance.  
The script generates a new file with the sanitized city names and a flag for registers that have to be manually checked.  
This flag is needed because the postal code provided is not guaranteed to be correct.

## Inputs
* File with city names and postal code (postal code is not guaranteed to be precise).  
* File with postal codes and city names.
