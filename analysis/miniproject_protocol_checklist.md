# Miniproject Protocol Checklist

This checklist follows the order in `MacGregor Miniproject Oxytocin Spiking Model.pdf` and `CMML Workshop 5.2.pdf`.

## 1. Freeze the spike-fit models

Use these as the working models unless a later GUI run clearly improves them.

### MAL11E

- `baseline + AHP`:
  - `PSP Rate = 400`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.05`
  - `halflifeAHP = 300`
  - `kDAP = 0`
  - `useNMDA = 0`
- `simple DAP`:
  - `PSP Rate = 380`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.05`
  - `halflifeAHP = 300`
  - `kDAP = 0.6`
  - `halflifeDAP = 80`
  - `useNMDA = 0`
- `NMDA-only`:
  - `PSP Rate = 350`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.05`
  - `halflifeAHP = 300`
  - `kDAP = 0`
  - `useNMDA = 1`
  - `NMDA PSP Mag = 0.8`
  - `NMDA PSP Rate = 350`
  - `NMDA PSP HL = 120`
  - `NMDA Sync = 0`

### CBA1R8C1

- `baseline + AHP`:
  - `PSP Rate = 340`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.10`
  - `halflifeAHP = 300`
  - `kDAP = 0`
  - `useNMDA = 0`
- `simple DAP`:
  - `PSP Rate = 330`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.10`
  - `halflifeAHP = 300`
  - `kDAP = 0.8`
  - `halflifeDAP = 80`
  - `useNMDA = 0`
- `NMDA-only`:
  - `PSP Rate = 318`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.10`
  - `halflifeAHP = 300`
  - `kDAP = 0`
  - `useNMDA = 1`
  - `NMDA PSP Mag = 0.8`
  - `NMDA PSP Rate = 300`
  - `NMDA PSP HL = 120`
  - `NMDA Sync = 0`

## 2. Save the six key spike-fitting screenshots

- `MAL11E baseline`
- `MAL11E simple DAP`
- `MAL11E NMDA-only`
- `CBA1R8C1 baseline`
- `CBA1R8C1 simple DAP`
- `CBA1R8C1 NMDA-only`

Each screenshot should show:

- `Cell Hist 5ms`
- `Mod Hist 5ms`
- `Cell Haz 5ms`
- `Mod Haz 5ms`
- `IoD Cell`
- `IoD Mod`

## 3. Miniproject main secretion test: fitted DAP model at low firing

Use the `MAL11E simple DAP` model first.

- Change plots to:
  - `memV`
  - `secB`
  - `secE`
  - `secC`
  - `secX`
  - `secPlasma`
- Set `PSP Rate = 150`
- Run and inspect how individual spikes drive:
  - broadening (`secB`)
  - fast calcium (`secE`)
  - slow calcium (`secC`)
  - secretion rate (`secX`)
  - plasma concentration (`secPlasma`)

Capture one screenshot for this step.

## 4. Miniproject main secretion sweep: fitted DAP model

Use the `MAL11E simple DAP` model and sweep:

- `PSP Rate = 150, 200, 250, 300, 330, 360, 390, 420`

For each run, record:

- model `Freq`
- steady `secPlasma`

Use `analysis/secretion_protocol_sweeps.csv` as the precomputed table.

Capture:

- one screenshot of the plasma plot at a low rate
- one screenshot at a higher rate

## 5. Workshop-style comparison: baseline + AHP secretion sweep

Use the `MAL11E baseline + AHP` model and run the same `PSP Rate` sweep.

Main question:

- how does the fitted DAP secretion curve compare against the baseline fitted spike model?

## 6. Workshop 5.2 task 5: remove AHP and repeat the sweep

Keep the `MAL11E baseline` parameters, but set:

- `kAHP = 0`

Run the same `PSP Rate` sweep.

Main question:

- at matched input rates, how does removing AHP change:
  - spike rate
  - stable plasma concentration

## 7. Optional extension: teacher-style NMDA secretion

Only do this if time remains.

- Use `CBA1R8C1 NMDA-only`
- Repeat a small sweep at `PSP Rate = 250, 300, 318, 340`
- Use this as a qualitative comparison, not the main secretion result

## 8. Final report structure

- Main cell: `MAL11E`
- Validation cell: `CBA1R8C1`
- Main fitted model for secretion section: `MAL11E simple DAP`
- Main comparison figures for secretion:
  - `simple DAP`
  - `baseline + AHP`
  - `baseline without AHP`
