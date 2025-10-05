import tweepy
import time
import config

def main():
    """
    Main function for the Twitter giveaway bot.
    """
    # Authenticate to Twitter
    client = tweepy.Client(
        bearer_token=config.bearer_token,
        consumer_key=config.api_key,
        consumer_secret=config.api_secret_key,
        access_token=config.access_token,
        access_token_secret=config.access_token_secret
    )

    print("Bot started!")

    while True:
        try:
            # Search for giveaway tweets
            query = " OR ".join(config.search_tags) + " -is:retweet"
            tweets = client.search_recent_tweets(query=query, max_results=100, tweet_fields=["text"])

            if tweets.data:
                for tweet in tweets.data:
                    tweet_text = tweet.text.lower()

                    # Check for retweet requirement
                    if any(tag in tweet_text for tag in config.retweet_tags):
                        try:
                            # Retweet
                            client.retweet(tweet.id)
                            print(f"Retweeted: {tweet.text}")

                            # Check for other actions
                            if any(tag in tweet_text for tag in config.like_tags):
                                client.like(tweet.id)
                                print(f"Liked: {tweet.text}")

                            # Check for follow requirement
                            if any(tag in tweet_text for tag in config.follow_tags):
                                client.follow_user(target_user_id=tweet.author_id)
                                print(f"Followed user: {tweet.author_id}")

                            # Check for DM requirement
                            if any(tag in tweet_text for tag in config.message_tags):
                                client.send_direct_message(
                                    recipient_id=tweet.author_id,
                                    text=config.dm_message
                                )
                                print(f"Sent DM to user: {tweet.author_id}")

                            time.sleep(config.retweet_rate)

                        except tweepy.errors.Forbidden as e:
                            if "You are not allowed to create a Tweet with duplicate content" in str(e):
                                print(f"Already retweeted: {tweet.text}")
                            else:
                                print(f"Error on tweet {tweet.id}: {e}")
                        except Exception as e:
                            print(f"An error occurred: {e}")

        except Exception as e:
            print(f"An error occurred during search: {e}")

        print(f"Search finished. Sleeping for {config.search_rate} seconds.")
        time.sleep(config.search_rate)

if __name__ == "__main__":
    main()