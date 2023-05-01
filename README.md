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
  provide insights in the form of a viewable PDF.

Options:
  -s, --statement TEXT  Bank statement csv filename.
  -v, --verbose         Includes itemized transactions along with insights
                        PDF.
  -p, --print-json      Prints pretty JSON (alternate to PDF).
  --help                Show this message and exit.
```