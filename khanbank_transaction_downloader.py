import requests
import configparser
import argparse
from html.parser import HTMLParser
from datetime import date
import pandas as pd


class BankHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if not hasattr(self, 'extracted_data'):
            self.extracted_data = {}
        if tag == 'input':
            name = ''
            value = ''
            for attr in attrs:
                if attr[0] == 'name':
                    name = attr[1]
                elif attr[0] == 'value':
                    value = attr[1]
            self.extracted_data[name] = value


class BankSession:
    def __init__(self, login_url, download_url):
        self.login_url = login_url
        self.download_url = download_url
        self.session = requests.session()
        self.content = None

    def login(self, username, password):
        try:
            r = self.session.get(self.login_url, verify=False)
            parser = BankHTMLParser()
            parser.feed(r.text)
            payload = parser.extracted_data
            payload['txtCustNo'] = username
            payload['txtPassword'] = password
            r = self.session.post(self.login_url, data=payload)
        except Exception as e:
            print('Can\'t login')
            print(e)

    def isloggedin(self):
        return '.ASPXAUTH' in self.session.cookies.keys() and '.ASPXFORMSAUTH' in self.session.cookies.keys()

    def get_transactions(self, account_number, currency=None, begin_date=None, end_date=None, save_path=None):
        if not self.isloggedin():
            return False
        if currency is None:
            currency = 'MNT'
        if end_date is None:
            end_date = date.today().strftime('%Y.%m.%d')
        if begin_date is None:
            begin_date = end_date
        r = self.session.get(self.download_url.format(
            begin_date=begin_date, end_date=end_date, account_number=currency + 'D0000000' + account_number))
        self.content = r.content
        if save_path is not None:
            with open(save_path, 'wb') as ofile:
                ofile.write(r.content)
        return self

    def to_dataframe(self):
        try:
            return pd.read_excel(self.content, header=1, skipfooter=1)
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('save_path', type=str)
    parser.add_argument('account_number', type=str)
    parser.add_argument('currency', type=str)
    parser.add_argument('-b', '--begin_date', type=str, default=None)
    parser.add_argument('-e', '--end_date', type=str, default=None)
    parser.add_argument('-c', '--config', type=str, default='config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    bank_info = config['BANK_INFO']
    client_info = config['CLIENT_INFO']

    bank = BankSession(bank_info['LOGIN_URL'],
                       bank_info['TRANSACTION_DOWNLOAD_URL'])
    bank.login(client_info['USERNAME'], client_info['PASSWORD'])
    bank.get_transactions(args.account_number, args.currency, begin_date=args.begin_date,
                          end_date=args.end_date, save_path=args.save_path)
    
    bank.to_dataframe()
