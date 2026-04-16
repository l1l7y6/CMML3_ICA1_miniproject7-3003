# Work Log

## Project aim

Model the depolarising afterpotential (DAP) in oxytocin neurons using the Week 5 HypoMod framework, compare a simple DAP against an NMDA-based formulation, fit selected recordings, and then test secretion and signal-processing consequences.

## Data selection

Selected recordings from `oxydata dap cells.xlsx`:

- `MAL11E` as the main result cell
- `CBA1R8C1` as the validation cell

Rationale:

- `MAL11E` gave the clearest and most teachable DAP-like short-ISI shoulder.
- `CBA1R8C1` provided a second DAP-like recording with slightly different fitting behaviour.

## Model development

### Existing baseline model

- integrate-and-fire membrane
- fast PSP input
- HAP
- AHP
- secretion model (`secB`, `secE`, `secC`, `secX`, `secPlasma`)

### Simple DAP branch

- implemented as a spike-triggered positive afterpotential
- key parameters:
  - `kDAP`
  - `halflifeDAP`

### NMDA branch

Final NMDA implementation was aligned to the teacher starter code:

- extra slow NMDA PSP pathway
- parameters:
  - `NMDA PSP Mag`
  - `NMDA PSP Rate`
  - `NMDA PSP HL`
  - `NMDA Sync`

Literature-inspired extension:

- a simple voltage dependence was retained in the NMDA branch
- this should be described as an exploratory extension, not as a separately validated result

## Workshop-style baseline fitting logic

Followed Workshop 5.2 order:

1. fit `PSP rate + HAP` against spike rate and ISI histogram
2. add `AHP` and judge whether it improves `IoD` without damaging spike-rate/histogram fit
3. freeze baseline before comparing `simple DAP` and `NMDA`

## Working parameter sets

### MAL11E

- `baseline + AHP`
  - `PSP Rate = 400`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.05`
  - `halflifeAHP = 300`
- `simple DAP`
  - `PSP Rate = 380`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.05`
  - `halflifeAHP = 300`
  - `kDAP = 0.6`
  - `halflifeDAP = 80`
- `NMDA-only`
  - `PSP Rate = 350`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.05`
  - `halflifeAHP = 300`
  - `NMDA PSP Mag = 0.8`
  - `NMDA PSP Rate = 350`
  - `NMDA PSP HL = 120`
  - `NMDA Sync = 0`

### CBA1R8C1

- `baseline + AHP`
  - `PSP Rate = 340`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.10`
  - `halflifeAHP = 300`
- `simple DAP`
  - `PSP Rate = 330`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.10`
  - `halflifeAHP = 300`
  - `kDAP = 0.8`
  - `halflifeDAP = 80`
- `NMDA-only`
  - `PSP Rate = 318`
  - `kHAP = 50`
  - `halflifeHAP = 8`
  - `kAHP = 0.10`
  - `halflifeAHP = 300`
  - `NMDA PSP Mag = 0.8`
  - `NMDA PSP Rate = 300`
  - `NMDA PSP HL = 120`
  - `NMDA Sync = 0`

## Spike-fitting conclusions

### MAL11E

- baseline alone did not explain the DAP-like short-ISI clustering
- simple DAP gave the cleanest and most stable improvement
- the teacher-style NMDA branch worked, but did not outperform simple DAP on this recording

### CBA1R8C1

- baseline again underfit the short-ISI clustering and `IoD`
- simple DAP improved the histogram/hazard fit
- teacher-style NMDA performed competitively and gave a credible alternative explanation on this recording

## Secretion sweep results

Precomputed from the current code using the `MAL11E` main-result pathway.

Protocol note:

- for the miniproject, the main secretion result should use the fitted DAP model
- the baseline + AHP and no-AHP curves are retained as workshop-style comparisons

### Baseline + AHP

- `PSP Rate 150 -> Freq 0.804 Hz, Plasma 0.6589`
- `PSP Rate 200 -> Freq 1.637 Hz, Plasma 1.9855`
- `PSP Rate 250 -> Freq 2.750 Hz, Plasma 4.5166`
- `PSP Rate 300 -> Freq 3.831 Hz, Plasma 10.0990`
- `PSP Rate 330 -> Freq 4.559 Hz, Plasma 13.1958`
- `PSP Rate 360 -> Freq 5.086 Hz, Plasma 17.9693`
- `PSP Rate 390 -> Freq 5.772 Hz, Plasma 21.2850`
- `PSP Rate 420 -> Freq 6.352 Hz, Plasma 28.8190`

### Baseline without AHP

- `PSP Rate 150 -> Freq 0.828 Hz, Plasma 0.6461`
- `PSP Rate 200 -> Freq 1.750 Hz, Plasma 2.2097`
- `PSP Rate 250 -> Freq 2.785 Hz, Plasma 5.1704`
- `PSP Rate 300 -> Freq 3.984 Hz, Plasma 10.5064`
- `PSP Rate 330 -> Freq 4.680 Hz, Plasma 13.2632`
- `PSP Rate 360 -> Freq 5.334 Hz, Plasma 17.6914`
- `PSP Rate 390 -> Freq 6.047 Hz, Plasma 25.3549`
- `PSP Rate 420 -> Freq 6.543 Hz, Plasma 31.7281`

### Simple DAP

- `PSP Rate 150 -> Freq 0.793 Hz, Plasma 0.7078`
- `PSP Rate 200 -> Freq 1.723 Hz, Plasma 2.0199`
- `PSP Rate 250 -> Freq 2.815 Hz, Plasma 4.6802`
- `PSP Rate 300 -> Freq 4.120 Hz, Plasma 10.1709`
- `PSP Rate 330 -> Freq 4.906 Hz, Plasma 17.4002`
- `PSP Rate 360 -> Freq 5.682 Hz, Plasma 23.6807`
- `PSP Rate 390 -> Freq 6.192 Hz, Plasma 27.0538`
- `PSP Rate 420 -> Freq 7.055 Hz, Plasma 36.3513`

Full table saved in `analysis/secretion_protocol_sweeps.csv`.

## Secretion conclusions

- increasing input rate increases both spike rate and stable plasma concentration
- removing AHP tends to increase spike rate and plasma concentration at the same input rate, especially at higher PSP rates
- adding simple DAP shifts the spike-rate/plasma mapping upward relative to the baseline + AHP model

## Recommended report narrative

- use `MAL11E` as the main cell because it is the clearest DAP exemplar
- use `CBA1R8C1` as the validation cell
- present `simple DAP` as the strongest model on `MAL11E`
- present the teacher-style `NMDA` branch as literature-guided and competitive on `CBA1R8C1`
- use secretion results mainly from the `MAL11E` pathway
- lead the secretion section with the fitted `simple DAP` model, because the miniproject specifically asks to test the fitted DAP model
- then compare it against:
  - baseline + AHP
  - baseline without AHP
