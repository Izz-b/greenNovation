import requests
import json
from datetime import datetime, timedelta

BASE = 'http://127.0.0.1:8001'

print('\n' + '='*70)
print('REPOPULATING DATA'.center(70))
print('='*70 + '\n')

# Populate well-being check-ins (last 7 days)
check_ins_data = [
    {"date": "2026-04-13", "sleep": "great", "focus": "low", "mood": "happy", "journal": "Good sleep but had trouble focusing today."},
    {"date": "2026-04-14", "sleep": "okay", "focus": "high", "mood": "neutral", "journal": "Adequate sleep. Managed to stay very focused."},
    {"date": "2026-04-15", "sleep": "great", "focus": "high", "mood": "happy", "journal": "Great sleep and productivity! Everything clicked."},
    {"date": "2026-04-16", "sleep": "great", "focus": "medium", "mood": "happy", "journal": "Good sleep. Steady focus throughout the day."},
    {"date": "2026-04-17", "sleep": "okay", "focus": "high", "mood": "sad", "journal": "Okay sleep. Despite high focus, feeling a bit down."},
    {"date": "2026-04-18", "sleep": "bad", "focus": "low", "mood": "neutral", "journal": "Poor sleep quality. Hard to concentrate today."},
    {"date": "2026-04-19", "sleep": "okay", "focus": "medium", "mood": "neutral", "journal": "Adequate sleep. Steady focus but neutral mood."},
]

print("📝 Submitting well-being check-ins...")
for i, data in enumerate(check_ins_data, 1):
    resp = requests.post(f'{BASE}/api/readiness/checkin', json=data)
    if resp.status_code == 200:
        print(f"   ✓ Check-in {i}: {data['date']} ({data['mood']})")
    else:
        print(f"   ✗ Check-in {i} failed: {resp.status_code}")

print("\n" + '='*70)
print('DISPLAYING REPOPULATED DATA'.center(70))
print('='*70 + '\n')

# Display well-being data
resp = requests.get(f'{BASE}/api/readiness/history?days=30')
readiness = resp.json()

print(f'Well-being Check-ins: {len(readiness["data"])}')
for checkin in readiness['data']:
    print(f'  • {checkin["date"]} → Sleep: {checkin["sleep"]:5} | Focus: {checkin["focus"]:6} | Mood: {checkin["mood"]:7}')

summary = readiness['week_summary']
print(f'\nWeekly Summary:')
print(f'  Mood: Happy {summary["happy_pct"]}% | Neutral {summary["neutral_pct"]}% | Sad {summary["sad_pct"]}%')
print(f'  Avg Sleep: {summary["avg_sleep"]} | Avg Focus: {summary["avg_focus"]}')

print('\n' + '='*70 + '\n')
