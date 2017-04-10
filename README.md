
The program compute-average.pl is a pure Python application based upon 
Python 2.7.5 on CentOS 7.3.1161

Running the program with:

`python compute_average.py [flags]`


Run with no flags the script will capture the data and print out the monthly
expense and income data along with the monthly average. The average does
not include the last (incomplete) month. If there were no transaction is a
month the month will be skipped in the output. The output format is JSON.


The allowed command line flags are:

`--help` which will print out the available options

`--ignore-donuts` which will exclude all donut expenses from the averages

`--crystal-ball` which downloads the projected transaction dataset and
       combines it with the existing data to compute a new average, In this
       case the incomplete data from the last month is combined with the
       projection to compute the average.

`--ignore-cc-payments` tries to isolate the credit card credits and debits.
       The transactions are identified by looking at the merchant label for two
       values 'CC Payment' and 'Credit Card Payment'. As these items appear not
       to be perfectly paired the script will print a warning if it detects 
       "orphan" transactions of either type. A list of both the paired and
       orphan transactions is written to the file 'credit_card_payments'.
       Currently the orphans are also excluded from the average calculations
       when this flag is picked. Note that just looking for the pairing of an
       expense and credit with a 24 hour period would not detect the orphans


Also there are a few unit tests that you can run with `python test.py`

