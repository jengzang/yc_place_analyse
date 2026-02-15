# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese dialect and village name analysis tool for Yangchun City (阳春市), Guangdong Province. The project has two main components:

1. **Dialect Lookup System**: Queries Chinese characters and their pronunciations from Excel-based dialect databases
2. **Village Name Analysis System**: Analyzes village names, frequencies, and naming patterns across towns in Yangchun City

## Project Structure

The repository has two main entry points:

- `main.py` (root): Combined dialect lookup and village analysis tool (development version)
- `your_module/main.py`: Standalone village analysis tool designed for PyInstaller packaging

### Core Modules (in `your_module/`)

- `data_parser.py`: Parses `阳春村庄名录.txt` and converts hierarchical village data structures
- `data_retriever.py`: Retrieves administrative divisions (towns, committees, villages)
- `data_analyzer.py`: Analyzes character frequency and distribution in village names
- `top_villages.py`: Finds villages with duplicate names across the city
- `analyze_tendencies.py`: Analyzes naming tendencies by town (which characters are preferred/avoided)
- `village_analysis.py`: **Shared interactive menu logic** - contains the 7-feature menu loop used by both entry points
- `new_way.py`: Manages the `dialects.txt` file for storing village metadata
- `rw.py`: Low-level read/write operations for the dialects data file
- `utils.py`: Utility functions for duplicate resolution and user navigation

### Architecture

**Shared Logic**: The village analysis interactive menu (features 1-7) is extracted into `village_analysis.py` to eliminate code duplication. Both `main.py` (root) and `your_module/main.py` import and use this shared module.

**Import Pattern**: The root `main.py` imports from `your_module`:
```python
from your_module import new_way
from your_module.data_parser import parse_village_file, convert_data_structure
from your_module.village_analysis import run_village_analysis
```

### Data Files

- `阳春方言.xlsx`: Excel file with two sheets:
  - `字表(总)`: Character pronunciation table
  - `口语字`: Colloquial character table
- `阳春村庄名录.txt`: Village registry with hierarchical structure (town → committee → natural village)
- `res/dialects.txt`: Generated file storing village metadata (created by feature 6/7 in the application)

## Building and Running

### Development Mode

Run the main application:
```bash
python main.py
```

Run the packaged version (village analysis only):
```bash
cd your_module
python main.py
```

### Building Executable

Build the standalone executable using PyInstaller:
```bash
cd your_module
pyinstaller main.spec
```

The executable will be created in `your_module/dist/main/main.exe` with resources bundled in `_internal/res/`.

## Data Structure

The village data follows this hierarchy:
```
Town (镇/街道)
├── Village Committees (村民委员会)
│   └── Natural Villages (自然村)
├── Resident Committees (居民委员会)
└── Communities (社区)
```

Parsed data structure:
```python
{
    "Town Name": {
        "村民委员会": ["Committee1", "Committee2"],
        "居民委员会": ["Committee3"],
        "社区": ["Community1"],
        "自然村": {
            "Committee1": ["Village1", "Village2"],
            "Committee2": ["Village3"]
        }
    }
}
```

## Key Features

The application provides 7 main features:

1. Query village registry (by town, committee, or all)
2. Search character/word frequency in village names
3. Find most common characters in village names
4. Find duplicate village names across the city
5. Analyze naming tendencies by town
6. Query village information from dialects.txt
7. Add information to villages in dialects.txt

## Resource Path Handling

The code uses `resource_path()` function to handle file paths in both development and PyInstaller-packaged environments:
- Development: Uses current directory
- Packaged: Uses `sys._MEIPASS` (PyInstaller's temporary extraction directory)

## Character Encoding

All files use UTF-8 encoding. The project handles Chinese characters throughout.

## Recent Refactoring (2024-06)

The project was refactored to improve code organization and eliminate duplication:

1. **Extracted Shared Logic**: Created `village_analysis.py` with the shared interactive menu (eliminates ~140 lines of duplication)
2. **Consolidated Modules**: All core modules now reside in `your_module/` (no duplicates in root)
3. **Fixed Bug**: Corrected `data_retriever.py` default values from `{}` to `[]` for 村民委员会
4. **Cleaned Up**: Removed obsolete files (main0.py, old/, build artifacts, duplicate modules)
5. **Updated Imports**: Root `main.py` now imports from `your_module` package

This refactoring eliminates ~400 lines of duplicated code while preserving all original functionality.

