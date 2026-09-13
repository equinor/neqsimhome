// Separate parallel-machine setup; an optimizer needs independent split decisions.
Stream feedA = new Stream("Train A feed", fluid.clone());
Stream feedB = new Stream("Train B feed", fluid.clone());
feedA.setFlowRate(10000.0, "kg/hr");
feedB.setFlowRate(10000.0, "kg/hr");
feedA.run();
feedB.run();
Compressor compA = new Compressor("Train A", feedA);
Compressor compB = new Compressor("Train B", feedB);
compA.setOutletPressure(120.0);
compB.setOutletPressure(120.0);
compA.run();
compB.run();
logger.info("Parallel baseline power: {} kW", compA.getPower("kW") + compB.getPower("kW"));
