from pathlib import Path
import re

BOOK = Path(__file__).resolve().parents[1]
def edit(n, fn):
    path = next((BOOK/'chapters').glob(f'ch{n:02}*/chapter.md'))
    path.write_text(fn(path.read_text(encoding='utf-8')), encoding='utf-8')

def intro(t):
    t = t.replace('The hydrocarbon dew point (cricondentherm) must typically be below $0°\\text{C}$.', 'The hydrocarbon dew point must meet the contract limit at the specified pressure or across its pressure range. The cricondentherm is the maximum temperature of the hydrocarbon two-phase envelope; it is not the dew point at an arbitrary delivery pressure.')
    t = re.sub(r'Fiscal metering must meet stringent accuracy requirements.*?\n', 'The permissible uncertainty, reference conditions, sampling, and calculation methods depend on the applicable custody-transfer agreement and jurisdiction. ISO 5167, AGA Report No. 9, and NORSOK I-104 address different measurement technologies and system requirements; the applicable editions and project uncertainty budget must be identified before design.\n', t)
    t = t.replace('**Quality specifications** for export gas typically include:', '**Quality specifications** are defined by the receiving network and sales agreement. The following values are illustrative teaching constraints, not universal export limits. The contract must also define pressure, standard volume reference conditions, averaging period, and measurement method.')
    t = t.replace('| Parameter | Typical Specification |', '| Parameter | Illustrative constraint |')
    t = t.replace('$< 0°\\text{C}$ (cricondentherm)', '$< 0°\\text{C}$ at the contract pressure')
    t = re.sub(r'Meeting these specifications is an \*equality constraint\*.*?\n', 'These limits enter optimization as inequalities, with a suitable operating margin for uncertainty and disturbances. Some become active at the optimum; others remain slack. NeqSim can calculate composition-based heating value and Wobbe index, phase-equilibrium dew points, and tracked component concentrations. Agreement with a fiscal or quality measurement also depends on representative sampling, the EOS and reference basis, water and aerosol entrainment, and the validity of the process removal model. Thermodynamic composition alone does not establish total-sulfur measurement or separator carry-over performance. Chapter 19 develops export specification tracking.\n', t)
    return t
edit(1,intro)

def balance(t):
    old=r'N_p[B_o + (R_p - R_s)B_g] = N\left[(B_o - B_{oi}) + (R_{si} - R_s)B_g + \frac{B_{oi}(c_w S_{wi} + c_f)}{1-S_{wi}}\Delta P\right] + \frac{m N B_{oi}}{B_{gi}}(B_g - B_{gi}) + W_e - W_p B_w'
    new=r'''\begin{aligned}
N_p[B_o + (R_p-R_s)B_g]
 &= N[(B_o-B_{oi})+(R_{si}-R_s)B_g] \\
 &\quad + N\frac{B_{oi}(c_w S_{wi}+c_f)}{1-S_{wi}}\Delta P \\
 &\quad + \frac{m N B_{oi}}{B_{gi}}(B_g-B_{gi}) \\
 &\quad + W_e-W_p B_w .
\end{aligned}'''
    return t.replace(old,new)
edit(4,balance)

