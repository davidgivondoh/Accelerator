#!/usr/bin/env python3
"""Get complete platform statistics"""

from src.scrapers.opportunity_sources import get_source_stats

stats = get_source_stats()
print('📊 COMPLETE PLATFORM STATISTICS:')
print('=' * 50)
print(f'Total Opportunity Sources: {stats["total_sources"]}')

print('\n📂 BY CATEGORY:')
for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
    print(f'  {cat}: {count} sources')

print('\n⚡ BY FREQUENCY:')
for freq, count in sorted(stats['by_frequency'].items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f'  {freq}: {count} sources')