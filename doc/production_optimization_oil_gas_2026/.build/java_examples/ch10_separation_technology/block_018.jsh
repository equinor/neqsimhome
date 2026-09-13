// Initialize mechanical design
separator.initMechanicalDesign();
SeparatorMechanicalDesign design =
    (SeparatorMechanicalDesign) separator.getMechanicalDesign();

// Set actual vessel dimensions
// Gas flow is obtained from the solved stream; impose project envelope separately.   // Max gas flow [am3/hr]
design.setMaxOperationPressure(85.0);
design.setMaxOperationTemperature(100.0, "C");
design.setMinOperationTemperature(0.0, "C");        // Design pressure [bara]
design.setGasLoadFactor(0.107);           // Design K-factor [m/s]
design.setRetentionTime(180.0);           // Design retention time [s]

// Run design calculation
design.readDesignSpecifications();
design.calcDesign();

// The mechanical design now provides:
// - Minimum vessel diameter (gas capacity)
// - Minimum vessel length (liquid capacity)
// - Wall thickness (ASME)
// - Vessel weight estimate
// - Nozzle sizes
String json = design.toJson();
