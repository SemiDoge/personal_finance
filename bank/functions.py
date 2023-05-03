import csv
import datetime
import re
import os

import datetime as dt

from .log import log, Log
from .enums import Bank


def generate_insights(categorizer: list[dict], statement: list[dict]):
    out = {}

    out["totMoneyOut"] = round(sum_list(statement, True), 2)
    out["totMoneyIn"] = round(sum_list(statement, False), 2)
    out["totDifference"] = round(out["totMoneyIn"] + out["totMoneyOut"], 2)

    out["categoryExpenditure"] = filter_categories(categorizer, statement)
    out["monthToMonthExpenditure"] = filter_months(statement)

    return out


def generate_monthly_insights(data: dict):
    month = {}

    bgm = max(
        data["monthToMonthExpenditure"], key=lambda cat: abs(cat["categoryMoneyOut"])
    )

    month["avgPM"] = abs(
        round(data["totMoneyOut"] / len(data["monthToMonthExpenditure"]), 2)
    )
    month["biggestMonth"] = dt.datetime.strptime(bgm["category"], "%Y/%m")
    month["biggestMonthSpend"] = abs(bgm["categoryMoneyOut"])

    return month


def generate_time_info(statement):
    time = {}

    latestDate = max(statement, key=lambda ts: ts["transactionTimestamp"])
    earliestDate = min(statement, key=lambda ts: ts["transactionTimestamp"])

    time["fTrnsDate"] = earliestDate["transactionTimestamp"]
    time["lTrnsDate"] = latestDate["transactionTimestamp"]

    return time


def sum_list(filtered: list, money_out: bool):
    ret = 0.0

    if money_out == True:
        for i in range(len(filtered)):
            if filtered[i]["transactionType"] == "DEBIT":
                ret += filtered[i]["transactionAmount"]
    else:
        for i in range(len(filtered)):
            if filtered[i]["transactionType"] == "CREDIT":
                ret += filtered[i]["transactionAmount"]

    return ret


def sum_category(category: str, filtered: list):
    out = {}

    out["category"] = category
    out["categoryMoneyOut"] = round(sum_list(filtered, True), 2)
    out["categoryMoneyIn"] = round(sum_list(filtered, False), 2)
    out["categoryDifference"] = round(
        out["categoryMoneyIn"] + out["categoryMoneyOut"], 2
    )

    return out


def set_metadata(
    file_path: str,
    title: str = "Transaction Insights",
    author: str = os.getlogin(),
    subject: str = "This document summarizes transactions...",
):
    with open(file_path, "r") as file:
        content = file.read()

    content = re.sub(r"/Title \(.*?\)", f"/Title ({title})", content)
    content = re.sub(r"/Author \(.*?\)", f"/Author ({author})", content)
    content = re.sub(
        r"/Subject \(.*?\)",
        f"/Subject ({subject})",
        content,
    )
    content = re.sub(r"/Producer \(.*?\)", f"/Producer (RML2PDF)", content)

    with open(file_path, "w") as file:
        file.write(content)


def extract_timestamp(ts: str):
    formats = ["%Y%m%d", "%m/%d/%Y"]

    for format in formats:
        try:
            timestamp = dt.datetime.strptime(ts, format)
            return timestamp
        except ValueError:
            pass
    raise ValueError("Unable to parse timestamp string")


def categorize(categorizer, transactionTitle: str):
    for i in range(len(categorizer)):
        for str in categorizer[i]["strings"]:
            term = transactionTitle.find(str)
            if term != -1:
                return categorizer[i]["category"]

    return "Others"


def filter_categories(categorizer: list[dict], statement):
    category_dicts = []
    out = []

    for i in range(len(categorizer)):
        category_dicts.append(
            [
                {**record}
                for record in statement
                if record["transactionCategory"] == categorizer[i]["category"]
            ]
        )

    category_dicts.append(
        [
            {**record}
            for record in statement
            if record["transactionCategory"] == "Others"
        ]
    )

    # removes empty categories so they don't mess up generated pie chart
    for i in range(len(category_dicts)):
        if len(category_dicts[i]) > 0:
            out.append(
                sum_category(
                    category_dicts[i][0]["transactionCategory"], category_dicts[i]
                )
            )
        else:
            continue

    return out


