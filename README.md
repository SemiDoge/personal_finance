# banking

This is a Python CLI application that will take a `.csv` bank statement and provide insights about the data.

Currently the insights are:
  * Total / YTD money out
  * Total / YTD money in
  * Total / YTD net money in
  * Categorized money in, out, and net
    * Categorizations can be defined in categorizer.yaml file
  * Monthly money in, out, and net

## Use

```
Usage: python -m bank [OPTIONS]

  Takes a BMO generated transaction .csv file and interprets that data to
  provide insights in the form of a viewable PDF.

Options:
  -s, --statement TEXT  Bank statement csv filename.
  -v, --verbose         Includes itemized transactions along with insights PDF.
  -p, --print-json      Prints pretty JSON (alternate to PDF).
  --help                Show this message and exit.
```

## Categorizer

The categorizer is a part of the program that interprets the bank's 'transaction title' and makes a determination on how any given transaction should be categorized. You can make your own categorizer by providing a `config/categorizer.yaml` config file that the program will read and use to guide the categorizer's behaviour.

The order in which categories and search strings are placed in the file is important. If a transaction title could fit under multiple categories it will be categorized into the category with the higher position in the config file.

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