from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch33*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
text=text.replace('deethanizer.addFeedStream(ngl_feed, 15)', 'deethanizer.addFeedStream(ngl_feed, 15)\ndeethanizer.setTopPressure(25.0)\ndeethanizer.setBottomPressure(25.5)')
text=text.replace('    deethanizer.addFeedStream(ngl_stream, 12)', '    deethanizer.addFeedStream(ngl_stream, 12)\n    deethanizer.setTopPressure(20.0)\n    deethanizer.setBottomPressure(20.5)')
text=text.replace('print("--- Deethanizer Results ---")', 'print("--- Deethanizer Results ---")\nprint("Column converged:", deethanizer.solved())')
text=text.replace('Ethane product rate:', 'Overhead product rate:').replace('Ethane product:     ', 'Overhead product:   ')
text=text.replace('print("\\n--- Area 4: Fractionation ---")', 'print("\\n--- Area 4: Fractionation ---")\nprint("Column converged:", deethanizer.solved())')
text+='''

### Qualification of the assembled plant example

The assembled plant is an instructional flowsheet. Its precooler imposes an outlet temperature and represents an external cooling duty; a heat-recovery design needs a second exchanger stream and a checked approach temperature. The recompressor has a specified discharge pressure and is not mechanically coupled to the expander. Check both shaft duties before claiming self-powered recompression.

For fractionation, report `deethanizer.solved()` with the product flows and verify composition and energy balances. An overhead stream is not automatically a saleable ethane product. Product purity, column hydraulics and refrigeration demand require additional specifications and acceptance checks. A state-serialization diagnostic from unsupported column internals does not constitute a saved or restorable full-plant state.
'''
p.write_text(text,encoding='utf-8')
p=next((B/'chapters').glob('ch29*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
text+='''

### Interpreting controller demonstrations

The controller and transient API examples demonstrate construction and execution. An exception-free call to `runTransient()` does not establish an inventory-validated dynamic plant model. Select the dynamic equipment mode, initialize the gas and liquid inventories, specify actuator behavior and verify integrated mass and energy balances before interpreting a disturbance trajectory as a physical prediction. The companion notebook's illustrative integrating-level controller model is separately identified and is not a NeqSim transient validation benchmark.
'''
p.write_text(text,encoding='utf-8')
