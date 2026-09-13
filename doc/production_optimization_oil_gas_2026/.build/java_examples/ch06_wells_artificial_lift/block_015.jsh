// Vertical tubing: 2500 m depth, 4-inch ID, 20 segments
network.addTubing("BH-A", "WH-A", "Tubing-A",
    2500.0,    // measured depth [m]
    0.1016,    // ID [m] (4-inch)
    90.0);     // inclination from horizontal [degrees] (90 = vertical)

// Deviated well: 3500 m MD, 60° average inclination
network.addTubing("BH-B", "WH-B", "Tubing-B",
    3500.0,    // measured depth [m]
    0.1016,    // ID [m]
    60.0);     // inclination [degrees]
