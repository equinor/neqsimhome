"""One-time correction of the debottlenecking chapter's Java examples."""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parents[1]
path = BOOK / 'chapters/ch21_debottlenecking/chapter.md'
original = path.read_text(encoding='utf-8-sig')
backup = BOOK / '.build/before_september_revision/ch21_before_java_repair.md'
if not backup.exists():
    backup.write_text(original, encoding='utf-8')
blocks = list(re.finditer(r'^```java\n(.*?)^```', original, re.M | re.S))
assert len(blocks) == 34, len(blocks)
changes = {}
for number, match in enumerate(blocks, 1):
    code = match[1]
    if number in (1, 4, 5, 10):
        if number == 1:
            code = code.replace('void enableConstraints();\n    void useEquinorConstraints();\n    void useAPIConstraints();', 'int enableAllConstraints();')
        if number == 5:
            code = '// Selected public method signatures (bodies omitted).\n' + '\n'.join(
                line.replace(' { ... }', ';') for line in code.splitlines() if line.startswith('public ')) + '\n'
        if number == 10:
            code = code.replace('boolean isOverloaded();', 'boolean isExceeded();').replace('String getSummary();', 'String toString();')
        changes[number] = '```text\n' + code + '```'
        continue
    if number == 3:
        code = 'double shadowPriceNokPerRpm = 250.0; // assumed marginal value for this example\n' + code
    if number == 6:
        code = code.replace('new MyCustomStrategy()', 'new SeparatorCapacityStrategy() {\n    @Override\n    public int getPriority() { return 10; }\n}')
    if number == 8:
        code = code.replace('ProcessSystem process = new ProcessSystem();\n// ... add equipment ...\n', '// Use the populated process from the shared fixture.\n')
    if number == 13:
        code = 'List<String> above80 = new ArrayList<String>();\nfor (Map.Entry<String, Double> item : process.getCapacityUtilizationSummary().entrySet()) {\n    if (item.getValue() > 0.80) { above80.add(item.getKey()); }\n}\nlogger.info("Equipment above 80 percent: {}", above80);\n'
    if number == 16:
        code = code.replace('bottleneck.getSummary()', 'bottleneck.toString()').replace('Equipment above 85%', 'Equipment above its configured warning threshold')
    if number == 17:
        code = code.replace('setFeedRate(process, rate);     // user-defined helper', 'feed.setFlowRate(10000.0 * rate, "kg/hr");')
    if number == 26:
        code = code.replace('// Run to find unconstrained production', '// Re-run the same fixed feed with capacity reporting disabled').replace('double unconstrainedProduction', 'double imposedFeedRate')
    if number == 29:
        code = '''// Thresholds are explicit filters of the current utilization summary.
List<String> tier1 = new ArrayList<String>();
List<String> tier2 = new ArrayList<String>();
List<String> tier3 = new ArrayList<String>();
for (Map.Entry<String, Double> item : process.getCapacityUtilizationSummary().entrySet()) {
    if (item.getValue() > 0.95) { tier1.add(item.getKey()); }
    if (item.getValue() > 0.85) { tier2.add(item.getKey()); }
    if (item.getValue() > 0.75) { tier3.add(item.getKey()); }
}
logger.info("Critical above 95 percent: {}", tier1);
logger.info("Warning above 85 percent: {}", tier2);
logger.info("Watch above 75 percent: {}", tier3);
'''
    if number in (30, 31):
        code = code.split('// Sets:')[0] + '// Inspect the resulting constraints; this preset is not a compliance certificate.\n'
    if number == 32:
        code = code.replace('.setWarningThreshold(0.88);', '.setWarningThreshold(0.88)\n    .setValueSupplier(() -> separator.getGasLoadFactor());')
    if number == 34:
        code = '''// A synthetic mass-flow case; field barrels require a separate density basis.
ProcessSystem topside = new ProcessSystem();
Stream wellStream = new Stream("Well Stream", reservoirFluid.clone());
wellStream.setFlowRate(100000.0, "kg/hr");
Separator hpSep = new Separator("HP Separator", wellStream);
Compressor hpComp = new Compressor("HP Compressor", hpSep.getGasOutStream());
hpComp.setOutletPressure(150.0, "bara");
hpComp.setIsentropicEfficiency(0.75);
topside.add(wellStream);
topside.add(hpSep);
topside.add(hpComp);
topside.run();
hpSep.autoSize(0.20);
hpComp.autoSize(0.15);
logger.info("Screening bottleneck: {}", topside.findBottleneck());
'''
    changes[number] = '```java\n' + code + '```'
