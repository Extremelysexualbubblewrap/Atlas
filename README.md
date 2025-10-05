# Twitter Giveaway Bot

This is a Python bot that automatically enters Twitter giveaways. It searches for tweets with specific keywords, retweets them, and performs other actions like liking, following, and sending DMs to enter the giveaways.

## Features

-   Searches for giveaways using customizable keywords.
-   Automatically retweets, likes, follows, and sends DMs.
-   Configurable rate limits to avoid getting banned.
-   Easy to set up and run.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/twitter-giveaway-bot.git
    cd twitter-giveaway-bot
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create a Twitter App:**

    -   Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) and create a new project and a new app.
    -   Make sure to give the app "Read and Write" permissions.
    -   Generate your API key, API secret key, access token, access token secret, and bearer token.

2.  **Edit `config.py`:**

    -   Open the `config.py` file and replace the placeholder values with your Twitter API credentials.
    -   You can also customize the `search_tags`, `action_tags`, and bot settings in this file.

## Usage

To run the bot, simply execute the following command:

```bash
python bot.py
```

The bot will then start searching for giveaways and entering them based on your configuration.

## Disclaimer

This bot is for educational purposes only. Using bots to enter giveaways may be against the terms of service of Twitter or the giveaway organizers. Use it at your own risk. The developer is not responsible for any consequences of using this bot.