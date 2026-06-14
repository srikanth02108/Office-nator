"""Quick verification that all components wire together correctly."""
import sys
sys.path.insert(0, ".")

from excel_actions import REGISTRY, get_steps
from brain.n8n_client import N8NClient, provider_config

print(f"Actions in library : {len(REGISTRY)}")
print(f"Active provider    : {provider_config.provider}")
print()

# Verify the previously-broken actions produce correct ribbon steps
CHECKS = {
    "wrap_text":            ("ribbon", ["w"]),
    "merge_and_center":     ("ribbon", ["m", "c"]),
    "merge_cells":          ("ribbon", ["m", "m"]),
    "unmerge_cells":        ("ribbon", ["m", "u"]),
    "autofit_column_width": ("ribbon", ["o", "i"]),
    "autofit_row_height":   ("ribbon", ["o", "a"]),
    "set_column_width":     ("ribbon", ["o", "w"]),
    "set_row_height":       ("ribbon", ["o", "h"]),
    "set_font_size":        ("ribbon", ["f", "s"]),
    "set_font":             ("ribbon", ["f", "f"]),
    "borders_all":          ("ribbon", ["b", "a"]),
    "borders_none":         ("ribbon", ["b", "n"]),
    "align_right":          ("ribbon", ["a", "r"]),
    "freeze_top_row":       ("ribbon", ["f", "r"]),
    "freeze_first_column":  ("ribbon", ["f", "c"]),
    "sort_ascending":       ("ribbon", ["s", "a"]),
    "toggle_filter":        ("hotkey", ["ctrl", "shift", "l"]),
    "bold":                 ("hotkey", ["ctrl", "b"]),
    "align_center":         ("hotkey", ["ctrl", "e"]),
    "undo":                 ("hotkey", ["ctrl", "z"]),
    "save":                 ("hotkey", ["ctrl", "s"]),
    "autosum":              ("hotkey", ["alt", "="]),
}

all_pass = True
for action_id, (exp_action, exp_keys) in CHECKS.items():
    steps = get_steps(action_id, size=14, width=20, height=20,
                      font_name="Arial", cell_ref="A1", text="test")
    # Find the matching step
    found = any(
        s["action"] == exp_action and (
            s.get("keys") == exp_keys or s.get("key") in exp_keys
        )
        for s in steps
    )
    status = "PASS" if found else "FAIL"
    if not found:
        all_pass = False
    print(f"  [{status}] {action_id}: {[s for s in steps if s['action'] == exp_action][:1]}")

print()
print("Overall:", "ALL PASS" if all_pass else "SOME FAILED")

# Show the full step count for key actions
print()
print("Step counts for common actions:")
for aid in ["set_font_size", "set_font", "set_column_width", "set_row_height",
            "format_as_header", "borders_all", "insert_row", "delete_row"]:
    steps = get_steps(aid, size=14, width=20, height=20, font_name="Arial")
    print(f"  {aid}: {len(steps)} steps")
