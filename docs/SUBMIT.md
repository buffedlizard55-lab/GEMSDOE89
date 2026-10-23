# Manual Submission Guide (`docs/SUBMIT.md`)

Automated access to `drivendata.org` is prohibited by challenge rules and agent constraints. A human operator must perform any upload and record the returned receipt.

## 1. Pre-Upload Verification (Local Check)

Before uploading any candidate in `releases/`, verify its SHA-256 hash on disk matches `ledger/submissions.csv`:

```bash
sha256sum releases/h33-h33-2-b2-spacing-*.tif releases/h33-h33-2-b2-relief-*.tif releases/h33-h33-2-b2-MASS*.tif
python3 tools/validate_raster.py
python3 tools/check_ledger.py
```

### `SPACING` Candidates Built This Session (Primary = NaN outside footprint)

| Slot Role | Primary File (`NaN` outside footprint) | SHA-256 (`primary`) | Fallback (`0.0` outside) | SHA-256 (`-zeros`) |
|---|---|---|---|---|
| **Slot 1 (`SPACING` primary)** | `releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif` | `3b263c7aa90ee0928d8ad8b2a81e42bc99decc7c881f46204af36b877d8bdbaa` | `...-zeros.tif` | `d18297a5192f05902b8baadd585de37de0d81fadb3dc9aba626767cfc9494cc6` |
| **Slot 2 (if Slot 1 >= 0.2878)** | `releases/h33-h33-2-b2-spacing-poisson-20261023-ff167173.tif` | `ff167173aa2b8e45187d123db0193ad8da7e16a6e65c0f466630be9db7cfea34` | `...-zeros.tif` | `f04da689f1da475c117d2332a84b6c91cb3f2a3febb01818d342678af0652f69` |
| **Hold (`SPACING` hex lattice)** | `releases/h33-h33-2-b2-spacing-lattice-20261023-454c9098.tif` | `454c909877ddd82b91cfb6b6b2f71710524b1d76d37a0f72d0d33107b0f0431d` | `...-zeros.tif` | `56c77db28955ebaae090d0878daa7f258d1d0c7bfe30c6f1279f266e17cf6fab` |

*(Orthogonal `GEMSDOE89` release pairs `RELIEF` `r10`/`r15`/`r15s` and `MASS` `m10uniq`/`m10rand`/`m20uniq` also remain verified in `releases/` and `ledger/submissions.csv`.)*

## 2. DrivenData Upload Steps

1. Log in to DrivenData (`GEMS: Geothermal Exploration with Machine Learning`, challenge `#306`) using the team's single authorized entity account (**3 scored slots/rolling week**).
2. Record **current `TOP_PUBLIC` score + date** and **remaining weekly slots** before submitting.
3. Upload the **primary `.tif`** (NaN outside footprint, matching `sample_submission.tif` encoding).
   - Paste the exact `<=140`-character `form_note` from `ledger/submissions.csv`:
     - `alongstrike`: `h33-h33-2-b2; SPACING alongstrike: 5222/37654 (13.9%) geodesic 1-swap on >=6-dot strands, n=37654; pred +0.002 (-0.003..+0.006)`
     - `poisson`: `h33-h33-2-b2; SPACING poisson: 7639/37654 (20.3%) 2D blue-noise disk in +-150m corridor, n=37654; pred -0.010 (-0.032..+0.004)`
     - `lattice`: `h33-h33-2-b2; SPACING lattice: 7305/37654 (19.4%) 3.5px hex lattice in +-200m corridor, n=37654; pred -0.007 (-0.025..+0.003)`
4. **Only if** the platform scorer rejects NaN outside the footprint, upload the matching `-zeros.tif` fallback twin instead (noting that doing so consumes a submission if the first was scored).

## 3. Recording the Receipt

After scoring completes:
1. Save a timestamped screenshot / receipt record outside public release artifacts if required, and update `ledger/submissions.csv`:
   - `score` and `receipt_score` -> exact 4-decimal live DTI returned by DrivenData
   - `evidence_class` -> `RECEIPT`
   - `receipt` -> `Y`
   - `status` -> `SCORED`
2. Apply the `SLOT_PLAN.md` decision tree (`|Delta| < 0.01` = no evidence).
