import requests
import json
import re

class YNABClient(object):
    BASE_URL = "https://api.youneedabudget.com/v1"

    def __init__(self, token):
        self.token = token
        self.budgetID = self.getBudgetID()

    # TODO: Only gets the 0th budget available.
    # We should eventually check all budgets just in case
    def getBudgetID(self):
        url = self.BASE_URL + "/budgets"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
        }
        rawResponse = requests.get(url ,headers=headers)
        resp = json.loads(rawResponse.content.decode('utf-8'))
        return resp["data"]["budgets"][0]["id"]

    def postTransactions(self, transactions):
        if len(transactions) == 0:
            print("No transactions to patch, skipping...")
            return
        url = self.BASE_URL + f"/budgets/{self.budgetID}/transactions"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        data = json.dumps({"transactions": transactions})
        resp = requests.post(url, data, headers=headers)
        if resp.status_code != 200:
            print (f"Something went wrong, got response: {resp.content}")
        else:
            print (f"Successfully updated transactions {transactions}")

    def listTransactionsInAccount(self, accountId):
        since_date = "2022-06-01"
        url = self.BASE_URL + f"/budgets/{self.budgetID}/accounts/{accountId}/transactions?since_date={since_date}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
        }
        rawResponse = requests.get(url ,headers=headers)
        resp = json.loads(rawResponse.content.decode('utf-8'))
        if rawResponse.status_code != 200:
            return None
        return resp["data"]["transactions"]