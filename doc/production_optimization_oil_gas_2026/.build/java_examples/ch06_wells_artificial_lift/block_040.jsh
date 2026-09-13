// Set ambient temperature and heat transfer for a subsea flowline
NetworkPipe flowline = network.getPipe("Flowline-A");
flowline.setAmbientTemperature(277.15);  // 4°C seabed
flowline.setOverallHeatTransferCoeff(5.0);  // W/m2K (insulated pipe)
// Overall U represents the selected insulation; geometric sizing is a separate calculation.
