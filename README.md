# TESS light-curve provenance and variable-star classification

This repository contains the notebooks, saved study inputs, feature tables, and results supporting:

**Jonathan Liang, “Quantifying the Impact of TESS Light-Curve Provenance on Random Forest Variable-Star Classification.”**

Repository: [TESS_Research_Publication](https://github.com/jonathanliang1/TESS_Research_Publication).

## Study overview

This study compares Random Forest variable-star classification using alternative light-curve representations from the Transiting Exoplanet Survey Satellite (TESS). The controlled comparisons use **506 matched SPOC–TESSCut stars** and **1,353 matched QLP–TESSCut stars**. SPOC is the Science Processing Operations Center; QLP is the Quick-Look Pipeline. The TESSCut representations are this study’s aperture-photometry extractions from full-frame-image cutouts.

Within each comparison, the stars, class labels, 39 predictor definitions, model settings, and star-level train/test assignments are held fixed. The primary analysis uses 100 repeated stratified 70/30 train/test splits. Models are fitted separately for each representation.

| Matched comparison | Official-product mean accuracy | TESSCut mean accuracy | Mean paired accuracy gap |
|---|---:|---:|---:|
| SPOC–TESSCut | 76.6% | 62.8% | 13.7 percentage points |
| QLP–TESSCut | 67.8% | 52.6% | 15.3 percentage points |

The paired gaps were calculated before rounding the individual mean accuracies.

The supporting analyses examine six-feature ablation, per-class paired errors, permutation-importance rankings, conditional detrending, sigma clipping, and aperture/crowding effects. The repository also retains the earlier full-dataset analyses. The controlled samples are subsets of the parent dataset, with their own class distributions and sky coverage.

## Choose what to reproduce

| Goal | Required inputs | Starting point |
|---|---|---|
| Inspect archived results | The saved outputs | Open the summary files under `results/`. |
| Regenerate summaries and figures | The validated saved inputs and outputs, validation helper, feature-validation sidecars, and the recorded configuration | Use notebook 04's saved-result mode once the prerequisites below are in place. |
| Refit the controlled models | The matching metadata and feature tables, run settings, and the saved Gaia caches for crowding analyses | See notebooks 04–08 and the settings below. |
| Reprocess light curves and regenerate features | The repository inputs plus the separate FITS archives | Configure local FITS paths before running the relevant processing sections. |

Start with the saved study inputs when reproducing the archived analyses. They preserve the original VSX sample and TESS acquisition results. Fresh queries can yield a different sample as the source catalogues change.

Use a working copy for reruns and archive the saved outputs for comparison. Several notebooks write to the same paths as the saved results. Replay from saved features covers the model analyses. Repeating the earlier photometry and feature extraction requires the relevant light-curve inputs.

## Repository layout

All paths below are relative to the repository root.

| Location | Contents |
|---|---|
| `notebooks/` | Eight analysis notebooks, listed below |
| `data/VSXCache/` | `VSXMetadata.parquet` and `VSX_TESS_MATCH_Metadata.parquet` |
| `data/TESSCache/` | Full-dataset metadata (`TESSAugmented.parquet` and `TESSAugmented_QC.parquet`), SIMBAD proper-motion cache, and destination for full-dataset FITS files |
| `data/feature_extraction/` | `TESS_features.parquet` and the saved full-dataset detrended feature table |
| `data/SPOC_TESSCutCache/` | SPOC–TESSCut metadata, QC feature tables, and earlier detrended tables; destination for this comparison’s FITS files |
| `data/QLP_TESSCutCache/` | QLP–TESSCut metadata, QC feature tables, and earlier detrended tables; destination for this comparison’s FITS files |
| `data/detrend_tesscut/output/` | Earlier full-dataset detrending metadata, features, and summaries |
| `data/external_cache/vsx/` | `vsx_query_xml.tgz`, containing saved VSX query responses |
| `data/external_cache/gaia/spoc/` and `data/external_cache/gaia/qlp/` | Saved `gaia_neighbors.parquet` files |
| `results/controlled_analysis/` | Full-dataset, representative matched-split, and repeated-split results; persistent splits, predictions, importance estimates, ablation, per-class results, and manifests |
| `results/detrending/` | Controlled detrending results and cached detrended features for SPOC and QLP |
| `results/sigma_clipping/` | Controlled sigma-clipping results and cached clipped-feature tables |
| `results/crowding/spoc/` and `results/crowding/qlp/` | Crowding measures, predictions, and summary tables |

The root also contains `requirements.txt`, `environment.yml`, `CITATION.cff`, and `LICENSE`.

The main controlled inputs are `SPOC_TESSCut_features_QC.parquet` and `SPOC_TESSCut_Metadata_Consolidated_QC.parquet` under `data/SPOC_TESSCutCache/`, with the corresponding `QLP_...` files under `data/QLP_TESSCutCache/`.

The earlier full-dataset detrending files under `data/detrend_tesscut/` are separate from the controlled experiment in notebook 05 and `results/detrending/`.

## Environment and local setup

Use `requirements.txt` or `environment.yml` to set up a dedicated environment. For the archived controlled runs, the manifests record Python 3.13.0, NumPy 2.5.1, pandas 3.0.1, and scikit-learn 1.8.0. Consult the run manifests for the recorded configuration and platform when reproducing the saved results.

For example, from a local clone or downloaded copy of this repository:

```bash
cd /path/to/TESS_Research_Publication
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install jupyterlab ipykernel
export Project_Root="$(pwd)"
python -m jupyter lab
```

Select a notebook kernel using this environment. If launching the kernel separately, set `Project_Root` in that kernel’s environment before running notebook configuration cells.

Set `Project_Root` to the local repository directory. The notebooks have an author-specific fallback path. Resolve absolute FITS paths stored in parquet metadata separately, as described below. Saved-run validation also checks paths, file hashes, and recorded software settings.

## Notebook guide and saved-input settings

Read the notebooks in numerical order to follow the research workflow. For model reruns, start at notebook 04 with the validated feature inputs and metadata.

| Notebook | Purpose and behavior with saved inputs |
|---|---|
| `01_data_pipeline.ipynb` | Sample construction, catalogue matching, acquisition, standardization, QC, and supporting diagnostics. Chapter 5 includes FITS processing. |
| `02_feature_extraction.ipynb` | Feature extraction from light curves and reuse of cached feature tables. Confirm the input and cache validation requirements before running extraction. |
| `03_analyze_comprehensive.ipynb` | Full-dataset models, representative matched comparisons, and exploratory diagnostics. Refits models and writes results. Keep the saved train/validation/test tables and all three phase-morphology caches together; retain `ForceRecomputePhaseFeatures=False`. Missing or incompatible morphology caches trigger FITS access. |
| `04_controlled_analysis_monte_carlo.ipynb` | Main 100-split comparisons, ablation, paired errors, repeated importance, and the check of the 20 selected importance splits. Can load saved results or refit models. |
| `05_controlled_detrending.ipynb` | Loads saved detrended features when `RUN_DETRENDING_FROM_FITS=False`. Still refits models across 100 splits and writes results. |
| `06_tesscut_sigma_clipping_controlled.ipynb` | Loads saved clipped features when `RUN_SIGMA_CLIPPING_FROM_FITS=False`. Still refits models and evaluates importance. |
| `07_spoc_tess_aperture_crowding.ipynb` | SPOC–TESSCut crowding/aperture analysis. Set `RUN_GAIA_QUERY=False` to use the supplied Gaia cache. No FITS files are needed. |
| `08_qlp_tesscut_aperture_crowding.ipynb` | QLP–TESSCut counterpart. Set `RUN_GAIA_QUERY=False` to use the supplied Gaia cache. No FITS files are needed. |

### Main controlled analysis (notebook 04)

Open the saved summaries in `results/controlled_analysis/` to inspect the archived results. Before using the saved-result workflow, obtain the matching `tess_research_validation.py` helper and the `QLP_TESSCut_features_QC.parquet.science_fix.json` and `SPOC_TESSCut_features_QC.parquet.science_fix.json` sidecars referenced by the manifests. Keep the sidecars with their feature tables and use the matching input and output hashes, paths, and software configuration recorded in the manifests.

For regeneration from validated saved results, use these settings.

```python
RUN_MONTE_CARLO = False
RUN_REPEATED_PERMUTATION_IMPORTANCE = True
RUN_METADATA_ABLATION = False
```

The first two settings are in the main configuration cell. Set `RUN_METADATA_ABLATION` in the ablation configuration cell. The permutation setting matches the archived full-run manifest. The saved-result path can write new summary tables and figures after validation. Use a working copy.

For a deliberate refit of the repeated-split, permutation-importance, and ablation analyses, enable all three flags with validated saved feature inputs. Archive the saved results first so you can compare the refit with the published analysis.

### Controlled detrending and clipping: notebooks 05 and 06

Keep `RUN_DETRENDING_FROM_FITS=False` in notebook 05 to read:

- `results/detrending/SPOC/TESSCut_conditional_detrended_features.parquet`
- `results/detrending/QLP/TESSCut_conditional_detrended_features.parquet`

Keep `RUN_SIGMA_CLIPPING_FROM_FITS=False` in notebook 06 to read:

- `results/sigma_clipping/SPOC_TESSCut_features_sigma_clipped.parquet`
- `results/sigma_clipping/QLP_TESSCut_features_sigma_clipped.parquet`

With these settings, both notebooks refit models from saved features and write new results. Notebook 05 uses `RUN_LIGHT_CURVE_STANDARDIZATION` within the FITS-processing branch.

### Crowding: notebooks 07 and 08

Set `RUN_GAIA_QUERY=False` in both notebooks to use the saved `gaia_neighbors.parquet` file in each configured cache folder.

These notebooks use the saved extraction metadata for aperture measurements and the cached Gaia data for crowding. They recalculate the crowding measures and model results.

## FITS data availability and extraction

The stored pre-standardization and standardized light-curve FITS files, including the study-specific TESSCut extractions, comprise approximately 24.22 GB in compressed archives. Attempts to deposit the archives in Zenodo encountered transfer problems. The author retains the files and provides them on reasonable request using the contact details in the manuscript. The saved feature tables support model analyses from the extracted features.

| Archive | Contents | Destination |
|---|---|---|
| `tesscache.tgz` | Full-dataset SPOC, QLP, and TESSCut light curves, pre-standardization and standardized | `data/TESSCache/` |
| `spoc_tesscutcache.tgz` | Controlled SPOC–TESSCut light curves, pre-standardization and standardized | `data/SPOC_TESSCutCache/` |
| `qlp_tesscutcache.tgz` | Controlled QLP–TESSCut light curves, pre-standardization and standardized | `data/QLP_TESSCutCache/` |

Before extraction, inspect the archive’s top-level entries, for example:

```bash
tar -tzf /path/to/tesscache.tgz | head -n 20
```

If the archive already includes `TESSCache/` as its top-level directory, extract it into `data/`. If it contains only that directory’s contents, extract it into `data/TESSCache/`. Apply the same rule to the other two archives. Preserve internal subdirectories and avoid duplicate nesting such as `data/TESSCache/TESSCache/`. If an archive contains metadata or feature parquets, retain the versions supplied with the code release when adding the FITS files.

These archives support reprocessing from saved light curves. Repeating the earlier photometric extraction requires the source TESS image cutouts, available through MAST. The acquisition and extraction procedures are documented in notebook 01.

### Before reprocessing FITS files

Some FITS settings in the supplied notebooks still refer to an earlier `data/raw/` layout. Check them against the actual archive contents and the `lightCurvePath` / `rawLightCurvePath` values in the metadata:

| Notebook | Settings or code to check |
|---|---|
| 01 | `TESS_CACHE_FOLDER` and the two comparison-cache folder settings |
| 02 | `fitsBasePath` in `ExtractFeaturesForRow` |
| 03 | The optional phase-morphology FITS path resolver |
| 05 and 06 | `RawDataRoot` and the FITS path resolvers |

Choose the base path that resolves the recorded relative paths to the extracted files. Remap absolute paths from the original computer in a working copy and verify the required files before starting extraction.

For a deliberate extraction rerun, check notebook 02’s cache and recomputation logic in a working copy. Preserve the archived feature tables before writing new outputs. The detrended cases also require their corresponding derived light curves.

After configuring and checking FITS paths, set `RUN_DETRENDING_FROM_FITS=True` in notebook 05 or `RUN_SIGMA_CLIPPING_FROM_FITS=True` in notebook 06 to repeat those processing steps.

The archive includes `data/TESSCache/SimbadProperMotion.parquet` for the optional proper-motion diagnostic in notebook 01. Set the diagnostic’s input path to that file if the local configuration uses a different cache directory. The controlled classification tests use the saved matched feature tables.

## Preserve the catalogue snapshot

For the recorded study sample, keep these notebook 01 query/download controls disabled:

```python
RUN_VSX_CATALOG_QUERY = False
RUN_XRAY_SPECIAL_REFRESH = False
RUN_VSX_405_TARGETED_RECOVERY = False
RUN_TESS_MATCH = False
RUN_TESS_LIGHT_CURVE_DOWNLOAD = False
RUN_SIMBAD_PROPER_MOTION = False
RUN_COMPARABLE_SPOC_TESS_DOWNLOAD = False
RUN_COMPARABLE_QLP_TESS_DOWNLOAD = False
```

Check each control in its own section. Other cells can still process FITS or update local metadata. Use a working copy when running notebook 01 because it can rewrite `TESSAugmented.parquet` and consolidate comparison metadata.

### Archived VSX responses

`data/external_cache/vsx/vsx_query_xml.tgz` contains 1,376 saved VSX XML/VOTable responses. The study’s `data/VSXCache/VSXMetadata.parquet` contains 8,062 stars and references 826 of those XML files. Extraction is unnecessary when using the saved sample and features.

The earlier snapshot audit found all 826 referenced XML files and exact matches for the saved `rawRow` records. The referenced files had recorded modification dates of 27 June 2026 for 8,000 non-XRAY stars and 29 August 2026 for 62 XRAY stars, consistent with the later XRAY-only refresh. These are filesystem modification dates.

To inspect the archived responses, extract only the XML files from the repository root:

```bash
tar -xzf data/external_cache/vsx/vsx_query_xml.tgz \
    -C data/external_cache/vsx \
    --strip-components=1 --wildcards 'VSXCache/*.xml'
```

This excludes the archive’s other files and leaves `data/VSXCache/VSXMetadata.parquet` untouched. Existing XML files with the same names will be replaced. Resolve the original `sourceXmlFile` paths by filename under `data/external_cache/vsx/` when inspecting them on another computer.

## Saved results and traceability

`results/controlled_analysis/` includes the `monte_carlo_*` and `metadata_ablation_*` outputs, split assignments, paired predictions, fixed feature lists, importance summaries, per-class tables, and run manifests. The archived `paper_asset_manifest.json` and `paper_figure_traceability_output.csv` are in that directory. The paper export cells write regenerated assets under `results/controlled_analysis/paper_assets_output/` when the saved-run prerequisites are satisfied. The detrending, sigma-clipping, and crowding directories retain their corresponding feature tables and summaries.

Use the saved split assignments and feature definitions when checking a rerun against the paper. Record the repository commit or release and the software environment used. If inputs, preprocessing, software, or split settings differ, record those differences alongside the new results.

## External data, citation, and license

The study uses VSX, TESS/MAST, the TESS Input Catalog, SIMBAD, and Gaia DR3. Follow the citation and usage requirements of those catalogues, missions, and software packages.

Cite the software using [`CITATION.cff`](CITATION.cff) and identify the release tag or commit used. Cite the associated manuscript when a citable record is available.

The original code and repository-authored documentation are released under the MIT License. See [`LICENSE`](LICENSE). Third-party astronomical data retain their original terms and citation requirements.
