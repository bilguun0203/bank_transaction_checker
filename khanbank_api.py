import requests
import json
import datetime
import base64
import uuid

TOKEN_URL = 'https://api.khanbank.com:9003/v1/auth/token?grant_type=password&username={}&password={}&channelId=I'
RECENT_TRANSACTIONS_URL = 'https://api.khanbank.com:9003/v1/omni/user/custom/recentTransactions?account={}'
TRANSACTIONS_URL = 'https://api.khanbank.com:9003/v1/omni/user/custom/operativeaccounts/{}/transactions?transactionValue=0&transactionDate={{\"lt\":\"{}\",\"gt\":\"{}\"}}&amount={{\"lt\":\"0\",\"gt\":\"0\"}}&amountType=&transactionCategoryId=&transactionRemarks=&customerName=ОЧИРБАТ+БИЛГҮҮН&transactionCurrency=MNT&branchCode=5041'

class KhanApi:
    def __init__(self):
        self.access_token = None

    def get_token(self, client_token, username, password):
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'device-id': str(uuid.uuid4()),
        'Accept-Language': 'mn-MN',
        'Authorization': 'Basic {}'.format(client_token)
        }
        response = requests.request("POST", TOKEN_URL.format(username, password), headers=headers)

        if response.status_code == 200:
            self.access_token = json.loads(response.text)['access_token']
            return self.access_token
        return None
    
    def get_transactions(self, account_number:str, days:int):
        if self.access_token is not None:
            now = datetime.datetime.now()
            one_day = datetime.timedelta(days=1)
            n_days = datetime.timedelta(days=days)
            begin_date = (now - n_days).strftime('%Y-%m-%dT%H:%M:%S')
            end_date = (now + one_day).strftime('%Y-%m-%dT%H:%M:%S')

            headers = {
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
            response = requests.request("GET", TRANSACTIONS_URL.format(account_number, begin_date, end_date), headers=headers)

            if response.status_code == 200:
                return json.loads(response.text)
        
        return None


if __name__ == '__main__':
    client_token = 'Vm00eHFtV1BaQks3Vm5UYjNRRXJZbjlJZkxoWmF6enI6dElJQkFsU09pVXIwclV5cA=='

    username = input('Username: ')
    password = input('Password: ')
    password = base64.b64encode(password.encode('ascii')).decode('ascii')
    
    print('Logging in...')
    khan_api = KhanApi()
    if khan_api.get_token(client_token, username, password) is not None:
        print('Logged in!')
        account_number = input('Account Number: ')
        transaction_days = int(input('How many days? '))
        print('Getting transactions...')
        transactions = khan_api.get_transactions(account_number, transaction_days)
        if transactions is not None:
            for transaction in transactions:
                print('---')
                print(transaction['transactionDate'].split('T')[0].replace('-', '.') + ' ' + transaction['txnTime'], end='\t')
                print(transaction['amount']['amount'], end='\t')
                print(transaction['amountType']['codeDescription'], end='\t')
                print(transaction['transactionRemarks'])
        else:
            print('No transactions.')
