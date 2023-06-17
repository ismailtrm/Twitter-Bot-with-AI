import tweepy
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TwitterBot:
    def __init__(self, bearer_token, api_key, api_secret, access_token, access_token_secret, openai_key):
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
        self.auth = tweepy.OAuth1UserHandler(consumer_key=self.api_key,
                                             consumer_secret=self.api_secret,
                                             access_token=self.access_token,
                                             access_token_secret=self.access_token_secret)
        self.api = tweepy.API(self.auth)

    def setup_selenium(self):
        service = Service("C:\Program Files (x86)\chromedriver.exe")
        self.driver = webdriver.Chrome(service=service)


    def retrieve_trending_topics(self):
        try:
            self.driver.get("https://twitter.com/i/trends")
            wait = WebDriverWait(self.driver, 10)
            trend_items = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0')))
            choices = [item.text.strip() for item in trend_items[:42]]
            trends = [choices[17], choices[20], choices[23], choices[26], choices[29]]
            return trends
        except Exception as e:
            logging.error("Failed to retrieve trending topics: %s", str(e))
            return []

    def generate_tweet(self, trend):
        prompt = f"Türkiyede şu anda Twitterda gündemde '{trend}' konusu var. Bana bununla alakalı tweet yaz."
        try:
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
            for i, trend in enumerate(trends):
                tweet = self.generate_tweet(trend)
                if tweet:
                    self.client.create_tweet(text=tweet)
                    logging.info(f"Tweet '%s' sent. Topic:'{trend}'", i+1)
        except Exception as e:
            logging.error("Failed to post tweets: %s", str(e))

    def run(self):
        logging.info("Execution has been started.")
        self.setup_twitter_api()
        logging.info("Twitter API has beed setted up.")
        self.setup_selenium()
        logging.info("Selenium has beed setted up.")
        trends = self.retrieve_trending_topics()
        logging.info("Trends has been detected.")
        self.post_tweets(trends)
        self.driver.quit()
        logging.info("Execution has been finished.")


if __name__ == "__main__":
    bearer_token = r"YOUR_BEARER_TOKEN"
    api_key = "YOUR_CONSUMER_KEY"
    api_secret = "YOUR_CONSUMER_SECRET"
    access_token = "YOUR_ACCESS_TOKEN"
    access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"
    openai_key = "YOUR_OPENAI_KEY"

    bot = TwitterBot(bearer_token, api_key, api_secret, access_token, access_token_secret, openai_key)
    bot.run()

