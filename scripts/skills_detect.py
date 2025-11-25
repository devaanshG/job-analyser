import re
from rapidfuzz import fuzz

# Canonical skill list with possible variants
SKILL_VARIANTS = {
    'python': [r'python\b'],
    # Use lookarounds for C++ so trailing non-word characters like + don't break \b
    'c++': [r'(?<!\w)c\+\+(?!\w)', r'\bcpp\b', r'cplusplus\b'],
    'matlab': [r'matlab\b'],
    'simulink': [r'simulink\b'],
    'ros': [r'\bros2?\b', r'\bRobot Operating System\b'],
    'gazebo': [r'gazebo\b'],
    'nvidia isaac': [r'nvidia\s+isaac\b', r'isaac\b'],
    'solidworks': [r'solidworks\b'],
    'cad': [r'\bcad\b'],
    'embedded': [r'\bembedded\b'],
    'pcb': [r'\bpcb\b'],
    'kicad': [r'kicad\b'],
    'altium': [r'altium\b'],
    'rtos': [r'\brtos\b'],
    'firmware': [r'firmware\b'],
    'plc': [r'\bplc\b'],
    'siemens': [r'siemens\b'],
    'allen-bradley': [r'allen-?bradley\b'],
    'control theory': [r'control\s+theory\b'],
    'pid': [r'\bPID\b', r'pid\b'],
    'mpc': [r'\bMPC\b', r'model\s*predictive\s*control'],
    'kalman': [r'kalman\b'],
    'state estimation': [r'state\s+estimation\b'],
    'sensor fusion': [r'sensor\s+fusion\b'],
    'computer vision': [r'computer\s+vision\b', r'\bCV\b', r'open\s*cv\b', r'opencv\b'],
    'ai': [r'\bAI\b', r'artificial\s+intelligence\b', r'machine\s+learning\b', r'deep\s+learning\b'],
    'openCV': [r'opencv\b', r'open\s*cv\b'],
    'automation': [r'automation\b'],
    'test': [r'\btest(ing)?\b'],
    'validation': [r'validation\b'],
    'integration': [r'integration\b', r'system\s+integration\b'],
    'mechatronics': [r'mechatronics\b'],
    'scada': [r'scada\b']
}

# Precompile regex map
COMPILED = {skill: [re.compile(pat, re.I) for pat in pats] for skill, pats in SKILL_VARIANTS.items()}


def detect_skills(text, use_fuzzy=False, fuzzy_threshold=90):
    """Return a list of canonical skills found in text (case-insensitive).
    If use_fuzzy is True, apply a fuzzy match fallback.
    """
    if not text:
        return []
    found = set()
    norm = text
    # Primary exact/regex matching
    for skill, patterns in COMPILED.items():
        for pat in patterns:
            if pat.search(norm):
                found.add(skill)
                break
    # Optional fuzzy matching for remaining skills
    if use_fuzzy:
        for skill in SKILL_VARIANTS.keys():
            if skill in found:
                continue
            ratio = fuzz.partial_ratio(skill.lower(), norm.lower())
            if ratio >= fuzzy_threshold:
                found.add(skill)
    return sorted(found)
