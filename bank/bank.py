import json
import click
import webbrowser
import os

from .log import log, Log
from .config import Configuration
from .functions import slurp_statement_csv, generate_insights, auto_detect_bank
from .pdf import commit_to_pdf
from .enums import Bank


def print_json(ctx, param, value):
    statement = ctx.params["statement"].replace(" ", "")

    if value == True:
        try:
            config = Configuration(config_dir="bank/config", config=ctx.params["categorizer_path"].replace(" ",""))
            categorizer = config.get_categorizer()
            bank = auto_detect_bank(statement)
            print(
                json.dumps(
                    slurp_statement_csv(categorizer, f"./{statement}", True, bank),
                    default=str,
                    indent=4,
                )
            )
            ctx.exit(0)
        except FileNotFoundError:
            log(Log.ERROR, f"File '{statement}' not found!")
            ctx.exit(-1)


@click.command(
    help="Takes a BMO or Scotiabank generated transaction .csv file and interprets that data to provide insights in the form of a viewable PDF.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "-s", "--statement", prompt=True, help="Path to bank statement `.csv` filename."
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Includes itemized transactions along with insights PDF.",
)
@click.option(
    "-p",
    "--print-json",
    help="Prints pretty JSON (alternate to PDF).",
    default=False,
    is_flag=True,
    callback=print_json,
)
@click.option(
    "-c",
    "--categorizer-path",
    help="Path to categorizer .yaml you wish to use to categorize your transaction data. Only looks in config/ directory.",
)
def main(statement: str, print_json: bool, categorizer_path: str, verbose: bool):
    statement = statement.replace(" ", "")
    # TODO: Instead of only passing the categorizer around, maybe the entire configuration object should be sent so that other ...
    # configuration options can change the program. For example change the colour of the banner in the PDF, to fit the bank's colours.

    config = Configuration(config_dir="bank/config", config=categorizer_path)
    categorizer = config.get_categorizer()

    try:
        bank = auto_detect_bank(statement)
        statement_obj = slurp_statement_csv(categorizer, statement, False, bank)
    except FileNotFoundError as error:
        log(Log.ERROR, f"File '{error.filename}' not found!")
        return -1

    insights_obj = generate_insights(categorizer, statement_obj)

    outfile = statement.replace(".csv", ".pdf")
    try:
        if verbose == True:
            outfile = f"{outfile[:len(outfile)-4]}_detailed.pdf"
            commit_to_pdf(insights_obj, outfile, statement_obj, bank, verbose=True)
        else:
            commit_to_pdf(insights_obj, outfile, statement_obj, bank)

        log(Log.INFO, f"Saved insight report to {os.path.abspath(outfile)}")
        webbrowser.open(outfile)
    except IOError as error:
        log(Log.ERROR, f"Error creating or writing to file '{outfile}'")
        return

    return
