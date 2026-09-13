// Set a specific K-factor design value
separator.setDesignGasLoadFactor(0.107);  // m/s, horizontal with wire mesh

// Note: setDesignGasLoadFactor() updates the stored value but does NOT
// automatically enable the constraint. You must call one of the enable
// methods (enableConstraints(), useEquinorConstraints(), etc.) to activate it.
