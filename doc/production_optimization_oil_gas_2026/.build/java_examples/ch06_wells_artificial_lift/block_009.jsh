// Oil well with PI = 15 Sm3/d/bar (converted internally to SI)
network.addWellIPR("Reservoir-A", "BH-A", "Well-A IPR",
    15.0 * 800.0 / 86400.0 / 1e5, // SI PI from 15 Sm3/day/bar and 800 kg/Sm3
    false);    // oil IPR; source node supplies reservoir pressure

// Gas well (set gasIPR flag)
NetworkPipe gasIPR = network.addWellIPR("Reservoir-B", "BH-B", "Well-B IPR",
    0.5 * 0.8 / 86400.0 / 1e10, // kg/s/Pa2 from 0.8 kg/Sm3 gas
    true);     // gas pressure-squared IPR
gasIPR.setGasIPR(true);
