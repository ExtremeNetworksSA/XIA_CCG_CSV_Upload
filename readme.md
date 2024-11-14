# XIQ CCG CSV
##### XIQ_CCG_CSV.py
### <span style="color:purple">Purpose</span>
This script will take a CSV file with these 2 columns: serialNumbers,cloudConfigGroup and assign the devices with the serial numbers to the named cloud config group, if it exists. 

## <span style="color:purple">Setting up the script</span>
At the top of the script there are some variables that need to be added.
1. <span style="color:purple">XIQ_API_token</span> - Update this with a valid token. The token will need the device and ccg permissions

## <span style="color:purple">Needed files</span>
the XIQ_CCG_CSV.py script uses several other files. If these files are missing the script will not function.
In the same folder as the XIQ_CCG_CSV.py script there should be an /app/ folder. Inside this folder should be a logger.py file and a xiq_api.py file. After running the script a new file 'serial-CCG_log.log' will be created

There also should be a /csv/ folder. This is where you can add the csv file or multiple csv files. The script will load in the file when ran.

The log file that is created when running will show any errors that the script might run into. It is a great place to look when troubleshooting any issues.

## <span style="color:purple">Running the script</span>
open the terminal to the location of the script and run this command.

```
python XIQ_CCG_CSV.py
```

## <span style="color:purple">requirements</span>
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.