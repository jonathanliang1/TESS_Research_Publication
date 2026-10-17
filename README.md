# TESS light-curve provenance and variable-star classification

This repository contains the notebooks, saved study inputs, feature tables, and results supporting:

**Jonathan Liang, “Quantifying the Impact of TESS Light-Curve Provenance on Random Forest Variable-Star Classification.”**

Prepared for submission to *RAS Techniques and Instruments (RASTI)*.

Repository: [TESS_Research_RASTI_Publication](https://github.com/jonathanliang1/TESS_Research_RASTI_Publication).

## Study overview

This study compares Random Forest variable-star classification using alternative light-curve representations from the Transiting Exoplanet Survey Satellite (TESS). The controlled comparisons use **506 matched SPOC–TESSCut stars** and **1,355 matched QLP–TESSCut stars**. SPOC is the Science Processing Operations Center; QLP is the Quick-Look Pipeline. The TESSCut representations are this study’s aperture-photometry extractions from full-frame-image cutouts.

Within each comparison, the stars, class labels, 39 predictor definitions, model settings, and star-level train/test assignments are held fixed. The primary analysis uses 100 repeated stratified 70/30 train/test splits. Models are fitted separately for each representation.

| Matched comparison | Official-product mean accuracy | TESSCut mean accuracy | Mean paired accuracy gap |
|---|---:|---:|---:|
| SPOC–TESSCut | 76.5% | 62.8% | 13.7 percentage points |
| QLP–TESSCut | 67.6% | 52.5% | 15.1 percentage points |

The supporting analyses examine six-feature ablation, per-class paired errors, permutation-importance rankings, conditional detrending, sigma clipping, and aperture/crowding effects. The repository also retains the earlier full-dataset analyses. The controlled samples were drawn from the parent dataset; they are not assumed to preserve its class or sky coverage.

## Choose what to reproduce

| Goal | Required inputs | Starting point |
|---|---|---|
| Inspect the main results and regenerate summaries/figures | Saved files in Git | Notebook 04 with its three analysis flags set to `False` |
| Refit the controlled models | Saved metadata, feature tables, and Gaia caches in Git | Notebooks 04–08, using the settings below |
| Reprocess light curves and regenerate features | Git files plus the separate FITS archives | Configure local FITS paths before running the relevant processing sections |

New VSX queries and new TESS downloads are **not required** to repeat the analyses from the saved study inputs. Live catalogues can change, so a fresh query is not expected to reproduce the archived sample exactly.

Use a working copy for reruns. Several notebooks write to the same paths as the saved results. Preserve the release files for comparison. Reproducing results from saved features does not independently check the earlier photometry and feature-extraction steps.

## Repository layout

All paths below are relative to the repository root.

| Location | Contents |
|---|---|
| `notebooks/` | Eight analysis notebooks, listed below |
| `data/VSXCache/` | `VSXMetadata.parquet` and `VSX_TESS_MATCH_Metadata.parquet` |
| `data/TESSCache/` | Full-dataset metadata: `TESSAugmented.parquet` and `TESSAugmented_QC.parquet`; destination for full-dataset FITS files |
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

The recorded analysis environment used Python 3.13. See `requirements.txt` and `environment.yml` for dependencies. Use a dedicated environment rather than installing into the system Python environment.

For example, from a local clone or downloaded copy of this repository:

```bash
cd /path/to/TESS_Research_RASTI_Publication
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install jupyterlab ipykernel
export Project_Root="$(pwd)"
python -m jupyter lab
```

Select a notebook kernel using this environment. If launching the kernel separately, set `Project_Root` in that kernel’s environment before running notebook configuration cells.

All eight notebooks read `Project_Root`. Their fallback path is specific to the author’s computer. Setting this variable configures the repository location, but does **not** rewrite absolute FITS paths stored inside parquet tables. Additional path configuration is needed for FITS reprocessing, as described below.

## Notebook guide and saved-input settings

Read the notebooks in numerical order to follow the research workflow. It is not necessary to run notebooks 01–03 before notebook 04 when using the supplied tables.

| Notebook | Purpose and behavior with saved inputs |
|---|---|
| `01_data_pipeline.ipynb` | Sample construction, catalogue matching, acquisition, standardization, QC, and supporting diagnostics. Not needed for model reruns from saved features. Its Chapter 5 still attempts FITS processing, so `Run All` is not a saved-table-only workflow. |
| `02_feature_extraction.ipynb` | Loads each configured feature parquet if it exists; otherwise extracts features from FITS. The repository supplies all six configured feature tables. There is currently no `RUN_FEATURE_EXTRACTION` switch. |
| `03_analyze_comprehensive.ipynb` | Full-dataset models, representative matched comparisons, and exploratory diagnostics. Refits models and writes results. Keep the saved train/validation/test tables and all three phase-morphology caches together; retain `ForceRecomputePhaseFeatures=False`. Missing or incompatible morphology caches trigger FITS access. |
| `04_controlled_analysis_monte_carlo.ipynb` | Main 100-split comparisons, ablation, paired errors, repeated importance, and the check of the 20 selected importance splits. Can load saved results or refit models. |
| `05_controlled_detrending.ipynb` | Loads saved detrended features when `RUN_DETRENDING_FROM_FITS=False`. Still refits models across 100 splits and writes results. |
| `06_tesscut_sigma_clipping_controlled.ipynb` | Loads saved clipped features when `RUN_SIGMA_CLIPPING_FROM_FITS=False`. Still refits models and evaluates importance. |
| `07_spoc_tess_aperture_crowding.ipynb` | SPOC–TESSCut crowding/aperture analysis. Set `RUN_GAIA_QUERY=False` to use the supplied Gaia cache. No FITS files are needed. |
| `08_qlp_tesscut_aperture_crowding.ipynb` | QLP–TESSCut counterpart. Set `RUN_GAIA_QUERY=False` to use the supplied Gaia cache. No FITS files are needed. |

### Main controlled analysis: notebook 04

To load the saved results and regenerate summaries and figures, retain:

```python
RUN_MONTE_CARLO = False
RUN_REPEATED_PERMUTATION_IMPORTANCE = False
RUN_METADATA_ABLATION = False
```

The first two settings are in the main configuration cell; `RUN_METADATA_ABLATION` is defined later in the ablation section. Saved-result mode can still write summary tables and figures.

To recompute the complete repeated-split, permutation-importance, and ablation analyses from the saved features, set all three flags to `True` at their configuration locations. No FITS files are required. Preserve existing outputs first: recomputing the main models with permutation evaluation disabled does not regenerate the saved importance results and can replace their output files.

### Controlled detrending and clipping: notebooks 05 and 06

Keep `RUN_DETRENDING_FROM_FITS=False` in notebook 05 to read:

- `results/detrending/SPOC/TESSCut_conditional_detrended_features.parquet`
- `results/detrending/QLP/TESSCut_conditional_detrended_features.parquet`

Keep `RUN_SIGMA_CLIPPING_FROM_FITS=False` in notebook 06 to read:

- `results/sigma_clipping/SPOC_TESSCut_features_sigma_clipped.parquet`
- `results/sigma_clipping/QLP_TESSCut_features_sigma_clipped.parquet`

These flags bypass light-curve processing, **not model fitting**. Both notebooks still calculate new model results. Notebook 05’s separate `RUN_LIGHT_CURVE_STANDARDIZATION=True` setting applies within its FITS-processing branch.

### Crowding: notebooks 07 and 08

Set `RUN_GAIA_QUERY=False` in **both** notebooks before running. The supplied notebooks currently set this flag to `True`; disabling it explicitly prevents new Gaia queries. Keep the corresponding saved `gaia_neighbors.parquet` file in each configured cache folder.

The aperture measurements are read from saved extraction metadata. These notebooks recalculate crowding measures and model results without opening FITS files.

## FITS data availability and extraction

The raw and standardized light-curve FITS files are distributed separately because of their size. A public archive download link is not yet provided here. To request the files, contact the author using the contact details in the associated manuscript. The repository already includes the feature tables needed for the model analyses described above.

| Archive | Contents | Destination |
|---|---|---|
| `tesscache.tgz` | Full-dataset SPOC, QLP, and TESSCut light curves, raw and standardized | `data/TESSCache/` |
| `spoc_tesscutcache.tgz` | Controlled SPOC–TESSCut light curves, raw and standardized | `data/SPOC_TESSCutCache/` |
| `qlp_tesscutcache.tgz` | Controlled QLP–TESSCut light curves, raw and standardized | `data/QLP_TESSCutCache/` |

Before extraction, inspect the archive’s top-level entries, for example:

```bash
tar -tzf /path/to/tesscache.tgz | head -n 20
```

If the archive already includes `TESSCache/` as its top-level directory, extract it into `data/`. If it contains only that directory’s contents, extract it into `data/TESSCache/`. Apply the same rule to the other two archives. Preserve internal subdirectories and avoid duplicate nesting such as `data/TESSCache/TESSCache/`. If an archive contains metadata or feature parquets, retain the versions supplied with the code release when adding the FITS files.

These archives support reprocessing from saved light curves. They do not by themselves reproduce the earlier photometric extraction from TESS image cutouts. The source TESS observations are available through MAST; the acquisition and extraction procedures are documented in notebook 01.

### Before reprocessing FITS files

Some FITS settings in the supplied notebooks still refer to an earlier `data/raw/` layout. Check them against the actual archive contents and the `lightCurvePath` / `rawLightCurvePath` values in the metadata:

| Notebook | Settings or code to check |
|---|---|
| 01 | `TESS_CACHE_FOLDER` and the two comparison-cache folder settings |
| 02 | `fitsBasePath` in `ExtractFeaturesForRow` |
| 03 | The optional phase-morphology FITS path resolver |
| 05 and 06 | `RawDataRoot` and the FITS path resolvers |

Choose the base path that resolves the recorded relative paths to the extracted files. Absolute paths from the original computer need explicit remapping in a working copy. Verify required files before starting extraction; changing `Project_Root` alone is insufficient for those absolute paths.

Notebook 02 skips extraction while its output feature parquets exist. For a deliberate extraction rerun, preserve those outputs and use a separate working copy with the intended output tables absent, or add an explicit recomputation control. Its additional detrended cases also require the corresponding derived light curves or regeneration of those files.

After configuring and checking FITS paths, set `RUN_DETRENDING_FROM_FITS=True` in notebook 05 or `RUN_SIGMA_CLIPPING_FROM_FITS=True` in notebook 06 to repeat those processing steps.

The optional proper-motion diagnostic in notebook 01 expects `data/external_cache/SimbadProperMotion.parquet`. This file is not included in this repository; that diagnostic needs the original cache or a separate SIMBAD query. It is not an input to the main controlled classification tests.

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

The controls occur in several sections; check each definition before running its section. They disable their respective queries and downloads but do not prevent other cells from processing FITS files or updating local metadata. In particular, notebook 01 can filter and rewrite `TESSAugmented.parquet`, and comparison-metadata consolidation is enabled in the supplied configuration.

### Archived VSX responses

`data/external_cache/vsx/vsx_query_xml.tgz` contains 1,376 saved VSX XML/VOTable responses. The study’s `data/VSXCache/VSXMetadata.parquet` contains 8,062 stars and references 826 of those XML files. Extraction is unnecessary when using the saved sample and features.

The earlier snapshot audit found all 826 referenced XML files and exact matches for the saved `rawRow` records. The referenced files had recorded modification dates of 27 June 2026 for 8,000 non-XRAY stars and 29 August 2026 for 62 XRAY stars, consistent with the later XRAY-only refresh. Modification dates are not independent verification of download dates.

To inspect the archived responses, extract only the XML files from the repository root:

```bash
tar -xzf data/external_cache/vsx/vsx_query_xml.tgz \
    -C data/external_cache/vsx \
    --strip-components=1 --wildcards 'VSXCache/*.xml'
```

This excludes the archive’s other files and leaves `data/VSXCache/VSXMetadata.parquet` untouched. Existing XML files with the same names will be replaced. Resolve the original `sourceXmlFile` paths by filename under `data/external_cache/vsx/` when inspecting them on another computer.

## Saved results and traceability

`results/controlled_analysis/` includes the `monte_carlo_*` and `metadata_ablation_*` outputs, split assignments, paired predictions, fixed feature lists, importance summaries, per-class tables, and run manifests. `paper_asset_manifest.json` and `paper_figure_traceability_output.csv` record figure/output traceability. The detrending, sigma-clipping, and crowding directories retain their corresponding feature tables and summaries.

Use the saved split assignments and feature definitions when checking a rerun against the paper. Record the repository commit or release and the software environment used. Differences after changing inputs, preprocessing, software, or split settings should be examined rather than treated as a reproduction of the archived run.

## External data, citation, and license

The study uses VSX, TESS/MAST, the TESS Input Catalog, SIMBAD, and Gaia DR3. Follow the citation and usage requirements of those catalogues, missions, and software packages.

If using this work, cite the associated manuscript and the software metadata in [`CITATION.cff`](CITATION.cff). Identify the release tag or commit used.

The original code and repository-authored documentation are released under the MIT License; see [`LICENSE`](LICENSE). Third-party astronomical data retain their original terms and citation requirements. The MIT License does not relicense those data.
