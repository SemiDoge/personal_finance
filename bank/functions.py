import csv
import datetime

def extract_timestamp(ts: str):
    year = ts[0:4]
    month = ts[4:6]
    day = ts[6:8]

    return datetime.datetime(int(year), int(month), int(day))

def categorize(transactionTitle: str):
    #TODO: Consider making the search strings for the different categories somehow factorable to a config file, possibly a .yaml?
    if transactionTitle.find('RECURRING') != -1:
       return "Subscriptions"

    if transactionTitle.find('REFUND') != -1:
        return "Refunds"
    
    govt_search_strings = ["CANADA", "GST", "HST", "CRA", "FED", "PRO", "GOV CA"]
    for str in govt_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "Government/Taxes"
    
    transfer_search_strings = ["ETRNSFR", "RECVD", "TF"]
    for str in transfer_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "Transfers"
    
    game_search_strings = ["STEAM", "JAGEX", "SONY", "XBOX", "NINTENDO"]
    for str in game_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "Steam/Games"

    amazon_search_strings = ["AMZN", "AMZN MKTP"]
    for str in amazon_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "Amazon/Others"
    
    grocer_search_strings = ["ZEHRS", "FRESHCO", "BULK BARN"]
    for str in grocer_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "Groceries"

    fast_food_search_strings = ["BK", "MCDONALD'S", "MCDONALDS", "PIZZA", "DAIRY QUEEN", "TIM HORTONS", "MARY BROWNS", "CAESARS", "WENDY'S"]
    for str in fast_food_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "FastFood/Others"

    keyboards_search_strings = ["KEYBOARDS", "KEEB", "TYPIST", "RINGER"]
    for str in keyboards_search_strings:
        i = transactionTitle.find(str)
        if i != -1:
            return "Keyboards" 

    # Should always be the last conditional
    if transactionTitle.find("ONLINE") != -1:
        return "Online/Others"

    return "Others"

def slurp_statement_csv(file: str, bForPrint: bool):

    records = []

    with open(file, "r", encoding='utf-8') as statement:
        reader = csv.reader(statement, delimiter=',')

        # Skip junk starting lines
        for i in range(6):
            next(reader)

        for row in reader:
            if bForPrint == True:
                records.append(dict(account = row[0], transactionType=row[1], transactionTimestamp=extract_timestamp(row[2]).strftime('%Y-%m-%d'), transactionAmount=float(row[3]), transactionCategory=categorize(row[4]), transactionTitle=row[4].rstrip()))
            else:
                records.append(dict(account = row[0], transactionType=row[1], transactionTimestamp=extract_timestamp(row[2]), transactionAmount=float(row[3]), transactionCategory=categorize(row[4]), transactionTitle=row[4].rstrip()))

    return records