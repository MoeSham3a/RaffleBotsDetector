import requests
import os
import pandas
import pprint
from bs4 import BeautifulSoup
from Function_testing import sheety_data

whitelist_addresses = ['0xe3dad9fd32e8cc14f65a6e5da82aca4395f223c3',
                       '0x22da8dd235b1aca9a3c1980c8a11bc24712f67c1']
print("Whitelist addresses created")

# Import Google Sheet #

address_list = []
doc_link = os.environ["SHEET_ENDPOINT"]
sheety_key = os.environ["TOKEN"]
etherscan_api = os.environ["ETHER_API"]

headers = {
    "Authorization": f"Bearer {sheety_key}"
}

# response = requests.get(doc_link, headers=headers)
# data = response.json()
data = sheety_data
# print(data)
print("Google sheet imported")
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
# print(list(data[sheet_name][0].keys()))
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
print("Addresses extracted")

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
print("Base API call created")

def Fetch_Trx_Type(hash: str):
    trx_doc = requests.get(f"{base_trx_url}{hash}", headers=http_header)
    trx_soup = BeautifulSoup(trx_doc.text, 'html.parser')
    # pprint.pp(trx_soup)
    trx_element = trx_soup.select("#wrapperContent")
    trx_type = trx_element[0].contents[0].find_all('span')[1].text.split()[0].lower()
    return trx_type


def modify_sheet(status_message: str, **tokens):
    print(f"Status message: {status_message}")
    print(f"Tokens dict: {tokens}")
    # print(f"Tokens passed type is: {type(tokens)}")
    base_dictionary = {
        f"{first_column_key}": data[sheet_name][i][f"{first_column_key}"],
        f"{second_column_key}": data[sheet_name][i][f"{second_column_key}"]
    }
    if tokens == {}:
        print("No tokens passed")
        base_dictionary[f"{third_column_key}"] = f"{status_message}"
        pprint.pp(f"New Dict: {base_dictionary}")
        modify = requests.put(
            f"{doc_link}{data[sheet_name][i]['id']}",
            json={f"{sheet_name}": base_dictionary}, headers=headers)
        print(f"Status code: {modify.status_code}\nContent: {modify.content}\nText: {modify.text}")
    elif tokens:
        print(f"Tokens in elif reached")
        count = 2
        for t in tokens:
            base_dictionary[list(data[sheet_name][0].keys())[count]] = f"{t} is {tokens[t]}"
            pprint.pp(base_dictionary)
            count += 1
        modify = requests.put(
            f"{doc_link}{data[sheet_name][i]['id']}",
            json={f"{sheet_name}": base_dictionary}, headers=headers)
        print(f"Status code: {modify.status_code}\nContent: {modify.content}\nText: {modify.text}")



