"""Runnable examples for MathBlocks Phase 2 components."""
from mathblocks import Math, Result, Text

# Editable LaTeX input (MathLive in an AnyWidget-compatible notebook).
equation = Math(r"\sigma = \frac{P}{A}", label="Normal stress")

# Static mathematical output (KaTeX).
identity = Math(r"\int_0^1 x^2\,dx = \frac{1}{3}", read_only=True)

# Plain explanatory annotation.
note = Text(
    "Check the sign convention before applying the load combination.",
    tone="note",
    label="Engineering note",
)

# Computed value, unit, and optional diagnostics.
result = Result(24.6, unit="MPa", diagnostics=["Below the specified design limit"], label="Stress")

# In Jupyter, the final expression in a cell is displayed automatically.
equation
identity
note
result
