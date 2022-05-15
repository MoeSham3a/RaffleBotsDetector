import requests
import os
import pandas
import pprint
from bs4 import BeautifulSoup

# Import Google Sheet #

address_list = []
doc_link = os.environ["SHEET_ENDPOINT"]
sheety_key = os.environ["TOKEN"]
etherscan_api = os.environ["ETHER_API"]

headers = {
    "Authorization": f"Bearer {sheety_key}"
}

response = requests.get(doc_link, headers=headers)
data = response.json()

# Troubleshoot data #
pprint.pp(data)

# Fetch Sheet Name #

print(f"data key:{data.keys()} of type: {type(data.keys())}")
sheet_name = list(data.keys())[0]

# Fetch Number of Entries #
entries_number = len(data[sheet_name])

# List wallet addresses #
sheet = pandas.DataFrame(data[sheet_name])

# Troubleshoot sheet#
# pprint.pp(sheet)


# Column names assignment #

first_column_key = list(data[sheet_name][0].keys())[0]
second_column_key = list(data[sheet_name][0].keys())[1]
third_column_key = list(data[sheet_name][0].keys())[2]

# Screen Addresses #

for column in sheet:
    # Check each column
    # pprint.pp(sheet[column].values)
    for item in sheet[column].values:
        try:
            if len(item) == 42 and item.startswith("0x"):
                # Check item type
                # print(type(item))
                address_list.append(item)
        except TypeError:
            pass

# Assign HTTP Header #

http_header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0",
    "Accept-Language": "en-US,en;q=0.5"
}

# Create Base URL Components #

base_ether_url = "https://etherscan.io/token/"
base_api_url_start = "https://api.etherscan.io/api?module=account&action=tokennfttx&contractaddress="
base_api_url_finish = f"&page=1&offset=100&startblock=14575110&endblock=27025780&sort=asc&apikey={etherscan_api}"

required_token_address = input("Enter the NFT token address: ")
api_url_with_token_address = f"{base_api_url_start}{required_token_address}"

for i in range(entries_number):
    if required_token_address is not None:

        url = f"{base_ether_url}{required_token_address}?a={address_list[i]}"

        token_doc = requests.get(url, headers=http_header)

        token_soup = BeautifulSoup(token_doc.text, 'html.parser')

        # troubleshoot token_soup (fetched html)
        # pprint.pp(token_soup)

        # Fetch Token Balance Element #

        balance_element = token_soup.select("#ContentPlaceHolder1_divFilteredHolderBalance")

        # Troubleshoot token balance #
        # print(balance[0]) print(f"element type is {type(balance_element[0])} then {balance_element[0].contents} has
        # type {type(balance_element[0].contents)}") print(f"{balance_element[0].contents[-1]} has type of {type({
        # balance_element[0].contents[-1]})}")

        # Select Balance element and string cast #

        nft_balance = str(balance_element[0].contents[-1])
        print(type(nft_balance))

        # First Scenario: No token found (Check balance) ->
        # last 2 transactions in and out addresses same vault AND previous transactions include vault = human
        #  Not == Bot

        # First number is on the second character #

        if nft_balance[1] == '0':
            print("Scenario 1: Check if vault to wallet or bot")

            token_trx = requests.get(f"{api_url_with_token_address}&address={address_list[i]}{base_api_url_finish}")
            # pprint.pp(token_trx.json())
            token_trx_data = token_trx.json()
            outgoing_token_id = token_trx_data['result'][-1]['tokenID']
            incoming_token_id = token_trx_data['result'][-2]['tokenID']
            # print(f"Incoming tokenID = {incoming_token_id} \nOutgoing tokenID = {outgoing_token_id}")
            outgoing_address = token_trx_data['result'][-1]['to']
            incoming_address = token_trx_data['result'][-2]['from']
            print(f"Token {incoming_token_id} from {incoming_address} SENT TO {outgoing_address} {outgoing_token_id}")

            if incoming_address != outgoing_address and incoming_token_id == outgoing_token_id:
                print("Bot Confirmed")
                # print(f"twitter handle = {data[sheet_name][i].keys()}")

                modify = requests.put(
                    f"https://api.sheety.co/a9a78efd5ca9e2fcf4ed22e08262cfd5/cpgXMv3BotDetection/allowlist/{data[sheet_name][i]['id']}",
                    json={f"{sheet_name}": {
                        f"{first_column_key}": data[sheet_name][i][f"{first_column_key}"],
                        f"{second_column_key}": data[sheet_name][i][f"{second_column_key}"],
                        f"{third_column_key}": "XXX"
                    }}, headers=headers)
                print(f"Status code: {modify.status_code}\nContent: {modify.content}\nText: {modify.text}")
            elif incoming_address != outgoing_address and incoming_token_id != outgoing_token_id:
                modify = requests.put(
                    f"https://api.sheety.co/a9a78efd5ca9e2fcf4ed22e08262cfd5/cpgXMv3BotDetection/allowlist/{data[sheet_name][i]['id']}",
                    json={f"{sheet_name}": {
                        f"{first_column_key}": data[sheet_name][i][f"{first_column_key}"],
                        f"{second_column_key}": data[sheet_name][i][f"{second_column_key}"],
                        f"{third_column_key}": "Double Check"
                    }}, headers=headers)
                print(f"Status code: {modify.status_code}\nContent: {modify.content}\nText: {modify.text}")

            else:
                print("Safe Address")

        # Second Scenario: Token found
        # Check if address is an outgoing one (vault) of existing candidates
        # Check if in is from a bot account

        else:
            print("Scenario 2: TOKEN FOUND\ncheck OUTGOING ADDRESS IS VAULT OR NOT")
