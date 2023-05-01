import csv
import datetime
import re
import yaml

import datetime as dt

from .log import log, Log

def generate_monthly_insights(data: dict):
    month = {}

    bgm = max(data['monthToMonthExpenditure'], key=lambda cat: abs(cat['categoryMoneyOut']))

    month['avgPM'] = abs(round(data['totMoneyOut'] / len(data['monthToMonthExpenditure']), 2))
    month['biggestMonth'] = dt.datetime.strptime(bgm['category'], "%Y/%m")
    month['biggestMonthSpend'] = abs(bgm['categoryMoneyOut'])

    return month

def generate_time_info(statement):
    time = {}

    latestDate = max(statement, key=lambda ts: ts['transactionTimestamp'])
    earliestDate = min(statement, key=lambda ts: ts['transactionTimestamp'])

    time['fTrnsDate'] = earliestDate['transactionTimestamp']
    time['lTrnsDate'] = latestDate['transactionTimestamp']

    return time

def sum_list(filtered: list, money_out: bool):
    ret = 0.0

    if money_out == True:
        for i in range(len(filtered)):
            if filtered[i]['transactionType'] == "DEBIT":
                ret += filtered[i]['transactionAmount']
    else:
        for i in range(len(filtered)):
            if filtered[i]['transactionType'] == "CREDIT":
                ret += filtered[i]['transactionAmount']

    return ret

def sum_category(category: str, filtered: list):
    out = {}

    out['category'] = category
    out['categoryMoneyOut'] = round(sum_list(filtered, True), 2)
    out['categoryMoneyIn'] = round(sum_list(filtered, False), 2)
    out['categoryDifference'] = round(out['categoryMoneyIn'] + out['categoryMoneyOut'], 2)

    return out

def extract_timestamp(ts: str):
    year = ts[0:4]
    month = ts[4:6]
    day = ts[6:8]

    return datetime.datetime(int(year), int(month), int(day))

def load_categorizer_config(configFile: str, default: bool = False):

    if default == True:
        return [
            {'category': 'Subscriptions', 'strings': ['RECURRING']},
            {'category': 'Refunds', 'strings': ['REFUND']},
            {'category': 'Government/Taxes', 'strings': ['CANADA', 'GST', 'HST', 'CRA', 'FED', 'GOV CA']},
            {'category': 'Transfers', 'strings': ['ETRNSFR', 'RECVD', 'TF ']}
        ]

    with open(configFile, 'r') as f:
        categorizer = yaml.load(f, Loader=yaml.SafeLoader)
    
    return categorizer

def categorize(categorizer, transactionTitle: str):
    

    for i in range(len(categorizer)):
        for str in categorizer[i]['strings']:
            term = transactionTitle.find(str)
            if term != -1:
                return categorizer[i]['category']
    
    return "Others"

def filter_categories(categorizer: list[dict], statement):
    category_dicts = []
    out = []

    for i in range(len(categorizer)):
        category_dicts.append([{**record} for record in statement if record['transactionCategory'] == categorizer[i]['category']])

    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Others"])

    for i in range(len(category_dicts)):
        if len(category_dicts[i]) > 0:
           out.append(sum_category(category_dicts[i][0]['transactionCategory'], category_dicts[i]))
        else:
            continue
    
    return out

def filter_months(statement):
    month_dicts = []
    out = []

    for i in range(12):
        month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == i])

    for i in range(len(month_dicts)):
        if len(month_dicts[i]) > 0:
            out.append(sum_category(month_dicts[i][0]['transactionTimestamp'].strftime("%Y/%m"), month_dicts[i]))
        else:
            continue
    
    return out

def slurp_statement_csv(file: str, bForPrint: bool):

    records = []
    configFile = "bank/categorizer.yaml"

    try: 
        categorizer = load_categorizer_config(configFile)
    except FileNotFoundError:
        log(Log.ERROR, f"Config file '{configFile}' not found!")
        log(Log.WARNING, f"Using default categorizer.")
        categorizer = load_categorizer_config(configFile, default=True)
    except yaml.scanner.ScannerError as error:
        log(Log.ERROR, f"Invalid YAML contained in config file '{configFile}': {error.context} {error.problem} near [{error.context_mark.line}, {error.context_mark.column}]")
        log(Log.WARNING, f"Using default categorizer.")
        categorizer = load_categorizer_config(configFile, default=True)

    try:
        with open(file, "r", encoding='utf-8') as statement:
            reader = csv.reader(statement, delimiter=',')

            # Skip junk starting lines
            # TODO: Replace this with a system to enforce a certain format (maybe in it's own function)
            # Raise a CSVFormatError exception
            for i in range(6):
                next(reader)

            for row in reader:
                if bForPrint == True:
                    records.append(
                        dict (
                                account = row[0].replace("'",""), 
                                transactionType=row[1], 
                                transactionTimestamp=extract_timestamp(row[2]).strftime('%Y-%m-%d'), 
                                transactionAmount=float(row[3]), 
                                transactionCategory=categorize(categorizer, row[4]), 
                                transactionTitle=re.sub(r"\s{3,}"," ", row[4].rstrip())
                            )
                        )
                else:
                    records.append(
                        dict (
                            account = row[0].replace("'",""),
                            transactionType=row[1],
                            transactionTimestamp=extract_timestamp(row[2]),
                            transactionAmount=float(row[3]),
                            transactionCategory=categorize(categorizer, row[4]),
                            transactionTitle=re.sub(r"\s{3,}"," ", row[4].rstrip())
                        )
                    )
    except PermissionError:
        log(Log.ERROR, f"User does not have permissions to access file '{file}'")
        exit(-1)
        

    return records