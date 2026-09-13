import java.util.*;
import java.util.function.*;
import java.nio.file.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import neqsim.thermo.system.*;
import neqsim.thermodynamicoperations.*;
import neqsim.process.processmodel.*;
import neqsim.process.processmodel.lifecycle.*;
import neqsim.process.equipment.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.heatexchanger.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.equipment.capacity.CapacityConstraint.*;
import neqsim.process.util.optimizer.*;
import neqsim.process.util.optimizer.ProductionOptimizer.*;
import neqsim.process.controllerdevice.*;
import neqsim.process.measurementdevice.*;
import neqsim.process.automation.*;
Logger logger = LogManager.getLogger("BookJavaExamples");

class BookSolutionChecks {
    static int fence = 0;
    static java.nio.file.Path destination;
    static java.util.List<java.util.Map<String,Object>> rows = new java.util.ArrayList<java.util.Map<String,Object>>();
    static void check(String name, boolean passed, double observed, double tolerance) {
        java.util.Map<String,Object> row = new java.util.LinkedHashMap<String,Object>();
        row.put("fence",fence); row.put("name",name);row.put("passed",passed);
        row.put("observed",observed);row.put("tolerance",tolerance);rows.add(row);
        try { java.nio.file.Files.write(destination,new com.google.gson.Gson().toJson(rows).getBytes(java.nio.charset.StandardCharsets.UTF_8)); }
        catch (java.io.IOException error) { throw new IllegalStateException(error); }
        if (!passed) { throw new IllegalStateException(name+" failed: "+observed); }
    }
    static void close(String name,double residual,double tolerance) {
        check(name,Double.isFinite(residual) && Math.abs(residual)<=tolerance,residual,tolerance);
    }
    static double mass(neqsim.process.equipment.stream.StreamInterface stream) {
        double value=stream.getFlowRate("kg/sec");
        check(stream.getName()+" finite nonnegative mass",Double.isFinite(value)&&value>=-1e-12,value,0);
        check(stream.getName()+" positive finite pressure",Double.isFinite(stream.getPressure())&&stream.getPressure()>0,stream.getPressure(),0);
        check(stream.getName()+" positive finite temperature",Double.isFinite(stream.getTemperature())&&stream.getTemperature()>0,stream.getTemperature(),0);
        return value;
    }
    static double h(neqsim.process.equipment.stream.StreamInterface stream) {
        if (stream.getFlowRate("kg/sec")<1e-12) { return 0; }
        stream.getFluid().initProperties();return stream.getFluid().getEnthalpy();
    }
    static void process(neqsim.process.processmodel.ProcessSystem process) {
        for (neqsim.process.equipment.ProcessEquipmentInterface unit:process.getUnitOperations()) {
            if (unit instanceof neqsim.process.equipment.stream.Stream) { continue; }
            java.util.List<neqsim.process.equipment.stream.StreamInterface> in=unit.getInletStreams();
            java.util.List<neqsim.process.equipment.stream.StreamInterface> out=unit.getOutletStreams();
            if (in.isEmpty()||out.isEmpty()) {continue;}
            double mi=0,mo=0,hi=0,ho=0,work=0,nscale=0;
            java.util.Map<String,Double> cin=new java.util.HashMap<String,Double>();
            java.util.Map<String,Double> cout=new java.util.HashMap<String,Double>();
            for (neqsim.process.equipment.stream.StreamInterface stream:in) {
                mi+=mass(stream);hi+=h(stream);
                for(int j=0;j<stream.getFluid().getNumberOfComponents();j++) {
                    String key=stream.getFluid().getComponent(j).getComponentName();
                    double value=stream.getFluid().getComponent(j).getNumberOfmoles();
                    cin.put(key,cin.getOrDefault(key,0.0)+value);nscale+=value;
                }
            }
            for (neqsim.process.equipment.stream.StreamInterface stream:out) {
                mo+=mass(stream);ho+=h(stream);
                for(int j=0;j<stream.getFluid().getNumberOfComponents();j++) {
                    String key=stream.getFluid().getComponent(j).getComponentName();
                    double value=stream.getFluid().getComponent(j).getNumberOfmoles();
                    cout.put(key,cout.getOrDefault(key,0.0)+value);
                }
            }
            if(mi<1e-10) {continue;}
            close(unit.getName()+" material balance relative",(mo-mi)/mi,1e-6);
            double componentError=0;
            for(String key:cin.keySet()) { componentError=Math.max(componentError,Math.abs(cout.getOrDefault(key,0.0)-cin.get(key))/Math.max(nscale,1e-12)); }
            close(unit.getName()+" component balance relative",componentError,1e-6);
            if(unit instanceof neqsim.process.equipment.compressor.Compressor) {
                check(unit.getName()+" single-phase compressor inlet",in.get(0).getFluid().getNumberOfPhases()==1,in.get(0).getFluid().getNumberOfPhases(),1);
                work=((neqsim.process.equipment.compressor.Compressor)unit).getPower();
                check(unit.getName()+" positive compressor shaft work",work>0,work,0);
            }
            if(unit instanceof neqsim.process.equipment.heatexchanger.Heater) { work=((neqsim.process.equipment.heatexchanger.Heater)unit).getDuty(); }
            if(unit instanceof neqsim.process.equipment.pipeline.PipeBeggsAndBrills) {
                check(unit.getName()+" upward/passive pressure decline",out.get(0).getPressure()>0&&out.get(0).getPressure()<=in.get(0).getPressure(),out.get(0).getPressure(),0);
            } else {
                close(unit.getName()+" energy balance relative",(ho-hi-work)/Math.max(1,Math.max(Math.abs(work),Math.max(Math.abs(hi),Math.abs(ho)))),1e-5);
            }
        }
    }
    static void optimizer(neqsim.process.util.optimizer.ProductionOptimizer.OptimizationResult result) {
        check("optimizer finite positive candidate rate",Double.isFinite(result.getOptimalRate())&&result.getOptimalRate()>0,result.getOptimalRate(),0);
        for(neqsim.process.util.optimizer.ProductionOptimizer.UtilizationRecord rec:result.getUtilizationRecords()) {
            if(result.isFeasible()) {check("feasible candidate utilization "+rec.getEquipmentName(),rec.getUtilization()<=rec.getUtilizationLimit()+1e-6,rec.getUtilization()-rec.getUtilizationLimit(),1e-6);}
        }
        if(!result.isFeasible()) {check("rejected candidate explicit diagnostic",result.getInfeasibilityDiagnosis()!=null,0,0);}
    }
    static void pareto(neqsim.process.util.optimizer.ProductionOptimizer.ParetoResult result,
            neqsim.process.processmodel.ProcessSystem model, String[] keys, boolean[] maximize) {
        java.util.List<neqsim.process.util.optimizer.ProductionOptimizer.ParetoPoint> front=result.getParetoFront();
        check("nonempty Pareto front",!front.isEmpty(),front.size(),0);
        for(neqsim.process.util.optimizer.ProductionOptimizer.ParetoPoint point:front) {
            java.util.Map<String,Double> values=point.getObjectiveValues();
            for(String key:keys) {check("finite Pareto objective "+key,Double.isFinite(values.get(key)),values.get(key),0);}
            boolean dominated=false;
            for(neqsim.process.util.optimizer.ProductionOptimizer.ParetoPoint other:front) {
                boolean weak=true,strict=false;
                for(int k=0;k<keys.length;k++) {
                    double a=values.get(keys[k]),b=other.getObjectiveValues().get(keys[k]);
                    weak=weak&&(maximize[k]?b>=a:b<=a);strict=strict||(maximize[k]?b>a:b<a);
                }
                dominated=dominated||(weak&&strict);
            }
            check("Pareto objective non-dominance",!dominated,0,0);
            neqsim.process.processmodel.ProcessSystem replay=model.copy();
            neqsim.process.equipment.stream.StreamInterface input=(neqsim.process.equipment.stream.StreamInterface)replay.getUnit("feed");
            input.setFlowRate(point.getFullResult().getOptimalRate(),"kg/hr");replay.run();process(replay);
            neqsim.process.equipment.compressor.Compressor compressor=(neqsim.process.equipment.compressor.Compressor)replay.getUnit("Export Comp");
            close("Pareto independently copied power replay",(compressor.getPower("MW")-values.get("power"))/Math.max(1e-6,Math.abs(values.get("power"))),1e-5);
            optimizer(point.getFullResult());
        }
    }
    static void table(neqsim.process.util.optimizer.MultiScenarioVFPGenerator.VFPTable table) {
        check("nonempty declared diagnostic table",table.getTotalPoints()>0,table.getTotalPoints(),0);
        check("feasibility count within table bounds",table.getFeasibleCount()>=0&&table.getFeasibleCount()<=table.getTotalPoints(),table.getFeasibleCount(),0);
    }
    static void fluid(neqsim.thermo.system.SystemInterface fluid,double rate,double temperature,double pressure) {
        fluid.initProperties();double sum=0;
        for(double value:fluid.getMolarComposition()) {check("fluid finite nonnegative molar fraction",Double.isFinite(value)&&value>=0,value,0);sum+=value;}
        close("fluid composition normalization",sum-1,1e-8);
        close("fluid declared mass-flow normalization",fluid.getFlowRate("kg/hr")-rate,1e-5);
        close("fluid declared temperature",fluid.getTemperature()-temperature,1e-8);
        close("fluid declared pressure",fluid.getPressure()-pressure,1e-8);
        check("fluid positive finite density",Double.isFinite(fluid.getDensity("kg/m3"))&&fluid.getDensity("kg/m3")>0,fluid.getDensity("kg/m3"),0);
    }
}