def assurance(t):
    # Enable the solid hydrate phase before invoking the formation calculation.
    t=t.replace('fluid.setMultiPhaseCheck(True)\n', 'fluid.setMultiPhaseCheck(True)\nfluid.setHydrateCheck(True)\n')
    t=t.replace('feed.setFlowRate(100000.0, "kg/hr")', 'feed.setFlowRate(50000.0, "kg/hr")')
    t=t.replace('    process.run()\n\n    # Velocity', '    try:\n        process.run()\n    except Exception as exc:\n        print(f"{flow:>14,}  INFEASIBLE: no positive outlet-pressure solution")\n        continue\n\n    # Velocity')
    t=t.replace('    proc.run()\n\n    P_arr = pipeline.', '    try:\n        proc.run()\n    except Exception as exc:\n        print(f"{name:>12}  INFEASIBLE: no positive outlet-pressure solution")\n        continue\n\n    P_arr = pipeline.')
    t=t.replace('    proc.run()\n\n    P_arr = pipeline_12.', '    try:\n        proc.run()\n    except Exception as exc:\n        print(f"{flow_kg:>14,}  INFEASIBLE: no positive outlet-pressure solution")\n        continue\n\n    P_arr = pipeline_12.')
    # API RP 14E C uses imperial units: SI conversion is required.
    t=t.replace('150.0 / math.sqrt(rho_gas)', '(150.0 * 0.3048 * math.sqrt(16.018463)) / math.sqrt(rho_gas)')
    t=t.replace('150.0 / math.sqrt(rho)', '(150.0 * 0.3048 * math.sqrt(16.018463)) / math.sqrt(rho)')
    t=t.replace("{'Flow (MSm3/d)':>14}","{'Flow (kg/hr)':>14}")
    return t
edit(9,assurance)

def columns(t):
    t=t.replace('SimpleTEGAbsorber("Amine Absorber")', 'SimpleAmineAbsorber("Amine Absorber")')
    t=t.replace('absorber.addFeedStream(wet_feed, 5)', 'absorber.addFeedStream(wet_feed, 0)')
    t=t.replace('absorber.addFeedStream(lean_teg, 1)', 'absorber.addFeedStream(lean_teg, 4)')
    t=t.replace('absorber.addFeedStream(lean_teg, 4)    # TEG enters at top', 'absorber.addFeedStream(lean_teg, 4)    # TEG enters at top\nabsorber.setMaxNumberOfIterations(60, True)')
    t=t.replace('"Deethanizer", 25, True, True', '"Deethanizer", 8, True, True')
    t=t.replace('deethanizer.addFeedStream(ngl_feed, 12)', 'deethanizer.addFeedStream(ngl_feed, 4)\ndeethanizer.setMaxNumberOfIterations(80, True)')
    t=t.replace('# Deethanizer column', '# Reduced eight-tray teaching column; not a 25-stage plant design')
    t=t.replace('print("=== Deethanizer Results ===")','print(deethanizer.getConvergenceDiagnostics())\nprint("=== Deethanizer Results ===")')
    t=t.replace('print("=== TEG Dehydration Results ===")','print(absorber.getConvergenceDiagnostics())\nprint("=== TEG Dehydration Results ===")')
    return t
edit(12,columns)

def chart(t):
    start=t.index('# Add speed curves\n')
    end=t.index('# Set surge curve',start)
    t=t[:start]+'''# setCurves also fits the reduced head and efficiency functions.
# addCurve alone leaves the default polynomial chart uninitialized.
feed.run()
conditions = [feed.getFluid().getMolarMass() * 1000.0,
              feed.getTemperature("K"), feed.getPressure("bara"),
              feed.getFluid().getPhase("gas").getZ()]
chart.setCurves(conditions, [11500.0, 10350.0, 9200.0],
                [speed100_flow, speed90_flow, speed80_flow],
                [speed100_head, speed90_head, speed80_head],
                [[v * 100.0 for v in row] for row in
                 [speed100_eff, speed90_eff, speed80_eff]])

'''+t[end:]
    # Keep the actual inlet flow inside the supplied teaching-map domain.
    t=t.replace('feed.setFlowRate(30000.0, "kg/hr")', 'feed.setFlowRate(16000.0, "kg/hr")',1)
    return t
edit(15,chart)

p=BOOK/'devtools/verify_foundations_python.py'
t=p.read_text(encoding='utf-8')
t=t.replace('            # Compatibility for the initial audit only; final source uses JPackage.\n            audited = code.replace(\'from neqsim import jneqsim\', \'import jpype\\njneqsim = jpype.JPackage("neqsim")\')\n','')
t=t.replace('compile(audited,','compile(code,')
p.write_text(t,encoding='utf-8')
