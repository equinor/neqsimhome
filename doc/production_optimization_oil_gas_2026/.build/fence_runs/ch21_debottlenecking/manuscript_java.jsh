import java.util.*;
import java.util.function.*;
import java.nio.file.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import neqsim.thermo.system.*;
import neqsim.thermodynamicoperations.*;
import neqsim.process.processmodel.*;
import neqsim.process.processmodel.lifecycle.*;
import neqsim.process.equipment.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.heatexchanger.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.equipment.capacity.CapacityConstraint.*;
import neqsim.process.util.optimizer.*;
import neqsim.process.util.optimizer.ProductionOptimizer.*;
Logger logger = LogManager.getLogger("BookJavaExamples");
logger.error("BOOK_FENCE_1");
public interface CapacityConstrainedEquipment {
    // Query capacity analysis state
    boolean isCapacityAnalysisEnabled();
    void setCapacityAnalysisEnabled(boolean enabled);

    // Get all constraints
    Map<String, CapacityConstraint> getCapacityConstraints();

    // Bottleneck identification
    CapacityConstraint getBottleneckConstraint();
    CapacityConstraint getLimitingConstraint();

    // Utilization queries
    double getMaxUtilization();
    boolean isOverloaded();
    boolean isHardLimitExceeded();

    // Constraint management
    int disableAllConstraints();
    void enableConstraints();
    void useEquinorConstraints();
    void useAPIConstraints();
}

logger.error("BOOK_FENCE_2");
CapacityConstraint speedConstraint = new CapacityConstraint(
        "speed", "RPM", ConstraintType.HARD)
    .setDesignValue(10000.0)
    .setMaxValue(11000.0)
    .setWarningThreshold(0.9)
    .setValueSupplier(() -> compressor.getSpeed());

logger.error("BOOK_FENCE_3");
speedConstraint.setShadowPrice(shadowPriceNokPerRpm);  // fluent, returns the constraint
double price = speedConstraint.getShadowPrice();         // 0.0 by default

logger.error("BOOK_FENCE_4");
public enum ConstraintType {
    HARD,    // Cannot exceed — causes trip or equipment damage
    SOFT,    // Can exceed temporarily — reduced efficiency or life
    DESIGN   // Information only — original design basis
}

logger.error("BOOK_FENCE_5");
// In ProcessEquipmentBaseClass (inherited by all equipment)
private final Map<String, CapacityConstraint> capacityConstraints = new LinkedHashMap<>();
private boolean capacityAnalysisEnabled = true;

public void addCapacityConstraint(CapacityConstraint constraint) { ... }
public Map<String, CapacityConstraint> getCapacityConstraints() { ... }
public CapacityConstraint getBottleneckConstraint() { ... }
public double getMaxUtilization() { ... }
public boolean isOverloaded() { ... }
public boolean isHardLimitExceeded() { ... }
public int disableAllConstraints() { ... }

logger.error("BOOK_FENCE_6");
EquipmentCapacityStrategyRegistry registry =
    EquipmentCapacityStrategyRegistry.getInstance();
registry.register(new MyCustomStrategy());

logger.error("BOOK_FENCE_7");
// Option 1: Enable with Equinor-standard constraint sets
equipment.useEquinorConstraints();

// Option 2: Enable with API-standard constraint sets
equipment.useAPIConstraints();

// Option 3: Enable all constraints
equipment.enableConstraints();

// Option 4: Enable capacity analysis (equipment-level)
equipment.setCapacityAnalysisEnabled(true);

logger.error("BOOK_FENCE_8");
ProcessSystem process = new ProcessSystem();
// ... add equipment ...
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

logger.error("BOOK_FENCE_9");
ProcessEquipmentInterface bottleneck = process.getBottleneck();
double utilization = process.getBottleneckUtilization();

logger.error("BOOK_FENCE_10");
public class BottleneckResult {
    ProcessEquipmentInterface getEquipment();    // The bottleneck equipment
    String getEquipmentName();                    // Equipment name
    CapacityConstraint getConstraint();           // The limiting constraint
    String getConstraintName();                   // Constraint name
    double getUtilization();                      // Utilization as fraction
    boolean hasBottleneck();                      // Whether a bottleneck was found
    boolean isOverloaded();                       // Utilization > 1.0
    String getSummary();                          // Human-readable summary
}

logger.error("BOOK_FENCE_11");
Map<String, Double> utilization = process.getCapacityUtilizationSummary();

