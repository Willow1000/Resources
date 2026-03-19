# Action Mapping System: Technical Documentation (Advanced)

## 1. Introduction

The **Action Mapping System** is an automated framework designed to map action icons to test screenshots and orchestrate task execution within a simulated environment. This system enables the creation, validation, and execution of automated sequences by establishing a robust structure for image recognition and procedural control.

## 2. System Architecture and Data Flow

The system operates in a three-stage pipeline:

1.  **Asset Acquisition**: Recording source videos and extracting frame-perfect screenshots.
2.  **Mapping Generation**: Analyzing visual relationships and generating `mapping.json`.
3.  **Comparison Execution**: Validating icons against test environments and reporting precision.
4.  **Orchestration**: Executing the procedural logic defined in `action_explained.txt`.

### 2.1. Project Structure
```text
runescape_actions/
├── common_action_framework/
│   └── image_matching_logic.py (Core CV logic)
├── runescape_actions/
│   ├── image_mapper.py (The Generator)
│   ├── run_test.py (The Runner)
│   └── {action_name}/
│       ├── action_explained.txt (The Script)
│       ├── mapping.json (The Lookup Table)
│       └── all_action_files/
│           └── screenshots/
│               ├── action/ (Icon Assets)
│               └── test/ (Environment Assets)
```

## 3. Asset Preparation and Acquisition

For every action, you must record **two separate videos** to serve as the source for your visual assets. These videos ensure consistency and provide a high-quality pool for image extraction.

### 3.1. Video Requirements:
1.  **Icon Source Video**: This video is used to extract individual action icons. These icons will be saved in the `all_action_files/screenshots/action/` folder.
2.  **Test Source Video**: This video is used to extract full-screen test images. These images will be saved in the `all_action_files/screenshots/test/` folder.

## 4. Naming Conventions and Optimization Strategies

To achieve optimal results with minimal manual input, it is essential to follow a strict naming convention. The `image_mapper.py` script relies on these patterns to automatically pair icons with their corresponding test screenshots.

### 4.1. Core Naming Principles
- **Underscore Separation**: Always use underscores (`_`) to separate words in filenames (e.g., `iron_ore.png`, `test_iron_ore.png`).
- **Lowercase Only**: Use lowercase for all filenames to avoid case-sensitivity issues during normalization.
- **Prefix Consistency**: Test images **must** start with the `test_` prefix (e.g., `test_ore.png`).

### 4.2. Strategy for Optimal Pairing
The script uses a prioritized hierarchy for matching. By naming your files strategically, you can control how they are paired:

| Pairing Level | Icon Filename | Test Filename | Use Case |
| :--- | :--- | :--- | :--- |
| **Global** | *Any* | `test_items.png`, `test_withdraw_items.png` | Universal checks (e.g., inventory or bank status). |
| **Category** | `[name]_[category].png` | `test_[category].png` | Grouping items (e.g., `iron_ore`, `gold_ore` both match `test_ore`). |
| **Full Name** | `[full_name].png` | `test_[full_name].png` | Specific item-to-test mapping (e.g., `superheat.png` matches `test_superheat.png`). |
| **Base Name** | `[base]_[suffix].png` | `test_[base].png` | Matching by the primary identifier (e.g., `fire_staff_equiped` matches `test_fire_staff`). |

### 4.3. Optimization Tips
1. **Leverage Categories**: If you have multiple similar items (like ores or bars), ensure their filenames end with the same suffix (e.g., `_ore` or `_bar`). If the suffix appears at least twice, the script will automatically pair them with `test_ore.png` or `test_bar.png`.
2. **Avoid Plurals**: The script does not handle pluralization. `iron_ore.png` will **not** match `test_ores.png`. Always use singular suffixes.
3. **Unique Suffixes for Unique Items**: If an item is unique, do not use an underscore before the last word if you don't want it categorized. Or, ensure the suffix only appears once in the entire folder.
4. **Clean Global Tests**: Use `test_items.png` and `test_withdraw_items.png` for tests that apply to every single icon in your action set.

## 5. Mapping Generation Logic (`image_mapper.py`)

The `image_mapper.py` script generates the `mapping.json` file. It follows a precise technical workflow to ensure accurate pairing between action icons and test screenshots.

### 5.1. Label Generation Sequence (`generate_labels` function)
Labels are generated alphabetically. After reaching **'Z'**, the sequence continues with double letters (`AA-ZZ`). This supports up to 702 unique action icons (26 single + 676 double).

