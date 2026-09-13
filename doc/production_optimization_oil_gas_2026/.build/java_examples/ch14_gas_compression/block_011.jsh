// Generate curves at the current design point
CompressorChartGenerator generator = new CompressorChartGenerator(compressor);
CompressorChartInterface chart = generator.generateCompressorChart("normal curves", 5);

// Apply to compressor
compressor.setCompressorChart(chart);
// Generated charts already use interpolation and extrapolation.