// Print sorted by utilization (highest first)
utilization.entrySet().stream()
    .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
    .forEach(entry -> logger.info(String.format("%-30s %6.1f%%\n",
        entry.getKey(), entry.getValue() * 100)));

logger.error("BOOK_FENCE_12");
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
if (!nearLimit.isEmpty()) {
    logger.info("WARNING: Equipment near capacity:");
    for (String name : nearLimit) {
        logger.info("  - " + name);
    }
}

logger.error("BOOK_FENCE_13");
// Equipment above 80% utilization
List<String> above80 = process.getEquipmentNearCapacityLimit(0.80);

logger.error("BOOK_FENCE_14");
// Any equipment above 100% of design capacity?
boolean overloaded = process.isAnyEquipmentOverloaded();

// Any HARD constraint violated (trip/safety condition)?
boolean hardViolation = process.isAnyHardLimitExceeded();

if (hardViolation) {
    logger.info("CRITICAL: Hard limit exceeded - check equipment!");
}

logger.error("BOOK_FENCE_15");
List<CapacityConstrainedEquipment> constrained =
    process.getConstrainedEquipment();
logger.info("Number of constrained equipment: " + constrained.size());

logger.error("BOOK_FENCE_16");
// Step 1: Run the process simulation
process.run();

// Step 2: Check for hard limit violations (safety first)
if (process.isAnyHardLimitExceeded()) {
    logger.info("ALERT: Hard constraints violated!");
    // Investigate immediately
}

// Step 3: Identify the bottleneck
BottleneckResult bottleneck = process.findBottleneck();
logger.info("Bottleneck: " + bottleneck.getSummary());

// Step 4: Review overall utilization
Map<String, Double> util = process.getCapacityUtilizationSummary();

// Step 5: Check early warning list
List<String> nearLimit = process.getEquipmentNearCapacityLimit(0.85);
logger.info("Equipment above 85%: " + nearLimit);

logger.error("BOOK_FENCE_17");
BottleneckTracker tracker = new BottleneckTracker();

for (double rate = 0.5; rate <= 1.3; rate += 0.05) {
    setFeedRate(process, rate);     // user-defined helper
    process.run();
    tracker.record(rate, "rate=" + rate, process.findBottleneck());
}

logger.info(tracker.getTimelineSummary());
logger.info("Distinct bottlenecks: "
    + tracker.getDistinctBottleneckEquipment());
logger.info("Migration events: " + tracker.getMigrationCount());
logger.info("Peak utilization: "
    + tracker.getPeakUtilizationPercent() + "%");

logger.error("BOOK_FENCE_18");
Separator hpSep = new Separator("HP Separator", feed);
process.add(hpSep);
process.run();

// Auto-size with 20% design margin
hpSep.autoSize(0.20);

// Now constraints are populated
Map<String, CapacityConstraint> constraints = hpSep.getCapacityConstraints();
CapacityConstraint gasLoad = constraints.get("gasLoadFactor");
logger.info("Gas load K-factor: " + gasLoad.getCurrentValue() + " m/s");
logger.info("Design K-factor:   " + gasLoad.getDesignValue() + " m/s");
logger.info("Utilization:       " +
    String.format("%.1f%%", gasLoad.getUtilization() * 100));

logger.error("BOOK_FENCE_19");
Compressor comp = new Compressor("HP Compressor", gasStream);
comp.setOutletPressure(150.0, "bara");
process.add(comp);
process.run();

comp.autoSize(0.15);  // 15% design margin

Map<String, CapacityConstraint> constraints = comp.getCapacityConstraints();

logger.error("BOOK_FENCE_20");
ThrottlingValve valve = new ThrottlingValve("Choke Valve", wellStream);
valve.setOutletPressure(60.0, "bara");
process.add(valve);
process.run();

valve.autoSize(0.20);

Map<String, CapacityConstraint> constraints = valve.getCapacityConstraints();
CapacityConstraint cvUtil = constraints.get("cvUtilization");
CapacityConstraint opening = constraints.get("valveOpening");

logger.error("BOOK_FENCE_21");
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Export Pipeline", gasStream);
pipeline.setPipeWallRoughness(5e-5);
pipeline.setLength(50.0, "km");
pipeline.setDiameter(0.3048);  // 12-inch
process.add(pipeline);
process.run();

pipeline.autoSize(0.15);

Map<String, CapacityConstraint> constraints = pipeline.getCapacityConstraints();

