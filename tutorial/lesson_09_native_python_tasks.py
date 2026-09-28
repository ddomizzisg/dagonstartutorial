"""Lesson 09: execute an importable native Python function."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import json
import tempfile
from pathlib import Path
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-09-") as scratch:
    wf = workflow("Meteorology09", scratch)
    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    # TaskType.NATIVE runs an importable Python function in-process instead
    # of a shell command: its "command" is a "module:function" path, and
    # inputs/outputs map argument names to files DAGon* stages and passes
    # in as paths. See tutorial/common/native_functions.py:mean_temperature,
    # which is called here as mean_temperature(observations=..., result=...).
    native = DagonTask(
        TaskType.NATIVE,
        "mean",
        "tutorial.common.native_functions:mean_temperature",
        inputs={"observations": "workflow:///prepare/outputs/observations.csv"},
        outputs={"result": "mean.json"},
    )
    wf.add_task(prepare)
    wf.add_task(native)
    wf.run()
    result = json.loads(Path(native.working_dir, "outputs/mean.json").read_text())
    assert result == {"mean_temperature_c": 13.0}
    print(result)