def filter_months(statement):
    month_dicts = []
    out = []

    # 12 for 12 months in year
    for i in range(12):
        month_dicts.append(
            [
                {**record}
                for record in statement
                if record["transactionTimestamp"].month == i
            ]
        )

    # removes empty/future months
    for i in range(len(month_dicts)):
        if len(month_dicts[i]) > 0:
            out.append(
                sum_category(
                    month_dicts[i][0]["transactionTimestamp"].strftime("%Y/%m"),
                    month_dicts[i],
                )
            )
        else:
            continue

    return out


def slurp_bmo_csv(categorizer, file: str, bForPrint: bool):
    records = []

    try:
        with open(file, "r", encoding="utf-8") as statement:
            reader = csv.reader(statement, delimiter=",")

            # Skip junk starting lines
            # TODO: Replace this with a system to enforce a certain format (maybe in it's own function)
            # Raise a CSVFormatError exception
            for i in range(6):
                next(reader)

            for row in reader:
                if bForPrint == True:
                    records.append(
                        dict(
                            account=row[0].replace("'", ""),
                            transactionType=row[1],
                            transactionTimestamp=extract_timestamp(row[2]).strftime(
                                "%Y-%m-%d"
                            ),
                            transactionAmount=float(row[3]),
                            transactionCategory=categorize(categorizer, row[4]),
                            transactionTitle=re.sub(r"\s{3,}", " ", row[4].rstrip()),
                        )
                    )
                else:
                    records.append(
                        dict(
                            account=row[0].replace("'", ""),
                            transactionType=row[1],
                            transactionTimestamp=extract_timestamp(row[2]),
                            transactionAmount=float(row[3]),
                            transactionCategory=categorize(categorizer, row[4]),
                            transactionTitle=re.sub(r"\s{3,}", " ", row[4].rstrip()),
                        )
                    )
    except ValueError as error:
        log(Log.ERROR, f"{error}")
        exit(-1)
    except PermissionError:
        log(
            Log.ERROR,
            f"User '{os.getlogin()}' does not have permissions to access file '{file}'",
        )
        exit(-1)

    return records


def auto_detect_bank(file: str):
    with open(file, "r", encoding="utf-8") as statement:
        reader = csv.reader(statement, delimiter=",")

        itr = next(reader)

        if itr[0].find("Following") != -1:
            return Bank.BMO
        elif len(itr[0]) < 15:
            return Bank.SCOTIA
        else:
            return Bank.NULL


def slurp_scotia_csv(categorizer, file: str, bForPrint: bool):
    records = []

    try:
        with open(file, "r", encoding="utf-8") as statement:
            reader = csv.reader(statement, delimiter=",")

            for row in reader:
                if bForPrint == True:
                    records.append(
                        dict(
                            transactionTimestamp=extract_timestamp(row[0]).strftime(
                                "%Y/%m/%d"
                            ),
                            transactionAmount=float(row[1]),
                            transactionType="CREDIT" if float(row[1]) > 0 else "DEBIT",
                            transactionCategory=categorize(categorizer, row[4]),
                            transactionTitle=re.sub(r"\s{3,}", " ", row[4].rstrip()),
                        )
                    )
                else:
                    records.append(
                        dict(
                            transactionTimestamp=extract_timestamp(row[0]),
                            transactionType="CREDIT" if float(row[1]) > 0 else "DEBIT",
                            transactionAmount=float(row[1]),
                            transactionCategory=categorize(categorizer, row[4]),
                            transactionTitle=re.sub(r"\s{3,}", " ", row[4].rstrip()),
                        )
                    )
    except PermissionError:
        log(
            Log.ERROR,
            f"User '{os.getlogin()}' does not have permissions to access file '{file}'",
        )
        exit(-1)

    return records


def slurp_statement_csv(categorizer, file: str, bForPrint: bool, bank: Bank):
    if bank == Bank.BMO:
        return slurp_bmo_csv(categorizer, file, bForPrint)
    elif bank == Bank.SCOTIA:
        # TODO: Raw data coming in from Scotiabank contains characters like an unmatched '(' or '&'
        # which do not play well with XML. Some sanitization must be done in order to prevent this
        return slurp_scotia_csv(categorizer, file, bForPrint)
    elif bank == Bank.TD:
        raise Exception(f"NOT IMPLEMENTED")
    else:
        raise Exception(f"Unknown bank: '{Bank}'")
