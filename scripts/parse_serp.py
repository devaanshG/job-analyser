from bs4 import BeautifulSoup
from urllib.parse import urljoin

DEFAULT_DOMAIN_BY_REGION = {
    'United States': 'https://www.indeed.com',
    'United Kingdom': 'https://www.indeed.co.uk',
    'Germany': 'https://de.indeed.com',
    'Australia': 'https://au.indeed.com',
    'New Zealand': 'https://www.indeed.co.nz',
}

# Robust SERP parsing: look for data-jk or article elements

def parse_serp(html, region=None, domain=None):
    """Parse Indeed SERP HTML and return list of job dicts:
    {job_id, job_title, company, raw_location, summary, url}
    """
    soup = BeautifulSoup(html, 'lxml')
    results = []

    # resolve domain from region if region given
    if region and not domain:
        domain = DEFAULT_DOMAIN_BY_REGION.get(region, 'https://www.indeed.com')
    domain = domain or 'https://www.indeed.com'

    # Try to find job containers with data-jk or job_seen_beacon
    job_cards = soup.select('article[data-jk], div.job_seen_beacon, div.jobsearch-SerpJobCard')
    if not job_cards:
        # fallback: any <a> with tapItem
        job_cards = soup.select('a.tapItem')

    for card in job_cards:
        # job id
        job_id = card.get('data-jk') or card.get('data-jobkey') or card.get('data-vjk')
        # title
        title_tag = card.select_one('h2.jobTitle') or card.select_one('a.jobtitle') or card.select_one('a.tapItem h2')
        job_title = None
        if title_tag:
            job_title = title_tag.get_text(strip=True)
        # company
        company_tag = card.select_one('span.companyName') or card.select_one('div.company') or card.select_one('span.company')
        company = company_tag.get_text(strip=True) if company_tag else None
        # location
        loc_tag = card.select_one('div.companyLocation') or card.select_one('span.companyLocation')
        raw_location = loc_tag.get_text(strip=True) if loc_tag else None
        # summary/snippet
        summary_tag = card.select_one('div.job-snippet') or card.select_one('div.summary')
        summary = summary_tag.get_text(separator=' ', strip=True) if summary_tag else None
        # url
        link_tag = card.select_one('a')
        url = None
        if link_tag and link_tag.get('href'):
            href = link_tag['href']
            url = href if href.startswith('http') else urljoin(domain, href)
        # fallback build url from job_id
        if not url and job_id:
            url = f"{domain}/viewjob?jk={job_id}"

        results.append({
            'job_id': job_id,
            'job_title': job_title,
            'company': company,
            'raw_location': raw_location,
            'summary': summary,
            'url': url
        })
    return results
