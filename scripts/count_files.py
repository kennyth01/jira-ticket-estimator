#!/usr/bin/env python3
"""
Helper script to count unique files from multiple grep/glob results.

Usage:
    python3 count_files.py <<EOF
    {
      "file_lists": [
        ["file1.php", "file2.php"],
        ["file2.php", "file3.php"],
        ["file4.php"]
      ]
    }
    EOF

Output:
    {
      "count": 4,
      "files": ["file1.php", "file2.php", "file3.php", "file4.php"]
    }
"""

import sys
import json


def count_unique_files(file_lists):
    """
    Count unique files across multiple search results.

    Args:
        file_lists: List of lists, where each inner list contains file paths

    Returns:
        dict with count and unique files
    """
    all_files = set()

    for file_list in file_lists:
        if file_list:  # Handle None or empty lists
            if isinstance(file_list, list):
                all_files.update(file_list)
            elif isinstance(file_list, str):
                # Single file path
                all_files.add(file_list)

    return {
        "count": len(all_files),
        "files": sorted(list(all_files))
    }


if __name__ == '__main__':
    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
        result = count_unique_files(data.get('file_lists', []))
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"Invalid JSON input: {e}",
            "count": 0,
            "files": []
        }), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"Unexpected error: {e}",
            "count": 0,
            "files": []
        }), file=sys.stderr)
        sys.exit(1)
