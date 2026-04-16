from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import wx

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from HypoModPy.hypospikes import NeuroDat, SpikeDat
from spikemod import SecData, SpikeModel, StateData

matplotlib.use("Agg")
import matplotlib.pyplot as plt


wx.QueueEvent = lambda *args, **kwargs: None

ANALYSIS_DIR = Path("analysis")
SELECTED_RECORDINGS_CSV = Path("data/selected_dap_recordings.csv")
HEADER_ROWS = 5
FIT_RUNTIME_S = 360
SWEEP_RUNTIME_S = 240
VARYING_INPUT_RUNTIME_S = 750
SECRETION_SWEEP_RATES = [150, 200, 250, 300, 330, 360, 390, 420]
BIN_S = 10

DEFAULT_SPIKE_PARAMS = {
    "runtime": FIT_RUNTIME_S,
    "hstep": 1,
    "Vrest": -62,
    "Vthresh": -50,
    "psprate": 300,
    "pspratio": 1,
    "pspmag": 3,
    "halflifeMem": 7.5,
    "kHAP": 50,
    "halflifeHAP": 8,
    "kAHP": 0.5,
    "halflifeAHP": 500,
    "kDAP": 0.0,
    "halflifeDAP": 80,
    "useNMDA": 0,
    "pspmag2": 0.0,
    "psprate2": 300,
    "halflifePSP2": 120.0,
    "nmdaSync": 1,
}

DEFAULT_SEC_PARAMS = {
    "kB": 0.021,
    "halflifeB": 2000,
    "Bbase": 0.5,
    "kC": 0.0003,
    "halflifeC": 20000,
    "kE": 1.5,
    "halflifeE": 100,
    "Cth": 0.14,
    "Cgradient": 5,
    "Eth": 12,
    "Egradient": 5,
    "beta": 120,
    "Rmax": 1000000,
    "Rinit": 1000000,
    "Pmax": 5000,
    "alpha": 0.003,
    "plasma_hstep": 1,
    "halflifeDiff": 61,
    "halflifeClear": 68,
    "VolPlasma": 100,
    "VolEVF": 9.75,
    "secExp": 2,
}

MODEL_PRESETS = {
    "MAL11E": {
        "baseline": {
            "psprate": 400,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.05,
            "halflifeAHP": 300,
            "kDAP": 0.0,
            "useNMDA": 0,
        },
        "simple_dap": {
            "psprate": 380,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.05,
            "halflifeAHP": 300,
            "kDAP": 0.6,
            "halflifeDAP": 80,
            "useNMDA": 0,
        },
        "nmda_only": {
            "psprate": 350,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.05,
            "halflifeAHP": 300,
            "kDAP": 0.0,
            "useNMDA": 1,
            "pspmag2": 0.8,
            "psprate2": 350,
            "halflifePSP2": 120.0,
            "nmdaSync": 0,
        },
        "no_ahp": {
            "psprate": 400,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.0,
            "halflifeAHP": 300,
            "kDAP": 0.0,
            "useNMDA": 0,
        },
    },
    "CBA1R8C1": {
        "baseline": {
            "psprate": 340,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.10,
            "halflifeAHP": 300,
            "kDAP": 0.0,
            "useNMDA": 0,
        },
        "simple_dap": {
            "psprate": 330,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.10,
            "halflifeAHP": 300,
            "kDAP": 0.8,
            "halflifeDAP": 80,
            "useNMDA": 0,
        },
        "nmda_only": {
            "psprate": 318,
            "kHAP": 50,
            "halflifeHAP": 8,
            "kAHP": 0.10,
            "halflifeAHP": 300,
            "kDAP": 0.0,
            "useNMDA": 1,
            "pspmag2": 0.8,
            "psprate2": 300,
            "halflifePSP2": 120.0,
            "nmdaSync": 0,
        },
    },
}

INPUT_PROTOCOL_S = [
    (0, 150, 160),
    (150, 300, 240),
    (300, 450, 360),
    (450, 600, 240),
    (600, 750, 180),
]

MODEL_LABELS = {
    "baseline": "Baseline + AHP",
    "simple_dap": "Simple DAP",
    "nmda_only": "NMDA-only",
    "no_ahp": "Baseline without AHP",
}

MODEL_COLOURS = {
    "target": "#111111",
    "baseline": "#1f77b4",
    "simple_dap": "#d62728",
    "nmda_only": "#2ca02c",
    "no_ahp": "#9467bd",
}


