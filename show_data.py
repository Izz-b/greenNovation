import requests
import json

BASE = 'http://127.0.0.1:8001'

try:
    print('\n' + '='*70)
    print('CURRENT DATA STORAGE'.center(70))
    print('='*70)

    resp = requests.get(f'{BASE}/api/readiness/history?days=30')
    readiness = resp.json()

    print(f'\n📝 WELL-BEING CHECK-INS: {len(readiness["data"])} entries')
    if readiness["data"]:
        for checkin in readiness['data']:
            print(f'  • {checkin["date"]} → Sleep: {checkin["sleep"]:5} | Focus: {checkin["focus"]:6} | Mood: {checkin["mood"]:7}')
            print(f'    Journal: {checkin["journal"]}')

        summary = readiness['week_summary']
        print(f'\n  Weekly Summary:')
        print(f'    Mood: Happy {summary["happy_pct"]}% | Neutral {summary["neutral_pct"]}% | Sad {summary["sad_pct"]}%')
        print(f'    Avg Sleep: {summary["avg_sleep"]} | Avg Focus: {summary["avg_focus"]}')

    forest = requests.get(f'{BASE}/api/forest/forest').json()
    inventory = requests.get(f'{BASE}/api/forest/inventory').json()
    stats = requests.get(f'{BASE}/api/forest/stats').json()

    print(f'\n🌳 ECO FOREST:')
    print(f'  Planted Trees: {forest["total_trees"]}')
    print(f'  Current Streak: {forest["streak_days"]} days 🔥')
    print(f'  Available Inventory: {inventory["available"]} trees 🌱')
    print(f'  Total Earned: {inventory["total_earned"]} trees')
    print(f'  Last Reward: {inventory["last_reward"]}')

    if forest["trees"]:
        print(f'\n  Tree Locations ({len(forest["trees"])} trees):')
        for i, tree in enumerate(forest['trees'], 1):
            pos = f'({tree["x"]}%, {tree["y"]}%)'
            planted = tree["planted_at"][:10]
            print(f'    {i:2}. {tree["kind"].upper():10} at {pos:20} scale: {tree["scale"]:3} | planted: {planted}')

    print(f'\n📊 GLOBAL STATS:')
    print(f'  Total Users: {stats["total_users"]}')
    print(f'  Total Trees Planted: {stats["total_trees_planted"]}')
    print(f'  CO2 Saved: {stats.get("co2_saved_kg", "N/A")} kg')

    print('\n' + '='*70 + '\n')

except Exception as e:
    print(f'\n❌ Error: {str(e)}\n')
    import traceback
    traceback.print_exc()

