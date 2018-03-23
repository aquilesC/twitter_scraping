import json

from datetime import timedelta
from time import sleep
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


BASE_URL = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A'
DELAY = 1

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def form_url(user, date):
    date_start = "{}-{:02}-{:02}".format(date.year, date.month, date.day)
    date = date + timedelta(days=1)
    date_end = "{}-{:02}-{:02}".format(date.year, date.month, date.day)
    return BASE_URL+'{}%20since%3A{}%20until%3A{}include%3Aretweets&src=typd'.format(user, date_start, date_end)



def get_tweets(driver, url):
    driver.get(url)
    sleep(DELAY)
    tweets = []
    try:
        found_tweets = driver.find_elements_by_class_name('tweet')
        increment = 10

        while len(found_tweets) >= increment:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(DELAY)
            found_tweets = driver.find_elements_by_class_name('tweet')
            increment += 10

        print('{} tweets found'.format(len(found_tweets)))

        for tweet in found_tweets:
            t = {}
            try:
                t = {'id': tweet.get_attribute('data-tweet-id'),
                     'text': tweet.find_elements_by_class_name('tweet-text')[0].text,
                     'time': tweet.find_elements_by_class_name('_timestamp')[0].get_attribute('data-time')}
                replies = \
                tweet.find_elements_by_class_name('ProfileTweet-action--reply')[0].find_elements_by_class_name(
                    'ProfileTweet-actionCount')[0].get_attribute('data-tweet-stat-count')
                favorite = \
                tweet.find_elements_by_class_name('ProfileTweet-action--favorite')[0].find_elements_by_class_name(
                    'ProfileTweet-actionCount')[0].get_attribute('data-tweet-stat-count')
                retweet = \
                tweet.find_elements_by_class_name('ProfileTweet-action--retweet')[0].find_elements_by_class_name(
                    'ProfileTweet-actionCount')[0].get_attribute('data-tweet-stat-count')

                t['replies'] = replies
                t['favorite'] = favorite
                t['retweet'] = retweet

            except StaleElementReferenceException as e:
                print('lost element reference', tweet)
            tweets.append(t)
        return json.dumps(tweets)

    except NoSuchElementException:
        print('No tweets on this day')