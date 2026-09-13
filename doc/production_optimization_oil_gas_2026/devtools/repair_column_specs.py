from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch12*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('deethanizer.setCondenserTemperature(273.15 + (-25.0))\ndeethanizer.getReboiler().setHeatInput(200000.0)  # W', 'deethanizer.getCondenser().setRefluxRatio(1.0)\ndeethanizer.getReboiler().setRefluxRatio(1.0)\n# Terminal ratios are specified; temperatures and duties are calculated.')
t=t.replace('print(deethanizer.getConvergenceDiagnostics())\nprint("=== Deethanizer Results ===")', 'print(deethanizer.getConvergenceDiagnostics())\nassert deethanizer.solved(), "Reject the column results: convergence gates failed"\nprint("=== Deethanizer Results ===")')
p.write_text(t,encoding='utf-8')
p=next((BOOK/'chapters').glob('ch06*/chapter.md'))
t=p.read_text(encoding='utf-8').replace('flowline.setInsulationThickness(0.05);  // 50 mm insulation','// Overall U represents the selected insulation; geometric sizing is a separate calculation.')
t=t.replace('target_total_mass_rate = 150.0','target_total_mass_rate = 40.0')
p.write_text(t,encoding='utf-8')
p=BOOK/'devtools/verify_foundations_java.py'
t=p.read_text(encoding='utf-8').replace("commands = ['/set feedback normal', 'import java.util.*;']", "commands = ['/set feedback normal', 'import java.util.*;', 'org.apache.logging.log4j.core.config.Configurator.setRootLevel(org.apache.logging.log4j.Level.INFO);']")
p.write_text(t,encoding='utf-8')
