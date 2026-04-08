"""
Rule-based classifier for IT tickets.
Swap the classify() function with an OpenAI call later.
"""

RULES = [
    {
        'keywords': ['password', 'reset', 'forgot', 'locked out', 'cant login', "can't login"],
        'category': 'password',
        'priority': 'medium',
        'level': 'associate',
        'sla_hours': 4,
    },
    {
        'keywords': ['printer', 'print', 'scanner', 'scanning'],
        'category': 'printer',
        'priority': 'low',
        'level': 'associate',
        'sla_hours': 8,
    },
    {
        'keywords': ['internet', 'wifi', 'wi-fi', 'network', 'vpn', 'connection', 'slow connection', 'no internet'],
        'category': 'network',
        'priority': 'high',
        'level': 'consultant',
        'sla_hours': 4,
    },
    {
        'keywords': ['email', 'outlook', 'mail', 'inbox', 'calendar'],
        'category': 'email',
        'priority': 'medium',
        'level': 'consultant',
        'sla_hours': 8,
    },
    {
        'keywords': ['access', 'permission', 'share', 'folder', 'drive', 'unauthorized'],
        'category': 'access',
        'priority': 'medium',
        'level': 'consultant',
        'sla_hours': 8,
    },
    {
        'keywords': ['laptop', 'computer', 'pc', 'screen', 'monitor', 'keyboard', 'mouse', 'hardware', 'broken', 'not turning on'],
        'category': 'hardware',
        'priority': 'high',
        'level': 'consultant',
        'sla_hours': 8,
    },
    {
        'keywords': ['install', 'software', 'application', 'app', 'update', 'crash', 'error', 'not working'],
        'category': 'software',
        'priority': 'medium',
        'level': 'associate',
        'sla_hours': 24,
    },
    {
        'keywords': ['new staff', 'onboarding', 'new employee', 'new hire', 'joining'],
        'category': 'onboarding',
        'priority': 'high',
        'level': 'senior',
        'sla_hours': 24,
    },
    {
        'keywords': ['server', 'database', 'system down', 'outage', 'breach', 'security', 'hacked'],
        'category': 'network',
        'priority': 'critical',
        'level': 'manager',
        'sla_hours': 1,
    },
]

DEFAULT = {
    'category': 'other',
    'priority': 'medium',
    'level': 'associate',
    'sla_hours': 24,
}


def classify(title: str, body: str) -> dict:
    """
    Classify a ticket based on title and body text.
    Returns dict with category, priority, level, sla_hours.
    """
    text = (title + ' ' + body).lower()

    for rule in RULES:
        if any(kw in text for kw in rule['keywords']):
            return {
                'category': rule['category'],
                'priority': rule['priority'],
                'level': rule['level'],
                'sla_hours': rule['sla_hours'],
            }

    return DEFAULT.copy()
