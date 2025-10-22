# XIQ CCG CSV UPLOAD
##### XIQ_CCG_CSV.py

|  _The software is provided as-is and [Extreme Networks](http://www.extremenetworks.com/) has no obligation to provide maintenance, support, updates, enhancements, or modifications. Any support provided by [Extreme Networks](http://www.extremenetworks.com/) is at its sole discretion._

_Issues and/or bug fixes may be reported on in the Issues for this repository._  |

### <span style="color:purple">Purpose</span>
This script will take a CSV file with these 2 columns: Serial Numbers,Cloud Config Group and assign the devices with the serial numbers to the named cloud config group, if it exists. 
### <span style="color:purple">Information</span>
The script will perform API calls to check if serial numbers exist in the VIQ, if not, it will log a message that the device doesn't exist. 
The script will also check if the Cloud Config Group name exists. If it does not exist the serial numbers will not be assigned to a CCG and a message will be logged.
## <span style="color:purple">Setting up the script</span>
The script will prompt the user for XIQ credentials.  You can alternatively provide an API token in the script to bypass this requirement if desired.  See line # 17.
1. <span style="color:purple">XIQ_API_token</span> - Update this with a valid token. The token will need the device and ccg permissions

## <span style="color:purple">Needed files</span>
the XIQ_CCG_CSV.py script uses several other files. If these files are missing the script will not function.
In the same folder as the XIQ_CCG_CSV.py script there should be an /app/ folder. Inside this folder should be a logger.py file and a xiq_api.py file. After running the script a new folder 'script_logs' will be created and a file named 'serial-CCG_log.log' will be created with the log messages from the script.

The log file that is created when running will show any errors that the script might run into. It is a great place to look when troubleshooting any issues.

## <span style="color:purple">Running the script</span>
open the terminal to the location of the script and run this command.

```
python XIQ_CCG_CSV.py
```
## <span style="color:purple">Optional Flags</span>
There is an optional flag that can be added to the script when running.
```
--external
```
This flag will enable you to execute this script on an XIQ account where you are an external user. After logging in with your XIQ credentials, the script will give you a numeric option of each of the XIQ instances you have access to. Choose the one you would like to use.

You can add the flag when running the script.
```
python XIQ_CCG_CSV.py --external
```
## <span style="color:purple">requirements</span>
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.