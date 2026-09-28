"""Lesson 07: create and reuse checkpoint state."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
import time
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.support import workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-07-") as scratch:
    checkpoint = Path(scratch, "checkpoint.json")
    wf = workflow("Meteorology07", scratch, checkpoint_file=str(checkpoint))
    # "sleep 2" stands in for an expensive computation: long enough that
    # skipping it on resume is clearly measurable, short enough to keep the
    # lesson quick to run.
    calculate_command = "sleep 2; mkdir -p outputs; printf 13 > outputs/mean.txt"
    task = DagonTask(TaskType.BATCH, "calculate", calculate_command)
    wf.add_task(task)
    start = time.perf_counter()
    wf.run()
    first_elapsed = time.perf_counter() - start
    assert checkpoint.is_file()
    first_dir = task.working_dir

    # A second, independent Workflow object simulates a fresh process
    # resuming an earlier run: it gets brand-new task objects, but passing
    # the same checkpoint file to run() tells DAGon* to reuse the completed
    # task's scratch directory instead of re-running its command.
    resumed = workflow("Meteorology07", scratch, checkpoint_file=str(checkpoint))
    second = DagonTask(TaskType.BATCH, "calculate", calculate_command)
    resumed.add_task(second)
    start = time.perf_counter()
    resumed.run(resume_checkpoint_file=str(checkpoint))
    resumed_elapsed = time.perf_counter() - start
    assert Path(second.working_dir, "outputs/mean.txt").read_text() == "13"
    print("checkpoint:", checkpoint, "scratch reused:", first_dir == second.working_dir)
    print(f"first run: {first_elapsed:.2f}s, resumed run: {resumed_elapsed:.2f}s")
    # Resume skips re-executing "sleep 2" entirely -- the saved time tracks
    # the sleep duration, not just measurement noise.
    assert resumed_elapsed < first_elapsed - 1
