// After process.run()
double utilization = separator.getMaxUtilization();

logger.info("Separator utilization: " + (utilization * 100) + "%");
if (utilization > 1.0) {
    logger.info("WARNING: Separator capacity exceeded!");
} else if (utilization > 0.85) {
    logger.info("CAUTION: Separator approaching capacity limit");
}

// Detailed constraint breakdown
Map<String, CapacityConstraint> constraints = separator.getCapacityConstraints();
for (Map.Entry<String, CapacityConstraint> entry : constraints.entrySet()) {
    CapacityConstraint c = entry.getValue();
    if (c.isEnabled()) {
        logger.info(entry.getKey() + ": " + c.getUtilization() * 100 + "%");
    }
}
