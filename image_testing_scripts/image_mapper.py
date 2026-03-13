import os
import json
import string

ACTION_DIR = "all_action_files/screenshots/action"
TEST_DIR = "all_action_files/screenshots/test"

mapping = {
    "icons": {},
    "tests": {}
}

# Assign letters to action images
letters = string.ascii_uppercase
action_images = sorted([f for f in os.listdir(ACTION_DIR) if f.endswith(".png")])

for i, img in enumerate(action_images):
    mapping["icons"][letters[i]] = os.path.join(ACTION_DIR, img)

# Assign numbers to test images
test_images = sorted([f for f in os.listdir(TEST_DIR) if f.endswith(".png")])

for i, img in enumerate(test_images):
    mapping["tests"][str(i+1)] = os.path.join(TEST_DIR, img)

# Save mapping
with open("image_mappings.json", "w") as f:
    json.dump(mapping, f, indent=4)

print("Mappings generated.")
