# Personal Finance - Demo
## Introduction

There are three files in this folder. `demo.csv`, `demo.pdf`, and `demo_detailed`. This readme will quickly summarize what they are.

## demo.csv
A fake BMO bank statement in the form of a `.csv` file. These bank statements are just a csv listing of all the transactions from a bank account.

## demo.pdf
A simple, single page, financial overview of the bank account's spending. It has a summary of spending as well as a customizable (via the categorizer) break down of the type of spending.

### Command
`python -m finance -s demo.csv -c demoCategorizer.yaml`

## demo_detailed.pdf
This is the same as the standard output pdf with the addition of replicating the list of transactions in a nice table on the pages after the summary.

### Command
`python -m finance -s demo.csv -c demoCategorizer.yaml -v`
