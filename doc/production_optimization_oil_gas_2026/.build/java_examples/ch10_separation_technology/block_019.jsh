// Step 1: Run process
process.run();

// Step 2: Auto-size based on current flow
separator.autoSize(1.2);

// Step 3: Initialize mechanical design
separator.initMechanicalDesign();
SeparatorMechanicalDesign design =
    (SeparatorMechanicalDesign) separator.getMechanicalDesign();

// Step 4: Set design K-factor (overrides autoSize if different)
design.setGasLoadFactor(0.107);

// Step 5: Calculate design
design.readDesignSpecifications();
design.calcDesign();

// Step 6: Check utilization with actual design K-factor
separator.setDesignGasLoadFactor(0.107);
separator.enableConstraints();
process.run();

double util = separator.getMaxUtilization();
logger.info("Utilization with design K-factor: " + (util * 100) + "%");
