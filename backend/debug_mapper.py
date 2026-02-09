#!/usr/bin/env python3
"""Debug script to test SQL template mapping"""

import sys
sys.path.insert(0, '/Users/carlostorres/alula-inspection-ai/backend')

from nlp.sql_mapper import SQLMapper

mapper = SQLMapper()

# Simulate a parsed query for 'Total violations'
parsed = {
    'intent': 'COUNT',
    'metric': 'violations',
    'entities': {
        'neighborhood': None,
        'activity': None,
        'inspector': None,
        'status': None,
        'severity': None
    },
    'time_range': {
        'year': None,
        'month': None,
        'quarter': None
    }
}

print('Testing template scoring for COUNT + violations metric:')
print('='*60)

# Get template mapping result
template_id, template = mapper.map(parsed)
print(f'\nSelected template: {template_id}')
print(f'Template ID: {template.get("id")}')
print(f'SQL: {template.get("sql")[:200]}...')

print('\n\nTop 5 scores:')
scored = []
for tid, tmpl in mapper.templates.items():
    score = mapper._calculate_template_score(tmpl, parsed['intent'], parsed['entities'], parsed['time_range'], parsed['metric'])
    if score > 0:
        scored.append((tid, score))

scored.sort(key=lambda x: x[1], reverse=True)
for tid, score in scored[:10]:
    sql = mapper.templates[tid].get('sql', '').lower()
    has_ev = 'eventviolation' in sql
    print(f'  {tid}: score={score}, has_eventviolation={has_ev}')
