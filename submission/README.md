# submission — the hand-in

**What it answers:** what was actually submitted, byte-for-byte.

**Contents**

| File | Bytes | SHA256 |
|---|---:|---|
| `philopateer.pdf` | 846,608 | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` |
| `philopateer.pptx` | 1,310,666 | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` |
| `philopateer.ipynb` | 1,857,125 | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` |

These are three of the five F1 artifacts. The two course-supplied `.docx` files are in `docs/reference/` by the Gate-1 decision, not here. Hashes: `versions/v4_addons/RELEASE_RECEIPT.md`; page/slide/cell counts: `evidence/delivery_checks.json` (15 pages, 15 slides, 25 executed code cells, 0 errors).

**Who reads it:** the assessor and the account holder.

**Current?** Yes — frozen v2, byte-identical to the v4 receipt and the D0 record. Never edit, re-save, convert or “Run All”.

**How it is regenerated:** from the frozen v2 pipeline; commands are documented in `pipeline/README.md` and were **not run** during the reorganization. The deck was built from the frozen charts and text, not by re-fitting.

**Working-directory assumptions of the frozen artifacts**

- The notebook's cells read `telecom/Client.csv`, `telecom/Record.csv`, `v1_frozen/analysis_outputs/…` relative to its old working directory. In this tree those inputs are `data/telecom/` and `versions/v1_frozen/`; opening is safe, executing is not (stale paths, and it is the frozen record).
- `philopateer.pdf` and `philopateer.pptx` are static files with no working-directory assumption.
- The notebook contains executed outputs, including prediction-table summaries with applicant-level column names (`notebook_output_scan.md`). It is not stripped; the dataset itself is not redistributed.

**Caveats:** the ranking is measured; the policy gain is retrospective; the dollar net is conditional on assumed prevention, cost, margin and horizon. No causal retention lift is claimed.