class DummyScaleBox:
    def GraphUpdateAll(self) -> None:
        pass


class DummyMainWin:
    def __init__(self) -> None:
        self.scalebox = DummyScaleBox()


class DummySpikeBox:
    def __init__(self) -> None:
        self.modflags = {"randomflag": 1}


class DummyMod:
    def __init__(self) -> None:
        self.datsample = 1
        self.secdata = SecData(1000000)
        self.statedata = StateData(1000000)
        self.modspike = SpikeDat()
        self.spikebox = DummySpikeBox()
        self.mainwin = DummyMainWin()


@dataclass
class TargetRecording:
    name: str
    metadata: list[str]
    times_s: np.ndarray
    analysis: SpikeDat


@dataclass
class RunResult:
    spike: SpikeDat
    secdata: SecData
    statedata: StateData
    runtime_s: int


def pdata_to_array(data, length: int) -> np.ndarray:
    return np.fromiter((float(data[i]) for i in range(length)), dtype=float, count=length)


def analyze_times(name: str, times_s: np.ndarray) -> SpikeDat:
    neuro = NeuroDat()
    neuro.name = name
    neuro.spikecount = len(times_s)
    neuro.times[: len(times_s)] = times_s * 1000.0

    spike = SpikeDat()
    spike.Analysis(neuro)
    spike.name = name
    return spike


def load_targets() -> dict[str, TargetRecording]:
    raw = pd.read_csv(SELECTED_RECORDINGS_CSV)
    targets: dict[str, TargetRecording] = {}

    for name in raw.columns:
        column = raw[name]
        metadata = ["" if pd.isna(x) else str(x) for x in column.iloc[:HEADER_ROWS].tolist()]
        times_s = pd.to_numeric(column.iloc[HEADER_ROWS:], errors="coerce").dropna().to_numpy(dtype=float)
        targets[name] = TargetRecording(name=name, metadata=metadata, times_s=times_s, analysis=analyze_times(name, times_s))

    return targets


def make_spike_params(overrides: dict[str, object], runtime_s: int) -> dict[str, object]:
    params = dict(DEFAULT_SPIKE_PARAMS)
    params["runtime"] = runtime_s
    params.update(overrides)
    return params


def run_model(spike_params: dict[str, object], sec_params: dict[str, float] | None = None) -> RunResult:
    mod = DummyMod()
    model = SpikeModel(mod, {"spike": spike_params, "sec": sec_params or DEFAULT_SEC_PARAMS})
    model.Model()
    mod.modspike.Analysis()
    return RunResult(spike=mod.modspike, secdata=mod.secdata, statedata=mod.statedata, runtime_s=int(spike_params["runtime"]))


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def normalised_rmse(a: np.ndarray, b: np.ndarray) -> float:
    scale = max(float(np.max(np.abs(b))), 1e-9)
    return rmse(a, b) / scale


def compare_model(model: SpikeDat, target: SpikeDat) -> dict[str, float]:
    # Lower fit_score means the simulated spike train is closer to the recording.
    # The early 0-200 ms window carries most of the visible DAP signature, while
    # the IoD terms retain a summary of longer-timescale irregularity.
    hist_target = np.asarray(target.hist5norm[:40], dtype=float)
    hist_model = np.asarray(model.hist5norm[:40], dtype=float)
    haz_target = np.asarray(target.haz5[:40], dtype=float)
    haz_model = np.asarray(model.haz5[:40], dtype=float)
    iod_target = np.asarray(target.IoDdata[:7], dtype=float)
    iod_model = np.asarray(model.IoDdata[:7], dtype=float)
    freq_error = abs(float(model.freq) - float(target.freq)) / max(float(target.freq), 1e-9)
    hist_error = normalised_rmse(hist_model, hist_target)
    haz_error = normalised_rmse(haz_model, haz_target)
    iod_error = normalised_rmse(iod_model, iod_target)

    return {
        "target_freq_hz": float(target.freq),
        "model_freq_hz": float(model.freq),
        "freq_error_rel": freq_error,
        "hist_rmse_norm": hist_error,
        "haz_rmse_norm": haz_error,
        "iod_rmse_norm": iod_error,
        "fit_score": 0.25 * freq_error + 0.30 * hist_error + 0.20 * haz_error + 0.25 * iod_error,
    }


