// Set up chart first
CompressorChartGenerator generator = new CompressorChartGenerator(comp);
comp.setCompressorChart(generator.generateCompressorChart("normal curves", 5));

// Now reinitialize constraints based on the chart
comp.reinitializeCapacityConstraints();
