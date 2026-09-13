// Step 1: Configure design parameters
separator.setDesignGasLoadFactor(0.107);
// separator.setDesignRetentionTime(180.0);  // If supported

// Step 2: Enable all constraints
separator.enableConstraints();

// Step 3: Run process and check utilization
process.run();
double util = separator.getMaxUtilization();