def wash_transfer_check(origin_address: str, last_tokenID: str, *existing_token):
    print("Wash transfer Function initiated")
    # print(f"Existing tokens are: {existing_token} of type: {type(existing_token)}")
    # print(f"Type of existing token is: {type(existing_token)}")
    # print(f"{api_url_with_token_address}&address={origin_address}{base_api_url_finish}")
    origin_address_trxs = requests.get(
        f"{api_url_with_token_address}&address={origin_address}{base_api_url_finish}").json()
    # check json data #
    # pprint.pp(f"Wash Transfer: {origin_address_trxs}")
    entry_token_trx_list = []
    for t in origin_address_trxs['result']:
        if t['tokenID'] == last_tokenID:
            entry_token_trx_list.append(t)
    # Check entries logged #
    # pprint.pp(f"Wash transfer: full entry token trx list{entry_token_trx_list}")
    if len(entry_token_trx_list) <= 2:
        print(f"Transaction list is less than 2\n")
        # pprint.pp(f"Wash transfer: Entry Token trx list 1: {entry_token_trx_list[0]}")
        # print(Fetch_Trx_Type(entry_token_trx_list[0]['hash']))
        if Fetch_Trx_Type(entry_token_trx_list[0]['hash']) == "sale:" or Fetch_Trx_Type(
                entry_token_trx_list[0]['hash']) == 'mint' or Fetch_Trx_Type(entry_token_trx_list[0]['hash']) == 'bid':
            if existing_token == ():
                modify_sheet("SAFE: origin Purchased or Minted")
            elif existing_token:
                print("Existing token: purchase or mint")
                result = "SAFE: origin Purchased or Minted"
                return result
            else:
                print("Purchase section: 3rd option??")
        elif Fetch_Trx_Type(entry_token_trx_list[0]['hash']) == "transfer":
            # print(Fetch_Trx_Type(entry_token_trx_list[0]['hash']) == "transfer")
            if existing_token == ():
                print(f"Modifying Sheet with no existing token")
                if entry_token_trx_list[0]['from'] in whitelist_addresses:
                    modify_sheet("Safe: Token transferred from team")
                else:
                    modify_sheet("90% BOT: transferred more than twice -- Check further")
            elif existing_token:
                print(f"Modifying Sheet Transfer with existing token")
                if entry_token_trx_list[0]['from'] in whitelist_addresses:
                    result = "Safe: Token transferred from team"
                    return result
                else:
                    result = "90% BOT: transferred more than twice -- Check further"
                    print(f"Result with existing token is: {result}")
                    return result
        else:
            if existing_token == ():
                modify_sheet("Double Check trx type")
                print(f"transaction type: {Fetch_Trx_Type(entry_token_trx_list[0]['hash'])} for "
                      f"hash:{entry_token_trx_list[0]['hash']}")
            elif existing_token:
                result = "Double Check trx type"
                print(f"transaction type: {Fetch_Trx_Type(entry_token_trx_list[0]['hash'])} for "
                      f"hash:{entry_token_trx_list[0]['hash']}")
                return result
    elif len(entry_token_trx_list) > 2:
        print(f"TRX List greater than 2\n")
        from_addresses = []
        for address in entry_token_trx_list:
            if Fetch_Trx_Type(address['hash']) == 'transfer':
                if address['from'] not in from_addresses:
                    from_addresses.append(address['from'])
        print(f"From addresses with length = {len(from_addresses)}\n{from_addresses}")
        if len(from_addresses) == 2:
            if existing_token == ():
                modify_sheet("Mostly Safe: In and out of Vault")
            elif existing_token:
                result = "Mostly Safe: In and out of Vault"
                return result
        elif len(from_addresses) >= 2:
            if existing_token == ():
                modify_sheet("100% BOT: Same token sent multiple times to different addresses")
            elif existing_token:
                print("Existing token: Bot transfer multiple times")
                result = "100% BOT: Same token sent multiple times to different addresses"
                return result


