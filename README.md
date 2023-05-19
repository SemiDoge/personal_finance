# Personal Finance
## Overview
This is a Python CLI application that will take a `.csv` finance statement and provide insights about the data.

Currently the insights are:
  * Total / YTD money out
  * Total / YTD money in
  * Total / YTD net money in
  * Categorized money in, out, and net
    * Categorizations can be defined in categorizer.yaml file
  * Monthly money in, out, and net
  * Current and previous quarter money out

## Prerequisites

* Python3
* pip

## Getting Started

* Clone the repository.
* Enter the cloned repo.
* Run: `python -m venv .venv` to create a virtual environment.
* Run: `pip install -r ./requirements.txt` to install the requirements.

The application is now ready to use!

## Use

```
Usage: python -m finance [OPTIONS]

  Takes a BMO or Scotiabank generated transaction .csv file and interprets    
  that data to provide insights in the form of a viewable PDF.

Options:
  -s, --statement TEXT         Path to bank statement .csv filename.        
  -v, --verbose                Includes itemized transactions along with      
                               insights PDF.
  -p, --print-json             Prints pretty JSON (alternate to PDF).
  -c, --categorizer-path TEXT  Path to categorizer .yaml you wish to use to   
                               categorize your transaction data. Only looks in
                               config/ directory.
  -h, --help                   Show this message and exit.
```

## Statement

This program accepts a `.csv` representing the transactions of a bank account. This kind of information can be downloaded from a bank. Unfortunately, due to the nature of different banks formatting their data differently this program only supports transaction data originating from Bank of Montreal and Scotiabank.

### BMO
``` csv
1:Following data is valid as of 20230113000000 (Year/Month/Day/Hour/Minute/Second)
2:
3:
4:First Bank Card,Transaction Type,Date Posted, Transaction Amount,Description
5:
6:
7:'${CARD_NUMBER}',${TRANSACTION_TYPE},20230113,-1.00,${TRANSACTION_DESCRIPTION}
8+:...
```

Line numbers included to make `.csv` structure more explicit. Don't include numbers when actually using program.

### Scotiabank
``` csv
1:x/xx/2023,-1.00,-,"${TRANSACTION_TYPE}","${TRANSACTION_DESCRIPTION}"
2+:...
```


## Categorizer

The categorizer is a part of the program that interprets the bank's 'transaction description' and makes a determination on how any given transaction should be categorized. You can make your own categorizer by providing a `config/categorizer.yaml` config file that the program will read and use to guide the categorizer's behaviour.

The order in which categories and search strings are placed in the file is important. If a transaction description could fit under multiple categories it will be categorized into the category with the higher position in the config file.

Below is what the default categorizer looks like as a `.yaml` file.

``` yaml
- category: Subscriptions
  strings:
    - RECURRING

- category: Refunds
  strings:
    - REFUND

- category: Government/Taxes
  strings:
    - ' GST/'
    - ' PRO/'
    - ' FED/'
    - CRA
    - GOV CA
    - 'CANADA '

- category: Transfers
  strings:
    - ETRNSFR
    - RECVD
    - 'TF '
  
- category: Online/Others
  strings:
    - ONLINE
```
