import configparser
from datetime import date
from khanbank_transaction_downloader import BankSession
import pandas as pd
import getpass

def log(bank):
    account_number = input('Account Number: ')
    currency = input('Currency (MNT): ')
    today = date.today().strftime('%Y.%m.%d')
    begin_date = input('Begin Date ({}): '.format(today))
    end_date = input('End Date ({}): '.format(begin_date))
    save_path = input('Save Path: ')
    if currency == '':
        currency = None
    if begin_date == '':
        begin_date = None
    if end_date == '':
        end_date = None
    if save_path == '':
        save_path = None
    result = bank.get_transactions(account_number, currency, begin_date=begin_date, end_date=end_date, save_path=save_path)
    if result is not False:
        df = bank.to_dataframe()
        if df is not None:
            for index, row in df.iterrows():
                print(row['Гүйлгээний огноо'], row['Эхний үлдэгдэл'], row['Дебит гүйлгээ'], row['Кредит гүйлгээ'], row['Гүйлгээний утга'])
    else:
        print('Not logged in!')

def login(bank):
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    bank.login(username, password)

commands = {
    'log': log,
    'login': login
}

if __name__ == '__main__':
    command = ''

    config_path = input('Config Path (config.ini): ')
    if config_path == '':
        config_path = 'config.ini'
    config = configparser.ConfigParser()
    config.read(config_path)

    bank_info = config['BANK_INFO']
    client_info = config['CLIENT_INFO']

    bank = BankSession(bank_info['LOGIN_URL'],
                       bank_info['TRANSACTION_DOWNLOAD_URL'])
    

    while command != 'end':
        command = input('> ')
        if command in commands:
            commands[command](bank)
