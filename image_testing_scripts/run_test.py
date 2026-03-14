import os
import sys
import json
import platform
import subprocess


# ------------------------------------------------------------
# Resolve tooling location from environment variable
# ------------------------------------------------------------
project_path = os.environ.get("path_containing_LocallyAvailableTooling")

if not project_path:
    print("Error: path_containing_LocallyAvailableTooling not set.")
    sys.exit(1)

tooling_path = os.path.join(project_path, "LocallyAvailableActionTooling")

# Add tooling folder to Python import path
sys.path.append(tooling_path)


# ------------------------------------------------------------
# Determine correct terminal clearing command based on OS
# ------------------------------------------------------------
system_os = platform.system()

if system_os.lower() == "windows":
    clearing_screen_command = ["cls"]
else:
    clearing_screen_command = ["clear"]


# ------------------------------------------------------------
# Import image comparison function from tooling package
# ------------------------------------------------------------
from compare_specific_image_list_to_other_base_image import compare_icon_to_image_list


# ------------------------------------------------------------
# Parse test input string
# Example input:
#   "13:V 14:A,B"
#
# Output structure:
#   {
#       "13": {"base": "...", "icons": [...]}
#   }
# ------------------------------------------------------------
def parse_test_string(command_str, mapping):

    tests = {}

    for chunk in command_str.split():

        if ":" not in chunk:
            continue

        test_id, icons_str = chunk.split(":", 1)

        icons = [mapping["icons"][x] for x in icons_str.split(",")]

        base_image = mapping["tests"].get(test_id)

        if not base_image:
            print(f"Warning: test ID {test_id} not found in mapping")
            continue

        tests[test_id] = {
            "base": base_image,
            "icons": icons
        }

    return tests


# ------------------------------------------------------------
# Execute comparison tests
# ------------------------------------------------------------
def run_tests(tests_dict):

    for test_id, data in tests_dict.items():

        base_image = data["base"]
        icons = data["icons"]

        test_pass = True

        for icon in icons:

            _, result = compare_icon_to_image_list(icon, [base_image])

            if not result:
                test_pass = False

        status = "PASS" if test_pass else "FAIL"

        print(
            f"Test {test_id}: Base image '{base_image}' with icons {icons} → {status}"
        )


# ------------------------------------------------------------
# Main interactive loop
# ------------------------------------------------------------
while True:

    action = input(
        "\nEnter action name (or type 'clear' / 'exit'): "
    ).strip().lower()

    # Exit runner
    if action == "exit":
        print("Exiting runner.")
        break

    # Clear terminal
    if action == "clear":
        subprocess.run(clearing_screen_command, shell=True)
        continue


    # --------------------------------------------------------
    # Determine mapping file name
    # --------------------------------------------------------
    if "all" in action:
        action_file = f"all_{os.path.basename(action)}.json"
    else:
        action_file = f"{action}.json"

    mapping_path = f"mappings/{action_file}"


    # --------------------------------------------------------
    # Validate mapping exists
    # --------------------------------------------------------
    if not os.path.exists(mapping_path):
        print(f"Mapping for '{action}' not found. Generate it first.")
        continue


    # --------------------------------------------------------
    # Load mapping and start test loop
    # --------------------------------------------------------
    try:

        with open(mapping_path) as f:
            mapping = json.load(f)

        while True:

            tests_input = input(
                "Enter tests (example: 13:V 14:A,B) or type 'back': "
            ).strip()

            if tests_input.lower() == "exit":
                print("Exiting runner.")
                sys.exit(0)

            if tests_input.lower() == "back":
                break

            test_dict = parse_test_string(tests_input, mapping)

            run_tests(test_dict)

    except Exception as e:
        print(f"An error occurred: {e}")