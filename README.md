# CMML3 ICA1 Mini-project 7

This repository contains my CMML3 ICA1 mini-project on modelling the depolarising afterpotential (DAP) in oxytocin neurones using the supplied HypoMod framework.

## Main files

- `SpikeModPython.py`: GUI entry point
- `spikemod.py`: main spiking and secretion model
- `spikepanels.py`: parameter panel definitions
- `tools/prepare_selected_dap_data.py`: export the selected recordings from the raw spreadsheet
- `tools/fit_selected_dap_baseline.py`: headless baseline fit sweep
- `tools/generate_ica1_results.py`: generate the report-ready comparison tables and figures
- `tools/build_word_docs.py`: build the report/supporting `.docx` files from the Markdown sources
- `tools/rebuild_submission.py`: one-command rebuild for the submission outputs

## Model changes

- Added a simple spike-triggered DAP branch to the integrate-and-fire model
- Added an NMDA-based alternative DAP branch with a simple voltage dependence
- Added optional scheduled PSP-rate input for reproducible varying-input tests
- Preserved the secretion model (`secB`, `secE`, `secC`, `secX`, `secPlasma`) for downstream analysis

## Environment

- Recommended platform: Windows with Python 3.12
- Install dependencies with `pip install -r requirements.txt`
- `wxPython` is required because the supplied HypoMod code still depends on `wx`, even for the headless analysis scripts

## Quick reproduction

Rebuild the final analysis outputs and Word documents with:

```bash
python tools/rebuild_submission.py
```

This runs the headless figure/table generation and rebuilds the report/supporting `.docx` files.

If you want to run the steps separately:

```bash
python tools/generate_ica1_results.py
python tools/build_word_docs.py
```

The main outputs are written to `analysis/`, including:

- `ica1_figure1_spike_fits.png`
- `ica1_figure2_system_outputs.png`
- `ica1_supplementary_figure_s1_fit_breakdown.png`
- `ica1_supplementary_figure_s2_numeric_summaries.png`
- `ica1_model_comparison.csv`
- `ica1_secretion_sweeps.csv`
- `ica1_varying_input_summary.csv`
- `ica1_parameter_sets.json`

## Rebuilding the selected-recording CSV from the raw spreadsheet

The repository already includes `data/selected_dap_recordings.csv`, so the submitted figures/tables can be reproduced without the original spreadsheet.

If the raw spreadsheet is available, regenerate the selected-recording export with:

```bash
python tools/prepare_selected_dap_data.py --source "path\\to\\oxydata dap cells.xlsx"
```

You can also set the environment variable `CMML3_ICA1_SOURCE_XLSX` instead of passing `--source`.

## Scoring note

- The final model-comparison score in `tools/generate_ica1_results.py` is a weighted fit score where lower is better
- The formula is `0.25 * freq_error + 0.30 * hist_error + 0.20 * haz_error + 0.25 * iod_error`
- Histogram and hazard errors are taken from the first 40 bins (`0-200 ms`), and IoD error is taken from the first 7 IoD points
- The earlier baseline search in `tools/fit_selected_dap_baseline.py` uses a two-stage version of the same idea: stage 1 uses firing rate, histogram and hazard; stage 2 adds IoD for the final comparison
