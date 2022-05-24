# RaffleBotDetector V1.0

# Introduction:

This script filters Bot wallet addresses that are used to enter raffles by sending tokens over and over to several addresses and gain multiple entries giving them an advantage over regular users.

# Methodology and limitations:

The script fetches a formatted google sheet using Sheety API and then creates a list of the existing wallet addresses to start filtering them out.

Format should be as follows:

First Column: Wallet addresses

Second Column: Twitter handles

Third Column: Address Status

https://drive.google.com/file/d/18P8TQtFxHPfxJGnSM2SQdIw8v-iLXDO2/view?usp=sharing

The script can filter the document regardless of the column name. The order is important!!!

In order to filter the addresses, the script checks 2 things.

## First

if the address holds the required token which is identified by entering the contract address of said token when prompted to

https://drive.google.com/file/d/1_Yc1KAv0ggrPhzMkOECuHhj4Dn74y03W/view?usp=sharing

This is achieved by web scraping etherscan and fetching the token balance using Beautiful Soup

## Second

Using etherscan API, it checks the token transactions for mint, purchase or transfer.

If the script detects differing addresses and no token in the address, it will mark it as a bot.

### First Scenario: No token found
This prompts a check for vault or bot address

Usually, botted addresses are used for quick transfers so the last 2 transactions of a specified token (identified by its token ID) are in and out to different wallet addresses instead of the same one which is the case if the token is transferred from and to a vault.

That said, and in order to avoid gameifying the script, it also checks the sender's address for wash transfer in order not to mark a vault erroneously.

### Second Scenario: Token found
The script fetches all token found corresponding to the contract address entered at the beginning, then proceeds to check each token for wash transfer.

If token is acquired through mint or purchase, then it is assumed safe. Else, it checks if transfer is from a team member (whitelist address list) or proceeds with wash transfer function which checks inbound transactions and digs further to verify legitimacy of origin address


Current Success rate: 95%

##### Further filtering methods will be implemented with community feedback
### For The Cultur3
## MoeSham3a
