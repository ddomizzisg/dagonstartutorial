# DagOnStar tutorial

DAGonStar, also written as DAGon\*, is a lightweight Python workflow engine for
running directed acyclic graph (DAG) workflows across local machines, remote
servers, HPC clusters, containers, and cloud infrastructure.

DAGonStar workflows are ordinary Python programs. Tasks can depend explicitly on
other tasks, or implicitly through `workflow://` data references that DAGonStar
resolves into task dependencies and staging operations.

This repository contains a self-contained tutorial: 17 runnable lesson scripts
(`tutorial/`), a matching Jupyter notebook (`DAGonStar_Tutorial.ipynb`), and the
slide deck and timing plan they accompany (`slides/`).

## Installation

Use Python 3.8 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install git+https://github.com/DagOnStar/dagonstar.git
```

Optional integrations are available as install extras:

```bash
pip install "dagonstar[all] @ git+https://github.com/DagOnStar/dagonstar.git"
```

Confirm the same interpreter can import DAGonStar:

```bash
python -c "import dagon; print(dagon.Workflow.__name__)"
```

## Running the tutorial scripts

Each lesson is a standalone script that finds the repository root itself, so it
can be run from anywhere once the virtual environment above is active:

```bash
python tutorial/lesson_01_first_local_task.py
```

See `tutorial/README.md` for the full list of lessons, what each one covers,
and the one-time setup needed for the Docker- and SSH-backed lessons (16 and 17).

## Running the notebook

`DAGonStar_Tutorial.ipynb` runs the same lessons as the slide deck, in the
order the slides present them, as one notebook.

**Option A -- VS Code:**
1. Open this repository's root folder in VS Code (the folder containing `tutorial/`).
2. Install the **Python** and **Jupyter** extensions if you do not already have them.
3. Open `DAGonStar_Tutorial.ipynb`.
4. Click the kernel picker (top right) and select the `.venv` interpreter created above.
5. Run All. The first Setup cell installs DAGonStar into that interpreter automatically
   -- no separate `pip install` of this repository is needed.

**Option B -- JupyterLab:**
```bash
. .venv/bin/activate
pip install jupyterlab
jupyter lab DAGonStar_Tutorial.ipynb
```
Then Run All Cells from the repository root, same as above.

The notebook must be opened from the repository root -- it checks that `tutorial/`
sits right next to it, the same requirement as running the scripts directly. Lesson
10 (Docker-Backed Task) needs a working Docker daemon; Lesson 11 (Remote Batch Task
over SSH) needs a reachable SSH host and an authorized key (see `tutorial/README.md`).
Everything else runs locally with no extra infrastructure.