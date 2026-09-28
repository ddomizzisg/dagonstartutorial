# DAGonStar tutorial examples

These scripts are authoritative runnable companions to the redesigned curriculum. Install DAGonStar (see the root `README.md`), then run any lesson script directly -- each one locates the repository root itself via its own file path, so no separate install step for this repository is needed and the scripts can be run from anywhere.

~~~bash
python tutorial/lesson_01_first_local_task.py
python tutorial/lesson_02_build_a_dag.py
python tutorial/lesson_03_workflow_data_dependencies.py
python tutorial/lesson_04_validate_and_fix_cycles.py
python tutorial/lesson_05_scratch_launchers_and_logs.py
python tutorial/lesson_06_data_staging.py
python tutorial/lesson_07_checkpoint_and_resume.py
python tutorial/lesson_08_asynchronous_execution.py
python tutorial/lesson_09_native_python_tasks.py
python tutorial/lesson_10_web_tasks.py
python tutorial/lesson_11_llm_tasks.py
python tutorial/lesson_14_explicit_checkpoint_task.py
python tutorial/lesson_15_fair_by_design.py
python tutorial/lesson_16_docker_backed_task.py
python tutorial/lesson_17_remote_batch_task_ssh.py
~~~

Lessons 01–09 use local files and processes. Lessons 10 and 11 bind short-lived deterministic mock services to `127.0.0.1` on an available port and close them cleanly. They use no public service or real credential. Every script uses an isolated temporary scratch directory and exact assertions.

Lessons 14 and 15 extend the set past the original eleven with two more
`dagon` features that also run fully locally, no credentials or extra
infrastructure required: `TaskType.CHECKPOINT` (an explicit checkpoint task
that snapshots one artifact mid-graph, distinct from lesson 07's
workflow-level `checkpoint_file=` resume) and `Workflow.enable_fair()`
(FAIR provenance recording -- RO-Crate, PROV-JSON, checksums -- written
automatically as a byproduct of the graph DAGon* already built).

Lesson 16 adds `TaskType.DOCKER`: the same `mean`-over-`prepare` pipeline as
earlier lessons, but `mean` now runs inside a real `alpine:latest` container.
Unlike every other lesson up to this point, this one needs a working Docker
daemon on the machine running it -- it is not a mock.

Lesson 17 adds the same pipeline again, but `mean` now runs on a remote
machine over SSH: `DagonTask(TaskType.BATCH, ..., ip=, ssh_username=,
keypath=)` -- there is no separate `TaskType.SSH`, remote execution is
BATCH with SSH parameters. Unlike lesson 16, this needs more than a running
daemon: it needs an SSH server and an authorized key with a specific,
scoped configuration, because DAGon*'s SSH backend (`dagon/communication/ssh.py`)
generates bash heredoc syntax and sends it through the target account's
*login shell* -- if that shell is not bash-compatible (for example fish),
the heredoc fails to parse. The one-time fix, applied once in this
environment, does not require changing the account's login shell:

~~~bash
ssh-keygen -t ed25519 -f ~/.ssh/dagonstar_tutorial_key -N "" -C "dagonstar-tutorial-lesson17"
PUBKEY=$(cat ~/.ssh/dagonstar_tutorial_key.pub)
echo "command=\"bash -c \\\"\$SSH_ORIGINAL_COMMAND\\\"\",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty $PUBKEY" >> ~/.ssh/authorized_keys
~~~

This adds one restricted `authorized_keys` entry, scoped to connections
authenticating with this one dedicated key: it forces every command that
key's connections send to run through `bash -c "$SSH_ORIGINAL_COMMAND"`
instead of the account's default login shell, and disables port/X11/agent
forwarding and interactive PTY allocation for that key. It changes nothing
for any other key or any other account.

By default, lesson 17 targets `127.0.0.1` as a stand-in for a genuinely
remote host and looks for `~/.ssh/dagonstar_tutorial_key`. Point it at a
different host, user, or key with `DAGON_TUTORIAL_SSH_HOST`,
`DAGON_TUTORIAL_SSH_USER`, and `DAGON_TUTORIAL_SSH_KEY`.

**Known upstream limitation:** `RemoteBatch.__init__` (`dagon/batch.py`)
does not forward `ssh_port` to its base class, even though `RemoteTask`
supports it (default 22) -- passing `ssh_port=` to a `BATCH` task with `ip=`
set raises `TypeError`. Use the default port 22, or a host reachable on 22,
until this is fixed upstream.

**Do not confuse these with the separate `DagOnStar/dagonstar` repository's
own numbered curriculum** (`docs/tutorial/lesson_00...lesson_18`, referenced
elsewhere in this project's slides), which happens to reuse the numbers 12-14
for Docker/SSH/Slurm and 15 for FAIR -- those are different files in a
different repository, covering the same *topics* with real infrastructure
requirements this local tutorial does not set up.

The canonical Lesson 10 and 11 entry points reuse the detailed local mock
implementations in `lesson_13_web_tasks.py` and `lesson_12_llm_tasks.py`.
Those implementation modules retain their historical filenames for import
compatibility; they are not additional numbered lessons.

## Notebook lesson numbers vs. these filenames

`DAGonStar_Tutorial.ipynb` numbers its lessons sequentially in the order the
slide deck presents them, which does not always match the number in these
filenames (a consequence of the historical renumbering above). The mapping:

| Notebook lesson | This file |
|---|---|
| 1 | `lesson_01_first_local_task.py` |
| 2 | `lesson_02_build_a_dag.py` |
| 3 | `lesson_05_scratch_launchers_and_logs.py` |
| 4 | `lesson_03_workflow_data_dependencies.py` |
| 5 | `lesson_04_validate_and_fix_cycles.py` |
| 6 | `lesson_06_data_staging.py` |
| 7 | `lesson_07_checkpoint_and_resume.py` |
| 8 | `lesson_14_explicit_checkpoint_task.py` |
| 9 | `lesson_08_asynchronous_execution.py` |
| 10 | `lesson_16_docker_backed_task.py` |
| 11 | `lesson_17_remote_batch_task_ssh.py` |
| 12 | `lesson_12_llm_tasks.py` |
| 13 | `lesson_13_web_tasks.py` |
| 14 | `lesson_09_native_python_tasks.py` |
| 15 | `lesson_15_fair_by_design.py` |
