"""Lesson 06: compare COPY and LINK input materialisation."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import tempfile
import time
from pathlib import Path
from dagon import DataMover
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow


def run(mode):
    scratch = tempfile.TemporaryDirectory(prefix="dagon-tutorial-06-")
    wf = workflow("Meteorology06" + mode.name, scratch.name)
    # DataMover controls how a workflow:/// input (lesson 03) is
    # materialised in the consumer's working directory: COPY duplicates the
    # producer's file, LINK symlinks to it instead.
    wf.set_data_mover(mode)
    producer = DagonTask(TaskType.BATCH, "prepare", observation_command())
    consumer = DagonTask(
        TaskType.BATCH,
        "consume",
        "cat workflow:///prepare/outputs/observations.csv > consumed.csv",
    )
    wf.add_task(producer)
    wf.add_task(consumer)
    # Time the run itself, not just the staging step, since that's the only
    # granularity DAGon* exposes here -- COPY duplicates bytes, LINK just
    # creates a symlink, so COPY should never be faster than LINK.
    start = time.perf_counter()
    wf.run()
    elapsed = time.perf_counter() - start
    staged = next(
        Path(consumer.working_dir).glob("**/prepare/outputs/observations.csv")
    )
    linked = staged.is_symlink()
    print(f"{mode.name}: is_symlink={linked} elapsed={elapsed:.4f}s {staged}")
    return scratch, linked, elapsed


copy_tmp, copied, copy_elapsed = run(DataMover.COPY)
link_tmp, linked, link_elapsed = run(DataMover.LINK)
assert copied is False and linked is True
# This test file is a few bytes, so the difference is likely within noise --
# the point is the mechanism, not a real benchmark. On large files, COPY's
# gap over LINK grows with file size; LINK stays roughly constant.
print(f"COPY took {copy_elapsed:.4f}s, LINK took {link_elapsed:.4f}s")
copy_tmp.cleanup()
link_tmp.cleanup()
