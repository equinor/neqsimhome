# Notebook release verification

Status: **PASSED**

- Chapter notebooks executed: 35 / 35
- Code cells executed: 300
- Fresh generated scientific figures: 104
- Figure discussion blocks: 104
- Source revision: `6cc8026202a5d3f9383c9abd1d97d448993813f9`

Executed code, source provenance, artifact integrity, finite-result audit and notebook engineering assertions. This does not constitute blanket validation against independent experimental or field data.

## Declared operating-domain gaps

Some hydraulic trial rates cannot satisfy a positive pressure solution, and a gas/oil phase ratio is undefined in a one-phase state. Those states are kept as explicit gaps rather than interpolated or replaced with invented values.

## Integrity checks

The gate checks every code-cell hash, notebook hash, generated PNG hash, the active Python executable, NeqSim's source-class origin, retained error outputs, and arrays containing no finite result.
