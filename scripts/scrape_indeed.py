#!/usr/bin/env python3
import argparse
import os
import yaml
import logging
from datetime import datetime
import pandas as pd
from tqdm import tqdm

from fetch_page import Fetcher
from parse_serp import parse_serp
from parse_detail import parse_detail
from skills_detect import detect_skills

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def load_config(path='config/config.yaml'):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_search_url(domain, keywords, location, start):
    # Basic indeed search URL builder
    # keywords should be URL-encoded by requests via params
    return f"{domain}/jobs"


def main(args):
    cfg = load_config(args.config)
    output_dir = cfg.get('output_dir', 'data')
    os.makedirs(output_dir, exist_ok=True)

    user_agents = cfg.get('user_agents')
    delay_min = cfg.get('delay_min', 2.0)
    delay_max = cfg.get('delay_max', 6.0)
    pages = args.pages or cfg.get('pages', 10)
    fetch_details = cfg.get('fetch_details', False)
    max_jobs = cfg.get('max_jobs_per_pair', 200)

    fetcher = Fetcher(user_agents=user_agents, delay_min=delay_min, delay_max=delay_max)

    horizontals = args.horizontals or cfg['horizontals']
    regions = args.regions or cfg['regions']

    rows = []
    for horizontal in horizontals:
        for region in regions:
            logger.info('Scraping horizontal=%s region=%s', horizontal, region)
            # choose domain per region
            domain_map = {
                'United States': 'https://www.indeed.com',
                'United Kingdom': 'https://www.indeed.co.uk',
                'Germany': 'https://de.indeed.com',
                'Australia': 'https://au.indeed.com',
                'New Zealand': 'https://www.indeed.co.nz',
            }
            domain = domain_map.get(region, 'https://www.indeed.com')

            seen_ids = set()
            count = 0
            for page in range(pages):
                start = page * 10
                search_url = f"{domain}/jobs"
                params = {'q': horizontal, 'l': region, 'start': start}
                try:
                    html = fetcher.fetch(search_url, params=params)
                except Exception as e:
                    logger.error('Failed to fetch SERP for %s/%s page %d: %s', horizontal, region, page, e)
                    break
                cards = parse_serp(html, region=region)
                if not cards:
                    logger.info('No cards parsed for page %d — stopping pagination', page)
                    break
                for job in cards:
                    if job['job_id'] in seen_ids:
                        continue
                    seen_ids.add(job['job_id'])
                    # optionally fetch detail
                    description = None
                    if fetch_details and job.get('url'):
                        try:
                            detail_html = fetcher.fetch(job['url'])
                            description = parse_detail(detail_html)
                        except Exception as e:
                            logger.warning('Detail fetch failed for %s: %s', job.get('url'), e)
                    summary = job.get('summary')
                    text_for_skills = ' '.join(filter(None, [job.get('job_title',''), summary or '', description or '']))
                    skills = detect_skills(text_for_skills)
                    rows.append({
                        'horizontal': horizontal,
                        'region': region,
                        'job_id': job.get('job_id'),
                        'job_title': job.get('job_title'),
                        'company': job.get('company'),
                        'raw_location': job.get('raw_location'),
                        'summary': summary,
                        'description': description,
                        'skills_found': ';'.join(skills),
                        'url': job.get('url'),
                        'scrape_date': datetime.utcnow().isoformat(),
                    })
                    count += 1
                    if count >= max_jobs:
                        logger.info('Reached max_jobs_per_pair=%d for %s/%s', max_jobs, horizontal, region)
                        break
                if count >= max_jobs:
                    break
            # end pages
    df = pd.DataFrame(rows)
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_path = os.path.join(output_dir, f'indeed_jobs_{timestamp}.csv')
    df.to_csv(out_path, index=False)
    logger.info('Saved %d jobs to %s', len(df), out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape Indeed for engineering roles')
    parser.add_argument('--config', default='config/config.yaml')
    parser.add_argument('--horizontals', nargs='+', help='Horizontals to scrape')
    parser.add_argument('--regions', nargs='+', help='Regions to scrape')
    parser.add_argument('--pages', type=int, help='Pages per horizontal-region')
    args = parser.parse_args()
    main(args)