"""Lesson 14: snapshot an artifact with an explicit checkpoint task."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.meteorological_data import CSV
from tutorial.common.support import observation_command, require_text, workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-14-") as scratch:
    wf = workflow("CheckpointTask14", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    # TaskType.CHECKPOINT is a different mechanism from lesson 07's
    # checkpoint_file= workflow-level resume: it is a task in the graph
    # whose "command" is one or more workflow:/// references to snapshot.
    # DAGon* stages those files in as usual, then moves them into the
    # checkpoint task's own working directory -- a stable, named copy that
    # downstream tasks can depend on instead of the original producer.
    snapshot = DagonTask(
        TaskType.CHECKPOINT, "snapshot", "workflow:///prepare/outputs/observations.csv"
    )
    # The checkpointed copy lives under <workflow name>/<producer>/<path>
    # inside the checkpoint task's own working directory.
    consume = DagonTask(
        TaskType.BATCH,
        "consume",
        "mkdir -p outputs; "
        "cat workflow:///snapshot/CheckpointTask14/prepare/outputs/observations.csv "
        "> outputs/echo.csv",
    )
    wf.add_task(prepare)
    wf.add_task(snapshot)
    wf.add_task(consume)
    wf.make_dependencies()
    # The dependency graph runs through the checkpoint, not around it:
    # consume never references "prepare" directly.
    assert [task.name for task in snapshot.prevs] == ["prepare"]
    assert [task.name for task in consume.prevs] == ["snapshot"]
    wf.run()
    result = Path(consume.working_dir, "outputs/echo.csv")
    require_text(result, CSV)
    print("consumed the checkpointed copy:", result)
