ThreePhaseSeparator threePhaseSep =
    new ThreePhaseSeparator("LP 3-Phase", feed);

// After running the process:
process.add(threePhaseSep);
process.run();

// Auto-size with 20% design margin
threePhaseSep.autoSize(1.2);

// The three-phase separator creates constraints for:
// - gasLoadFactor (gas section)
// - liquid retention time (oil section)
// - water retention time (water section)
