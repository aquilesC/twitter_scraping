import json
import datetime

from threading import Thread
from queue import Queue
from selenium import webdriver

from scrape_functions import daterange, form_url, get_tweets


class TwitterScraper(Thread):
    def __init__(self, url_queue, info_queue):
        super().__init__()
        self.url_queue = url_queue
        self.info_queue = info_queue
        self.driver = webdriver.Firefox()

    def run(self):
        while True:
            info = self.url_queue.get()
            if info is None:
                break
            url = info['url']
            data = get_tweets(self.driver, url)
            if len(data)>0:
                self.info_queue.put(data)
            self.url_queue.task_done()

        self.driver.quit()


class SaveData(Thread):
    def __init__(self, info_queue, filename):
        super().__init__()
        self.info_queue = info_queue
        self.filename = filename

    def run(self):
        with open(self.filename, 'w') as f:
            header = "Timestamp, Id, Text, Replies, Favorite, Retweet\n"
            f.write(header)
            while True:
                if not info_queue.empty():
                    data = json.loads(self.info_queue.get())
                    if data is not None:
                        for d in data:
                            tweet_data = "{time}, {id}, {text}, {replies}, {favorite}, {retweet}\n".format(**d)
                            f.write(tweet_data)
                            f.flush()
                    self.info_queue.task_done()


if __name__ == '__main__':
    user = 'mauriciomacri'
    start = datetime.datetime(2017, 1, 1)  # year, month, day
    end = datetime.datetime(2017, 12, 31)  # year, month, day
    url_queue = Queue()
    info_queue = Queue()

    for day in daterange(start, end):
        day_str = "{}-{:02}-{:02}".format(day.year, day.month, day.day)
        url_queue.put({'day': day_str, 'url': form_url(user, day)})

    for x in range(4):
        print('Thread: {}'.format(x))
        worker = TwitterScraper(url_queue, info_queue)
        worker.daemon = True
        worker.start()

    worker_saver = SaveData(info_queue, 'mauri.csv')
    worker_saver.daemon = True
    worker_saver.start()

    url_queue.join()
    print('Finished with urls')
    info_queue.join()
    print('Finished saving')
