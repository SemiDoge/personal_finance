import json
import click
import webbrowser
import os
import yaml

from .log import log, Log
from .functions import slurp_statement_csv, filter_categories, filter_months, sum_list, load_categorizer_config
from .pdf import commit_to_pdf

def print_json(ctx, param, value):

    statement = ctx.params['statement'].replace(' ','')

    try:
        if value == True:
            print(json.dumps(slurp_statement_csv(f"./{statement}", True), default=str, indent=4))
            ctx.exit(0)
    except FileNotFoundError: 
        log(Log.ERROR, f"File '{statement}' not found!")
        ctx.exit(-1)

def generate_insights(statement: list[dict]):
    out = {}
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

    out['totMoneyOut'] = round(sum_list(statement, True), 2)
    out['totMoneyIn'] = round(sum_list(statement, False), 2)
    out['totDifference'] = round(out['totMoneyIn'] + out['totMoneyOut'], 2)

    out['categoryExpenditure'] = filter_categories(categorizer, statement)
    out['monthToMonthExpenditure'] = filter_months(statement)
    
    return out

@click.command(help='Takes a BMO generated transaction .csv file and interprets that data to provide insights in the form of a viewable PDF.')
@click.option('-s', '--statement', prompt=True, help='Bank statement csv filename.')
@click.option('-v', '--verbose', is_flag=True, help='Includes itemized transactions along with insights PDF.')
@click.option('-p', '--print-json', help='Prints pretty JSON (alternate to PDF).', default=False, is_flag=True, callback=print_json)
def main(statement: str, print_json: bool, verbose: bool):
    statement = statement.replace(' ','')

    try:
        statement_obj = slurp_statement_csv(statement, False)
    except FileNotFoundError:
        log(Log.ERROR, f"File '{statement}' not found!")
        return -1

    insights_obj = generate_insights(statement_obj)

    outfile = statement.replace('.csv','.pdf')
    if verbose == True:
        outfile = f"{outfile[:len(outfile)-4]}_detailed.pdf"
        commit_to_pdf(insights_obj, outfile, statement_obj, True)
    else:
        commit_to_pdf(insights_obj, outfile, statement_obj)

    print(f"Saved insight to {os.path.abspath(outfile)}")
    webbrowser.open(outfile)

    return