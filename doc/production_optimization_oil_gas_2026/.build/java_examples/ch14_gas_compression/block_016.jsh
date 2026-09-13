// Gas turbine with 25 MW rated power at ISO conditions
// De-rate for ambient temperature of 30°C
double ambientTemp = 30.0;  // °C
double isoRating = 25.0e6;  // W
double derating = 1.0 - 0.007 * (ambientTemp - 15.0);  // ~0.7%/°C
comp.updatePowerConstraint((isoRating * derating) / 1000.0);  // ~22.4 MW available