def existing_token_check(tokens_list: list):
    print(f"Existing tokens are: {tokens_list}")
    token_message_dict = {}
    for t in tokens_list:
        print(f"token #{t}")
        trxs_list = []
        for tr in token_trx_data['result']:
            print(tr)
            if t == tr['tokenID']:
                trxs_list.append(tr)
        print(f"Transactions for token number {t} are: {trxs_list}")
        # last_transaction_hash = trxs_list[-1]['hash']
        # last_tokenID_used = trxs_list[-1]['tokenID']
        last_transaction_hash = trxs_list[-1]['hash']
        if Fetch_Trx_Type(last_transaction_hash) == "sale:" or Fetch_Trx_Type(
                last_transaction_hash) == "mint" or Fetch_Trx_Type(last_transaction_hash) == "bid":
            token_message_dict[t] = "SAFE: Purchased or Minted"
            print(token_message_dict)
            # modify_sheet("SAFE: Purchased or Minted")
        elif Fetch_Trx_Type(last_transaction_hash) == "transfer":
            # Check first couple of trx if mints #
            counters = 0
            for trx in trxs_list:
                if trx['from'] == '0x0000000000000000000000000000000000000000':
                    token_message_dict[t] = "Safe: Minted and transferred from vault"
                    print(token_message_dict)
                    # modify_sheet("Safe: Minted and transferred from vault")
                else:
                    counters += 1
            if counters == len(trxs_list):
                print("No mint detected")
                if type(wash_transfer_check(trxs_list[-1]['from'], t, t)) == str:
                    token_message_dict[list(data[sheet_name][0].keys())[2]] = wash_transfer_check(trxs_list[-1]['from'], t, t)
                # print(f"Wash transfer for {t} has type:{type(wash_transfer_check(trxs_list[-1]['from'], t, t))}")
                # print(trxs_list[-1]['from'])
                # print(t)
                # print(wash_transfer_check(trxs_list[-1]['from'], t, t))

        else:
            token_message_dict[t] = f"Double Check transaction type:{Fetch_Trx_Type(last_transaction_hash)} for hash:{last_transaction_hash}"
            print(token_message_dict)
            # modify_sheet(
            #     f"Double Check transaction type:{Fetch_Trx_Type(last_transaction_hash)} for hash:{last_transaction_hash}")
    pprint.pp(token_message_dict)
    modify_sheet("E", **token_message_dict)


# for i in range(entries_number):
for i in range(98, 100):
    if required_token_address is not None:

        url = f"{base_ether_url}{required_token_address}?a={address_list[i]}"

        token_doc = requests.get(url, headers=http_header)

        token_soup = BeautifulSoup(token_doc.text, 'html.parser')
        print("Soup created")
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
        print(f"NFT Balance: {nft_balance[1]}")
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
            total_addresses = []

            if Fetch_Trx_Type(last_token_hash) == "transfer":
                print("Transfer detected: 0 Balance")
                # Check incoming token trx
                for trx in token_trx_data['result']:
                    # pprint.pp(f"{trx}\n{last_tokenID_used}\n{token_trx_data['result'][0]}")
                    if trx['tokenID'] == last_tokenID_used and token_trx_data['result'][0]['from'] == '0x0000000000000000000000000000000000000000':
                        modify_sheet("Safe: Minted and transferred")
                    elif trx['tokenID'] == last_tokenID_used and trx['to'] == token_trx_data['result'][-1]["from"]:
                        trx_hash = trx['hash']
                        Fetch_Trx_Type(trx_hash)
                        print(f"Transaction fetched is: {Fetch_Trx_Type(trx_hash)}")
                        if Fetch_Trx_Type(trx_hash) == "sale:" or Fetch_Trx_Type(trx_hash) == 'mint' or Fetch_Trx_Type(
                                trx_hash) == 'bid':
                            modify_sheet("SAFE: Purchased or minted")
                        elif Fetch_Trx_Type(trx_hash) == 'transfer':
                            # Check for wash transfer from originating address #
                            # modify_sheet("Check origin address for wash transfer")
                            wash_transfer_check(trx['from'], last_tokenID_used)
                        else:
                            modify_sheet("DOUBLE CHECK incoming trx")
                            print(f"Hash={trx_hash} with type: {Fetch_Trx_Type(trx_hash)}")

            elif Fetch_Trx_Type(last_token_hash) == "sale:" or Fetch_Trx_Type(
                    last_token_hash) == 'mint' or Fetch_Trx_Type(last_token_hash) == 'bid':
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
            existing_tokens = []

            # fetch last token action #
            # Better fetch existing token #
            for transaction in token_trx_data['result']:
                if transaction['to'] == address_list[i]:
                    existing_tokens.append(transaction['tokenID'])
                elif transaction['from'] == address_list[i]:
                    existing_tokens.remove(transaction['tokenID'])
                else:
                    print(f"Token #:{transaction['tokenID']} is not in list:{existing_tokens}")
            existing_token_check(existing_tokens)
