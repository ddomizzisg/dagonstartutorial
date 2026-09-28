"""Lesson 10: run the deterministic local web-task example.

This file is intentionally a thin wrapper, not the lesson content itself.
The mock HTTP server, the TaskType.WEB task, and the workflow all live in
lesson_13_web_tasks.py -- that was this lesson's filename before the
tutorial was renumbered, and it was kept as-is so nothing that imports it
by name breaks. Open lesson_13_web_tasks.py to read or edit the actual
lesson; there is no separate "lesson 13" waiting later in the sequence.
"""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
from tutorial.lesson_13_web_tasks import main

if __name__ == "__main__":
    main()
