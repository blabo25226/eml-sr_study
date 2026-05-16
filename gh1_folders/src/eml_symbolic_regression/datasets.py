"""Demo datasets based on sources/FOR_DEMO.md."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np
import sympy as sp

from .expression import Candidate, SympyCandidate, exp_expr, log_expr
from .verify import DataSplit

ArrayFn = Callable[[np.ndarray], np.ndarray]
MultiArrayFn = Callable[[Mapping[str, np.ndarray]], np.ndarray]
REAL_DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "real"


@dataclass(frozen=True)
class DemoSpec:
    name: str
    variable: str
    description: str
    target: ArrayFn
    candidate: Candidate
    train_domain: tuple[float, float]
    heldout_domain: tuple[float, float]
    extrap_domain: tuple[float, float]
    source_document: str
    source_linkage: str
    normalized_dimensionless: bool

    def make_splits(self, *, points: int = 80, seed: int = 0) -> list[DataSplit]:
        rng = np.random.default_rng(seed)

        def sample(domain: tuple[float, float], count: int) -> np.ndarray:
            low, high = domain
            values = np.linspace(low, high, count)
            jitter = (high - low) * 0.002 * rng.standard_normal(count)
            return np.sort(values + jitter).astype(np.float64)

        train_x = sample(self.train_domain, points)
        heldout_x = sample(self.heldout_domain, max(16, points // 2))
        extrap_x = sample(self.extrap_domain, max(16, points // 2))
        target_hp = lambda context: self.candidate.evaluate_mpmath(context)
        return [
            DataSplit("train", {self.variable: train_x}, self.target(train_x), target_hp),
            DataSplit("heldout", {self.variable: heldout_x}, self.target(heldout_x), target_hp),
            DataSplit("extrapolation", {self.variable: extrap_x}, self.target(extrap_x), target_hp),
        ]

    def formula_provenance(self) -> dict[str, Any]:
        candidate_name = getattr(self.candidate, "name", getattr(self.candidate, "candidate_kind", type(self.candidate).__name__))
        return {
            "formula_id": self.name,
            "variable": self.variable,
            "description": self.description,
            "symbolic_expression": sp.sstr(self.candidate.to_sympy()),
            "candidate_name": str(candidate_name),
            "source_document": self.source_document,
            "source_linkage": self.source_linkage,
            "normalized_dimensionless": self.normalized_dimensionless,
        }


@dataclass(frozen=True)
class ExpandedDatasetSpec:
    id: str
    formula_id: str
    description: str
    variables: tuple[str, ...]
    target: MultiArrayFn | None
    candidate: Candidate | None
    split_domains: dict[str, dict[str, tuple[float, float]]]
    units: dict[str, str]
    target_unit: str
    classification: str
    category: str
    source: str
    source_url: str | None
    generator: str
    noise_policy: dict[str, Any]
    split_policy: dict[str, Any]
    domain_constraints: dict[str, Any]
    compatible_contracts: tuple[str, ...]
    data_path: Path | None = None

    def make_splits(self, *, points: int = 80, seed: int = 0) -> list[DataSplit]:
        points = int(points)
        if points <= 0:
            raise ValueError("points must be positive")
        if self.data_path is not None:
            return self._real_data_splits()

        rng = np.random.default_rng(seed)
        splits: list[DataSplit] = []
        for split_name, domains in self.split_domains.items():
            count = _split_count(split_name, points)
            inputs = _sample_inputs(domains, count=count, rng=rng)
            if self.target is None:
                raise ValueError(f"expanded dataset {self.id!r} has no target generator")
            clean_target = self.target(inputs).astype(np.complex128)
            observed_target = _apply_noise(clean_target, self.noise_policy, split_name=split_name, rng=rng)
            splits.append(
                DataSplit(
                    split_name,
                    dict(inputs),
                    observed_target,
                    self.candidate.evaluate_mpmath if self.candidate is not None else None,
                    self.candidate.to_sympy() if self.candidate is not None else None,
                    role=_split_role(split_name),
                    domain={name: tuple(domain) for name, domain in domains.items()},
                )
            )
        return splits

    def manifest(self, *, points: int = 80, seed: int = 0, tolerance: float = 1e-8) -> dict[str, Any]:
        points = int(points)
        tolerance = float(tolerance)
        if points <= 0:
            raise ValueError("points must be positive")
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")
        splits = self.make_splits(points=points, seed=seed)
        split_metadata: list[dict[str, Any]] = []
        for split in splits:
            input_hashes = {name: _array_sha256(values) for name, values in split.inputs.items()}
            split_metadata.append(
                {
                    "name": split.name,
                    "role": split.role or _split_role(split.name),
                    "domain": {
                        name: [float(value) for value in domain]
                        for name, domain in (split.domain or self.split_domains.get(split.name, {})).items()
                    },
                    "count": int(len(split.target)),
                    "input_sha256": input_hashes,
                    "target_sha256": _array_sha256(split.target),
                    "units": {name: self.units[name] for name in split.inputs},
                    "target_unit": self.target_unit,
                }
            )

        manifest: dict[str, Any] = {
            "schema": "eml.expanded_dataset_manifest.v1",
            "dataset_id": self.id,
            "formula_id": self.formula_id,
            "description": self.description,
            "variables": list(self.variables),
            "target_expression": sp.sstr(self.candidate.to_sympy()) if self.candidate is not None else None,
            "classification": self.classification,
            "category": self.category,
            "source": self.source,
            "source_url": self.source_url,
            "data_path": str(self.data_path) if self.data_path is not None else None,
            "generator": self.generator,
            "units": {**self.units, "target": self.target_unit},
            "noise_policy": self.noise_policy,
            "split_policy": self.split_policy,
            "domain_constraints": self.domain_constraints,
            "compatible_contracts": list(self.compatible_contracts),
            "seed": int(seed),
            "points": points,
            "tolerance": tolerance,
            "splits": split_metadata,
        }
        encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return {**manifest, "manifest_sha256": hashlib.sha256(encoded).hexdigest()}

    def _real_data_splits(self) -> list[DataSplit]:
        if self.data_path is None:
            raise ValueError("real data path is not configured")
        rows = _read_hubble_rows(self.data_path)
        grouped: dict[str, list[dict[str, float | str]]] = {}
        for row in rows:
            grouped.setdefault(str(row["split"]), []).append(row)
        splits: list[DataSplit] = []
        for split_name in ("train", "heldout", "final_confirmation"):
            split_rows = grouped.get(split_name, [])
            distance = np.asarray([float(row["distance_mpc"]) for row in split_rows], dtype=np.float64)
            velocity = np.asarray([float(row["velocity_km_s"]) for row in split_rows], dtype=np.complex128)
            splits.append(
                DataSplit(
                    split_name,
                    {"distance_mpc": distance},
                    velocity,
                    role=_split_role(split_name),
                    domain={"distance_mpc": (float(np.min(distance)), float(np.max(distance)))},
                )
            )
        return splits


def _sympy_candidate(expr: sp.Expr, variable: str, name: str) -> SympyCandidate:
    return SympyCandidate(expr, (variable,), name=name)


def _expanded_split_roles() -> dict[str, str]:
    return {
        "train": "training",
        "selection": "selection",
        "heldout": "diagnostic",
        "extrapolation": "diagnostic",
        "final_confirmation": "final_confirmation",
    }


def _split_role(split_name: str) -> str:
    return _expanded_split_roles().get(split_name, "diagnostic")


def _split_count(split_name: str, points: int) -> int:
    if split_name == "train":
        return points
    if split_name == "final_confirmation":
        return max(16, points // 2)
    return max(12, points // 2)


def _sample_inputs(
    domains: Mapping[str, tuple[float, float]],
    *,
    count: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    inputs: dict[str, np.ndarray] = {}
    multivariable = len(domains) > 1
    for name, domain in domains.items():
        low, high = domain
        if multivariable:
            values = rng.uniform(low, high, count)
        else:
            values = np.linspace(low, high, count)
            jitter = (high - low) * 0.002 * rng.standard_normal(count)
            values = np.sort(values + jitter)
        inputs[name] = values.astype(np.float64)
    return inputs


def _apply_noise(
    clean_target: np.ndarray,
    noise_policy: Mapping[str, Any],
    *,
    split_name: str,
    rng: np.random.Generator,
) -> np.ndarray:
    if noise_policy.get("type") != "gaussian_relative":
        return clean_target
    applies_to = tuple(str(value) for value in noise_policy.get("applies_to", ()))
    if applies_to and split_name not in applies_to:
        return clean_target
    sigma = float(noise_policy.get("relative_sigma", 0.0))
    if sigma <= 0:
        return clean_target
    scale = np.maximum(np.abs(clean_target.real), 1e-12)
    noise = rng.normal(0.0, sigma, clean_target.shape) * scale
    return (clean_target.real + noise).astype(np.complex128)


def _read_hubble_rows(path: Path) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    with path.open("r", encoding="utf-8") as handle:
        header = handle.readline().strip().split(",")
        expected = ["split", "distance_mpc", "velocity_km_s"]
        if header != expected:
            raise ValueError(f"unexpected Hubble CSV header: {header!r}")
        for line in handle:
            if not line.strip():
                continue
            split, distance, velocity = line.strip().split(",")
            rows.append({"split": split, "distance_mpc": float(distance), "velocity_km_s": float(velocity)})
    return rows


def _basin_demo_specs() -> dict[str, DemoSpec]:
    from .basin import basin_target_specs

    specs: dict[str, DemoSpec] = {}
    for spec in basin_target_specs():
        specs[spec.id] = DemoSpec(
            name=spec.id,
            variable=spec.variable,
            description=f"Phase 31 deterministic exact EML basin target {spec.id}.",
            target=lambda a, expr=spec.expression, var=spec.variable: expr.evaluate_numpy({var: a}),
            candidate=spec.expression,
            train_domain=spec.train_domain,
            heldout_domain=spec.heldout_domain,
            extrap_domain=spec.extrap_domain,
            source_document=spec.source_document,
            source_linkage=spec.source_linkage,
            normalized_dimensionless=True,
        )
    return specs


def _depth_curve_demo_specs() -> dict[str, DemoSpec]:
    from .depth_curve import depth_curve_target_specs

    specs: dict[str, DemoSpec] = {}
    for spec in depth_curve_target_specs():
        specs[spec.id] = DemoSpec(
            name=spec.id,
            variable=spec.variable,
            description=spec.description,
            target=lambda a, expr=spec.expression, var=spec.variable: expr.evaluate_numpy({var: a}),
            candidate=spec.expression,
            train_domain=spec.train_domain,
            heldout_domain=spec.heldout_domain,
            extrap_domain=spec.extrap_domain,
            source_document=spec.source_document,
            source_linkage=spec.source_linkage,
            normalized_dimensionless=True,
        )
    return specs


def demo_specs() -> dict[str, DemoSpec]:
    x = sp.Symbol("x")
    t = sp.Symbol("t")
    specs = {
        "exp": DemoSpec(
            name="exp",
            variable="x",
            description="Paper smoke test: exp(x) = eml(x, 1).",
            target=lambda a: np.exp(a).astype(np.complex128),
            candidate=exp_expr("x"),
            train_domain=(-1.0, 1.0),
            heldout_domain=(-0.8, 0.8),
            extrap_domain=(1.05, 1.5),
            source_document="sources/paper.pdf",
            source_linkage="sources/NORTH_STAR.md paper EML identity smoke test for exp(x)",
            normalized_dimensionless=True,
        ),
        "log": DemoSpec(
            name="log",
            variable="x",
            description="Paper smoke test: ln(x) EML identity on the positive real axis.",
            target=lambda a: np.log(a).astype(np.complex128),
            candidate=log_expr("x"),
            train_domain=(0.25, 3.0),
            heldout_domain=(0.35, 2.75),
            extrap_domain=(3.1, 4.2),
            source_document="sources/paper.pdf",
            source_linkage="sources/NORTH_STAR.md paper EML identity smoke test for ln(x)",
            normalized_dimensionless=True,
        ),
        "beer_lambert": DemoSpec(
            name="beer_lambert",
            variable="x",
            description="High-probability exponential-decay showcase.",
            target=lambda a: np.exp(-0.8 * a).astype(np.complex128),
            candidate=_sympy_candidate(sp.exp(-sp.Float("0.8") * x), "x", "beer_lambert_catalog"),
            train_domain=(0.0, 3.0),
            heldout_domain=(0.15, 2.7),
            extrap_domain=(3.1, 4.5),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Beer-Lambert law high-success-probability sanity check",
            normalized_dimensionless=True,
        ),
        "arrhenius": DemoSpec(
            name="arrhenius",
            variable="x",
            description="Normalized reciprocal-temperature Arrhenius law from FOR_DEMO.md.",
            target=lambda a: np.exp(-0.8 / a).astype(np.complex128),
            candidate=_sympy_candidate(sp.exp(-sp.Float("0.8") / x), "x", "arrhenius_catalog"),
            train_domain=(0.5, 3.0),
            heldout_domain=(0.6, 2.7),
            extrap_domain=(3.1, 4.2),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Arrhenius law normalized reciprocal-temperature dimensionless input from FOR_DEMO.md",
            normalized_dimensionless=True,
        ),
        "radioactive_decay": DemoSpec(
            name="radioactive_decay",
            variable="t",
            description="FOR_DEMO-style one-term exponential decay baseline.",
            target=lambda a: np.exp(-0.4 * a).astype(np.complex128),
            candidate=_sympy_candidate(sp.exp(-sp.Float("0.4") * t), "t", "radioactive_decay_catalog"),
            train_domain=(0.0, 5.0),
            heldout_domain=(0.15, 4.7),
            extrap_domain=(5.1, 7.0),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Radioactive decay / Newton cooling smoke-test family",
            normalized_dimensionless=True,
        ),
        "scaled_exp_growth": DemoSpec(
            name="scaled_exp_growth",
            variable="x",
            description="Phase 30 signed/scaled exponential proof target with a positive exponent coefficient.",
            target=lambda a: np.exp(0.4 * a).astype(np.complex128),
            candidate=_sympy_candidate(sp.exp(sp.Float("0.4") * x), "x", "scaled_exp_growth_catalog"),
            train_domain=(-2.0, 2.0),
            heldout_domain=(-1.7, 1.7),
            extrap_domain=(2.1, 3.2),
            source_document="sources/NORTH_STAR.md",
            source_linkage="Phase 30 signed/scaled exponential proof coverage: exp(0.4*x) coefficient-growth variant",
            normalized_dimensionless=True,
        ),
        "scaled_exp_fast_decay": DemoSpec(
            name="scaled_exp_fast_decay",
            variable="x",
            description="Phase 30 signed/scaled exponential proof target with a larger negative exponent coefficient.",
            target=lambda a: np.exp(-1.2 * a).astype(np.complex128),
            candidate=_sympy_candidate(sp.exp(-sp.Float("1.2") * x), "x", "scaled_exp_fast_decay_catalog"),
            train_domain=(0.0, 2.5),
            heldout_domain=(0.1, 2.3),
            extrap_domain=(2.6, 3.5),
            source_document="sources/NORTH_STAR.md",
            source_linkage="Phase 30 signed/scaled exponential proof coverage: exp(-1.2*x) fast-decay coefficient variant",
            normalized_dimensionless=True,
        ),
        "michaelis_menten": DemoSpec(
            name="michaelis_menten",
            variable="x",
            description="Mechanistic biochemistry law from FOR_DEMO.md.",
            target=lambda a: (2.0 * a / (0.5 + a)).astype(np.complex128),
            candidate=_sympy_candidate(2 * x / (sp.Float("0.5") + x), "x", "michaelis_menten_catalog"),
            train_domain=(0.05, 5.0),
            heldout_domain=(0.08, 4.5),
            extrap_domain=(5.1, 7.0),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Michaelis-Menten best showcase set mechanistic biochemistry law",
            normalized_dimensionless=True,
        ),
        "logistic": DemoSpec(
            name="logistic",
            variable="x",
            description="Nonlinear growth progression demo.",
            target=lambda a: (1.0 / (1.0 + 2.0 * np.exp(-1.3 * a))).astype(np.complex128),
            candidate=_sympy_candidate(1 / (1 + 2 * sp.exp(-sp.Float("1.3") * x)), "x", "logistic_catalog"),
            train_domain=(0.0, 5.0),
            heldout_domain=(0.1, 4.8),
            extrap_domain=(5.1, 7.0),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Logistic growth first serious demo after simpler warm-ups",
            normalized_dimensionless=True,
        ),
        "shockley": DemoSpec(
            name="shockley",
            variable="x",
            description="Electronics demo structurally close to exponential-minus-constant behavior.",
            target=lambda a: (0.2 * (np.exp(1.4 * a) - 1.0)).astype(np.complex128),
            candidate=_sympy_candidate(sp.Float("0.2") * (sp.exp(sp.Float("1.4") * x) - 1), "x", "shockley_catalog"),
            train_domain=(0.0, 2.0),
            heldout_domain=(0.05, 1.8),
            extrap_domain=(2.05, 2.5),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Shockley diode equation electronics demo structurally close to exponential-minus-constant behavior",
            normalized_dimensionless=True,
        ),
        "damped_oscillator": DemoSpec(
            name="damped_oscillator",
            variable="t",
            description="Stretch demo: oscillation plus decay.",
            target=lambda a: (np.exp(-0.15 * a) * np.cos(2.5 * a + 0.2)).astype(np.complex128),
            candidate=_sympy_candidate(sp.exp(-sp.Float("0.15") * t) * sp.cos(sp.Float("2.5") * t + sp.Float("0.2")), "t", "damped_oscillator_catalog"),
            train_domain=(0.0, 6.0),
            heldout_domain=(0.05, 5.8),
            extrap_domain=(6.1, 8.0),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Damped harmonic oscillator headline time-series symbolic-recovery demo",
            normalized_dimensionless=True,
        ),
        "sin_pi": DemoSpec(
            name="sin_pi",
            variable="x",
            description="v1.15 periodic target: sin(pi*x) on a normalized real domain.",
            target=lambda a: np.sin(np.pi * a).astype(np.complex128),
            candidate=_sympy_candidate(sp.sin(sp.pi * x), "x", "sin_pi_catalog"),
            train_domain=(-1.0, 1.0),
            heldout_domain=(-0.9, 0.9),
            extrap_domain=(1.05, 1.45),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-01 periodic i*pi EML natural-bias target",
            normalized_dimensionless=True,
        ),
        "cos_pi": DemoSpec(
            name="cos_pi",
            variable="x",
            description="v1.15 periodic target: cos(pi*x) on a normalized real domain.",
            target=lambda a: np.cos(np.pi * a).astype(np.complex128),
            candidate=_sympy_candidate(sp.cos(sp.pi * x), "x", "cos_pi_catalog"),
            train_domain=(-1.0, 1.0),
            heldout_domain=(-0.9, 0.9),
            extrap_domain=(1.05, 1.45),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-01 periodic i*pi EML natural-bias target",
            normalized_dimensionless=True,
        ),
        "harmonic_sum": DemoSpec(
            name="harmonic_sum",
            variable="x",
            description="v1.15 harmonic target: sin(pi*x) + 0.5*cos(2*pi*x).",
            target=lambda a: (np.sin(np.pi * a) + 0.5 * np.cos(2.0 * np.pi * a)).astype(np.complex128),
            candidate=_sympy_candidate(sp.sin(sp.pi * x) + sp.Float("0.5") * sp.cos(2 * sp.pi * x), "x", "harmonic_sum_catalog"),
            train_domain=(-1.0, 1.0),
            heldout_domain=(-0.9, 0.9),
            extrap_domain=(1.05, 1.45),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-01 harmonic i*pi EML natural-bias target",
            normalized_dimensionless=True,
        ),
        "standing_wave_snapshot": DemoSpec(
            name="standing_wave_snapshot",
            variable="x",
            description="v1.15 standing-wave spatial snapshot: sin(pi*x)*cos(pi*x).",
            target=lambda a: (np.sin(np.pi * a) * np.cos(np.pi * a)).astype(np.complex128),
            candidate=_sympy_candidate(sp.sin(sp.pi * x) * sp.cos(sp.pi * x), "x", "standing_wave_snapshot_catalog"),
            train_domain=(-1.0, 1.0),
            heldout_domain=(-0.9, 0.9),
            extrap_domain=(1.05, 1.45),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-02 standing-wave i*pi EML natural-bias target",
            normalized_dimensionless=True,
        ),
        "log_periodic_oscillation": DemoSpec(
            name="log_periodic_oscillation",
            variable="x",
            description="v1.15 log-periodic target on a strictly positive normalized domain.",
            target=lambda a: (np.sqrt(a) * np.cos(2.0 * np.log(a) + 0.3)).astype(np.complex128),
            candidate=_sympy_candidate(sp.sqrt(x) * sp.cos(2 * sp.log(x) + sp.Float("0.3")), "x", "log_periodic_oscillation_catalog"),
            train_domain=(0.35, 3.5),
            heldout_domain=(0.45, 3.2),
            extrap_domain=(3.6, 5.0),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-03 log-periodic positive-domain i*pi EML target",
            normalized_dimensionless=True,
        ),
        "quadratic_polynomial": DemoSpec(
            name="quadratic_polynomial",
            variable="x",
            description="v1.15 negative control: compact quadratic polynomial.",
            target=lambda a: (1.0 + a + 0.5 * a**2).astype(np.complex128),
            candidate=_sympy_candidate(1 + x + sp.Float("0.5") * x**2, "x", "quadratic_polynomial_catalog"),
            train_domain=(-1.0, 1.0),
            heldout_domain=(-0.9, 0.9),
            extrap_domain=(1.05, 1.6),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-04 polynomial negative control",
            normalized_dimensionless=True,
        ),
        "rational_decay": DemoSpec(
            name="rational_decay",
            variable="x",
            description="v1.15 negative control: 1/(1+x) on a positive safe domain.",
            target=lambda a: (1.0 / (1.0 + a)).astype(np.complex128),
            candidate=_sympy_candidate(1 / (1 + x), "x", "rational_decay_catalog"),
            train_domain=(0.0, 4.0),
            heldout_domain=(0.1, 3.7),
            extrap_domain=(4.1, 5.5),
            source_document=".planning/ROADMAP.md",
            source_linkage="v1.15 BENCH-04 rational negative control",
            normalized_dimensionless=True,
        ),
        "planck": DemoSpec(
            name="planck",
            variable="x",
            description="Flagship normalized Planck spectrum from FOR_DEMO.md.",
            target=lambda a: (a**3 / (np.exp(a) - 1.0)).astype(np.complex128),
            candidate=_sympy_candidate(x**3 / (sp.exp(x) - 1), "x", "planck_catalog"),
            train_domain=(0.2, 8.0),
            heldout_domain=(0.25, 7.5),
            extrap_domain=(8.1, 10.0),
            source_document="sources/FOR_DEMO.md",
            source_linkage="Normalized Planck spectrum flagship dimensionless physics demo",
            normalized_dimensionless=True,
        ),
    }
    specs.update(_basin_demo_specs())
    specs.update(_depth_curve_demo_specs())
    return specs


def expanded_dataset_specs() -> dict[str, ExpandedDatasetSpec]:
    x = sp.Symbol("x")
    t = sp.Symbol("t")
    a = sp.Symbol("a")
    current = sp.Symbol("current_amp")
    resistance = sp.Symbol("resistance_ohm")
    return {
        "noisy_beer_lambert_sweep": ExpandedDatasetSpec(
            id="noisy_beer_lambert_sweep",
            formula_id="beer_lambert",
            description="Synthetic Beer-Lambert sweep with controlled relative Gaussian observation noise.",
            variables=("x",),
            target=lambda inputs: np.exp(-0.8 * inputs["x"]),
            candidate=_sympy_candidate(sp.exp(-sp.Float("0.8") * x), "x", "noisy_beer_lambert_clean_law"),
            split_domains={
                "train": {"x": (0.0, 3.0)},
                "selection": {"x": (0.1, 2.8)},
                "heldout": {"x": (0.15, 2.7)},
                "extrapolation": {"x": (3.1, 4.5)},
                "final_confirmation": {"x": (0.05, 4.25)},
            },
            units={"x": "dimensionless_absorbance_path"},
            target_unit="relative_intensity",
            classification="synthetic",
            category="noisy_synthetic_sweep",
            source="generated_from_clean_beer_lambert_formula",
            source_url=None,
            generator="linspace_with_seeded_jitter_plus_relative_gaussian_noise",
            noise_policy={"type": "gaussian_relative", "relative_sigma": 0.01, "applies_to": ["train", "selection", "heldout"]},
            split_policy={"type": "independent_domains", "roles": _expanded_split_roles()},
            domain_constraints={"x": {"min": 0.0, "max": 4.5, "closed": True}},
            compatible_contracts=("verifier", "benchmark_track", "baseline_harness"),
        ),
        "michaelis_parameter_identifiability": ExpandedDatasetSpec(
            id="michaelis_parameter_identifiability",
            formula_id="michaelis_menten",
            description="Synthetic Michaelis-Menten parameter-identifiability stress with low-substrate and saturation-biased splits.",
            variables=("x",),
            target=lambda inputs: 2.0 * inputs["x"] / (0.5 + inputs["x"]),
            candidate=_sympy_candidate(2 * x / (sp.Float("0.5") + x), "x", "michaelis_identifiability_clean_law"),
            split_domains={
                "train": {"x": (0.05, 0.9)},
                "selection": {"x": (0.12, 1.6)},
                "heldout": {"x": (1.8, 4.5)},
                "extrapolation": {"x": (4.8, 7.0)},
                "final_confirmation": {"x": (0.08, 6.5)},
            },
            units={"x": "millimolar_substrate_concentration"},
            target_unit="micromole_per_minute",
            classification="synthetic",
            category="parameter_identifiability_stress",
            source="generated_from_michaelis_menten_formula_with_fixed_parameters",
            source_url=None,
            generator="split_domains_selected_to_stress_vmax_km_identifiability",
            noise_policy={"type": "none"},
            split_policy={"type": "domain_shift_identifiability", "roles": _expanded_split_roles()},
            domain_constraints={"x": {"min": 0.05, "max": 7.0, "positive": True}},
            compatible_contracts=("verifier", "benchmark_track", "baseline_harness"),
        ),
        "multivariable_arrhenius_surface": ExpandedDatasetSpec(
            id="multivariable_arrhenius_surface",
            formula_id="arrhenius",
            description="Synthetic multivariable Arrhenius surface with variable pre-exponential factor and dimensionless temperature.",
            variables=("a", "t"),
            target=lambda inputs: inputs["a"] * np.exp(-0.8 / inputs["t"]),
            candidate=SympyCandidate(a * sp.exp(-sp.Float("0.8") / t), ("a", "t"), name="multivariable_arrhenius_clean_law"),
            split_domains={
                "train": {"a": (0.8, 1.2), "t": (0.6, 2.5)},
                "selection": {"a": (0.85, 1.3), "t": (0.7, 2.7)},
                "heldout": {"a": (0.75, 1.35), "t": (0.65, 2.8)},
                "extrapolation": {"a": (1.25, 1.6), "t": (2.9, 4.2)},
                "final_confirmation": {"a": (0.7, 1.55), "t": (0.6, 4.0)},
            },
            units={"a": "dimensionless_rate_prefactor", "t": "dimensionless_temperature"},
            target_unit="dimensionless_rate",
            classification="synthetic",
            category="multivariable_case",
            source="generated_from_multivariable_arrhenius_formula",
            source_url=None,
            generator="independent_seeded_uniform_multivariable_sampling",
            noise_policy={"type": "none"},
            split_policy={"type": "independent_multivariable_domains", "roles": _expanded_split_roles()},
            domain_constraints={"a": {"min": 0.7, "max": 1.6}, "t": {"min": 0.6, "max": 4.2, "positive": True}},
            compatible_contracts=("verifier", "benchmark_track", "baseline_harness"),
        ),
        "unit_aware_ohm_law": ExpandedDatasetSpec(
            id="unit_aware_ohm_law",
            formula_id="ohm_law",
            description="Unit-aware semi-synthetic Ohm-law formulation with current, resistance, and voltage units.",
            variables=("current_amp", "resistance_ohm"),
            target=lambda inputs: inputs["current_amp"] * inputs["resistance_ohm"],
            candidate=SympyCandidate(current * resistance, ("current_amp", "resistance_ohm"), name="unit_aware_ohm_law"),
            split_domains={
                "train": {"current_amp": (0.01, 0.5), "resistance_ohm": (50.0, 500.0)},
                "selection": {"current_amp": (0.02, 0.45), "resistance_ohm": (75.0, 650.0)},
                "heldout": {"current_amp": (0.05, 0.7), "resistance_ohm": (100.0, 800.0)},
                "extrapolation": {"current_amp": (0.75, 1.0), "resistance_ohm": (850.0, 1200.0)},
                "final_confirmation": {"current_amp": (0.015, 0.95), "resistance_ohm": (60.0, 1100.0)},
            },
            units={"current_amp": "ampere", "resistance_ohm": "ohm"},
            target_unit="volt",
            classification="semi_synthetic",
            category="unit_aware_formulation",
            source="generated_from_ohm_law_with_physical_units",
            source_url=None,
            generator="unit_aware_independent_uniform_sampling",
            noise_policy={"type": "none"},
            split_policy={"type": "unit_aware_independent_domains", "roles": _expanded_split_roles()},
            domain_constraints={
                "current_amp": {"min": 0.01, "max": 1.0, "unit": "ampere", "positive": True},
                "resistance_ohm": {"min": 50.0, "max": 1200.0, "unit": "ohm", "positive": True},
            },
            compatible_contracts=("verifier", "benchmark_track", "baseline_harness"),
        ),
        "real_hubble_1929": ExpandedDatasetSpec(
            id="real_hubble_1929",
            formula_id="hubble_velocity_distance",
            description="Real Hubble 1929 nebula distance and recession-velocity observations with fixed independent splits.",
            variables=("distance_mpc",),
            target=None,
            candidate=None,
            split_domains={},
            units={"distance_mpc": "megaparsec"},
            target_unit="kilometre_per_second",
            classification="real",
            category="real_dataset_path",
            source="Hubble 1929 velocity-distance data table",
            source_url="https://www2.stat.duke.edu/courses/Fall03/sta113/Hubble.html",
            generator="committed_csv_fixture_with_fixed_split_column",
            noise_policy={"type": "observational", "known_noise_model": False},
            split_policy={"type": "fixed_csv_split_column", "roles": _expanded_split_roles()},
            domain_constraints={"distance_mpc": {"min": 0.032, "max": 2.0, "positive": True}},
            compatible_contracts=("verifier", "benchmark_track", "baseline_harness"),
            data_path=REAL_DATA_ROOT / "hubble_1929_velocity_distance.csv",
        ),
    }


def list_expanded_datasets() -> tuple[str, ...]:
    return tuple(expanded_dataset_specs())


def get_expanded_dataset(dataset_id: str) -> ExpandedDatasetSpec:
    specs = expanded_dataset_specs()
    try:
        return specs[dataset_id]
    except KeyError as exc:
        available = ", ".join(sorted(specs))
        raise KeyError(f"Unknown expanded dataset {dataset_id!r}. Available: {available}") from exc


def make_expanded_dataset_splits(dataset_id: str, *, points: int = 80, seed: int = 0) -> list[DataSplit]:
    return get_expanded_dataset(dataset_id).make_splits(points=points, seed=seed)


def expanded_dataset_manifest(dataset_id: str, *, points: int = 80, seed: int = 0, tolerance: float = 1e-8) -> dict[str, Any]:
    return get_expanded_dataset(dataset_id).manifest(points=points, seed=seed, tolerance=tolerance)


def get_demo(name: str) -> DemoSpec:
    specs = demo_specs()
    try:
        return specs[name]
    except KeyError as exc:
        available = ", ".join(sorted(specs))
        raise KeyError(f"Unknown demo {name!r}. Available: {available}") from exc


def _array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("utf-8"))
    digest.update(json.dumps(array.shape, separators=(",", ":")).encode("utf-8"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def proof_dataset_manifest(formula_id: str, *, points: int = 80, seed: int = 0, tolerance: float = 1e-8) -> dict[str, Any]:
    points = int(points)
    tolerance = float(tolerance)
    if points <= 0:
        raise ValueError("points must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    spec = get_demo(formula_id)
    splits = spec.make_splits(points=points, seed=seed)
    domains = {
        "train": spec.train_domain,
        "heldout": spec.heldout_domain,
        "extrapolation": spec.extrap_domain,
    }
    split_metadata: list[dict[str, Any]] = []
    for split in splits:
        inputs = split.inputs[spec.variable]
        split_metadata.append(
            {
                "name": split.name,
                "domain": [float(value) for value in domains[split.name]],
                "count": int(len(inputs)),
                "input_sha256": _array_sha256(inputs),
                "target_sha256": _array_sha256(split.target),
            }
        )

    manifest: dict[str, Any] = {
        "schema": "eml.proof_dataset_manifest.v1",
        "formula_id": spec.name,
        "variable": spec.variable,
        "seed": int(seed),
        "points": points,
        "tolerance": tolerance,
        "sample_policy": "linspace_with_seeded_0.2_percent_jitter",
        "splits": split_metadata,
        "provenance": spec.formula_provenance(),
    }
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**manifest, "manifest_sha256": hashlib.sha256(encoded).hexdigest()}