def steady_plasma(run: RunResult, last_seconds: int = 60) -> float:
    runtime_ms = run.runtime_s * 1000
    plasma = pdata_to_array(run.secdata.secPlasma, runtime_ms)
    window = min(runtime_ms, last_seconds * 1000)
    return float(plasma[-window:].mean())


def binned_spike_rate(spike: SpikeDat, runtime_s: int, bin_s: int) -> tuple[np.ndarray, np.ndarray]:
    spike_count = int(spike.spikecount)
    spike_times_s = np.asarray(spike.times[:spike_count], dtype=float) / 1000.0
    edges = np.arange(0, runtime_s + bin_s, bin_s)
    counts, edges = np.histogram(spike_times_s, bins=edges)
    rate = counts / float(bin_s)
    centres = edges[:-1] + bin_s / 2
    return centres, rate


def protocol_to_schedule(protocol_s: list[tuple[int, int, int]]) -> list[dict[str, int]]:
    return [
        {"start_ms": start_s * 1000, "end_ms": end_s * 1000, "value": rate}
        for start_s, end_s, rate in protocol_s
    ]


def protocol_trace(protocol_s: list[tuple[int, int, int]], runtime_s: int, bin_s: int) -> tuple[np.ndarray, np.ndarray]:
    centres = np.arange(bin_s / 2, runtime_s + 0.1, bin_s)
    values = np.zeros_like(centres, dtype=float)
    for idx, time_s in enumerate(centres):
        for start_s, end_s, rate in protocol_s:
            if start_s <= time_s < end_s:
                values[idx] = rate
                break
    return centres, values


def collect_fit_results(targets: dict[str, TargetRecording]) -> tuple[pd.DataFrame, dict[str, dict[str, RunResult]]]:
    rows: list[dict[str, object]] = []
    fit_runs: dict[str, dict[str, RunResult]] = {}

    for recording, variants in MODEL_PRESETS.items():
        if recording not in targets:
            continue

        fit_runs[recording] = {}
        target = targets[recording]
        for model_name in ("baseline", "simple_dap", "nmda_only"):
            params = make_spike_params(variants[model_name], FIT_RUNTIME_S)
            run = run_model(params)
            fit_runs[recording][model_name] = run

            metrics = compare_model(run.spike, target.analysis)
            row = {
                "recording": recording,
                "model": model_name,
                "label": MODEL_LABELS[model_name],
                **metrics,
            }
            rows.append(row)

    frame = pd.DataFrame(rows).sort_values(["recording", "fit_score", "model"]).reset_index(drop=True)
    return frame, fit_runs


def collect_secretion_sweeps() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    mal_presets = MODEL_PRESETS["MAL11E"]

    for model_name in ("baseline", "no_ahp", "simple_dap"):
        for psprate in SECRETION_SWEEP_RATES:
            overrides = dict(mal_presets[model_name])
            overrides["psprate"] = psprate
            params = make_spike_params(overrides, SWEEP_RUNTIME_S)
            run = run_model(params)
            rows.append(
                {
                    "model": model_name,
                    "label": MODEL_LABELS[model_name],
                    "psprate": psprate,
                    "freq_hz": float(run.spike.freq),
                    "steady_plasma": steady_plasma(run),
                }
            )

    return pd.DataFrame(rows)


def collect_varying_input_results() -> tuple[pd.DataFrame, dict[str, RunResult]]:
    rows: list[dict[str, object]] = []
    runs: dict[str, RunResult] = {}
    schedule = protocol_to_schedule(INPUT_PROTOCOL_S)

    for model_name in ("baseline", "simple_dap"):
        overrides = dict(MODEL_PRESETS["MAL11E"][model_name])
        overrides["psprate"] = INPUT_PROTOCOL_S[0][2]
        overrides["psprate_schedule"] = schedule
        params = make_spike_params(overrides, VARYING_INPUT_RUNTIME_S)
        run = run_model(params)
        runs[model_name] = run

        plasma = pdata_to_array(run.secdata.secPlasma, run.runtime_s * 1000)
        for start_s, end_s, rate in INPUT_PROTOCOL_S:
            start_ms = start_s * 1000
            end_ms = end_s * 1000
            spike_times_s = np.asarray(run.spike.times[: int(run.spike.spikecount)], dtype=float) / 1000.0
            in_window = (spike_times_s >= start_s) & (spike_times_s < end_s)
            segment_duration = max(end_s - start_s, 1)
            segment_rate = float(np.sum(in_window) / segment_duration)
            window_ms = min(60000, end_ms - start_ms)
            tail_plasma = float(plasma[end_ms - window_ms:end_ms].mean())
            rows.append(
                {
                    "model": model_name,
                    "label": MODEL_LABELS[model_name],
                    "segment_start_s": start_s,
                    "segment_end_s": end_s,
                    "input_psprate": rate,
                    "segment_freq_hz": segment_rate,
                    "tail_plasma": tail_plasma,
                }
            )

    return pd.DataFrame(rows), runs


