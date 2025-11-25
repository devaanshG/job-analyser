import time
import random
import logging
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

class Fetcher:
    def __init__(self, user_agents, delay_min=2.0, delay_max=6.0, max_retries=5, backoff_base=1.0, backoff_cap=60.0, proxies=None):
        self.session = requests.Session()
        self.user_agents = user_agents or ["Mozilla/5.0 (compatible; Bot/0.1)"]
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.proxies = proxies

    def _random_delay(self):
        d = random.uniform(self.delay_min, self.delay_max)
        jitter = random.uniform(-0.5, 0.5)
        sleep_time = max(0.1, d + jitter)
        logger.debug(f"Sleeping for {sleep_time:.2f}s")
        time.sleep(sleep_time)

    def fetch(self, url, headers=None, params=None, allow_redirects=True):
        headers = headers or {}
        headers.setdefault('User-Agent', random.choice(self.user_agents))
        headers.setdefault('Accept-Language', 'en-US,en;q=0.9')
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self._random_delay()
                resp = self.session.get(url, headers=headers, params=params, proxies=self.proxies, allow_redirects=allow_redirects, timeout=30)
                if resp.status_code == 200:
                    return resp.text
                elif resp.status_code in (429, 503):
                    logger.warning(f"Rate limited (status {resp.status_code}) on {url}. Backing off (attempt {attempt}).")
                    sleep = min(self.backoff_cap, self.backoff_base * (2 ** (attempt - 1))) + random.random()
                    time.sleep(sleep)
                else:
                    logger.warning(f"Unexpected status {resp.status_code} for {url}")
                    return resp.text
            except Exception as e:
                last_exc = e
                logger.exception(f"Exception fetching {url} (attempt {attempt}): {e}")
                sleep = min(self.backoff_cap, self.backoff_base * (2 ** (attempt - 1)))
                time.sleep(sleep)
        raise last_exc if last_exc is not None else RuntimeError('Failed to fetch')
