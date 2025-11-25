from bs4 import BeautifulSoup


def parse_detail(html):
    """Extract full job description text from a job detail page HTML.
    """
    if not html:
        return None
    soup = BeautifulSoup(html, 'lxml')
    desc = None
    # Common selector
    tag = soup.select_one('#jobDescriptionText') or soup.select_one('div.jobsearch-JobComponent-description')
    if tag:
        desc = tag.get_text(separator='\n', strip=True)
    else:
        # Fallback: find large div with many p/li children
        candidates = soup.find_all('div')
        longest = ''
        for c in candidates:
            text = c.get_text(separator='\n', strip=True)
            if len(text) > len(longest):
                longest = text
        desc = longest if longest else None
    return desc
