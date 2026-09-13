Separator hpSep = separator;
ThrottlingValve mpValve = new ThrottlingValve("HP-MP", hpSep.getLiquidOutStream());
mpValve.setOutletPressure(15.0);
Separator mpSep = new Separator("MP", mpValve.getOutletStream());
ThrottlingValve lpValve = new ThrottlingValve("MP-LP", mpSep.getLiquidOutStream());
lpValve.setOutletPressure(2.0);
Separator lpSep = new Separator("LP", lpValve.getOutletStream());
process.add(mpValve);
process.add(mpSep);
process.add(lpValve);
process.add(lpSep);
process.run();
for (Separator stage : Arrays.asList(hpSep, mpSep, lpSep)) {
    stage.autoSize(1.2);
    stage.enableConstraints();
}
logger.info("Separation train configured; pressure optimization requires explicit decision bounds.");
