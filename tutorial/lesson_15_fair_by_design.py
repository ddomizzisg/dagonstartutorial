"""Lesson 15: record FAIR provenance metadata for a workflow."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # see lesson_01
import json
import tempfile
from pathlib import Path
from dagon.fair import Agent, Artifact, FairProfile
from dagon.task import DagonTask, TaskType
from tutorial.common.support import observation_command, workflow

with tempfile.TemporaryDirectory(prefix="dagon-tutorial-15-") as scratch:
    # output_dir pins the FAIR report next to this run's own scratch dir
    # instead of the library's default (nested under a random run id),
    # so the assertions below know exactly where to look.
    fair_dir = Path(scratch, "fair-report")
    wf = workflow("FairDemo15", scratch)
    # enable_fair() turns on lifecycle recording with no change to task
    # execution: it just listens to the same workflow events lesson 08
    # uses (on_task_start/end, ...) and writes a provenance bundle on exit.
    profile = FairProfile(
        title="Weather observation pipeline",
        description="Deterministic tutorial workflow computing a mean temperature.",
        creators=[Agent(name="DAGonStar Tutorial")],
        license="Apache-2.0",
        keywords=["weather", "tutorial"],
        output_dir=str(fair_dir),
    )
    wf.enable_fair(profile)

    prepare = DagonTask(TaskType.BATCH, "prepare", observation_command())
    # declare_outputs() tells the recorder which files are the scientific
    # artifacts worth describing, as opposed to incidental scratch files.
    prepare.declare_outputs(
        Artifact(
            "outputs/observations.csv",
            name="Observations",
            media_type="text/csv",
            license="Apache-2.0",
        )
    )
    command = (
        "mkdir -p outputs; "
        "awk -F, 'NR>1{s+=$3;n++}END{print s/n}' "
        "workflow:///prepare/outputs/observations.csv "
        "> outputs/mean.txt"
    )
    mean = DagonTask(TaskType.BATCH, "mean", command)
    mean.declare_outputs(
        Artifact(
            "outputs/mean.txt",
            name="Mean temperature",
            media_type="text/plain",
            license="Apache-2.0",
        )
    )
    wf.add_task(prepare)
    wf.add_task(mean)
    wf.run()

    run = json.loads(Path(fair_dir, "run.json").read_text())
    # The recorder inferred this workflow:// edge itself (lesson 03) --
    # FAIR provenance is a byproduct of the graph, not separately declared.
    assert run["dependencies"] == [
        {
            "consumer": "mean",
            "path": "outputs/observations.csv",
            "producer": "prepare",
            "type": "workflow-edge",
        }
    ]
    assert len(run["artifacts"]) == 2
    assert all(artifact["checksum"] for artifact in run["artifacts"])

    report = json.loads(Path(fair_dir, "fairness-report.json").read_text())
    assert report["status"] == "passed"
    assert Path(fair_dir, "ro-crate-metadata.json").is_file()

    print("FAIR report written to:", fair_dir)
    print("fairness status:", report["status"])
    print("artifacts recorded:", [a["path"] for a in run["artifacts"]])
