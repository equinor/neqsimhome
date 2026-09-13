import neqsim.process.equipment.heatexchanger.HeatExchanger;
import neqsim.process.mechanicaldesign.heatexchanger.HeatExchangerDesignFeasibilityReport;
SystemSrkEos coldFluid = new SystemSrkEos(288.15, 5.0);
coldFluid.addComponent("water", 1.0);
coldFluid.setMixingRule("classic");
Stream cold = new Stream("Cooling water", coldFluid);
cold.setFlowRate(30000.0, "kg/hr");
cold.run();
feed.setTemperature(120.0, "C");
feed.run();
HeatExchanger heatExchanger = new HeatExchanger("HX-01", feed, cold);
heatExchanger.setUAvalue(10000.0);
heatExchanger.run();
// Generate a screening report; supplier matching is not a vendor guarantee.
HeatExchangerDesignFeasibilityReport hxReport =
    new HeatExchangerDesignFeasibilityReport(heatExchanger);
hxReport.setExchangerType("shell-and-tube");
hxReport.setDesignStandard("TEMA-R");
hxReport.generateReport();

String verdict = hxReport.getVerdict();  // FEASIBLE / NOT_FEASIBLE
String json = hxReport.toJson();         // Full JSON report
