"""Lesson 16: run a task inside a Docker container."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import shutil
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow

# tempfile.TemporaryDirectory()'s automatic cleanup is not used here: the
# container below runs as root by default, so files it writes into the
# bind-mounted scratch directory are root-owned on the host and a
# non-root user cannot remove them. shutil.rmtree(..., ignore_errors=True)
# cleans up everything it can and silently skips the rest -- a real,
# common Docker bind-mount gotcha, not a bug in this lesson.
scratch = tempfile.mkdtemp(prefix="dagon-tutorial-16-")
try:
    wf = workflow("Meteorology16", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    command = (
        "mkdir -p outputs; "
        "awk -F, 'NR>1{s+=$3;n++}END{print s/n}' "
        "workflow:///prepare/outputs/observations.csv "
        "> outputs/mean.txt"
    )
    # TaskType.DOCKER runs the same kind of shell command as BATCH, but
    # inside a container started from `image`. DAGon* stages workflow:///
    # inputs the same way; only where the command executes changes.
    mean = DagonTask(TaskType.DOCKER, "mean", command, image="alpine:latest")
    wf.add_task(prepare)
    wf.add_task(mean)
    wf.run()
    result = Path(mean.working_dir, "outputs/mean.txt").read_text().strip()
    assert result == "13"
    print("mean (computed inside alpine:latest):", result)
finally:
    shutil.rmtree(scratch, ignore_errors=True)
