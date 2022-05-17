# RaffleBotDetector V1.0

# Introduction:

This script filters Bot wallet addresses that are used to enter raffles by sending tokens over and over to several addresses and gain multiple entries giving them an advantage over regular users.

# Methodology and limitations:

The script fetches a formatted google sheet using Sheety API and then creates a list of the existing wallet addresses to start filtering them out.

Format should be as follows:

First Column: Wallet addresses

Second Column: Twitter handles

Third Column: Bot status

![](RackMultipart20220515-1-s264z4_html_5552a48f5d0a4034.png)

The script can filter the document regardless of the column name. The order is important!!!

In order to filter the addresses, the script checks 2 things.

## First

if the address holds the requires token which is identified by entering the contract address of said token when prompted to

![](RackMultipart20220515-1-s264z4_html_5b3f11f08a83191d.jpg)

This is achieved by web scraping etherscan and fetching the token balance using Beautiful Soup

## Second

Using etherscan API, it checks the last 2 transactions for token transfers.

limitation: unable to check if transfer is wallet transfer or purchase due to etherscan API which can cause false positives in case of a purchase.

Usually, botted addresses are used for quick transfers so the last 2 transactions of a specified token (identified by its token ID) are in and out to different wallet addresses instead of the same one which is the case if the token is transferred from and to a vault.

If the script detects differing addresses and no token in the address, it will mark it as a bot.

If the last 2 transfers have differing addresses but different token IDs, the address is marked for double checking.

Current Success rate: 78%

##### Further filtering methods will be implemented with community feedback
### For The Cultur3
## MoeSham3a
