import json
import click

from .functions import slurp_statement_csv

def print_json(ctx, param, value):
    if value == True:
        print(json.dumps(slurp_statement_csv(f"./{ctx.params['statement'].replace(' ','')}", True), default=str, indent=4))
        ctx.exit(0)

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
    out = {
        "category": category,
        "categoryMoneyOut": 0.0,
        "categoryMoneyIn": 0.0,
        "categoryDifference": 0.0,
    }

    out['categoryMoneyOut'] = sum_list(filtered, True)
    out['categoryMoneyIn'] = sum_list(filtered, False)
    out['categoryDifference'] = out['categoryMoneyIn'] + out['categoryMoneyOut']

    return out

def filter_categories(statement):
    category_dicts = []
    out = []

    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Subscriptions"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Refunds"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Transfers"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Government/Taxes"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Steam/Games"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Amazon/Others"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Groceries"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "FastFood/Others"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Keyboards"])
    category_dicts.append([{**record} for record in statement if record['transactionCategory'] == "Online/Others"])
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

    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 1])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 2])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 3])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 4])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 5])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 6])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 7])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 8])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 9])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 10])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 11])
    month_dicts.append([{**record} for record in statement if record['transactionTimestamp'].month == 12])

    for i in range(len(month_dicts)):
        if len(month_dicts[i]) > 0:
            out.append(sum_category(month_dicts[i][0]['transactionTimestamp'].strftime("%Y/%m"), month_dicts[i]))
        else:
            continue
    
    return out

def generate_insights(statement: list):
    #print("Generating insights...")

    # Just so I know what I'm trying to achieve
    out = {
        "totMoneyOut": 0.0,
        "totMoneyIn": 0.0,
        "totDifference": 0.0,
        "categoryExpenditure": [],
        "monthToMonthExpenditure": []
    }

    out['totMoneyOut'] = sum_list(statement, True)
    out['totMoneyIn'] = sum_list(statement, False)
    out['totDifference'] = out['totMoneyIn'] + out['totMoneyOut']

    out['categoryExpenditure'] = filter_categories(statement)
    out['monthToMonthExpenditure'] = filter_months(statement)
    
    return out


@click.command(help='Takes a BMO generated transaction .csv file and interprets that data to provide insights.')
@click.option('-s', '--statement', prompt=True, help='Bank statement csv filename')
@click.option('-p', '--print-json', help='Prints pretty JSON', default=False, is_flag=True, callback=print_json)
def main(statement: str, print_json: bool):
    statement_obj = slurp_statement_csv(f"./{statement.replace(' ','')}", False)

    insights_obj = generate_insights(statement_obj)

    print(json.dumps(insights_obj, indent=4))
    return