BookSolutionChecks.destination=Paths.get("C:\\Users\\solbraa\\OneDrive - NTNU\\Documents\\GitHub\\neqsim\\neqsim-paperlab\\books\\production_optimization_oil_gas_2026\\.build\\java_solution_runs\\ch29_dynamic_simulation_and_control\\checks.json");
BookSolutionChecks.fence=7;
import neqsim.thermo.system.*;
import neqsim.process.processmodel.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.util.optimizer.*;
import neqsim.process.util.optimizer.ProductionOptimizer.*;
import neqsim.process.automation.*;
import neqsim.process.processmodel.lifecycle.*;
import java.util.*;
import org.apache.logging.log4j.*;
Logger logger = LogManager.getLogger("ProductionBook");
SystemInterface gas = new SystemSrkEos(313.15, 60.0);
gas.addComponent("methane", 0.90);
gas.addComponent("ethane", 0.10);
gas.setMixingRule("classic");
Stream feed = new Stream("Feed", gas);
feed.setFlowRate(100000.0, "kg/hr");
Separator separator = new Separator("HP Sep", feed);
Compressor compressor = new Compressor("Compressor", separator.getGasOutStream());
compressor.setOutletPressure(150.0, "bara");
compressor.setPolytropicEfficiency(0.78);
compressor.setUsePolytropicCalc(true);
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(separator);
process.add(compressor);
process.run(); BookSolutionChecks.process(process);

