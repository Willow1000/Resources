import os
import sys
import json
import argparse

# --- Argument parsing ---
parser = argparse.ArgumentParser(description='Run multiple image comparison tests in one command.')
parser.add_argument('tests', help='String like "13:V 14:A,B 15:C" representing test IDs and icons')
args = parser.parse_args()

# --- Get environment variable ---
project_path = os.environ.get("path_containing_LocallyAvailableTooling")
if not project_path:
    print("Error: path_containing_LocallyAvailableTooling not set (export the variable)")
    sys.exit(1)

tooling_path = os.path.join(project_path, "LocallyAvailableActionTooling")
sys.path.append(tooling_path)

# --- Import your existing comparison function ---
from compare_specific_image_list_to_other_base_image import compare_icon_to_image_list

# --- Load JSON mappings ---
with open("image_mappings.json") as f:
    mapping = json.load(f)

# --- Helper: parse multi-test string ---
def parse_test_string(command_str):
    tests = {}
    for chunk in command_str.split():
        if ':' in chunk:
            test_id, icons_str = chunk.split(':', 1)
            icons = [mapping["icons"][x] for x in icons_str.split(',')]
            base_image = mapping["tests"].get(test_id)
            if not base_image:
                print(f"Warning: test ID {test_id} not found in JSON mappings")
                continue
            tests[test_id] = {"base": base_image, "icons": icons}
    return tests

# --- Run tests with concise output ---
def run_tests(tests_dict):
    summary = {}
    for test_id, data in tests_dict.items():
        base_image = data["base"]
        icons = data["icons"]
        test_pass = True
        for icon in icons:
            _, result = compare_icon_to_image_list(icon, [base_image])
            if not result:
                test_pass = False
        summary[test_id] = test_pass
        status = "PASS" if test_pass else "FAIL"
        print(f"Test {test_id}: Base image '{base_image}' with icons {icons} → {status}")
    return summary

# --- Main execution ---
test_dict = parse_test_string(args.tests)
run_tests(test_dict)