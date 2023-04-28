# banking

This is a Python CLI application that will take a `.csv` bank statement and provide insights about the data.

Currently the insights are:
  * total / YTD money out
  * total / YTD money in
  * total / YTD net money in
  * categorized money in, out, and net (CATEGORIES UNDER CONSTRUCTION)
  * monthly money in, out, and net

## Use

```
Usage: python -m bank [OPTIONS]

  Takes a BMO generated transaction .csv file and interprets that data to
  provide insights.

Options:
  -s, --statement TEXT  Bank statement csv filename
  -p, --print-json      Prints pretty JSON
  --help                Show this message and exit.
```