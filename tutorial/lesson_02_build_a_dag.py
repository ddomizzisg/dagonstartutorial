"""Lesson 02: build a fan-out/fan-in DAG."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-02-") as scratch:
    wf = workflow("Meteorology02", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    temperature = DagonTask(
        TaskType.BATCH,
        "temperature",
        "mkdir -p outputs; printf temperature > outputs/metric.txt",
    )
    wind = DagonTask(
        TaskType.BATCH,
        "wind",
        "mkdir -p outputs; printf wind > outputs/metric.txt",
    )
    report = DagonTask(
        TaskType.BATCH,
        "report",
        "mkdir -p outputs; printf complete > outputs/report.txt",
    )
    for task in (prepare, temperature, wind, report):
        wf.add_task(task)

    # make_dependencies() must run once, after every task is registered and
    # before any add_dependency_to() call below: it prepares the internal
    # prevs/nexts bookkeeping that those calls then populate.
    wf.make_dependencies()

    # Fan-out: both "temperature" and "wind" depend on "prepare".
    temperature.add_dependency_to(prepare)
    wind.add_dependency_to(prepare)
    # Fan-in: "report" waits for both "temperature" and "wind" to finish.
    report.add_dependency_to(temperature)
    report.add_dependency_to(wind)

    # Validate_WF() checks the graph (e.g. for cycles, see lesson 04) before
    # anything is allowed to run.
    wf.Validate_WF()
    assert {task.name for task in report.prevs} == {"temperature", "wind"}
    wf.run()
    assert Path(report.working_dir, "outputs/report.txt").read_text() == "complete"
    print("report predecessors:", sorted(task.name for task in report.prevs))
