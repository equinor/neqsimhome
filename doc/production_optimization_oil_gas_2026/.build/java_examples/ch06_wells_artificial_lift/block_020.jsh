// Get pressure at any node
double whPressure = network.getNodePressure("WH-A");  // bara

// Get flow rate through any element
double pipeFlow = network.getPipeFlowRate("Flowline-A") / 3600.0;  // kg/s

// Get element details
NetworkPipe pipe = network.getPipe("Flowline-A");
double velocity = pipe.getVelocity();        // m/s
double reynolds = pipe.getReynoldsNumber();  // dimensionless
double holdup = pipe.getLiquidHoldup();       // fraction