```python
def generate_labels(n: int) -> List[str]:
    letters = string.ascii_uppercase
    result = []
    # Single letters (A-Z)
    for l in letters:
        result.append(l)
        if len(result) >= n:
            return result
    # Double letters (AA-ZZ)
    for pair in product(letters, repeat=2):
        result.append("".join(pair))
        if len(result) >= n:
            return result
    return result
```

**Example:**
- **Input**: `n = 28`
- **Expected Output**: `['A', 'B', ..., 'Z', 'AA', 'AB']`

### 5.2. Category Generation and Classification
The script identifies "valid categories" based on their frequency within an action folder.

#### 5.2.1. Suffix Validation Logic
A suffix is only designated as a **Valid Category** if it appears in at least **two distinct icons** within the same action folder.

```python
# Extract suffixes and count occurrences
suffixes = []
for a_name in normalized_actions.values():
    parts = a_name.split('_')
    if len(parts) > 1:
        suffixes.append(parts[-1])

suffix_counts = Counter(suffixes)
valid_categories = {s for s, count in suffix_counts.items() if count >= 2}
```

**Example:**
- **Input Icons**: `['iron_ore.png', 'gold_ore.png', 'unique_item.png']`
- **Extracted Suffixes**: `['ore', 'ore', 'item']`
- **Expected `valid_categories`**: `{'ore'}` (because `ore` appears twice, while `item` only appears once).

#### 5.2.2. The `extract_category` Function
This helper function classifies each icon into a category and base name.

```python
def extract_category(full_name: str) -> tuple:
    parts = full_name.split('_')
    if len(parts) > 1:
        suffix = parts[-1]
        if suffix in valid_categories:
            return suffix, '_'.join(parts[:-1])  # category, base_name
        else:
            return None, '_'.join(parts[:-1]) # No category, but still has a base_name
    return None, full_name
```

**Example:**
- **Input**: `full_name = "iron_ore"`, `valid_categories = {"ore"}`
- **Expected Output**: `("ore", "iron")`

- **Input**: `full_name = "unique_item"`, `valid_categories = {"ore"}`
- **Expected Output**: `(None, "unique")`

### 5.3. Automated Comparison Pairing Rules (Simplified)
The system uses a four-step priority system to decide which test images should be used to verify an icon.

```python
# STEP 1: Identify Universal (Global) Tests
# Some tests like "test_items" and "test_withdraw_items" are always included for every icon.
global_test_ids = [
    t_id for t_id, t_name in normalized_tests.items()
    if t_name in ["test_items", "test_withdraw_items"]
]

# STEP 2: Build the Comparison List for each Icon
for label, info in action_categories.items():
    # Start with the universal tests we found in Step 1
    matched_tests = set(global_test_ids)  
    
    for t_id, t_name in normalized_tests.items():
        # If we already added this test, skip it
        if t_id in matched_tests: continue
        
        # Rule 2: Category Match
        # If the icon is an "ore" (category), look for "test_ore"
        if info["category"] and t_name == f"test_{info['category']}":
            matched_tests.add(t_id)
            
        # Rule 3: Full Name Match
        # If the icon is "iron_ore", look for "test_iron_ore"
        elif t_name == f"test_{info['full_name']}":
            matched_tests.add(t_id)
            
        # Rule 4: Base Name Match
        # If the icon is "iron_ore", look for "test_iron" (the base name)
        elif t_name == f"test_{info['base_name']}":
            matched_tests.add(t_id)
            
    # Save the final sorted list of test IDs for this icon label
    mapping["comparisons"][label] = sorted(matched_tests)
```

**Example Pairing:**
- **Icon**: `Label 'M' (iron_ore)`
- **Test IDs**: `{'1': 'test_items', '2': 'test_ore', '3': 'test_iron_ore'}`
- **Expected `mapping["comparisons"]["M"]`**: `["1", "2", "3"]`
  - `1` (Global Match)
  - `2` (Category Match: `test_ore`)
  - `3` (Full Name Match: `test_iron_ore`)

## 6. Comparison Execution Logic (`run_test.py`)

The `run_test.py` script executes the visual validation defined in `mapping.json`.

### 6.1. Path Resolution
The `resolve_path` function handles URI translation for assets stored in local action folders or the global `commons` directory.

```python
def resolve_path(image_path: str, section: str) -> str:
    if not image_path.startswith("all/"):
        return image_path
    rest = image_path.split("all/", 1)[1]
    
    if rest.startswith("0common_photos"):
        return os.path.join("commons", rest)
    
    first_folder = rest.split("/", 1)[0]
    image_name = rest.split("/")[-1]
    folder_type = "action" if section == "icons" else "test"
    return os.path.join("commons", first_folder, "all_action_files", "screenshots", folder_type, image_name)
```

