"""Test one command end-to-end through LLM → action library."""
import sys, json
sys.path.insert(0, ".")
from brain.n8n_client import N8NClient

client = N8NClient()

test_cases = [
    "bold karo",
    "font size 16 set karo",
    "text ko wrap karo",
]

for cmd in test_cases:
    print(f"\n>>> {cmd}")
    result = client.send_command(cmd)
    print(f"    Plan    : {result['plan']}")
    print(f"    Actions : {result.get('action_ids', [])}")
    print(f"    Steps   : {len(result['steps'])}")
    print(f"    Confirm : {result['requires_confirmation']}")
    if result['steps']:
        print(f"    First   : {result['steps'][0]}")
    import time; time.sleep(3)