def save_parameter_sets() -> Path:
    out = ANALYSIS_DIR / "ica1_parameter_sets.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(MODEL_PRESETS, handle, indent=2)
    return out


def plot_spike_fits(targets: dict[str, TargetRecording], fit_runs: dict[str, dict[str, RunResult]]) -> Path:
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)

    for row_idx, recording in enumerate(("MAL11E", "CBA1R8C1")):
        target = targets[recording].analysis
        runs = fit_runs[recording]

        hist_ax, haz_ax, iod_ax = axes[row_idx]
        x_hist = np.arange(120) * 5
        hist_ax.plot(x_hist, np.asarray(target.hist5norm[:120]), color=MODEL_COLOURS["target"], lw=2.4, label="Target")
        haz_ax.plot(x_hist, np.asarray(target.haz5[:120]), color=MODEL_COLOURS["target"], lw=2.4, label="Target")
        iod_x = np.asarray(target.IoDdataX[:7], dtype=float)
        iod_ax.plot(iod_x, np.asarray(target.IoDdata[:7]), color=MODEL_COLOURS["target"], lw=2.4, marker="o", label="Target")

        for model_name in ("baseline", "simple_dap", "nmda_only"):
            run = runs[model_name].spike
            label = MODEL_LABELS[model_name]
            colour = MODEL_COLOURS[model_name]
            hist_ax.plot(x_hist, np.asarray(run.hist5norm[:120]), color=colour, lw=1.8, label=label)
            haz_ax.plot(x_hist, np.asarray(run.haz5[:120]), color=colour, lw=1.8, label=label)
            iod_ax.plot(iod_x, np.asarray(run.IoDdata[:7]), color=colour, lw=1.8, marker="o", label=label)

        for axis in (hist_ax, haz_ax):
            axis.axvspan(20, 80, color="gold", alpha=0.15)
            axis.grid(alpha=0.25)
            axis.set_xlim(0, 600)

        hist_ax.set_title(f"{recording}: 5 ms ISI histogram")
        hist_ax.set_ylabel("Norm count")
        haz_ax.set_title(f"{recording}: 5 ms hazard function")
        haz_ax.set_ylabel("Hazard")
        iod_ax.set_title(f"{recording}: IoD")
        iod_ax.set_xlabel("IoD window index")
        iod_ax.set_ylabel("IoD")
        iod_ax.grid(alpha=0.25)

        if row_idx == 1:
            hist_ax.set_xlabel("Interspike interval (ms)")
            haz_ax.set_xlabel("Interspike interval (ms)")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False)

    out = ANALYSIS_DIR / "ica1_figure1_spike_fits.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def plot_system_outputs(sweep_df: pd.DataFrame, varying_runs: dict[str, RunResult]) -> Path:
    fig, axes = plt.subplots(3, 1, figsize=(12, 11), constrained_layout=True)

    sweep_ax, rate_ax, plasma_ax = axes

    for model_name in ("baseline", "no_ahp", "simple_dap"):
        subset = sweep_df[sweep_df["model"] == model_name]
        sweep_ax.plot(
            subset["psprate"],
            subset["steady_plasma"],
            marker="o",
            lw=2,
            color=MODEL_COLOURS[model_name],
            label=MODEL_LABELS[model_name],
        )

    sweep_ax.set_title("Secretion sweep using MAL11E-derived parameters")
    sweep_ax.set_xlabel("PSP rate")
    sweep_ax.set_ylabel("Stable plasma concentration")
    sweep_ax.grid(alpha=0.25)
    sweep_ax.legend(frameon=False)

    centres, input_trace = protocol_trace(INPUT_PROTOCOL_S, VARYING_INPUT_RUNTIME_S, BIN_S)
    rate_ax.plot(centres, input_trace / 60.0, color="#7f7f7f", lw=2, linestyle="--", label="Input (scaled)")

    for model_name in ("baseline", "simple_dap"):
        run = varying_runs[model_name]
        rate_time, rate_trace = binned_spike_rate(run.spike, run.runtime_s, BIN_S)
        rate_ax.plot(rate_time, rate_trace, color=MODEL_COLOURS[model_name], lw=2, label=MODEL_LABELS[model_name])

        plasma = pdata_to_array(run.secdata.secPlasma, run.runtime_s * 1000)
        plasma_bin = plasma.reshape(run.runtime_s // BIN_S, BIN_S * 1000).mean(axis=1)
        plasma_ax.plot(rate_time, plasma_bin, color=MODEL_COLOURS[model_name], lw=2, label=MODEL_LABELS[model_name])

    # Mark protocol epochs so the recovery segment discussed in the report is
    # easy to identify directly from the figure.
    epoch_boundaries = [start_s for start_s, _, _ in INPUT_PROTOCOL_S[1:]]
    for idx, (start_s, end_s, rate) in enumerate(INPUT_PROTOCOL_S):
        if idx % 2 == 1:
            for axis in (rate_ax, plasma_ax):
                axis.axvspan(start_s, end_s, color="#f2f2f2", alpha=0.4, zorder=0)

        centre_s = (start_s + end_s) / 2
        rate_ax.text(
            centre_s,
            rate_ax.get_ylim()[1] * 0.95,
            f"PSP {rate}",
            ha="center",
            va="top",
            fontsize=9,
            color="#555555",
        )

    for boundary_s in epoch_boundaries:
        for axis in (rate_ax, plasma_ax):
            axis.axvline(boundary_s, color="#999999", linestyle=":", lw=1.2, alpha=0.8)

    rate_ax.set_title("Varying-input protocol: binned spike-rate response")
    rate_ax.set_ylabel("Spike rate (Hz)")
    rate_ax.grid(alpha=0.25)
    rate_ax.legend(frameon=False)

    plasma_ax.set_title("Varying-input protocol: plasma response")
    plasma_ax.set_xlabel("Time (s)")
    plasma_ax.set_ylabel("Plasma concentration")
    plasma_ax.grid(alpha=0.25)
    plasma_ax.legend(frameon=False)

    out = ANALYSIS_DIR / "ica1_figure2_system_outputs.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def plot_supporting_fit_breakdown(fit_df: pd.DataFrame) -> Path:
    metrics = ["freq_error_rel", "hist_rmse_norm", "haz_rmse_norm", "iod_rmse_norm", "fit_score"]
    metric_labels = ["Rate err", "Hist err", "Haz err", "IoD err", "Weighted total"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    vmax = float(fit_df[metrics].to_numpy(dtype=float).max())

    heatmap = None
    for axis, recording in zip(axes, ("MAL11E", "CBA1R8C1")):
        subset = fit_df[fit_df["recording"] == recording].sort_values("fit_score").reset_index(drop=True)
        data = subset[metrics].to_numpy(dtype=float)
        heatmap = axis.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0.0, vmax=vmax)
        axis.set_title(f"{recording}: fit-score components")
        axis.set_xticks(np.arange(len(metric_labels)), labels=metric_labels, rotation=30, ha="right")
        axis.set_yticks(np.arange(len(subset)), labels=subset["label"])

        for row_idx in range(data.shape[0]):
            for col_idx in range(data.shape[1]):
                value = data[row_idx, col_idx]
                text_colour = "white" if value > 0.55 * vmax else "black"
                axis.text(col_idx, row_idx, f"{value:.3f}", ha="center", va="center", fontsize=9, color=text_colour)

        axis.set_xticks(np.arange(-0.5, data.shape[1], 1), minor=True)
        axis.set_yticks(np.arange(-0.5, data.shape[0], 1), minor=True)
        axis.grid(which="minor", color="white", linewidth=1.4)
        axis.tick_params(which="minor", bottom=False, left=False)

    if heatmap is not None:
        colourbar = fig.colorbar(heatmap, ax=axes, fraction=0.03, pad=0.02)
        colourbar.set_label("Error magnitude (lower is better)")

    out = ANALYSIS_DIR / "ica1_supplementary_figure_s1_fit_breakdown.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def plot_supporting_numeric_summaries(sweep_df: pd.DataFrame, dynamic_df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(13, 7.6), constrained_layout=True, gridspec_kw={"height_ratios": [1.0, 1.25]})
    sweep_ax, dynamic_ax = axes

    for axis in axes:
        axis.axis("off")

    sweep_table = (
        sweep_df.pivot(index="label", columns="psprate", values="steady_plasma")
        .loc[[MODEL_LABELS["baseline"], MODEL_LABELS["no_ahp"], MODEL_LABELS["simple_dap"]]]
        .round(2)
    )
    sweep_cells = [[f"{value:.2f}" for value in row] for row in sweep_table.to_numpy()]
    sweep = sweep_ax.table(
        cellText=sweep_cells,
        rowLabels=sweep_table.index.tolist(),
        colLabels=[str(col) for col in sweep_table.columns.tolist()],
        bbox=[0.02, 0.05, 0.96, 0.72],
        cellLoc="center",
    )
    sweep.auto_set_font_size(False)
    sweep.set_fontsize(10)
    sweep_ax.set_title("A. MAL11E secretion sweep: steady plasma concentration by PSP rate", fontsize=13, pad=10)

    dynamic_rows: list[list[str]] = []
    dynamic_labels = [MODEL_LABELS["baseline"], MODEL_LABELS["simple_dap"]]
    dynamic_cols = [f"{start}-{end}s\ninput {rate}" for start, end, rate in INPUT_PROTOCOL_S]
    for model_name in ("baseline", "simple_dap"):
        row: list[str] = []
        for start_s, end_s, rate in INPUT_PROTOCOL_S:
            record = dynamic_df[
                (dynamic_df["model"] == model_name)
                & (dynamic_df["segment_start_s"] == start_s)
                & (dynamic_df["segment_end_s"] == end_s)
                & (dynamic_df["input_psprate"] == rate)
            ].iloc[0]
            row.append(f"{record['segment_freq_hz']:.2f} Hz\n{record['tail_plasma']:.2f}")
        dynamic_rows.append(row)

    dynamic = dynamic_ax.table(
        cellText=dynamic_rows,
        rowLabels=dynamic_labels,
        colLabels=dynamic_cols,
        bbox=[0.02, 0.12, 0.96, 0.7],
        cellLoc="center",
    )
    dynamic.auto_set_font_size(False)
    dynamic.set_fontsize(10)
    dynamic_ax.set_title("B. Varying-input summary: segment firing rate and late-segment plasma", fontsize=13, pad=10)
    dynamic_ax.text(
        0.0,
        0.02,
        "Each cell reports segment firing rate on the first line and late-segment plasma concentration on the second.",
        transform=dynamic_ax.transAxes,
        fontsize=9,
        ha="left",
    )

    out = ANALYSIS_DIR / "ica1_supplementary_figure_s2_numeric_summaries.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def main() -> None:
    ANALYSIS_DIR.mkdir(exist_ok=True)
    targets = load_targets()

    fit_df, fit_runs = collect_fit_results(targets)
    fit_csv = ANALYSIS_DIR / "ica1_model_comparison.csv"
    fit_df.to_csv(fit_csv, index=False)

    sweep_df = collect_secretion_sweeps()
    sweep_csv = ANALYSIS_DIR / "ica1_secretion_sweeps.csv"
    sweep_df.to_csv(sweep_csv, index=False)

    dynamic_df, varying_runs = collect_varying_input_results()
    dynamic_csv = ANALYSIS_DIR / "ica1_varying_input_summary.csv"
    dynamic_df.to_csv(dynamic_csv, index=False)

    fig1 = plot_spike_fits(targets, fit_runs)
    fig2 = plot_system_outputs(sweep_df, varying_runs)
    supp_fig1 = plot_supporting_fit_breakdown(fit_df)
    supp_fig2 = plot_supporting_numeric_summaries(sweep_df, dynamic_df)
    param_json = save_parameter_sets()

    print(f"wrote {fit_csv}")
    print(f"wrote {sweep_csv}")
    print(f"wrote {dynamic_csv}")
    print(f"wrote {fig1}")
    print(f"wrote {fig2}")
    print(f"wrote {supp_fig1}")
    print(f"wrote {supp_fig2}")
    print(f"wrote {param_json}")


if __name__ == "__main__":
    main()
