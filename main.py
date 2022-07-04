# Get transactions from splitwise
from splitwise import Splitwise
import logging
import configparser
from ynab_client import YNABClient
from datetime import datetime

myConfigFilePath = "secrets/credentials.ini"

def parseConfig(configFilePath):
    config = configparser.ConfigParser()
    config.read(configFilePath)
    return config['DEFAULT']
    

logging.basicConfig(level=logging.DEBUG)

myConfig = parseConfig(myConfigFilePath)
ynabToken = myConfig["ynabToken"]
ynabAccountID = myConfig["ynabAccountID"]
splitwiseGroupId = myConfig["splitwiseGroupId"]
splitwise_user_id = int(myConfig["splitwiseUserId"])
splitwise_api_key = myConfig["splitwise_api_key"]
splitwise_consumer_key = myConfig["splitwise_consumer_key"]
splitwise_consumer_secret = myConfig["splitwise_consumer_secret"]


def getSplitwiseExpenses(from_date, splitwise_user_id):
    s = Splitwise(splitwise_consumer_key,splitwise_consumer_secret,api_key=splitwise_api_key)

    current = s.getCurrentUser()
    limit = 20
    offset = 0
    expenses = []
    while True:
        gotExpenses = s.getExpenses(group_id = splitwiseGroupId, dated_after=from_date, offset = offset, limit = limit)
        print(gotExpenses)
        if gotExpenses == None or len(gotExpenses) == 0:
            break
        offset += limit
        expenses.extend(gotExpenses)
    parsedExpenses = []
    for expense in expenses:
        expenseUsers = expense.getUsers()
        for expenseUser in expenseUsers:
            # Negative net balance is owed to Amber, positive owed to me
            if splitwise_user_id == expenseUser.getId():
                parsedExpenses.append(
                    {
                        "payee_name": expense.getDescription(),
                        "date": expense.getDate(),
                        "amount": int(float(expenseUser.getNetBalance())*1000),
                        
                    }
                )
    return parsedExpenses

# Change the format of it

# Upload to YNAB
myYNAB = YNABClient(ynabToken)

def getMostRecentYNABTransactionDate(myYNAB):
    transactions = myYNAB.listTransactionsInAccount(ynabAccountID)
    mostRecentTransaction = max(transactions, key = lambda transaction: datetime.strptime(transaction["date"], "%Y-%m-%d").date())
    return mostRecentTransaction["date"]

mostRecentTransactionDate = getMostRecentYNABTransactionDate(myYNAB)
expenses = getSplitwiseExpenses(from_date = mostRecentTransactionDate, splitwise_user_id = splitwise_user_id)
for expense in expenses:
    expense["account_id"] = ynabAccountID
    expense["cleared"] = "cleared"
myYNAB.postTransactions(expenses)