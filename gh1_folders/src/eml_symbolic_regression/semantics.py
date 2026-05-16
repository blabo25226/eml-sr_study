"""Canonical and training-mode EML semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch

from .branch import principal_log_branch_diagnostics


@dataclass(frozen=True)
class EmlOperator:
    """Operator-family metadata for raw, centered, and GEML nodes."""

    family: str = "raw_eml"
    s: float = 1.0
    t: complex = 1.0 + 0.0j
    terminal: str = "one"
    a: complex = 1.0 + 0.0j
    specialization: str = ""

    def __post_init__(self) -> None:
        family = str(self.family)
        if family in {"eml", "raw"}:
            family = "raw_eml"
        if family in {"geml", "geml_a"}:
            family = "geml_a"
        if family in {"ipi_eml", "i*pi_eml", "ipieml"}:
            family = "geml_a"
            object.__setattr__(self, "a", 1j * np.pi)
            object.__setattr__(self, "specialization", "ipi_eml")
        if family not in {"raw_eml", "ceml_s_t", "ceml_s", "zeml_s", "geml_a"}:
            raise ValueError(f"unknown EML operator family: {family!r}")
        s = float(self.s)
        if not np.isfinite(s) or s <= 0:
            raise ValueError("centered EML scale s must be finite and positive")
        t = complex(self.t)
        if not (np.isfinite(t.real) and np.isfinite(t.imag)):
            raise ValueError("centered EML shift t must be finite")
        a = complex(self.a)
        if not (np.isfinite(a.real) and np.isfinite(a.imag)):
            raise ValueError("GEML parameter a must be finite")
        if abs(a) <= 0.0:
            raise ValueError("GEML parameter a must be nonzero")
        terminal = str(self.terminal)
        specialization = str(self.specialization)
        if family == "raw_eml":
            s = 1.0
            t = 1.0 + 0.0j
            terminal = "one"
            a = 1.0 + 0.0j
            specialization = "eml"
        elif family == "ceml_s":
            t = 1.0 + 0.0j
            terminal = "one"
            a = 1.0 + 0.0j
            specialization = ""
        elif family == "zeml_s":
            t = 0.0 + 0.0j
            terminal = "zero"
            a = 1.0 + 0.0j
            specialization = ""
        elif family == "ceml_s_t":
            terminal = terminal or "shifted"
            a = 1.0 + 0.0j
            specialization = ""
        elif family == "geml_a":
            if specialization == "ipi_eml" and abs(a - 1j * np.pi) > 1e-12:
                raise ValueError("i*pi EML specialization requires a = i*pi")
            if specialization == "eml" and abs(a - 1.0) > 1e-15:
                raise ValueError("EML specialization requires a = 1")
            if abs(a - 1.0) <= 1e-15 and specialization in {"", "eml", "custom"}:
                family = "raw_eml"
                s = 1.0
                t = 1.0 + 0.0j
                terminal = "one"
                a = 1.0 + 0.0j
                specialization = "eml"
            else:
                s = 1.0
                t = 1.0 + 0.0j
                terminal = "one"
                if abs(a - 1j * np.pi) <= 1e-12:
                    specialization = "ipi_eml"
                elif not specialization:
                    specialization = "custom"
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "s", s)
        object.__setattr__(self, "t", t)
        object.__setattr__(self, "terminal", terminal)
        object.__setattr__(self, "a", a)
        object.__setattr__(self, "specialization", specialization)

    @property
    def is_raw(self) -> bool:
        return self.family == "raw_eml"

    @property
    def is_centered(self) -> bool:
        return self.family in {"ceml_s_t", "ceml_s", "zeml_s"}

    @property
    def is_geml(self) -> bool:
        return self.family == "geml_a"

    @property
    def label(self) -> str:
        if self.family == "raw_eml":
            return "raw_eml"
        if self.family == "ceml_s":
            return f"CEML_{_format_number(self.s)}"
        if self.family == "zeml_s":
            return f"ZEML_{_format_number(self.s)}"
        if self.family == "geml_a":
            if self.specialization == "ipi_eml":
                return "ipi_eml"
            if self.specialization == "eml":
                return "GEML_1"
            return f"GEML_{_format_complex(self.a)}"
        return f"cEML_s{_format_number(self.s)}_t{_format_complex(self.t)}"

    @property
    def singularity(self) -> complex:
        return self.t - self.s

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "family": self.family,
            "label": self.label,
            "s": self.s,
            "terminal": self.terminal,
        }
        if self.t.imag:
            payload["t"] = {"real": repr(float(self.t.real)), "imag": repr(float(self.t.imag))}
        else:
            payload["t"] = float(self.t.real)
        if self.is_geml:
            payload["a"] = _complex_payload(self.a)
            payload["geml_parameter"] = _complex_payload(self.a)
            payload["named_specialization"] = self.specialization
        if self.is_centered:
            payload["singularity"] = (
                {"real": repr(float(self.singularity.real)), "imag": repr(float(self.singularity.imag))}
                if self.singularity.imag
                else float(self.singularity.real)
            )
        return payload

    @classmethod
    def from_mapping(cls, payload: dict[str, Any] | None) -> "EmlOperator":
        if payload is None:
            return raw_eml_operator()
        t_payload = payload.get("t", 1.0)
        t = _complex_from_payload(t_payload)
        a_payload = payload.get("a", payload.get("geml_parameter", 1.0))
        return cls(
            family=str(payload.get("family", payload.get("name", "raw_eml"))),
            s=float(payload.get("s", 1.0)),
            t=t,
            terminal=str(payload.get("terminal", "")),
            a=_complex_from_payload(a_payload),
            specialization=str(payload.get("named_specialization", payload.get("specialization", ""))),
        )


def _format_number(value: float) -> str:
    value = float(value)
    return str(int(value)) if value.is_integer() else repr(value)


def _format_complex(value: complex) -> str:
    value = complex(value)
    if abs(value.imag) < 1e-15:
        return _format_number(value.real)
    if abs(value.real) < 1e-15 and abs(value.imag - np.pi) <= 1e-12:
        return "i*pi"
    return repr(value)


def _complex_payload(value: complex) -> str | float | dict[str, str]:
    value = complex(value)
    if abs(value.imag) < 1e-15:
        return float(value.real)
    return {"real": repr(float(value.real)), "imag": repr(float(value.imag))}


def _complex_from_payload(value: Any) -> complex:
    if isinstance(value, dict):
        return complex(float(value["real"]), float(value["imag"]))
    if isinstance(value, complex):
        return value
    if isinstance(value, str):
        return _complex_from_spec(value)
    return complex(float(value), 0.0)


def _complex_from_spec(text: str) -> complex:
    normalized = text.strip().lower().replace(" ", "")
    if normalized in {"i*pi", "ipi", "pi*i", "1j*pi", "j*pi"}:
        return 1j * np.pi
    if normalized in {"-i*pi", "-ipi", "-pi*i", "-1j*pi", "-j*pi"}:
        return -1j * np.pi
    return complex(normalized.replace("i", "j"))


def raw_eml_operator() -> EmlOperator:
    return EmlOperator("raw_eml")


def geml_operator(a: complex, *, specialization: str = "") -> EmlOperator:
    if abs(complex(a) - 1.0) <= 1e-15 and specialization in {"", "eml", "custom"}:
        return raw_eml_operator()
    return EmlOperator("geml_a", a=complex(a), specialization=specialization)


def ipi_eml_operator() -> EmlOperator:
    return geml_operator(1j * np.pi, specialization="ipi_eml")


def ceml_operator(s: float, t: complex = 1.0 + 0.0j) -> EmlOperator:
    return EmlOperator("ceml_s_t", s=s, t=t, terminal="shifted")


def ceml_s_operator(s: float) -> EmlOperator:
    return EmlOperator("ceml_s", s=s)


def zeml_s_operator(s: float) -> EmlOperator:
    return EmlOperator("zeml_s", s=s)


def eml_operator_from_spec(value: Any) -> EmlOperator:
    """Parse an operator family from stable artifact/config input."""

    if value is None:
        return raw_eml_operator()
    if isinstance(value, EmlOperator):
        return value
    if isinstance(value, dict):
        return EmlOperator.from_mapping(value)
    text = str(value).strip()
    lower = text.lower()
    if lower in {"raw", "raw_eml", "eml"}:
        return raw_eml_operator()
    if lower in {"ipi", "i*pi", "ipi_eml", "i*pi_eml", "geml:ipi", "geml:i*pi", "geml_a:i*pi"}:
        return ipi_eml_operator()
    if lower.startswith("geml:") or lower.startswith("geml_a:"):
        return geml_operator(_complex_from_spec(text.split(":", 1)[1]))
    if lower.startswith("ceml_s:"):
        return ceml_s_operator(float(text.split(":", 1)[1]))
    if lower.startswith("zeml_s:"):
        return zeml_s_operator(float(text.split(":", 1)[1]))
    if lower.startswith("ceml_s_t:"):
        _, scale, shift = text.split(":", 2)
        return ceml_operator(float(scale), complex(float(shift), 0.0))
    if lower.startswith("ceml_"):
        return ceml_s_operator(float(text.split("_", 1)[1]))
    if lower.startswith("zeml_"):
        return zeml_s_operator(float(text.split("_", 1)[1]))
    raise ValueError(f"cannot parse EML operator family spec: {value!r}")


@dataclass
class TrainingSemanticsConfig:
    """Training-only numerical controls that leave verification semantics unchanged."""

    clamp_exp_real: float = 40.0
    log_domain_epsilon: float = 1e-9
    log_safety_weight: float = 0.0
    log_safety_margin: float = 1e-6
    log_safety_imag_tolerance: float = 1e-6
    mode: str = "guarded"

    def __post_init__(self) -> None:
        mode = str(self.mode)
        if mode not in {"guarded", "faithful"}:
            raise ValueError("training semantics mode must be 'guarded' or 'faithful'")
        self.mode = mode

    @property
    def uses_training_guards(self) -> bool:
        return self.mode == "guarded"


@dataclass
class AnomalyStats:
    """Small diagnostic bundle for one or more EML evaluations."""

    nan_count: int = 0
    inf_count: int = 0
    clamp_count: int = 0
    max_abs: float = 0.0
    max_exp_real: float = 0.0
    exp_overflow_count: int = 0
    log_small_magnitude_count: int = 0
    log_non_positive_real_count: int = 0
    log_branch_cut_count: int = 0
    branch_input_count: int = 0
    log_branch_cut_proximity_count: int = 0
    log_branch_cut_crossing_count: int = 0
    log_branch_cut_min_distance: float | None = None
    log_non_finite_input_count: int = 0
    invalid_domain_skip_count: int = 0
    expm1_overflow_count: int = 0
    log1p_branch_cut_count: int = 0
    shifted_singularity_near_count: int = 0
    shifted_singularity_min_distance: float | None = None
    log_safety_penalty: float = 0.0
    by_node: dict[str, dict[str, float | int]] = field(default_factory=dict)
    _training_penalty: torch.Tensor | None = field(default=None, init=False, repr=False, compare=False)

    def update_torch(
        self,
        value: torch.Tensor,
        exp_arg: torch.Tensor | None = None,
        log_arg: torch.Tensor | None = None,
        node: str | None = None,
        clamp_count: int = 0,
        exp_overflow_count: int = 0,
        log_small_magnitude_count: int = 0,
        log_non_positive_real_count: int = 0,
        log_branch_cut_count: int = 0,
        branch_input_count: int = 0,
        log_branch_cut_proximity_count: int = 0,
        log_branch_cut_crossing_count: int = 0,
        log_branch_cut_min_distance: float | None = None,
        log_non_finite_input_count: int = 0,
        invalid_domain_skip_count: int = 0,
        expm1_overflow_count: int = 0,
        log1p_branch_cut_count: int = 0,
        shifted_singularity_near_count: int = 0,
        shifted_singularity_min_distance: float | None = None,
        log_safety_penalty: torch.Tensor | None = None,
    ) -> None:
        detached = value.detach()
        finite_abs = torch.nan_to_num(torch.abs(detached), nan=0.0, posinf=0.0, neginf=0.0)
        nan_count = int(torch.isnan(detached.real).sum().item() + torch.isnan(detached.imag).sum().item())
        inf_count = int(torch.isinf(detached.real).sum().item() + torch.isinf(detached.imag).sum().item())
        max_abs = float(finite_abs.max().item()) if finite_abs.numel() else 0.0
        max_exp_real = 0.0
        if exp_arg is not None and exp_arg.numel():
            max_exp_real = float(torch.max(torch.abs(exp_arg.detach().real)).item())

        self.nan_count += nan_count
        self.inf_count += inf_count
        self.clamp_count += clamp_count
        self.max_abs = max(self.max_abs, max_abs)
        self.max_exp_real = max(self.max_exp_real, max_exp_real)
        self.exp_overflow_count += exp_overflow_count
        self.log_small_magnitude_count += log_small_magnitude_count
        self.log_non_positive_real_count += log_non_positive_real_count
        self.log_branch_cut_count += log_branch_cut_count
        self.branch_input_count += branch_input_count
        self.log_branch_cut_proximity_count += log_branch_cut_proximity_count
        self.log_branch_cut_crossing_count += log_branch_cut_crossing_count
        if log_branch_cut_min_distance is not None and np.isfinite(log_branch_cut_min_distance):
            if self.log_branch_cut_min_distance is None:
                self.log_branch_cut_min_distance = float(log_branch_cut_min_distance)
            else:
                self.log_branch_cut_min_distance = min(self.log_branch_cut_min_distance, float(log_branch_cut_min_distance))
        self.log_non_finite_input_count += log_non_finite_input_count
        self.invalid_domain_skip_count += invalid_domain_skip_count
        self.expm1_overflow_count += expm1_overflow_count
        self.log1p_branch_cut_count += log1p_branch_cut_count
        self.shifted_singularity_near_count += shifted_singularity_near_count
        if shifted_singularity_min_distance is not None and np.isfinite(shifted_singularity_min_distance):
            if self.shifted_singularity_min_distance is None:
                self.shifted_singularity_min_distance = float(shifted_singularity_min_distance)
            else:
                self.shifted_singularity_min_distance = min(
                    self.shifted_singularity_min_distance,
                    float(shifted_singularity_min_distance),
                )

        penalty_value = 0.0
        if log_safety_penalty is not None:
            penalty_value = float(log_safety_penalty.detach().item())
            self.log_safety_penalty += penalty_value
            if self._training_penalty is None:
                self._training_penalty = log_safety_penalty
            else:
                self._training_penalty = self._training_penalty + log_safety_penalty

        if node:
            self.by_node[node] = {
                "nan_count": nan_count,
                "inf_count": inf_count,
                "clamp_count": clamp_count,
                "max_abs": max_abs,
                "max_exp_real": max_exp_real,
                "exp_overflow_count": exp_overflow_count,
                "log_small_magnitude_count": log_small_magnitude_count,
                "log_non_positive_real_count": log_non_positive_real_count,
                "log_branch_cut_count": log_branch_cut_count,
                "branch_input_count": branch_input_count,
                "log_branch_cut_proximity_count": log_branch_cut_proximity_count,
                "log_branch_cut_crossing_count": log_branch_cut_crossing_count,
                "log_branch_cut_min_distance": log_branch_cut_min_distance,
                "log_non_finite_input_count": log_non_finite_input_count,
                "invalid_domain_skip_count": invalid_domain_skip_count,
                "expm1_overflow_count": expm1_overflow_count,
                "log1p_branch_cut_count": log1p_branch_cut_count,
                "shifted_singularity_near_count": shifted_singularity_near_count,
                "shifted_singularity_min_distance": shifted_singularity_min_distance,
                "log_safety_penalty": penalty_value,
            }

    def as_dict(self) -> dict[str, Any]:
        return {
            "nan_count": self.nan_count,
            "inf_count": self.inf_count,
            "clamp_count": self.clamp_count,
            "max_abs": self.max_abs,
            "max_exp_real": self.max_exp_real,
            "exp_overflow_count": self.exp_overflow_count,
            "log_small_magnitude_count": self.log_small_magnitude_count,
            "log_non_positive_real_count": self.log_non_positive_real_count,
            "log_branch_cut_count": self.log_branch_cut_count,
            "branch_input_count": self.branch_input_count,
            "log_branch_cut_proximity_count": self.log_branch_cut_proximity_count,
            "log_branch_cut_crossing_count": self.log_branch_cut_crossing_count,
            "log_branch_cut_min_distance": self.log_branch_cut_min_distance,
            "log_non_finite_input_count": self.log_non_finite_input_count,
            "invalid_domain_skip_count": self.invalid_domain_skip_count,
            "expm1_overflow_count": self.expm1_overflow_count,
            "log1p_branch_cut_count": self.log1p_branch_cut_count,
            "shifted_singularity_near_count": self.shifted_singularity_near_count,
            "shifted_singularity_min_distance": self.shifted_singularity_min_distance,
            "log_safety_penalty": self.log_safety_penalty,
            "by_node": self.by_node,
        }

    def training_penalty(self, *, device: torch.device | None = None) -> torch.Tensor:
        if self._training_penalty is None:
            return torch.zeros((), dtype=torch.float64, device=device)
        return self._training_penalty.to(device=device) if device is not None else self._training_penalty


def as_complex_tensor(value: Any, *, device: torch.device | None = None) -> torch.Tensor:
    """Convert input data to torch.complex128."""

    if isinstance(value, torch.Tensor):
        tensor = value.to(dtype=torch.complex128)
        return tensor.to(device=device) if device is not None else tensor
    return torch.as_tensor(value, dtype=torch.complex128, device=device)


def _torch_branch_diagnostics(log_arg: torch.Tensor, semantics: TrainingSemanticsConfig) -> dict[str, Any]:
    return principal_log_branch_diagnostics(
        log_arg.detach().cpu().numpy(),
        proximity_tolerance=max(float(semantics.log_safety_imag_tolerance), float(semantics.log_domain_epsilon)),
        zero_tolerance=float(semantics.log_domain_epsilon),
    ).as_dict()


def eml_torch(
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    training: bool = False,
    clamp_exp_real: float = 40.0,
    semantics: TrainingSemanticsConfig | None = None,
    stats: AnomalyStats | None = None,
    node: str | None = None,
) -> torch.Tensor:
    """Evaluate EML in PyTorch.

    Training mode clamps only the real part entering exp. Verification
    should call this with training=False.
    """

    x = as_complex_tensor(x)
    y = as_complex_tensor(y, device=x.device)
    semantics = semantics or TrainingSemanticsConfig(clamp_exp_real=clamp_exp_real)
    exp_arg = x
    clamp_count = 0
    exp_overflow_count = 0

    use_training_guards = training and semantics.uses_training_guards
    if use_training_guards:
        real = torch.clamp(x.real, min=-semantics.clamp_exp_real, max=semantics.clamp_exp_real)
        clamp_count = int((real != x.real).sum().detach().item())
        exp_overflow_count = int((x.detach().real > semantics.clamp_exp_real).sum().item())
        exp_arg = torch.complex(real, x.imag)
    else:
        exp_overflow_threshold = float(np.log(np.finfo(np.float64).max))
        exp_overflow_count = int((x.detach().real > exp_overflow_threshold).sum().item())

    log_arg = y.detach()
    log_abs = torch.nan_to_num(torch.abs(log_arg), nan=float("inf"), posinf=float("inf"), neginf=float("inf"))
    log_small_magnitude_count = int((log_abs < semantics.log_domain_epsilon).sum().item())
    log_non_positive_real_count = int((log_arg.real <= 0).sum().item())
    log_branch_cut_count = int(
        ((torch.abs(log_arg.imag) <= semantics.log_domain_epsilon) & (log_arg.real <= 0)).sum().item()
    )
    log_non_finite_input_count = int(
        torch.isnan(log_arg.real).sum().item()
        + torch.isnan(log_arg.imag).sum().item()
        + torch.isinf(log_arg.real).sum().item()
        + torch.isinf(log_arg.imag).sum().item()
    )
    branch_diagnostics = _torch_branch_diagnostics(log_arg, semantics)

    log_safety_penalty = None
    if use_training_guards and semantics.log_safety_weight > 0:
        safe_margin = max(float(semantics.log_safety_margin), float(semantics.log_domain_epsilon))
        imag_tolerance = max(float(semantics.log_safety_imag_tolerance), float(semantics.log_domain_epsilon))
        real_pressure = torch.relu(safe_margin - y.real)
        axis_proximity = torch.relu(imag_tolerance - torch.abs(y.imag)) / imag_tolerance
        magnitude_pressure = torch.relu(safe_margin - torch.abs(y))
        log_safety_penalty = semantics.log_safety_weight * torch.mean(real_pressure * axis_proximity + magnitude_pressure)

    out = torch.exp(exp_arg) - torch.log(y)
    if stats is not None:
        stats.update_torch(
            out,
            exp_arg=exp_arg,
            log_arg=log_arg,
            node=node,
            clamp_count=clamp_count,
            exp_overflow_count=exp_overflow_count,
            log_small_magnitude_count=log_small_magnitude_count,
            log_non_positive_real_count=log_non_positive_real_count,
            log_branch_cut_count=log_branch_cut_count,
            branch_input_count=int(branch_diagnostics["input_count"]),
            log_branch_cut_proximity_count=int(branch_diagnostics["branch_cut_proximity_count"]),
            log_branch_cut_crossing_count=int(branch_diagnostics["branch_cut_crossing_count"]),
            log_branch_cut_min_distance=branch_diagnostics["min_branch_cut_distance"],
            log_non_finite_input_count=log_non_finite_input_count,
            invalid_domain_skip_count=int(branch_diagnostics["invalid_domain_skip_count"]),
            log_safety_penalty=log_safety_penalty,
        )
    return out


def centered_eml_torch(
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    operator: EmlOperator,
    training: bool = False,
    clamp_exp_real: float = 40.0,
    semantics: TrainingSemanticsConfig | None = None,
    stats: AnomalyStats | None = None,
    node: str | None = None,
) -> torch.Tensor:
    """Evaluate centered/scaled EML in PyTorch using expm1/log1p coordinates."""

    if operator.is_raw:
        return eml_torch(
            x,
            y,
            training=training,
            clamp_exp_real=clamp_exp_real,
            semantics=semantics,
            stats=stats,
            node=node,
        )
    if operator.is_geml:
        return geml_torch(
            x,
            y,
            operator=operator,
            training=training,
            clamp_exp_real=clamp_exp_real,
            semantics=semantics,
            stats=stats,
            node=node,
        )
    if not operator.is_centered:
        raise ValueError(f"centered EML evaluator cannot handle operator family {operator.family!r}")

    x = as_complex_tensor(x)
    y = as_complex_tensor(y, device=x.device)
    semantics = semantics or TrainingSemanticsConfig(clamp_exp_real=clamp_exp_real)
    s_real = torch.tensor(operator.s, dtype=torch.float64, device=x.device)
    s = torch.complex(s_real, torch.zeros_like(s_real))
    t = torch.tensor(operator.t, dtype=torch.complex128, device=x.device)

    exp_arg = x / s
    clamp_count = 0
    expm1_overflow_count = 0
    use_training_guards = training and semantics.uses_training_guards
    if use_training_guards:
        real = torch.clamp(exp_arg.real, min=-semantics.clamp_exp_real, max=semantics.clamp_exp_real)
        clamp_count = int((real != exp_arg.real).sum().detach().item())
        expm1_overflow_count = int((exp_arg.detach().real > semantics.clamp_exp_real).sum().item())
        exp_arg = torch.complex(real, exp_arg.imag)
    else:
        exp_overflow_threshold = float(np.log(np.finfo(np.float64).max))
        expm1_overflow_count = int((exp_arg.detach().real > exp_overflow_threshold).sum().item())

    log1p_input = (y - t) / s
    log_arg = 1.0 + log1p_input.detach()
    log_abs = torch.nan_to_num(torch.abs(log_arg), nan=float("inf"), posinf=float("inf"), neginf=float("inf"))
    log_small_magnitude_count = int((log_abs < semantics.log_domain_epsilon).sum().item())
    log_non_positive_real_count = int((log_arg.real <= 0).sum().item())
    log_branch_cut_count = int(
        ((torch.abs(log_arg.imag) <= semantics.log_domain_epsilon) & (log_arg.real <= 0)).sum().item()
    )
    log_non_finite_input_count = int(
        torch.isnan(log_arg.real).sum().item()
        + torch.isnan(log_arg.imag).sum().item()
        + torch.isinf(log_arg.real).sum().item()
        + torch.isinf(log_arg.imag).sum().item()
    )
    branch_diagnostics = _torch_branch_diagnostics(log_arg, semantics)
    singularity = t - s
    shifted_distance = torch.nan_to_num(torch.abs(y.detach() - singularity), nan=float("inf"), posinf=float("inf"), neginf=float("inf"))
    shifted_singularity_near_count = int((shifted_distance < semantics.log_domain_epsilon).sum().item())
    shifted_singularity_min_distance = float(shifted_distance.min().item()) if shifted_distance.numel() else None

    log_safety_penalty = None
    if use_training_guards and semantics.log_safety_weight > 0:
        safe_margin = max(float(semantics.log_safety_margin), float(semantics.log_domain_epsilon))
        imag_tolerance = max(float(semantics.log_safety_imag_tolerance), float(semantics.log_domain_epsilon))
        real_pressure = torch.relu(safe_margin - log_arg.real)
        axis_proximity = torch.relu(imag_tolerance - torch.abs(log_arg.imag)) / imag_tolerance
        magnitude_pressure = torch.relu(safe_margin - torch.abs(log_arg))
        log_safety_penalty = semantics.log_safety_weight * torch.mean(real_pressure * axis_proximity + magnitude_pressure)

    out = s * torch.expm1(exp_arg) - s * torch.log1p(log1p_input)
    if stats is not None:
        stats.update_torch(
            out,
            exp_arg=exp_arg,
            log_arg=log_arg,
            node=node,
            clamp_count=clamp_count,
            expm1_overflow_count=expm1_overflow_count,
            log_small_magnitude_count=log_small_magnitude_count,
            log_non_positive_real_count=log_non_positive_real_count,
            log_branch_cut_count=log_branch_cut_count,
            branch_input_count=int(branch_diagnostics["input_count"]),
            log_branch_cut_proximity_count=int(branch_diagnostics["branch_cut_proximity_count"]),
            log_branch_cut_crossing_count=int(branch_diagnostics["branch_cut_crossing_count"]),
            log_branch_cut_min_distance=branch_diagnostics["min_branch_cut_distance"],
            log1p_branch_cut_count=log_branch_cut_count,
            log_non_finite_input_count=log_non_finite_input_count,
            invalid_domain_skip_count=int(branch_diagnostics["invalid_domain_skip_count"]),
            shifted_singularity_near_count=shifted_singularity_near_count,
            shifted_singularity_min_distance=shifted_singularity_min_distance,
            log_safety_penalty=log_safety_penalty,
        )
    return out


def geml_torch(
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    operator: EmlOperator,
    training: bool = False,
    clamp_exp_real: float = 40.0,
    semantics: TrainingSemanticsConfig | None = None,
    stats: AnomalyStats | None = None,
    node: str | None = None,
) -> torch.Tensor:
    """Evaluate fixed-parameter GEML in PyTorch."""

    if operator.is_raw:
        return eml_torch(
            x,
            y,
            training=training,
            clamp_exp_real=clamp_exp_real,
            semantics=semantics,
            stats=stats,
            node=node,
        )
    if not operator.is_geml:
        raise ValueError(f"GEML evaluator cannot handle operator family {operator.family!r}")

    x = as_complex_tensor(x)
    y = as_complex_tensor(y, device=x.device)
    semantics = semantics or TrainingSemanticsConfig(clamp_exp_real=clamp_exp_real)
    a = torch.tensor(operator.a, dtype=torch.complex128, device=x.device)
    exp_arg = a * x
    clamp_count = 0
    exp_overflow_count = 0

    use_training_guards = training and semantics.uses_training_guards
    if use_training_guards:
        real = torch.clamp(exp_arg.real, min=-semantics.clamp_exp_real, max=semantics.clamp_exp_real)
        clamp_count = int((real != exp_arg.real).sum().detach().item())
        exp_overflow_count = int((exp_arg.detach().real > semantics.clamp_exp_real).sum().item())
        exp_arg = torch.complex(real, exp_arg.imag)
    else:
        exp_overflow_threshold = float(np.log(np.finfo(np.float64).max))
        exp_overflow_count = int((exp_arg.detach().real > exp_overflow_threshold).sum().item())

    log_arg = y.detach()
    log_abs = torch.nan_to_num(torch.abs(log_arg), nan=float("inf"), posinf=float("inf"), neginf=float("inf"))
    log_small_magnitude_count = int((log_abs < semantics.log_domain_epsilon).sum().item())
    log_non_positive_real_count = int((log_arg.real <= 0).sum().item())
    log_branch_cut_count = int(
        ((torch.abs(log_arg.imag) <= semantics.log_domain_epsilon) & (log_arg.real <= 0)).sum().item()
    )
    log_non_finite_input_count = int(
        torch.isnan(log_arg.real).sum().item()
        + torch.isnan(log_arg.imag).sum().item()
        + torch.isinf(log_arg.real).sum().item()
        + torch.isinf(log_arg.imag).sum().item()
    )
    branch_diagnostics = _torch_branch_diagnostics(log_arg, semantics)

    log_safety_penalty = None
    if use_training_guards and semantics.log_safety_weight > 0:
        safe_margin = max(float(semantics.log_safety_margin), float(semantics.log_domain_epsilon))
        imag_tolerance = max(float(semantics.log_safety_imag_tolerance), float(semantics.log_domain_epsilon))
        real_pressure = torch.relu(safe_margin - y.real)
        axis_proximity = torch.relu(imag_tolerance - torch.abs(y.imag)) / imag_tolerance
        magnitude_pressure = torch.relu(safe_margin - torch.abs(y))
        log_safety_penalty = semantics.log_safety_weight * torch.mean(real_pressure * axis_proximity + magnitude_pressure)

    out = torch.exp(exp_arg) - torch.log(y) / a
    if stats is not None:
        stats.update_torch(
            out,
            exp_arg=exp_arg,
            log_arg=log_arg,
            node=node,
            clamp_count=clamp_count,
            exp_overflow_count=exp_overflow_count,
            log_small_magnitude_count=log_small_magnitude_count,
            log_non_positive_real_count=log_non_positive_real_count,
            log_branch_cut_count=log_branch_cut_count,
            branch_input_count=int(branch_diagnostics["input_count"]),
            log_branch_cut_proximity_count=int(branch_diagnostics["branch_cut_proximity_count"]),
            log_branch_cut_crossing_count=int(branch_diagnostics["branch_cut_crossing_count"]),
            log_branch_cut_min_distance=branch_diagnostics["min_branch_cut_distance"],
            log_non_finite_input_count=log_non_finite_input_count,
            invalid_domain_skip_count=int(branch_diagnostics["invalid_domain_skip_count"]),
            log_safety_penalty=log_safety_penalty,
        )
    return out


def eml_numpy(x: Any, y: Any) -> np.ndarray:
    """Evaluate canonical EML with NumPy complex128 arrays."""

    x_arr = np.asarray(x, dtype=np.complex128)
    y_arr = np.asarray(y, dtype=np.complex128)
    return np.exp(x_arr) - np.log(y_arr)


def centered_eml_numpy(x: Any, y: Any, *, operator: EmlOperator) -> np.ndarray:
    """Evaluate centered/scaled EML with NumPy complex128 arrays."""

    if operator.is_raw:
        return eml_numpy(x, y)
    if operator.is_geml:
        return geml_numpy(x, y, operator=operator)
    if not operator.is_centered:
        raise ValueError(f"centered EML evaluator cannot handle operator family {operator.family!r}")
    x_arr = np.asarray(x, dtype=np.complex128)
    y_arr = np.asarray(y, dtype=np.complex128)
    s = np.complex128(operator.s)
    t = np.complex128(operator.t)
    return s * np.expm1(x_arr / s) - s * np.log1p((y_arr - t) / s)


def geml_numpy(x: Any, y: Any, *, operator: EmlOperator) -> np.ndarray:
    """Evaluate fixed-parameter GEML with NumPy complex128 arrays."""

    if operator.is_raw:
        return eml_numpy(x, y)
    if not operator.is_geml:
        raise ValueError(f"GEML evaluator cannot handle operator family {operator.family!r}")
    x_arr = np.asarray(x, dtype=np.complex128)
    y_arr = np.asarray(y, dtype=np.complex128)
    a = np.complex128(operator.a)
    return np.exp(a * x_arr) - np.log(y_arr) / a


def mse_complex_numpy(a: Any, b: Any) -> float:
    """Mean squared complex residual."""

    a_arr = np.asarray(a, dtype=np.complex128)
    b_arr = np.asarray(b, dtype=np.complex128)
    return float(np.mean(np.abs(a_arr - b_arr) ** 2))
