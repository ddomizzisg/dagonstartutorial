"""Lesson 11: run the deterministic local LLM-task example.

This file is intentionally a thin wrapper -- see lesson_10_web_tasks.py for
why. The mock chat server, the TaskType.LLM task, and the workflow all live
in lesson_12_llm_tasks.py (this lesson's filename before renumbering); open
that file to read or edit the actual lesson.
"""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
from tutorial.lesson_12_llm_tasks import main

if __name__ == "__main__":
    main()
