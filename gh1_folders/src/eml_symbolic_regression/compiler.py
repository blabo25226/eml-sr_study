"""Fail-closed SymPy subset compiler for exact EML ASTs."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

import numpy as np
import sympy as sp

from .expression import Const, Eml, Expr, Var, exp_of, format_constant_value, log_of


class CompileReason:
    UNSUPPORTED_OPERATOR = "unsupported_operator"
    UNSUPPORTED_POWER = "unsupported_power"
    UNKNOWN_VARIABLE = "unknown_variable"
    UNSAFE_CONSTANT = "unsafe_constant"
    CONSTANT_POLICY = "constant_policy"
    DEPTH_EXCEEDED = "depth_exceeded"
    NODE_BUDGET_EXCEEDED = "node_budget_exceeded"
    VALIDATION_FAILED = "validation_failed"


@dataclass(frozen=True)
class CompilerConfig:
    variables: tuple[str, ...] | None = None
    constant_policy: str = "literal_constants"
    max_depth: int = 13
    max_nodes: int = 256
    max_power: int = 3
    validation_tolerance: float = 1e-8
    enable_macros: bool = True


@dataclass(frozen=True)
class RuleTrace:
    rule: str
    source: str
    output_depth: int
    output_nodes: int
    assumptions: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "source": self.source,
            "output_depth": self.output_depth,
            "output_nodes": self.output_nodes,
            "assumptions": list(self.assumptions),
        }


@dataclass(frozen=True)
class CompileMetadata:
    source_expression: str
    normalized_expression: str
    variables: tuple[str, ...]
    constants: tuple[complex, ...]
    constant_policy: str
    depth: int
    node_count: int
    assumptions: tuple[str, ...]
    trace: tuple[RuleTrace, ...]
    unsupported_reason: str | None = None
    macro_diagnostics: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_expression": self.source_expression,
            "normalized_expression": self.normalized_expression,
            "variables": list(self.variables),
            "constants": [format_constant_value(value) for value in self.constants],
            "constant_policy": self.constant_policy,
            "depth": self.depth,
            "node_count": self.node_count,
            "assumptions": list(self.assumptions),
            "trace": [entry.as_dict() for entry in self.trace],
            "unsupported_reason": self.unsupported_reason,
            "macro_diagnostics": dict(self.macro_diagnostics) if self.macro_diagnostics is not None else None,
        }


@dataclass(frozen=True)
class CompileValidation:
    passed: bool
    max_abs_error: float
    mse: float
    tolerance: float
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "max_abs_error": self.max_abs_error,
            "mse": self.mse,
            "tolerance": self.tolerance,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CompileResult:
    expression: Expr
    metadata: CompileMetadata
    validation: CompileValidation | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "eml.compiler_result.v1",
            "metadata": self.metadata.as_dict(),
            "ast": self.expression.to_document(
                variables=list(self.metadata.variables),
                source="compiled_sympy",
                constant_policy=self.metadata.constant_policy,
            ),
            "validation": self.validation.as_dict() if self.validation else None,
        }


MACRO_RULES = (
    "reciprocal_shift_template",
    "saturation_ratio_template",
    "exponential_saturation_template",
    "low_degree_power_template",
    "direct_division_template",
    "scaled_exp_minus_one_template",
)


class UnsupportedExpression(ValueError):
    def __init__(self, reason: str, expression: Any, detail: str) -> None:
        self.reason = reason
        self.expression = str(expression)
        self.detail = detail
        super().__init__(f"{reason}: {self.expression}: {detail}")

    def as_dict(self) -> dict[str, str]:
        return {"reason": self.reason, "expression": self.expression, "detail": self.detail}


@dataclass(frozen=True)
class _UnitShift:
    base: sp.Expr
    offset: complex


@dataclass(frozen=True)
class _ExponentialSaturation:
    exponent: sp.Expr
    coefficient: complex


def subtract_expr(left: Expr, right: Expr) -> Expr:
    """Verified EML identity for left - right on the principal branch."""

    return Eml(log_of(left), exp_of(right))


def negate_expr(expr: Expr) -> Expr:
    """Verified EML identity for -expr over the complex evaluation path."""

    one = Const(1.0)
    return Eml(
        Eml(one, Eml(Eml(one, Eml(one, exp_of(expr))), one)),
        Eml(Eml(one, one), one),
    )


def add_expr(left: Expr, right: Expr) -> Expr:
    return subtract_expr(left, negate_expr(right))


def multiply_expr(left: Expr, right: Expr) -> Expr:
    """Verified EML identity for left * right."""

    one = Const(1.0)
    return Eml(
        Eml(
            one,
            Eml(
                Eml(Eml(one, Eml(Eml(one, Eml(one, left)), one)), right),
                one,
            ),
        ),
        one,
    )


def scaled_exponential_expr(variable: str, coefficient: complex) -> Expr:
    """Exact EML shape evidence for exp(coefficient * variable)."""

    return exp_of(multiply_expr(Const(coefficient), Var(variable)))


def divide_expr(left: Expr, right: Expr) -> Expr:
    """Verified EML identity for left / right."""

    one = Const(1.0)
    return Eml(
        Eml(
            Eml(one, Eml(Eml(one, Eml(one, right)), one)),
            Eml(Eml(one, left), one),
        ),
        one,
    )


def reciprocal_expr(expr: Expr) -> Expr:
    return divide_expr(Const(1.0), expr)


@dataclass
class _Compiler:
    config: CompilerConfig
    trace: list[RuleTrace] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    def compile(self, expr: sp.Expr) -> Expr:
        expr = sp.sympify(expr)
        special = self._compile_special(expr)
        if special is not None:
            return special

        if isinstance(expr, sp.Symbol):
            return self._record("variable", expr, Var(self._variable_name(expr)))

        if expr.is_number:
            return self._record("constant", expr, Const(self._constant_value(expr)))

        if expr.func == sp.exp and len(expr.args) == 1:
            self.assumptions.append("exp uses canonical complex exponential")
            return self._record("exp", expr, exp_of(self.compile(expr.args[0])))

        if expr.func == sp.log and len(expr.args) == 1:
            self.assumptions.append("log uses principal branch")
            return self._record("log", expr, log_of(self.compile(expr.args[0])))

        if isinstance(expr, sp.Add):
            terms = list(expr.args)
            if not terms:
                return self._record("empty_add", expr, Const(0.0))
            result = self.compile(terms[0])
            for term in terms[1:]:
                result = add_expr(result, self.compile(term))
            self.assumptions.append("addition compiled as a - (-b) with principal-branch intermediates")
            return self._record("addition", expr, result)

        if isinstance(expr, sp.Mul):
            factors = list(expr.args)
            if not factors:
                return self._record("empty_mul", expr, Const(1.0))
            result = self.compile(factors[0])
            for factor in factors[1:]:
                result = multiply_expr(result, self.compile(factor))
            self.assumptions.append("multiplication uses verified EML arithmetic identity")
            return self._record("multiplication", expr, result)

        if isinstance(expr, sp.Pow):
            return self._compile_power(expr)

        raise UnsupportedExpression(
            CompileReason.UNSUPPORTED_OPERATOR,
            expr,
            f"operator {expr.func} is not in the v1.1 compiler subset",
        )

    def _compile_special(self, expr: sp.Expr) -> Expr | None:
        if not self.config.enable_macros:
            return None
        if isinstance(expr, sp.Pow):
            macro = self._compile_exponential_saturation(expr)
            if macro is not None:
                return macro
            macro = self._compile_reciprocal_shift(expr)
            if macro is not None:
                return macro
            return self._compile_low_degree_power(expr)
        if isinstance(expr, sp.Mul):
            macro = self._compile_exponential_saturation(expr)
            if macro is not None:
                return macro
            macro = self._compile_saturation_ratio(expr)
            if macro is not None:
                return macro
            macro = self._compile_direct_division(expr)
            if macro is not None:
                return macro
        if isinstance(expr, sp.Add):
            return self._compile_scaled_exp_minus_one(expr)
        return None

    def _match_unit_shift(self, expr: sp.Expr) -> _UnitShift | None:
        if not isinstance(expr, sp.Add):
            return None

        base_terms: list[sp.Expr] = []
        numeric_terms: list[sp.Expr] = []
        for term in expr.args:
            if term.is_number:
                numeric_terms.append(term)
                continue

            coeff, rest = term.as_coeff_Mul()
            if not rest.is_number and sp.simplify(coeff - 1) == 0:
                base_terms.append(rest)
                continue

            return None
        if len(base_terms) != 1 or len(numeric_terms) != 1:
            return None

        offset = self._constant_value(numeric_terms[0])
        return _UnitShift(base=base_terms[0], offset=offset)

    def _build_unit_shift(self, match: _UnitShift) -> Expr | None:
        with np.errstate(over="ignore", invalid="ignore", under="ignore"):
            derived = complex(np.exp(-match.offset))
        if not (np.isfinite(derived.real) and np.isfinite(derived.imag)):
            return None
        if self.config.constant_policy == "basis_only" and abs(derived - 1.0) > 1e-12:
            return None
        if self.config.constant_policy not in {"basis_only", "literal_constants"}:
            return None
        try:
            compiled_base = self.compile(match.base)
        except UnsupportedExpression:
            return None
        self.assumptions.append("unit shift g+b compiled as eml(log(g), exp(-b)) behind validation")
        return Eml(log_of(compiled_base), Const(derived))

    def _compile_reciprocal_shift(self, expr: sp.Pow) -> Expr | None:
        base, exponent = expr.args
        if exponent != -1:
            return None

        match = self._match_unit_shift(base)
        if match is None:
            return None

        shifted = self._build_unit_shift(match)
        if shifted is None:
            return None
        self.assumptions.append("reciprocal shift shortcut lowers shifted denominator before exact divide identity")
        return self._record(
            "reciprocal_shift_template",
            expr,
            reciprocal_expr(shifted),
        )

    def _compile_saturation_ratio(self, expr: sp.Mul) -> Expr | None:
        numerator_factors: list[sp.Expr] = []
        denominator_matches: list[_UnitShift] = []

        for factor in expr.args:
            if isinstance(factor, sp.Pow) and factor.exp == -1:
                match = self._match_unit_shift(factor.base)
                if match is None:
                    return None
                denominator_matches.append(match)
            else:
                numerator_factors.append(factor)

        if len(denominator_matches) != 1:
            return None

        coefficient = 1.0 + 0.0j
        numerator_base_factors: list[sp.Expr] = []
        for factor in numerator_factors:
            if factor.is_number:
                coefficient *= self._constant_value(factor)
            else:
                factor_coeff, factor_rest = factor.as_coeff_Mul()
                if factor_coeff.is_number and sp.simplify(factor_coeff - 1) != 0:
                    coefficient *= self._constant_value(factor_coeff)
                else:
                    factor_rest = factor
                if factor_rest.is_number:
                    return None
                numerator_base_factors.append(factor_rest)

        if not numerator_base_factors:
            return None

        numerator_base = sp.Mul(*numerator_base_factors)
        shift = denominator_matches[0]
        if sp.simplify(numerator_base - shift.base) != 0:
            return None

        try:
            compiled_base = self.compile(numerator_base)
        except UnsupportedExpression:
            return None
        numerator = multiply_expr(Const(coefficient), compiled_base)
        denominator = self._build_unit_shift(shift)
        if denominator is None:
            return None
        self.assumptions.append("saturation ratio shortcut lowers c*g/(g+b) as one structural motif")
        return self._record(
            "saturation_ratio_template",
            expr,
            divide_expr(numerator, denominator),
        )

    def _compile_exponential_saturation(self, expr: sp.Expr) -> Expr | None:
        match = self._match_exponential_saturation(expr)
        if match is None:
            return None
        compiled = self._build_exponential_saturation(match)
        if compiled is None:
            return None
        self.assumptions.append("exponential saturation shortcut lowers 1/(1+c*exp(a)) behind validation")
        return self._record("exponential_saturation_template", expr, compiled)

    def _match_exponential_saturation(self, expr: sp.Expr) -> _ExponentialSaturation | None:
        if isinstance(expr, sp.Pow) and expr.exp == -1:
            return self._match_unit_plus_scaled_exp(expr.base)

        if isinstance(expr, sp.Mul):
            numerator_factors: list[sp.Expr] = []
            denominator_bases: list[sp.Expr] = []
            for factor in expr.args:
                if isinstance(factor, sp.Pow) and factor.exp == -1:
                    denominator_bases.append(factor.base)
                else:
                    numerator_factors.append(factor)
            if len(denominator_bases) != 1:
                return None

            numerator = sp.Mul(*numerator_factors)
            numerator_scaled_exp = self._match_scaled_exp_term(numerator)
            if numerator_scaled_exp is None:
                return None
            numerator_scale, numerator_arg = numerator_scaled_exp

            denominator_match = self._match_exp_plus_constant(denominator_bases[0])
            if denominator_match is None:
                return None
            denominator_arg, denominator_scale, constant = denominator_match
            if sp.simplify(numerator_arg - denominator_arg) != 0:
                return None
            scale_delta = abs(numerator_scale - denominator_scale)
            scale_limit = 1e-12 * max(1.0, abs(numerator_scale), abs(denominator_scale))
            if scale_delta > scale_limit:
                return None
            return _ExponentialSaturation(exponent=-denominator_arg, coefficient=constant / denominator_scale)

        return None

    def _match_unit_plus_scaled_exp(self, expr: sp.Expr) -> _ExponentialSaturation | None:
        if not isinstance(expr, sp.Add):
            return None

        unit_terms: list[complex] = []
        exp_terms: list[tuple[complex, sp.Expr]] = []
        for term in expr.args:
            if term.is_number:
                unit_terms.append(self._constant_value(term))
                continue
            scaled_exp = self._match_scaled_exp_term(term)
            if scaled_exp is None:
                return None
            exp_terms.append(scaled_exp)

        if len(unit_terms) != 1 or len(exp_terms) != 1:
            return None
        if abs(unit_terms[0] - 1.0) > 1e-12:
            return None

        coefficient, exponent = exp_terms[0]
        return _ExponentialSaturation(exponent=exponent, coefficient=coefficient)

    def _match_exp_plus_constant(self, expr: sp.Expr) -> tuple[sp.Expr, complex, complex] | None:
        if not isinstance(expr, sp.Add):
            return None

        constant_terms: list[complex] = []
        exp_terms: list[tuple[complex, sp.Expr]] = []
        for term in expr.args:
            if term.is_number:
                constant_terms.append(self._constant_value(term))
                continue
            scaled_exp = self._match_scaled_exp_term(term)
            if scaled_exp is None:
                return None
            exp_terms.append(scaled_exp)

        if len(constant_terms) != 1 or len(exp_terms) != 1:
            return None
        exp_scale, exponent = exp_terms[0]
        return exponent, exp_scale, constant_terms[0]

    def _match_scaled_exp_term(self, expr: sp.Expr) -> tuple[complex, sp.Expr] | None:
        coefficient, rest = expr.as_coeff_Mul()
        if rest.func != sp.exp or len(rest.args) != 1:
            return None
        scale = self._constant_value(coefficient) if coefficient.is_number else 1.0 + 0.0j
        if not (np.isfinite(scale.real) and np.isfinite(scale.imag)):
            return None
        if abs(scale) <= 1e-15:
            return None
        return scale, rest.args[0]

    def _build_exponential_saturation(self, match: _ExponentialSaturation) -> Expr | None:
        if self.config.constant_policy != "literal_constants":
            return None
        if not (np.isfinite(match.coefficient.real) and np.isfinite(match.coefficient.imag)):
            return None
        if abs(match.coefficient) <= 1e-15:
            return None

        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            shifted_constant = complex(np.log(np.e * match.coefficient))
            exp_minus_e = complex(np.exp(-np.e))
        if not (
            np.isfinite(shifted_constant.real)
            and np.isfinite(shifted_constant.imag)
            and np.isfinite(exp_minus_e.real)
            and np.isfinite(exp_minus_e.imag)
        ):
            return None

        try:
            compiled_exponent = self.compile(match.exponent)
        except UnsupportedExpression:
            return None

        shifted_exponent = add_expr(compiled_exponent, Const(shifted_constant))
        scaled_denominator = Eml(shifted_exponent, Const(exp_minus_e))
        negative_log_denominator = Eml(Const(0.0), scaled_denominator)
        return exp_of(negative_log_denominator)

    def _compile_low_degree_power(self, expr: sp.Pow) -> Expr | None:
        base, exponent = expr.args
        if not exponent.is_Integer:
            return None
        power = int(exponent)
        if power <= 1 or power > self.config.max_power:
            return None
        if self.config.constant_policy != "literal_constants":
            return None

        try:
            compiled_base = self.compile(base)
        except UnsupportedExpression:
            return None

        repeated = self._positive_power(compiled_base, power)
        candidate = exp_of(multiply_expr(Const(float(power)), log_of(compiled_base)))
        if (candidate.depth(), candidate.node_count()) >= (repeated.depth(), repeated.node_count()):
            return None

        self.assumptions.append("low-degree power shortcut lowers g**n as exp(n*log(g)) behind validation")
        return self._record("low_degree_power_template", expr, candidate)

    def _compile_direct_division(self, expr: sp.Mul) -> Expr | None:
        numerator_factors: list[sp.Expr] = []
        denominator_factors: list[sp.Expr] = []
        for factor in expr.args:
            if isinstance(factor, sp.Pow) and factor.exp == -1:
                denominator_factors.append(factor.base)
            else:
                numerator_factors.append(factor)
        if not denominator_factors:
            return None
        numerator = sp.Mul(*numerator_factors)
        if sp.simplify(numerator - 1) == 0:
            return None
        denominator = sp.Mul(*denominator_factors)
        try:
            compiled_numerator = self.compile(numerator)
            compiled_denominator = self.compile(denominator)
        except UnsupportedExpression:
            return None
        self.assumptions.append("direct division shortcut lowers numerator/denominator once before exact divide identity")
        return self._record(
            "direct_division_template",
            expr,
            divide_expr(compiled_numerator, compiled_denominator),
        )

    def _compile_scaled_exp_minus_one(self, expr: sp.Add) -> Expr | None:
        terms = list(expr.args)
        numeric_terms = [term for term in terms if term.is_number]
        non_numeric_terms = [term for term in terms if not term.is_number]
        if len(numeric_terms) != 1 or len(non_numeric_terms) != 1:
            return None

        coeff, rest = non_numeric_terms[0].as_coeff_Mul()
        if not coeff.is_number or rest.func != sp.exp or len(rest.args) != 1:
            return None

        scale = self._constant_value(coeff)
        offset = self._constant_value(numeric_terms[0])
        if abs(offset + scale) > 1e-12:
            return None

        compiled_arg = self.compile(rest.args[0])
        self.assumptions.append("scale*(exp(a)-1) compiled with lower-depth EML template")
        return self._record(
            "scaled_exp_minus_one_template",
            expr,
            multiply_expr(Const(scale), Eml(compiled_arg, Const(np.e))),
        )

    def _compile_power(self, expr: sp.Pow) -> Expr:
        base, exponent = expr.args
        if not exponent.is_Integer:
            raise UnsupportedExpression(CompileReason.UNSUPPORTED_POWER, expr, "only literal integer powers are supported")
        power = int(exponent)
        if abs(power) > self.config.max_power:
            raise UnsupportedExpression(
                CompileReason.UNSUPPORTED_POWER,
                expr,
                f"power {power} exceeds max_power={self.config.max_power}",
            )
        if power == 0:
            return self._record("power_zero", expr, Const(1.0))
        compiled_base = self.compile(base)
        if power < 0:
            self.assumptions.append("negative integer power compiled through reciprocal; denominator must be nonzero")
            return self._record("negative_power", expr, reciprocal_expr(self._positive_power(compiled_base, -power)))
        return self._record("positive_power", expr, self._positive_power(compiled_base, power))

    def _positive_power(self, base: Expr, power: int) -> Expr:
        result = base
        for _ in range(power - 1):
            result = multiply_expr(result, base)
        return result

    def _variable_name(self, expr: sp.Symbol) -> str:
        name = str(expr)
        if self.config.variables is not None and name not in self.config.variables:
            raise UnsupportedExpression(CompileReason.UNKNOWN_VARIABLE, expr, f"allowed variables: {self.config.variables}")
        return name

    def _constant_value(self, expr: sp.Expr) -> complex:
        if self.config.constant_policy == "basis_only" and sp.simplify(expr - 1) != 0:
            raise UnsupportedExpression(CompileReason.CONSTANT_POLICY, expr, "basis_only policy only allows literal 1")
        if self.config.constant_policy not in {"basis_only", "literal_constants"}:
            raise UnsupportedExpression(
                CompileReason.CONSTANT_POLICY,
                expr,
                f"unknown constant policy {self.config.constant_policy!r}",
            )
        value = complex(sp.N(expr, 17))
        if not (np.isfinite(value.real) and np.isfinite(value.imag)):
            raise UnsupportedExpression(CompileReason.UNSAFE_CONSTANT, expr, "constant is not finite")
        return value

    def _record(self, rule: str, source: sp.Expr, output: Expr) -> Expr:
        self.trace.append(RuleTrace(rule, str(source), output.depth(), output.node_count(), tuple(self.assumptions[-2:])))
        return output


def compile_sympy_expression(expression: sp.Expr | str, config: CompilerConfig | None = None) -> CompileResult:
    config = config or CompilerConfig()
    source = sp.sympify(expression)
    symbols = tuple(sorted(str(symbol) for symbol in source.free_symbols))
    variables = config.variables or symbols
    compiler = _Compiler(CompilerConfig(**{**config.__dict__, "variables": tuple(variables)}))
    compiled = compiler.compile(source)
    constants = tuple(sorted(compiled.constants(), key=lambda value: (value.real, value.imag)))
    macro_hits = tuple(dict.fromkeys(entry.rule for entry in compiler.trace if entry.rule in MACRO_RULES))
    macro_diagnostics = _macro_diagnostics(source, config, compiled, macro_hits) if config.enable_macros else None

    if compiled.depth() > config.max_depth:
        raise UnsupportedExpression(
            CompileReason.DEPTH_EXCEEDED,
            source,
            f"compiled depth {compiled.depth()} exceeds max_depth={config.max_depth}",
        )
    if compiled.node_count() > config.max_nodes:
        raise UnsupportedExpression(
            CompileReason.NODE_BUDGET_EXCEEDED,
            source,
            f"compiled node count {compiled.node_count()} exceeds max_nodes={config.max_nodes}",
        )

    metadata = CompileMetadata(
        source_expression=str(source),
        normalized_expression=str(sp.factor(source)),
        variables=tuple(variables),
        constants=constants,
        constant_policy=config.constant_policy,
        depth=compiled.depth(),
        node_count=compiled.node_count(),
        assumptions=tuple(dict.fromkeys(compiler.assumptions)),
        trace=tuple(compiler.trace),
        macro_diagnostics=macro_diagnostics,
    )
    return CompileResult(compiled, metadata)


def _macro_diagnostics(
    source: sp.Expr,
    config: CompilerConfig,
    compiled: Expr,
    macro_hits: tuple[str, ...],
) -> dict[str, Any]:
    baseline_depth: int | None = None
    baseline_nodes: int | None = None
    if macro_hits:
        baseline_config = CompilerConfig(
            variables=config.variables,
            constant_policy=config.constant_policy,
            max_depth=max(config.max_depth * 4, compiled.depth() + 32),
            max_nodes=max(config.max_nodes * 4, compiled.node_count() + 512),
            max_power=config.max_power,
            validation_tolerance=config.validation_tolerance,
            enable_macros=False,
        )
        baseline = compile_sympy_expression(source, baseline_config)
        baseline_depth = baseline.metadata.depth
        baseline_nodes = baseline.metadata.node_count
    return {
        "hits": list(macro_hits),
        "misses": [rule for rule in MACRO_RULES if rule not in macro_hits],
        "baseline_depth": baseline_depth,
        "baseline_node_count": baseline_nodes,
        "depth_delta": baseline_depth - compiled.depth() if baseline_depth is not None else 0,
        "node_delta": baseline_nodes - compiled.node_count() if baseline_nodes is not None else 0,
        "validation_status": "not_run",
        "validation_passed": None,
    }


def default_validation_inputs(variables: Sequence[str], points: int = 8) -> dict[str, np.ndarray]:
    base = np.linspace(0.25, 2.5, points, dtype=np.float64).astype(np.complex128)
    return {name: base + 0.05 * index for index, name in enumerate(variables)}


def validate_compiled_expression(
    result: CompileResult,
    inputs: Mapping[str, Any] | None = None,
    *,
    tolerance: float | None = None,
) -> CompileValidation:
    variables = result.metadata.variables
    inputs = inputs or default_validation_inputs(variables)
    tolerance = result.metadata.as_dict().get("validation_tolerance", None) or tolerance or 1e-8
    symbols = [sp.Symbol(name) for name in variables]
    ordinary = sp.lambdify(symbols, sp.sympify(result.metadata.source_expression), modules="numpy")
    values = [np.asarray(inputs[name], dtype=np.complex128) for name in variables]

    with np.errstate(all="ignore"):
        expected = np.asarray(ordinary(*values), dtype=np.complex128)
        actual = result.expression.evaluate_numpy(inputs)
        residual = actual - expected

    finite = np.all(np.isfinite(expected)) and np.all(np.isfinite(actual))
    max_abs = float(np.max(np.abs(residual))) if finite and residual.size else float("inf")
    mse = float(np.mean(np.abs(residual) ** 2)) if finite and residual.size else float("inf")
    passed = bool(finite and max_abs <= tolerance)
    reason = "validated" if passed else CompileReason.VALIDATION_FAILED
    return CompileValidation(passed, max_abs, mse, float(tolerance), reason)


def compile_and_validate(
    expression: sp.Expr | str,
    config: CompilerConfig | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> CompileResult:
    result = compile_sympy_expression(expression, config)
    validation = validate_compiled_expression(result, inputs, tolerance=(config or CompilerConfig()).validation_tolerance)
    if not validation.passed:
        raise UnsupportedExpression(
            CompileReason.VALIDATION_FAILED,
            expression,
            f"max_abs_error={validation.max_abs_error:.3e}",
        )
    metadata = _metadata_with_validation(result.metadata, validation)
    return CompileResult(result.expression, metadata, validation)


def _metadata_with_validation(metadata: CompileMetadata, validation: CompileValidation) -> CompileMetadata:
    if metadata.macro_diagnostics is None:
        return metadata
    return replace(
        metadata,
        macro_diagnostics={
            **dict(metadata.macro_diagnostics),
            "validation_status": validation.reason,
            "validation_passed": validation.passed,
        },
    )


def diagnose_compile_expression(
    expression: sp.Expr | str,
    config: CompilerConfig | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return strict failure details plus relaxed compile metadata when available."""

    config = config or CompilerConfig()
    try:
        strict = compile_and_validate(expression, config, inputs)
        return {
            "schema": "eml.compiler_diagnostic.v1",
            "status": "compiled",
            "strict": {
                "metadata": strict.metadata.as_dict(),
                "validation": strict.validation.as_dict() if strict.validation else None,
            },
        }
    except UnsupportedExpression as strict_error:
        diagnostic: dict[str, Any] = {
            "schema": "eml.compiler_diagnostic.v1",
            "status": "unsupported",
            "strict": strict_error.as_dict(),
        }

    relaxed_config = CompilerConfig(
        variables=config.variables,
        constant_policy=config.constant_policy,
        max_depth=max(config.max_depth * 4, config.max_depth + 12),
        max_nodes=max(config.max_nodes * 4, config.max_nodes + 512),
        max_power=config.max_power,
        validation_tolerance=config.validation_tolerance,
    )
    try:
        relaxed = compile_sympy_expression(expression, relaxed_config)
        validation = validate_compiled_expression(relaxed, inputs, tolerance=config.validation_tolerance)
        relaxed_metadata = _metadata_with_validation(relaxed.metadata, validation)
        diagnostic["relaxed"] = {
            "metadata": relaxed_metadata.as_dict(),
            "validation": validation.as_dict(),
        }
    except UnsupportedExpression as relaxed_error:
        diagnostic["relaxed_error"] = relaxed_error.as_dict()
    return diagnostic
