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
# pprint.pp(data)

# Fetch Sheet Name #

# print(f"data key:{data.keys()} of type: {type(data.keys())}")
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

base_trx_url = "https://etherscan.io/tx/"
base_ether_url = "https://etherscan.io/token/"
base_api_url_start = "https://api.etherscan.io/api?module=account&action=tokennfttx&contractaddress="
base_api_url_finish = f"&page=1&offset=100&startblock=14575110&endblock=27025780&sort=asc&apikey={etherscan_api}"

required_token_address = input("Enter the NFT token address: ")
api_url_with_token_address = f"{base_api_url_start}{required_token_address}"


def Fetch_Trx_Type(hash: str):
    trx_doc = requests.get(f"{base_trx_url}{hash}", headers=http_header)
    trx_soup = BeautifulSoup(trx_doc.text, 'html.parser')
    # pprint.pp(trx_soup)
    trx_element = trx_soup.select("#wrapperContent")
    trx_type = trx_element[0].contents[0].find_all('span')[1].text.split()[0].lower()
    return trx_type


def modify_sheet(status_message: str):
    modify = requests.put(
        f"{doc_link}{data[sheet_name][i]['id']}",
        json={f"{sheet_name}": {
            f"{first_column_key}": data[sheet_name][i][f"{first_column_key}"],
            f"{second_column_key}": data[sheet_name][i][f"{second_column_key}"],
            f"{third_column_key}": f"{status_message}"
        }}, headers=headers)
    print(f"Status code: {modify.status_code}\nContent: {modify.content}\nText: {modify.text}")


def wash_transfer_check(origin_address:str, last_tokenID:str):
    origin_address_trxs = requests.get(
        f"{api_url_with_token_address}&address={origin_address}{base_api_url_finish}").json()
    # check json data #
    # pprint.pp(origin_address_trxs)
    entry_token_trx_list = []
    for t in origin_address_trxs['result']:
        if t['tokenID'] == last_tokenID:
            entry_token_trx_list.append(t)
    # Check entries logged #
    # pprint.pp(entry_token_trx_list)
    if len(entry_token_trx_list) == 2:
        # print(entry_token_trx_list[0])
        if Fetch_Trx_Type(entry_token_trx_list[0]['hash']) == "sale:" or Fetch_Trx_Type(
                entry_token_trx_list[0]['hash']) == 'mint' or Fetch_Trx_Type(
                entry_token_trx_list[0]['hash']) == 'bid':
            modify_sheet("SAFE: origin Purchased or Minted")
        elif Fetch_Trx_Type(entry_token_trx_list[0]['hash']) == "transfer":
            modify_sheet("90% BOT: transferred more than twice -- Check further")
        else:
            modify_sheet("Double Check trx type")
            print(f"transaction type: {Fetch_Trx_Type(entry_token_trx_list[0]['hash'])} for "
                  f"hash:{entry_token_trx_list[0]['hash']}")
    elif len(entry_token_trx_list) > 2:
        modify_sheet("100% BOT: Same token sent multiple times to different addresses")


# for i in range(entries_number):
for i in range(10, entries_number):
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
        # print(type(nft_balance))

        # First Scenario: No token found (Check balance) ->
        # last 2 transactions in and out addresses same vault AND previous transactions include vault = human
        #  Not == Bot

        # First number is on the second character #

        if nft_balance[1] == '0':
            print("Scenario 1: No Token: Check if vault to wallet or bot")

            token_trx = requests.get(f"{api_url_with_token_address}&address={address_list[i]}{base_api_url_finish}")
            # pprint.pp(token_trx.json())
            token_trx_data = token_trx.json()
            # fetch last token action #
            last_tokenID_used = token_trx_data['result'][-1]['tokenID']
            last_token_hash = token_trx_data['result'][-1]['hash']

            if Fetch_Trx_Type(last_token_hash) == "transfer":
                # Check incoming token trx
                for trx in token_trx_data['result']:
                    if trx['tokenID'] == last_tokenID_used and trx['to'] == token_trx_data['result'][-1]["from"]:
                        trx_hash = trx['hash']
                        Fetch_Trx_Type(trx_hash)
                        print(f"Transaction fetched is: {Fetch_Trx_Type(trx_hash)}")
                        if Fetch_Trx_Type(trx_hash) == "sale:" or Fetch_Trx_Type(trx_hash) == 'mint' or Fetch_Trx_Type(trx_hash) == 'bid':
                            modify_sheet("SAFE: Purchased or minted")
                        elif Fetch_Trx_Type(trx_hash) == 'transfer':
                            # Check for wash transfer from originating address #
                            # modify_sheet("Check origin address for wash transfer")
                            wash_transfer_check(trx['from'], last_tokenID_used)
                        else:
                            modify_sheet("DOUBLE CHECK incoming trx")
                            print(f"Hash={trx_hash} with type: {Fetch_Trx_Type(trx_hash)}")
            elif Fetch_Trx_Type(last_token_hash) == "sale:" or Fetch_Trx_Type(last_token_hash) == 'mint' or Fetch_Trx_Type(last_token_hash) == 'bid':
                # Mark as safe #
                modify_sheet("SAFE: Purchased or Minted")
            else:
                modify_sheet(f"Double Check trx type")
                print(f"trx type of:{Fetch_Trx_Type(last_token_hash)} hash:{last_token_hash}")
        else:
            print("Scenario 2: TOKEN FOUND -- check Origin ADDRESS IS VAULT OR NOT")
            token_trx = requests.get(f"{api_url_with_token_address}&address={address_list[i]}{base_api_url_finish}")
            # pprint.pp(token_trx.json())
            token_trx_data = token_trx.json()

            # fetch last token action #
            last_tokenID_used = token_trx_data['result'][-1]['tokenID']
            last_token_hash = token_trx_data['result'][-1]['hash']
            if Fetch_Trx_Type(last_token_hash) == "sale:" or Fetch_Trx_Type(last_token_hash) == "mint" or Fetch_Trx_Type(last_token_hash) == "bid":
                modify_sheet("SAFE: Purchased or Minted")
            elif Fetch_Trx_Type(last_token_hash) == "transfer":
                # modify_sheet("May be Safe but Check for wash transfer")
                wash_transfer_check(token_trx_data['result'][-1]['from'], last_tokenID_used)
            else:
                modify_sheet(f"Double Check transaction type:{Fetch_Trx_Type(last_token_hash)} for hash:{last_token_hash}")
