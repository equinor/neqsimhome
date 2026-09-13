// Check erosional velocity after solving
for (String pipeName : network.getPipeNames()) {
    NetworkPipe pipe = network.getPipe(pipeName);
    double ratio = pipe.getErosionalVelocityRatio();
    if (ratio > 0.8) {
        logger.info(String.format("WARNING: %s erosional ratio = %.2f%n",
            pipeName, ratio));
    }
}