text = original
for number, match in reversed(list(enumerate(blocks, 1))):
    text = text[:match.start()] + changes[number] + text[match.end():]

fixture = '''import java.util.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import neqsim.thermo.system.*;
import neqsim.process.processmodel.*;
import neqsim.process.equipment.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.equipment.capacity.CapacityConstraint.ConstraintType;
import neqsim.process.optimization.valuechain.*;

public class CapacityExample {
    private static final Logger logger = LogManager.getLogger(CapacityExample.class);
    private static SystemInterface fluid, reservoirFluid;
    private static Stream feed;
    private static StreamInterface gasStream, oilStream, wellStream;
    private static Separator separator, hpSep;
    private static Compressor compressor, comp;
    private static ProcessSystem process;
    private static ProcessEquipmentBaseClass equipment;
    private static BottleneckResult bottleneck;
    private static CapacityConstraint speedConstraint;

    private static void setup() {
        fluid = new SystemSrkEos(303.15, 70.0);
        fluid.addComponent("methane", 0.70);
        fluid.addComponent("ethane", 0.10);
        fluid.addComponent("n-decane", 0.20);
        fluid.setMixingRule("classic");
        reservoirFluid = fluid.clone();
        feed = new Stream("Feed", fluid);
        feed.setFlowRate(10000.0, "kg/hr");
        separator = new Separator("Fixture Separator", feed);
        compressor = new Compressor("Fixture Compressor", separator.getGasOutStream());
        compressor.setOutletPressure(150.0, "bara");
        compressor.setIsentropicEfficiency(0.75);
        process = new ProcessSystem();
        process.add(feed);
        process.add(separator);
        process.add(compressor);
        process.run();
        separator.autoSize(0.20);
        compressor.autoSize(0.15);
        separator.enableConstraints();
        compressor.enableConstraints();
        gasStream = separator.getGasOutStream();
        oilStream = separator.getLiquidOutStream();
        wellStream = feed;
        hpSep = separator;
        comp = compressor;
        equipment = separator;
        bottleneck = process.findBottleneck();
        speedConstraint = new CapacityConstraint("speed", "RPM", ConstraintType.HARD);
    }

    public static void main(String[] args) {
        setup();
        runExample();
    }

    private static void runExample() {
        // Insert one Java operation fragment from this chapter here.
        logger.info("Fixture bottleneck: {}", process.findBottleneck());
    }
}
'''
intro = '''### Java Example Setup

The Java operation fragments in this chapter use the following shared fixture. Copy the imports and class once, then replace the body of `runExample()` with one fragment and run the class. Each example starts with a fresh synthetic separator–compressor process. Auto-sizing establishes an assumed screening capacity; replace those capacities with installed ratings for a plant study. API signature summaries are printed as plain text and are not standalone programs.

```java
''' + fixture + '```\n\n'
text = text.replace('### 21.2.1 Architecture Overview', intro + '### 21.2.1 Architecture Overview', 1)
text = text.replace('A study of 47 North Sea platforms found that debottlenecking projects delivered an average production increase of 12–18% at 20–40% of the cost of a new platform (Statoil Engineering Reports, 2014). ', 'The gain and investment depend on the field, the binding constraint and the modification scope; establish them from the actual study rather than applying a generic percentage. ')
text = text.replace('Utilization is capped at 9.99', 'For minimum constraints, the ratio is the declared minimum divided by the current value; the direction of violation is therefore reversed. Missing or non-finite measurements require a separate evidence check. Utilization is capped at 9.99')
text = text.replace('register a custom strategy:', 'register a higher-priority specialization of an existing strategy:')
text = text.replace('**`isHardLimitExceeded()`** returns `true` if any HARD-type constraint exceeds its maximum value. This indicates a safety or trip condition.', '**`isHardLimitExceeded()`** returns `true` when a declared HARD constraint violates its maximum or minimum. This reports the modeled limit; it does not replace a protective system or an independent safety assessment.')
text = text.replace('## 21.6', '## 21.6', 1)
path.write_text(text, encoding='utf-8')
(BOOK / 'verification/ch21_fixture_source.txt').write_text(fixture, encoding='utf-8')
print('Updated Chapter21: 30 operation fragments, one shared fixture, four API summaries.')
