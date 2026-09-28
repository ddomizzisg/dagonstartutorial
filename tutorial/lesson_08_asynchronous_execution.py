"""Lesson 08: launch asynchronously and observe lifecycle events."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
import time
from dagon.task import DagonTask, TaskType
from tutorial.common.support import workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-08-") as scratch:
    wf = workflow("Meteorology08", scratch)
    events = []
    wf.add_listener("on_workflow_start", lambda _: events.append("workflow_start"))
    wf.add_listener("on_workflow_end", lambda _: events.append("workflow_end"))
    wf.add_task(DagonTask(TaskType.BATCH, "analyse", "sleep 0.05; true"))

    # launch() starts the workflow on a background thread and returns
    # immediately, unlike run() (used in every earlier lesson) which blocks
    # until the workflow finishes.
    start = time.monotonic()
    thread = wf.launch()
    launch_elapsed = time.monotonic() - start
    # If launch() were secretly blocking like run(), this would take at
    # least the task's own 0.05s sleep -- proof it returns immediately.
    assert launch_elapsed < 0.05
    assert thread.is_alive() or events
    # wait() blocks -- with a timeout, here 5s -- until the workflow ends.
    assert wf.wait(5)
    assert events == ["workflow_start", "workflow_end"]
    print("events:", events)
