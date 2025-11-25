import os
import sys
import pytest

# Ensure project src is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.parse_serp import parse_serp
from scripts.parse_detail import parse_detail
from scripts.skills_detect import detect_skills


def load_fixture(name):
    path = os.path.join(ROOT, 'tests', 'fixtures', name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def test_parse_serp_basic():
    html = load_fixture('serp_sample.html')
    results = parse_serp(html, region='United States')
    assert isinstance(results, list)
    assert len(results) == 1
    job = results[0]
    assert job['job_id'] == 'test123'
    assert 'Robotics Engineer' in (job['job_title'] or '')
    assert job['company'] == 'Acme Robotics'
    assert 'San Francisco' in (job['raw_location'] or '')
    assert 'Python' in (job['summary'] or '')
    assert job['url'] is not None


def test_parse_detail_basic():
    html = load_fixture('detail_sample.html')
    desc = parse_detail(html)
    assert desc is not None
    assert 'Acme Robotics' in desc or 'Robotics Engineer' in desc
    assert 'C++' in desc or 'MATLAB' in desc or 'Gazebo' in desc


def test_skills_detection():
    text = 'We use Python, C++, ROS, OpenCV and Gazebo in our stack.'
    skills = detect_skills(text)
    # basic expected skills
    assert 'python' in skills
    assert 'c++' in skills or 'cpp' in skills
    # ros/opencv/gazebo
    assert any(s in skills for s in ('ros', 'ros2'))
    assert 'opencv' in skills or 'computer vision' in skills or 'openCV' in skills
    assert 'gazebo' in skills
