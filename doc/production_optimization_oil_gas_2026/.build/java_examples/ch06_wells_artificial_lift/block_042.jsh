// Comparison example
network.setSolverType(SolverType.HARDY_CROSS);
long t1 = System.nanoTime();
network.run();
long hardyCrossTime = System.nanoTime() - t1;
int hcIter = network.getIterationCount();

network.setSolverType(SolverType.NEWTON_RAPHSON);
long t2 = System.nanoTime();
network.run();
long nrTime = System.nanoTime() - t2;
int nrIter = network.getIterationCount();

logger.info(String.format("Hardy Cross: %d iterations, %.1f ms%n",
    hcIter, hardyCrossTime / 1e6));
logger.info(String.format("Newton-Raphson: %d iterations, %.1f ms%n",
    nrIter, nrTime / 1e6));
