import java.util.*;
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
    private static Separator equipment;
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
        separator.autoSize(1.20);
        compressor.autoSize(1.15);
        separator.enableAllConstraints();
        compressor.enableAllConstraints();
        process.run();  // Solve the chart model activated by autoSize
        gasStream = separator.getGasOutStream();
        oilStream = separator.getLiquidOutStream();
        wellStream = feed;
        hpSep = separator;
        comp = compressor;
        equipment = separator;
        bottleneck = process.findBottleneck();
        speedConstraint = new CapacityConstraint("speed", "RPM", ConstraintType.HARD);
    }

    private static void example01() throws Exception {
CapacityConstraint speedConstraint = new CapacityConstraint(
        "speed", "RPM", ConstraintType.HARD)
    .setDesignValue(10000.0)
    .setMaxValue(11000.0)
    .setWarningThreshold(0.9)
    .setValueSupplier(() -> compressor.getSpeed());

    }

    private static void example02() throws Exception {
double shadowPriceNokPerRpm = 250.0; // assumed marginal value for this example
speedConstraint.setShadowPrice(shadowPriceNokPerRpm);  // fluent, returns the constraint
double price = speedConstraint.getShadowPrice();         // 0.0 by default

    }

    private static void example03() throws Exception {
EquipmentCapacityStrategyRegistry registry =
    EquipmentCapacityStrategyRegistry.getInstance();
registry.register(new SeparatorCapacityStrategy() {
    @Override
    public int getPriority() { return 10; }
});

    }

    private static void example04() throws Exception {
// Option 1: Enable with Equinor-standard constraint sets
equipment.useEquinorConstraints();

// Option 2: Enable with API-standard constraint sets
equipment.useAPIConstraints();

// Option 3: Enable all constraints
equipment.enableAllConstraints();

// Option 4: Enable capacity analysis (equipment-level)
equipment.setCapacityAnalysisEnabled(true);

    }

    private static void example05() throws Exception {
// Use the populated process from the shared fixture.
process.run();

// Find the bottleneck
BottleneckResult result = process.findBottleneck();

if (result.hasBottleneck()) {
    logger.info("Bottleneck: " + result.getEquipmentName());
    logger.info("Constraint: " + result.getConstraintName());
    logger.info("Utilization: " +
        String.format("%.1f%%", result.getUtilization() * 100));
    logger.info("Type: " + result.getConstraint().getType());
} else {
    logger.info("No bottleneck found (no constraints defined)");
}

    }

    private static void example06() throws Exception {
ProcessEquipmentInterface bottleneck = process.getBottleneck();
double utilization = process.getBottleneckUtilization();

    }

    private static void example07() throws Exception {
Map<String, Double> utilization = process.getCapacityUtilizationSummary();

// Print sorted by utilization (highest first)
utilization.entrySet().stream()
    .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
    .forEach(entry -> logger.info(String.format("%-30s %6.1f%%\n",
        entry.getKey(), entry.getValue())));

    }

    private static void example08() throws Exception {
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
if (!nearLimit.isEmpty()) {
    logger.info("WARNING: Equipment near capacity:");
    for (String name : nearLimit) {
        logger.info("  - " + name);
    }
}

    }

    private static void example09() throws Exception {
List<String> above80 = new ArrayList<String>();
for (Map.Entry<String, Double> item : process.getCapacityUtilizationSummary().entrySet()) {
    if (item.getValue() > 80.0) { above80.add(item.getKey()); }
}
logger.info("Equipment above 80 percent: {}", above80);

    }

    private static void example10() throws Exception {
// Any equipment above 100% of design capacity?
boolean overloaded = process.isAnyEquipmentOverloaded();

// Any declared HARD maximum/minimum exceeded?
boolean hardViolation = process.isAnyHardLimitExceeded();

if (hardViolation) {
    logger.info("CRITICAL: Hard limit exceeded - check equipment!");
}

    }

    private static void example11() throws Exception {
List<CapacityConstrainedEquipment> constrained =
    process.getConstrainedEquipment();
logger.info("Number of constrained equipment: " + constrained.size());

    }

    private static void example12() throws Exception {
// Step 1: Run the process simulation
process.run();

// Step 2: Check for hard limit violations (safety first)
if (process.isAnyHardLimitExceeded()) {
    logger.info("ALERT: Hard constraints violated!");
    // Investigate immediately
}

// Step 3: Identify the bottleneck
BottleneckResult bottleneck = process.findBottleneck();
logger.info("Bottleneck: " + bottleneck.toString());

// Step 4: Review overall utilization
Map<String, Double> util = process.getCapacityUtilizationSummary();

// Step 5: Check early warning list
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
logger.info("Equipment above its configured warning threshold: " + nearLimit);

    }

    private static void example13() throws Exception {
BottleneckTracker tracker = new BottleneckTracker();

for (int step = 0; step <= 16; step++) {
    double rate = 0.5 + 0.05 * step;
    feed.setFlowRate(10000.0 * rate, "kg/hr");
    process.run();
    tracker.record(rate, "rate=" + rate, process.findBottleneck());
}

logger.info(tracker.getTimelineSummary());
logger.info("Distinct bottlenecks: "
    + tracker.getDistinctBottleneckEquipment());
logger.info("Migration events: " + tracker.getMigrationCount());
logger.info("Peak utilization: "
    + tracker.getPeakUtilizationPercent() + "%");

    }

    private static void example14() throws Exception {
Separator hpSep = new Separator("HP Separator", feed);
process.add(hpSep);
process.run();

// Auto-size with 20% design margin
hpSep.autoSize(1.20);

// Now constraints are populated
Map<String, CapacityConstraint> constraints = hpSep.getCapacityConstraints();
CapacityConstraint gasLoad = constraints.get("gasLoadFactor");
logger.info("Gas load K-factor: " + gasLoad.getCurrentValue() + " m/s");
logger.info("Design K-factor:   " + gasLoad.getDesignValue() + " m/s");
logger.info("Utilization:       " +
    String.format("%.1f%%", gasLoad.getUtilization() * 100));

    }

    private static void example15() throws Exception {
Compressor comp = new Compressor("HP Compressor", gasStream);
comp.setOutletPressure(150.0, "bara");
process.add(comp);
process.run();

comp.autoSize(1.15);  // Multiplicative factor: 15% design margin
process.run();  // Recompute after activating the generated chart

Map<String, CapacityConstraint> constraints = comp.getCapacityConstraints();

    }

    private static void example16() throws Exception {
ThrottlingValve valve = new ThrottlingValve("Choke Valve", wellStream);
valve.setOutletPressure(60.0, "bara");
process.add(valve);
process.run();

valve.autoSize(1.20);

Map<String, CapacityConstraint> constraints = valve.getCapacityConstraints();
CapacityConstraint cvUtil = constraints.get("cvUtilization");
CapacityConstraint opening = constraints.get("valveOpening");

    }

    private static void example17() throws Exception {
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Export Pipeline", gasStream);
pipeline.setPipeWallRoughness(5e-5);
pipeline.setLength(1000.0);  // 1 km teaching line, length is in metres
pipeline.setDiameter(0.3048);  // 12-inch
process.add(pipeline);
process.run();

pipeline.initMechanicalDesign();  // Required before assigning capacity ratings
pipeline.autoSize(1.15);

Map<String, CapacityConstraint> constraints = pipeline.getCapacityConstraints();

    }

    private static void example18() throws Exception {
Pump pump = new Pump("Export Pump", oilStream);
pump.setOutletPressure(80.0, "bara");
process.add(pump);
process.run();

pump.autoSize(1.20);

    }

    private static void example19() throws Exception {
// Build process
ProcessSystem process = new ProcessSystem();
Stream feed = new Stream("Feed", fluid);
Separator hpSep = new Separator("HP Sep", feed);
Compressor comp = new Compressor("HP Comp", hpSep.getGasOutStream());
comp.setOutletPressure(150.0, "bara");
process.add(feed);
process.add(hpSep);
process.add(comp);
process.run();

// Auto-size all equipment
hpSep.autoSize(1.20);
comp.autoSize(1.15);
process.run();  // Recompute after activating the generated chart

// Find the bottleneck
BottleneckResult result = process.findBottleneck();
logger.info("Bottleneck: " + result.getEquipmentName());
logger.info("Constraint: " + result.getConstraintName());
logger.info("Utilization: " +
    String.format("%.1f%%", result.getUtilization() * 100));

    }

    private static void example20() throws Exception {
// Get the bottleneck constraint
BottleneckResult bottleneck = process.findBottleneck();
CapacityConstraint limitingConstraint = bottleneck.getConstraint();

// Disable it
limitingConstraint.setEnabled(false);

// Re-run and check the new bottleneck
process.run();
BottleneckResult newBottleneck = process.findBottleneck();

logger.info("Previous bottleneck: " + bottleneck.getEquipmentName()
    + " (" + bottleneck.getConstraintName() + ")");
logger.info("New bottleneck:      " + newBottleneck.getEquipmentName()
    + " (" + newBottleneck.getConstraintName() + ")");

    }

    private static void example21() throws Exception {
// Disable all constraints on the bottleneck equipment
CapacityConstrainedEquipment bottleneckEquip =
    (CapacityConstrainedEquipment) bottleneck.getEquipment();
int disabled = bottleneckEquip.disableAllConstraints();
logger.info("Disabled " + disabled + " constraints on "
    + bottleneck.getEquipmentName());

    }

    private static void example22() throws Exception {
// Disable ALL constraints on ALL equipment
int totalDisabled = process.disableAllConstraints();
logger.info("Disabled " + totalDisabled + " constraints system-wide");

// Re-run the same fixed feed with capacity reporting disabled
process.run();
double imposedFeedRate =
    feed.getFlowRate("kg/hr");

    }

    private static void example23() throws Exception {
// Exclude equipment from all capacity analysis
equipment.setCapacityAnalysisEnabled(false);

    }

    private static void example24() throws Exception {
Map<String, Double> utilization = process.getCapacityUtilizationSummary();

// Color coding based on utilization level
for (Map.Entry<String, Double> entry : utilization.entrySet()) {
    double u = entry.getValue();
    String status;
    if (u > 100.0) {
        status = "OVERLOADED";
    } else if (u > 90.0) {
        status = "NEAR LIMIT";
    } else if (u > 75.0) {
        status = "MODERATE";
    } else {
        status = "OK";
    }
    logger.info(String.format("%-25s %6.1f%%  [%s]\n",
        entry.getKey(), u, status));
}

    }

    private static void example25() throws Exception {
// Thresholds are explicit filters of the current utilization summary.
List<String> tier1 = new ArrayList<String>();
List<String> tier2 = new ArrayList<String>();
List<String> tier3 = new ArrayList<String>();
for (Map.Entry<String, Double> item : process.getCapacityUtilizationSummary().entrySet()) {
    if (item.getValue() > 95.0) { tier1.add(item.getKey()); }
    if (item.getValue() > 85.0) { tier2.add(item.getKey()); }
    if (item.getValue() > 75.0) { tier3.add(item.getKey()); }
}
logger.info("Critical above 95 percent: {}", tier1);
logger.info("Warning above 85 percent: {}", tier2);
logger.info("Watch above 75 percent: {}", tier3);

    }

    private static void example26() throws Exception {
separator.useEquinorConstraints();
// Inspect the resulting constraints; this preset is not a compliance certificate.

    }

    private static void example27() throws Exception {
separator.disableAllConstraints();  // Presets add enabled keys; first clear the old selection.
separator.useAPIConstraints();
// Inspect the resulting constraints; this preset is not a compliance certificate.

    }

    private static void example28() throws Exception {
// Create custom constraints
CapacityConstraint customGasLoad = new CapacityConstraint(
    "gasLoadFactor", "m/s", ConstraintType.SOFT)
    .setDesignValue(0.12)     // Custom K-factor
    .setMaxValue(0.15)        // Absolute max
    .setWarningThreshold(0.88)
    .setValueSupplier(() -> separator.getGasLoadFactor());  // Warn at 88%

separator.addCapacityConstraint(customGasLoad);

    }

    private static void example29() throws Exception {
EconomicParameters econ = new EconomicParameters()
    .setOilPrice(4500.0)        // NOK/Sm3
    .setDiscountRate(0.08)
    .setCurrency("NOK");

DebottleneckingAdvisor advisor = new DebottleneckingAdvisor(econ);

// addCandidate(name, targetEquipment, capexNok, firstYear, lastYear,
//              annualIncrementalValueNok, CapacityConstraint (nullable))
advisor.addCandidate(new DebottleneckingAdvisor.DebottleneckCandidate(
    "Uprate HP compressor driver", "HP compressor",
    45.0e6, 1, 10, 190.0e6,
    compressor.getCapacityConstraints().get("power")));

advisor.addCandidate(new DebottleneckingAdvisor.DebottleneckCandidate(
    "Add cyclone inlet to HP sep", "HP separator",
    15.0e6, 1, 10, 105.0e6, null));

List<DebottleneckingAdvisor.Recommendation> ranked = advisor.evaluate();
for (DebottleneckingAdvisor.Recommendation r : ranked) {
    logger.info(String.format("%-32s NPV=%,.0f  BCR=%.2f  payback=%.1f yr  %s%n",
        r.getCandidate().getName(), r.getNpvNok(), r.getBenefitCostRatio(),
        r.getPaybackYears(), r.isAttractive() ? "ATTRACTIVE" : "reject"));
}

    }

    private static void example30() throws Exception {
// A synthetic mass-flow case; field barrels require a separate density basis.
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
hpSep.autoSize(1.20);
hpComp.autoSize(1.15);
topside.run();  // Recompute after activating the generated chart
logger.info("Screening bottleneck: {}", topside.findBottleneck());

    }
    public static void main(String[] args) throws Exception {
        List<String> outcomes = new ArrayList<String>();
        for (int n = 1; n <= 30; n++) {
            try {
                setup();
                CapacityExample.class.getDeclaredMethod(String.format("example%02d", n)).invoke(null);
                logger.error("BOOK_JAVA_PASS_{}", n);
                outcomes.add("BOOK_JAVA_PASS_" + n);
            } catch (Throwable error) {
                logger.error("BOOK_JAVA_FAIL_{} {}", n, error.toString(), error);
                outcomes.add("BOOK_JAVA_FAIL_" + n + " " + error.toString() + " cause=" + error.getCause());
            }
        }
        java.nio.file.Files.write(java.nio.file.Paths.get("outcomes.txt"), outcomes, java.nio.charset.StandardCharsets.UTF_8);
    }
}
CapacityExample.main(new String[0]);
/exit
