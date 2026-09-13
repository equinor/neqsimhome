Compressor comp = new Compressor("Export Compressor", feed);
comp.setOutletPressure(120.0);
comp.setPolytropicEfficiency(0.82);
comp.setUsePolytropicCalc(true);

// Set explicit constraints
comp.setMaximumSpeed(11500.0);       // rpm
comp.updatePowerConstraint((25.0e6) / 1000.0);        // kW (25 MW)
comp.getAntiSurge().setSurgeControlFactor(1.10);           // 10% minimum
comp.reinitializeCapacityConstraints();            // Activate constraint tracking

process.add(comp);
process.run();
Compressor compressor = comp;