**Example:**
- **Input**: `image_path = "all/superheat/iron_ore.png"`, `section = "icons"`
- **Expected Output**: `"commons/superheat/all_action_files/screenshots/action/iron_ore.png"`

### 6.2. Image Matching Logic
Actual matching is performed using the `compare_icon_to_image_list` utility.

- **Algorithm**: `MatchingAlgorithm.TEMPLATE_MATCH` using OpenCV's `cv2.TM_CCOEFF_NORMED`.
- **Precision**: Hardcoded threshold of **0.8**.

```python
def evaluate_comparison(icon_path: str, test_path: str) -> Tuple[bool, float]:
    try:
        _, result = compare_icon_to_image_list(
            icon_image=icon_path,
            background_images_to_find_icon_in=[test_path],
            algorithm=MatchingAlgorithm.TEMPLATE_MATCH,
            precision=0.8
        )
        
        if result and len(result) >= 3:
            match_x, _, precision_value = result
            return match_x >= 0, round(float(precision_value), 2)
        return False, 0.0
    except Exception:
        return False, 0.0
```

**Example Matching Result:**
- **Input**: `iron_ore.png` vs `test_ore.png`
- **Internal Match Score**: `0.85`
- **Expected Output**: `(True, 0.85)` (Status: PASS)

- **Internal Match Score**: `0.72`
- **Expected Output**: `(False, 0.0)` (Status: FAILED, precision reset to 0.0 for failure)

## 7. Action Orchestration (`action_explained.txt`)

The `action_explained.txt` file defines the formal execution sequence using labels from `mapping.json`.

### 7.1. Structure and Syntax
An `action_explained.txt` file consists of two main parts: the **Overview** (descriptive task explanation) and the **Order Flow** (formal procedural logic).

- **Action Execution**: Referenced by its label (e.g., `A`).
- **Verification**: Enclosed in parentheses `()` following an action. Refers to `test_id`s from `mapping.json`.
    - `A(B)`: Execute action `A`, then verify that test `B` passes.
    - `A(!B)`: Execute action `A`, then verify that test `B` fails (`!` is negation).
- **Boolean Logic in Conditions**: Supports `&` (AND) and `|` (OR) for complex state verification.
    - `while (X & F)`: Loop while both test `X` and test `F` pass.
- **Control Flow**:
    - `while !D`: Continuously execute the indented block as long as test `D` fails.
    - `if Z`: Execute the block only if test `Z` passes.
    - `for item in list`: Iterative execution over a defined set of labels.
    - `end`: Terminates a loop or conditional block.
- **Common Actions**: `use_spell(Label)`, `withdraw_bank(Label)`, and `deposit_bank(Label)` allow for standardized calls to shared framework functions.

### 7.2. Comprehensive Example: `superheat_items`

```
# superheating_items

# Overview
withdraw all the required items (nature_runes,fire_runes,fire_staff, required_ores) based on the desired bar
Equip item (fire_staff...) if required
suerheat items
unequip fire_staff (if was equipped)
deposit everything to bank

# Order flow
items_required = [I,Q,X,F] nature_runes and fire_staff are a must have, the rest vary based on what bar you want
items_to_be_deposited = [I,Q,C] -> remaining nature_runes, fire_staff, and the bronze_bars
I used bronze bar for demonstration, note that each bar has specific requirements

start

#step_1: withdraw
for item in items_required
    withdraw_bank(item) -> withdraw_x

#step_2: equip fire_staff
Z(AA) -> click worn_equipment
while (!J)-> check if fire_staff is equipped in worn_equipment
    I(J)

#step_3:superheat
while (X & F) #i.e tin_ore and coppper_ore requird to make bronze bar, still exists in inventory:
    use_spell(W)
    F(AB) -> suerheat coppper_ore

#step_4: unequip fire_staff
Z(AA) -> click worn_equipment
while (!I)-> check if fire_staff is in inventory(has been unequiped)
   J(I)

#step_5: deposit
for item items_to_be_deposited
    deposit_bank(item) -> deposit_all
end
```

## 8. Conclusion

The Action Mapping System leverages frequency-based categorization and prioritized matching rules to automate the creation of robust visual testing suites. By following the alphabetical labeling and underscore-based naming conventions, developers can ensure seamless integration between visual assets and procedural logic.
