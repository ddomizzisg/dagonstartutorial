"""Lesson 01: execute one deterministic local task."""
import sys
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.meteorological_data import CSV
from tutorial.common.support import observation_command, require_text, workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-01-") as scratch:
    wf = workflow("Meteorology01", scratch)
    # A single BATCH task: DagonTask wraps a shell command that DAGon* runs
    # inside its own working directory under `scratch`.
    task = DagonTask(TaskType.BATCH, "prepare_observations", observation_command())
    wf.add_task(task)
    wf.run()
    # After run(), DAGon* has written the task's output under
    # <task.working_dir>/outputs/<name> -- no path guessing required.
    result = Path(task.working_dir, "outputs", "observations.csv")
    require_text(result, CSV)
    print("verified", result)
