# Indeed Robotics & Automation Job Scraper

This project scrapes Indeed for engineering roles (robotics, automation, control systems, electronics, embedded, mechatronics, computer vision) and extracts job metadata and keyword/skill occurrences.

Quick start

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure `config/config.yaml` (UA list, delays, pages, etc.).

3. Run the scraper (example):

```bash
python3 scripts/scrape_indeed.py --pages 2
```

Output

- CSV files are saved to `data/indeed_jobs_*.csv` with columns including `horizontal`, `region`, `job_title`, `company`, `raw_location`, `summary`, `description`, `skills_found`.

CI / tests

This repository includes a GitHub Actions workflow that runs unit tests on pushes and pull requests. Once pushed to GitHub you will see CI results in the Actions tab.

To show the status in `README` (example badge):

![CI status](https://github.com/devaanshG/job-analyser/actions/workflows/ci.yml/badge.svg)

Notes & safety

- Check `robots.txt` and Indeed Terms of Service for the domain(s) you target before running high-volume scraping.
- Default config uses conservative pacing; increase limits only if you have permission or use proxies/partner APIs.