logger.error("BOOK_FENCE_22");
Pump pump = new Pump("Export Pump", oilStream);
pump.setOutletPressure(80.0, "bara");
process.add(pump);
process.run();

pump.autoSize(0.20);

logger.error("BOOK_FENCE_23");
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
hpSep.autoSize(0.20);
comp.autoSize(0.15);

// Find the bottleneck
BottleneckResult result = process.findBottleneck();
logger.info("Bottleneck: " + result.getEquipmentName());
logger.info("Constraint: " + result.getConstraintName());
logger.info("Utilization: " +
    String.format("%.1f%%", result.getUtilization() * 100));

logger.error("BOOK_FENCE_24");
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

logger.error("BOOK_FENCE_25");
// Disable all constraints on the bottleneck equipment
CapacityConstrainedEquipment bottleneckEquip =
    (CapacityConstrainedEquipment) bottleneck.getEquipment();
int disabled = bottleneckEquip.disableAllConstraints();
logger.info("Disabled " + disabled + " constraints on "
    + bottleneck.getEquipmentName());

logger.error("BOOK_FENCE_26");
// Disable ALL constraints on ALL equipment
int totalDisabled = process.disableAllConstraints();
logger.info("Disabled " + totalDisabled + " constraints system-wide");

// Run to find unconstrained production
process.run();
double unconstrainedProduction =
    feed.getFlowRate("kg/hr");

logger.error("BOOK_FENCE_27");
// Exclude equipment from all capacity analysis
equipment.setCapacityAnalysisEnabled(false);

logger.error("BOOK_FENCE_29");
Map<String, Double> utilization = process.getCapacityUtilizationSummary();

// Color coding based on utilization level
for (Map.Entry<String, Double> entry : utilization.entrySet()) {
    double u = entry.getValue();
    String status;
    if (u > 1.0) {
        status = "OVERLOADED";
    } else if (u > 0.90) {
        status = "NEAR LIMIT";
    } else if (u > 0.75) {
        status = "MODERATE";
    } else {
        status = "OK";
    }
    logger.info(String.format("%-25s %6.1f%%  [%s]\n",
        entry.getKey(), u * 100, status));
}

logger.error("BOOK_FENCE_30");
// Three-tier early warning
List<String> tier1 = process.getEquipmentNearCapacityLimit(0.95);  // Critical
List<String> tier2 = process.getEquipmentNearCapacityLimit(0.85);  // Warning
List<String> tier3 = process.getEquipmentNearCapacityLimit(0.75);  // Watch

logger.info("=== Capacity Early Warning ===");
logger.info("CRITICAL (>95%): " + tier1);
logger.info("WARNING  (>85%): " + tier2);
logger.info("WATCH    (>75%): " + tier3);

logger.error("BOOK_FENCE_36");
separator.useEquinorConstraints();
// Sets: K-factor = 0.107 m/s (wire mesh), retention time = 120 s
// Warning thresholds at 85% (more conservative)

logger.error("BOOK_FENCE_37");
separator.useAPIConstraints();
// Sets: K-factor per API 12J tables, retention time per API 12J
// Warning thresholds at 90% (standard)

logger.error("BOOK_FENCE_38");
// Create custom constraints
CapacityConstraint customGasLoad = new CapacityConstraint(
    "gasLoadFactor", "m/s", ConstraintType.SOFT)
    .setDesignValue(0.12)     // Custom K-factor
    .setMaxValue(0.15)        // Absolute max
    .setWarningThreshold(0.88);  // Warn at 88%

separator.addCapacityConstraint(customGasLoad);

logger.error("BOOK_FENCE_40");
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

logger.error("BOOK_FENCE_41");
// Key process setup (simplified)
ProcessSystem topside = new ProcessSystem();

Stream wellStream = new Stream("Well Stream", reservoirFluid);
wellStream.setFlowRate(80000.0 * 159.0, "kg/day");  // 80k bbl/d to kg/day

Separator hpSep = new Separator("HP Separator", wellStream);
Compressor hpComp = new Compressor("HP Compressor", hpSep.getGasOutStream());
hpComp.setOutletPressure(150.0, "bara");

// ... (full model with all equipment) ...

topside.run();

// AutoSize all equipment
hpSep.autoSize(0.20);
hpComp.autoSize(0.15);
// ... autoSize remaining equipment ...

logger.error("BOOK_FENCE_END");
/exit
