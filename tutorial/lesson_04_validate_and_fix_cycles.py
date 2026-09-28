"""Lesson 04: reject then repair a cycle."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
from dagon.task import DagonTask, TaskType
from tutorial.common.support import workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-04-") as scratch:
    wf = workflow("Meteorology04", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", "true")
    analyse = DagonTask(TaskType.BATCH, "analyse", "true")
    report = DagonTask(TaskType.BATCH, "report", "true")
    for task in (prepare, analyse, report):
        wf.add_task(task)

    # Deliberately wire a cycle: prepare -> analyse -> report -> prepare.
    analyse.add_dependency_to(prepare)
    report.add_dependency_to(analyse)
    prepare.add_dependency_to(report)

    try:
        wf.Validate_WF()
    except Exception as exc:
        # Validate_WF() raises instead of silently accepting a graph that
        # could never finish running. A real workflow would fix its edges
        # here rather than re-raise.
        assert "cycle" in str(exc).lower()
        print("rejected:", exc)
    else:
        raise AssertionError("cycle was not rejected")

    # Repair the graph by removing just the back-edge that closed the loop.
    prepare.prevs.remove(report)
    report.nexts.remove(prepare)
    wf.Validate_WF()
    print("repaired graph validates")
