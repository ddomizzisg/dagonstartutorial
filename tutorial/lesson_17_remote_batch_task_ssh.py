"""Lesson 17: run a task on a remote machine over SSH."""
import os
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow

# DagonTask(TaskType.BATCH, ..., ip=..., ssh_username=..., keypath=...) is the
# same BATCH task as lesson_01, except passing `ip` switches DAGon* to its
# RemoteBatch implementation: it opens an SSH connection (via Paramiko),
# stages workflow:/// inputs onto the remote host, runs the command there,
# and reads outputs back over the same connection. Only where the command
# executes changes -- the workflow:/// staging URI from lesson_03 still
# works unchanged, here reading a file the (local) `prepare` task produced.
#
# This lesson targets 127.0.0.1 as a stand-in for a genuinely remote host,
# using a dedicated SSH key with a scoped, restricted authorized_keys entry
# (see tutorial/README.md for the one-time setup this lesson needs -- it is
# not runnable out of the box the way lessons 01-15 are).
remote_host = os.environ.get("DAGON_TUTORIAL_SSH_HOST", "127.0.0.1")
remote_user = os.environ.get("DAGON_TUTORIAL_SSH_USER", os.environ.get("USER", ""))
key_path = os.environ.get(
    "DAGON_TUTORIAL_SSH_KEY", str(Path.home() / ".ssh" / "dagonstar_tutorial_key")
)

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-17-") as scratch:
    wf = workflow("Meteorology17", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    mean_command = (
        "mkdir -p outputs; "
        "awk -F, 'NR>1{s+=$3;n++}END{print s/n}' "
        "workflow:///prepare/outputs/observations.csv "
        "> outputs/mean.txt"
    )
    mean = DagonTask(
        TaskType.BATCH,
        "mean",
        mean_command,
        ip=remote_host,
        ssh_username=remote_user,
        keypath=key_path,
    )
    wf.add_task(prepare)
    wf.add_task(mean)
    wf.run()
    result = Path(mean.working_dir, "outputs/mean.txt").read_text().strip()
    assert result == "13"
    print(f"mean (computed over SSH on {remote_host}):", result)
