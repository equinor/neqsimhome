// Set max speed 15% above current operating speed
double designSpeed = compressor.getSpeed();
compressor.setMaximumSpeed(designSpeed * 1.15);
