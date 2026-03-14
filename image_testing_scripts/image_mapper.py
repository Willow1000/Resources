import os
import json
import string


# ------------------------------------------------------------
# Ask user for action name
# Example:
#   superheat
#   all_superheat
# ------------------------------------------------------------
action_name = input("Enter action name: ").strip().lower()


# ------------------------------------------------------------
# Determine base folder location
# "all" actions live inside the commons directory
# ------------------------------------------------------------
if "all" in action_name:
    base_folder = os.path.join("commons", os.path.basename(action_name))
else:
    base_folder = action_name


# ------------------------------------------------------------
# Construct image directories
# ------------------------------------------------------------
action_dir = os.path.join(
    base_folder,
    "all_action_files",
    "screenshots",
    "action"
)

test_dir = os.path.join(
    base_folder,
    "all_action_files",
    "screenshots",
    "test"
)


# ------------------------------------------------------------
# Determine mapping filename
# ------------------------------------------------------------
if "commons" in base_folder:
    mapping_filename = f"all_{os.path.basename(base_folder)}.json"
else:
    mapping_filename = f"{os.path.basename(base_folder)}.json"


# ------------------------------------------------------------
# Mapping structure
# ------------------------------------------------------------
mapping = {
    "icons": {},
    "tests": {}
}


try:

    # --------------------------------------------------------
    # Validate directories exist
    # --------------------------------------------------------
    if not os.path.exists(action_dir):
        raise FileNotFoundError(f"Action directory not found: {action_dir}")

    if not os.path.exists(test_dir):
        raise FileNotFoundError(f"Test directory not found: {test_dir}")


    # --------------------------------------------------------
    # Assign letters (A,B,C...) to action images
    # --------------------------------------------------------
    letters = string.ascii_uppercase

    action_images = sorted(
        f for f in os.listdir(action_dir) if f.endswith(".png")
    )

    if len(action_images) > len(letters):
        raise ValueError("Too many action images. Maximum supported is 26.")


    for index, image in enumerate(action_images):

        mapping["icons"][letters[index]] = os.path.join(
            action_dir,
            image
        )


    # --------------------------------------------------------
    # Assign numbers (1,2,3...) to test images
    # --------------------------------------------------------
    test_images = sorted(
        f for f in os.listdir(test_dir) if f.endswith(".png")
    )

    for index, image in enumerate(test_images):

        mapping["tests"][str(index + 1)] = os.path.join(
            test_dir,
            image
        )


    # --------------------------------------------------------
    # Ensure mappings folder exists
    # --------------------------------------------------------
    mappings_folder = "mappings"

    if not os.path.exists(mappings_folder):
        os.makedirs(mappings_folder)


    mapping_path = os.path.join(mappings_folder, mapping_filename)


    # --------------------------------------------------------
    # Replace existing mapping for the same action
    # --------------------------------------------------------
    if os.path.exists(mapping_path):
        os.remove(mapping_path)


    # --------------------------------------------------------
    # Save JSON mapping
    # --------------------------------------------------------
    with open(mapping_path, "w") as file:
        json.dump(mapping, file, indent=4)


    print(f"\nMapping successfully generated:")
    print(mapping_path)


except Exception as error:

    print(f"Error while generating mapping: {error}")