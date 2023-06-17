# Importing necessary libraries
import tweepy
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai

# Seting up the logging module
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TwitterBot:
    def __init__(self, bearer_token, api_key, api_secret, access_token, access_token_secret, openai_key):
        # Initialize the bot's credentials
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.openai_key = openai_key
        self.auth = None
        self.api = None
        self.driver = None
        self.client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

    def setup_twitter_api(self):
        # Set up the Twitter API authentication and API object
        self.auth = tweepy.OAuth1UserHandler(consumer_key=self.api_key,
                                             consumer_secret=self.api_secret,
                                             access_token=self.access_token,
                                             access_token_secret=self.access_token_secret)
        self.api = tweepy.API(self.auth)

    def setup_selenium(self):
        # Set up the Selenium webdriver using Chrome
        service = Service("C:\Program Files (x86)\chromedriver.exe")
        self.driver = webdriver.Chrome(service=service)


    def retrieve_trending_topics(self):
        try:
            # Navigate to Twitter's trending topics page using Selenium
            self.driver.get("https://twitter.com/i/trends")
            wait = WebDriverWait(self.driver, 10)
            # Find the elements containing the trending topics using CSS selector
            trend_items = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0'))) 
            # Extract the text of the trending topics
            choices = [item.text.strip() for item in trend_items[:42]] # The CSS selection is not optimized. There is a bunch of things that is under that class therefore we detect the first 10 trending topics for an experiment.
            # Choose a subset of trending topics to focus on
            trends = [choices[17], choices[20], choices[23], choices[26], choices[29]] #Top 5 trending topics.
            return trends
        except Exception as e:
            logging.error("Failed to retrieve trending topics: %s", str(e))
            return []
        
        # NOTE: The free twitter api does not allow me to pull trend topics from the api due to the access leveling that's why I had to do web scraping instead of get_place_trends()

    def generate_tweet(self, trend):
        prompt = f"Türkiyede şu anda Twitterda gündemde '{trend}' konusu var. Bana bununla alakalı tweet yaz." # In Turkey, '{trend}' is currently on the agenda on Twitter. Tweet me about it.
        try:
            # Generate a tweet using the OpenAI GPT-3 model
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                api_key=self.openai_key
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logging.error("Failed to generate tweet for trend '%s': %s", trend, str(e))
            return ""

    def post_tweets(self, trends):
        try:
            # Iterate over the trends and post tweets for each trend
            for i, trend in enumerate(trends):
                tweet = self.generate_tweet(trend)
                if tweet:
                    self.client.create_tweet(text=tweet)
                    logging.info(f"Tweet '%s' sent. Topic:'{trend}'", i+1)
        except Exception as e:
            logging.error("Failed to post tweets: %s", str(e))

    def run(self):
        logging.info("Execution has been started.")
        # Set up the Twitter API
        self.setup_twitter_api()
        logging.info("Twitter API has beed setted up.")
        # Set up Selenium
        self.setup_selenium()
        logging.info("Selenium has beed setted up.")
        # Retrieve trending topics
        trends = self.retrieve_trending_topics()
        logging.info("Trends has been detected.")
        # Post tweets
        self.post_tweets(trends)
        # Quit Selenium webdriver
        self.driver.quit()
        logging.info("Execution has been finished.")

        # NOTE: I also used selenium webdriver as a debug module

if __name__ == "__main__":
    # Twitter API credentials
    bearer_token = r"YOUR_BEARER_TOKEN"
    api_key = "YOUR_CONSUMER_KEY"
    api_secret = "YOUR_CONSUMER_SECRET"
    access_token = "YOUR_ACCESS_TOKEN"
    access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"
    # OpenAI API key
    openai_key = "YOUR_OPENAI_KEY"
    
    # Initialize the TwitterBot object
    bot = TwitterBot(bearer_token, api_key, api_secret, access_token, access_token_secret, openai_key)
    # Run the bot
    bot.run()