import neqsim.process.controllerdevice.*;
Stream feedStream = feed;

ThrottlingValve valve = new ThrottlingValve("V-100", feedStream);

ControllerDeviceBaseClass levelController = new ControllerDeviceBaseClass();
levelController.setKp(2.0);
levelController.setTi(120.0);
levelController.setControllerSetPoint(0.5);

ControllerDeviceBaseClass pressureController = new ControllerDeviceBaseClass();
pressureController.setKp(1.5);
pressureController.setControllerSetPoint(50.0);


valve.addController("LC-100", levelController);
valve.addController("PC-200", pressureController);


ControllerDeviceInterface lc = valve.getController("LC-100");
Collection<ControllerDeviceInterface> all = valve.getControllers();
BookSolutionChecks.process(process);
BookSolutionChecks.fence=8;




BookSolutionChecks.fence=9;

ProcessAutomation auto = process.getAutomation();


List<String> units = auto.getUnitList();  
String eqType = auto.getEquipmentType("HP Sep");  


List<SimulationVariable> vars = auto.getVariableList("HP Sep");
for (SimulationVariable v : vars) {
    logger.info(v.getAddress() + " [" + v.getType() + "] " + v.getDescription());
    
    
}


double T = auto.getVariableValue("HP Sep.gasOutStream.temperature", "C");
double P = auto.getVariableValue("HP Sep.pressure", "bara");
double flow = auto.getVariableValue("HP Sep.gasOutStream.flowRate", "kg/hr");


auto.setVariableValue("Compressor.outletPressure", 150.0, "bara");
process.run(); BookSolutionChecks.process(process);  
BookSolutionChecks.process(process);
BookSolutionChecks.close("Celsius automation readback",T-separator.getGasOutStream().getTemperature("C"),1e-8);BookSolutionChecks.close("pressure automation readback",P-separator.getGasOutStream().getPressure("bara"),1e-8);BookSolutionChecks.close("flow automation readback kg/hr",flow-separator.getGasOutStream().getFlowRate("kg/hr"),1e-6);
BookSolutionChecks.fence=10;
ProcessModel plant = new ProcessModel();
plant.add("Separation", process);
ProcessAutomation plantAuto = plant.getAutomation();
List<String> areas = plantAuto.getAreaList();  


double T = plantAuto.getVariableValue("Separation::HP Sep.gasOutStream.temperature", "C");
plantAuto.setVariableValue("Separation::Compressor.outletPressure", 170.0, "bara");
plant.run();
BookSolutionChecks.fence=11;
ProcessAutomation auto = process.getAutomation();


String result = auto.getVariableValueSafe("hp separator.temperature", "C");






String setResult = auto.setVariableValueSafe("Compressor.outletPressure", 150.0, "bara");



String badResult = auto.setVariableValueSafe("Compressor.outletPressure", -50.0, "bara");


BookSolutionChecks.fence=12;
AutomationDiagnostics diag = auto.getDiagnostics();
String report = diag.getLearningReport();


/exit
