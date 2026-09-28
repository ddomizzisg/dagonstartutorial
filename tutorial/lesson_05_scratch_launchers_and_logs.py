"""Lesson 05: inspect task artifacts without guessing a /tmp path."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-05-") as scratch:
    wf = workflow("Meteorology05", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    # "workflow:///prepare/outputs/observations.csv" is the same staging URI
    # from lesson 03: DAGon* infers that "consume" depends on "prepare" and
    # stages the file into consume's own working directory before this
    # command runs.
    consume_command = (
        "mkdir -p outputs; "
        "cat workflow:///prepare/outputs/observations.csv > outputs/echo.csv"
    )
    consume = DagonTask(TaskType.BATCH, "consume", consume_command)
    wf.add_task(prepare)
    wf.add_task(consume)
    wf.run()

    # task.working_dir is the actual directory DAGon* used for this run --
    # read it from the task object instead of reconstructing it yourself.
    # Alongside "outputs" (lesson 01), DAGon* keeps its own bookkeeping
    # (launcher script, exit status, logs) in a ".dagon" directory.
    meta = Path(prepare.working_dir, ".dagon")
    names = sorted(path.name for path in meta.iterdir())
    assert Path(prepare.working_dir, "outputs/observations.csv").is_file()
    assert names
    print("task directory:", prepare.working_dir)
    print(".dagon files:", names)

    # "consume" received its own scratch directory, plus the file staged in
    # from "prepare" via the workflow:// reference above.
    assert Path(consume.working_dir, "outputs/echo.csv").is_file()
    print("consume directory:", consume.working_dir)
