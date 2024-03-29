
# Nyan Quests Bot

## 🔗 Links

🔔 CHANNEL: https://t.me/JamBitPY

💬 CHAT: https://t.me/JamBitChat

💰 DONATION EVM ADDRESS: 0x08e3fdbb830ee591c0533C5E58f937D312b07198

## ⚙️ Configuration (config > settings.yaml)

`` referral_code - the account for which you want to spin referrals``

``timeout_between_quests - delay between quests in seconds``

``threads - number of accounts that will work simultaneously``

``ignored_quests_categories - categories of quests that need to be ignored (by standard, all quests that require the purchase of NFTs or the creation of videos/posts are ignored) ``


## ⚙️ Accounts format (config > accounts.txt)

- twitter_auth_token|wallet_mnemonic|proxy
- twitter_auth_token|wallet_mnemonic
- twitter_auth_token|proxy
- twitter_auth_token

`` Proxy format: IP:PORT:USER:PASS``


## 🚀 Installation
`` Required python >= 3.10``

``1. Create a folder and open CMD (console) inside it``

``2. Install requirements: pip install -r requirements.txt``

``3. Setup configuration and accounts``

``4. Run: python run.py``

OR

`` 1. Open: install.cmd``

`` 2. Setup configuration and accounts``

`` 3. Open: start.cmd``


## Results (config > success_accounts.txt/failed_accounts.txt)

`` After the script is completed, all accounts will be exported to the corresponding TXT files in the format auth_token:mnemonic ``





