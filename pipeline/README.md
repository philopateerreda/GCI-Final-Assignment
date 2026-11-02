# pipeline — how the result was produced

**What it answers:** which code produced the frozen v2 delivery, and how to replay it.

**Contents**

| File | Bytes | Role |
|---|---:|---|
| `analysis_pipeline.py` | 353,674 | Frozen v2 pipeline: assertions, model, policy, economics, v2 workstreams |
| `build_notebook.py` | 21,249 | Builds/executes the submitted notebook |
| `export_and_verify.py` | 7,309 | Delivery QA: claims, geometry, renders, hashes |
| `restore_v1.py` | 3,751 | Restores the v1 snapshot from its SHA256 manifest |
| `references.txt` | 18,843 | Verified bibliography and AI-use disclosure |
| `requirements-python311.txt` | 346 | Pinned Python 3.11 environment |

All six are Tier C: byte-identical to `pre-reorg`; no path was edited (V8).

**Who reads it:** a reviewer reproducing the run, and the author restoring a snapshot.

**Current?** Historical provenance. Not run during the reorganization; no notebook cell was executed.

**How it is regenerated — commands are documented, not run**

```bash
python -m pip install -r pipeline/requirements-python311.txt
# Stage the new locations into an old-layout workspace (the scripts assume it):
mkdir -p /tmp/finalA-repro/telecom
cp pipeline/analysis_pipeline.py pipeline/build_notebook.py pipeline/export_and_verify.py /tmp/finalA-repro/
cp pipeline/references.txt /tmp/finalA-repro/
cp data/telecom/*.csv /tmp/finalA-repro/telecom/
cp -r versions/v1_frozen /tmp/finalA-repro/v1_frozen
cd /tmp/finalA-repro && python analysis_pipeline.py
```

For a faithful old-layout replay instead: `git worktree add ../finalA-pre-reorg pre-reorg`, then copy `versions/v1_frozen` and `data/telecom` into that worktree and run the same scripts there. Environment: Python 3.11.9, six threads, seed `20261028` (`evidence/environment.json`).

**Caveats:** `analysis_pipeline.py` uses `ROOT = Path.cwd()`; the other three use the script's own directory. Running them in place writes into `pipeline/` and will not find the moved inputs. `export_and_verify.py` needs Windows, Office, `pywin32` and `pymupdf`. Rebuilding would overwrite the frozen notebook — never point it at `submission/`.
