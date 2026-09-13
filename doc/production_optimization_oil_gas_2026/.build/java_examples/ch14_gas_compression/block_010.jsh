// After process.run()
double utilization = comp.getMaxUtilization();
Map<String, CapacityConstraint> constraints = comp.getCapacityConstraints();

for (Map.Entry<String, CapacityConstraint> entry : constraints.entrySet()) {
    CapacityConstraint c = entry.getValue();
    logger.info(entry.getKey() + ": "
        + c.getCurrentValue() + " / " + c.getDesignValue()
        + " = " + String.format("%.1f%%", c.getUtilization() * 100));
}
