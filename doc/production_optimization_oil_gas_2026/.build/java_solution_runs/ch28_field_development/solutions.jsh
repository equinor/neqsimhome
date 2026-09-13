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

class Chapter28Checks {
    static Object field(Object object,String name) {
        try { java.lang.reflect.Field f=object.getClass().getDeclaredField(name); f.setAccessible(true); return f.get(object); }
        catch(Exception e) { throw new IllegalStateException(e); }
    }
    static void fluid(neqsim.thermo.system.SystemInterface fluid,neqsim.process.util.optimizer.FluidMagicInput input,double gor,double wc,double liquidRate,double temperature,double pressure) {
        fluid.initProperties();
        BookSolutionChecks.close("operating temperature K",fluid.getTemperature()-temperature,1e-8);
        BookSolutionChecks.close("operating pressure bara",fluid.getPressure()-pressure,1e-8);
        double[] z=fluid.getMolarComposition();double sum=0;
        double[] mixture=new double[z.length];double[] contribution=new double[z.length];double total=0;
        neqsim.thermo.system.SystemInterface[] phases={input.getGasPhase(),input.getOilPhase(),input.getWaterPhase()};
        double[] q={liquidRate*(1-wc)*gor/3600,liquidRate*(1-wc)/3600,liquidRate*wc/3600};
        for(int p=0;p<3;p++) {
            double v=phases[p].getVolume("m3");BookSolutionChecks.check("reference phase positive standard volume",v>0&&Double.isFinite(v),v,0);
            for(int i=0;i<z.length;i++) {
                neqsim.thermo.component.ComponentInterface component=phases[p].getComponent(fluid.getComponent(i).getComponentName());
                if(component!=null) { contribution[i]+=q[p]/v*component.getNumberOfmoles(); }
            }
        }
        for(double value:contribution) {total+=value;}
        for(int i=0;i<z.length;i++) {
            sum+=z[i];BookSolutionChecks.check("fluid nonnegative finite composition",z[i]>=0&&Double.isFinite(z[i]),z[i],0);
            BookSolutionChecks.close("independent reference phase recombination composition",z[i]-contribution[i]/total,1e-8);
            for(int p=0;p<fluid.getNumberOfPhases();p++) { mixture[i]+=fluid.getBeta(p)*fluid.getPhase(p).getComponent(i).getx(); }
            BookSolutionChecks.close("operating flash component phase balance",mixture[i]-z[i],1e-8);
        }
        BookSolutionChecks.close("fluid composition normalized",sum-1,1e-8);
        BookSolutionChecks.check("operating density positive",fluid.getDensity("kg/m3")>0&&Double.isFinite(fluid.getDensity("kg/m3")),fluid.getDensity("kg/m3"),0);
        neqsim.thermo.system.SystemInterface std=fluid.clone();std.setTemperature(288.15);std.setPressure(1.01325);
        new neqsim.thermodynamicoperations.ThermodynamicOperations(std).TPflash();std.initProperties();
        BookSolutionChecks.check("standard gas oil aqueous phase applicability",std.hasPhaseType("gas")&&std.hasPhaseType("oil")&&std.hasPhaseType("aqueous"),std.getNumberOfPhases(),3);
        double oil=std.getPhase("oil").getVolume("m3")*3600,water=std.getPhase("aqueous").getVolume("m3")*3600,gas=std.getPhase("gas").getVolume("m3")*3600;
        BookSolutionChecks.close("standard liquid Sm3/hr normalization relative",(oil+water-liquidRate)/liquidRate,1e-6);
        BookSolutionChecks.close("this recipe equilibrium GOR versus declared blend relative",(gas/oil-gor)/gor,1e-6);
        BookSolutionChecks.close("this recipe equilibrium watercut versus declared blend absolute",water/(oil+water)-wc,1e-6);
        BookSolutionChecks.check("equilibrated GOR reported separately from blend target",gas/oil>0&&Double.isFinite(gas/oil),gas/oil,0);
        BookSolutionChecks.check("equilibrated water cut is physical",water/(oil+water)>=0&&water/(oil+water)<=1,water/(oil+water),0);
        BookSolutionChecks.check("resulting mass kg/hr reported not confused with liquid Sm3/hr",fluid.getFlowRate("kg/hr")>0,fluid.getFlowRate("kg/hr"),0);
    }
    static neqsim.process.processmodel.ProcessSystem replay(neqsim.process.util.optimizer.MultiScenarioVFPGenerator gen,double rate,double wc,double gor,double pin) {
        java.util.function.Supplier<neqsim.process.processmodel.ProcessSystem> factory=(java.util.function.Supplier<neqsim.process.processmodel.ProcessSystem>)field(gen,"processFactory");
        neqsim.process.processmodel.ProcessSystem process=factory.get();
        String name=(String)field(gen,"feedStreamName");
        neqsim.process.equipment.stream.StreamInterface feed=(neqsim.process.equipment.stream.StreamInterface)process.getUnit(name);
        neqsim.thermo.system.SystemInterface fluid=gen.getFlashGenerator().generateFluid(gor,wc,rate,gen.getInletTemperature(),pin);
        feed.setFluid(fluid);feed.setPressure(pin,"bara");feed.setTemperature(gen.getInletTemperature(),"K");feed.setFlowRate(rate,gen.getFlowRateUnit());process.run();
        BookSolutionChecks.close("pressure-table declared mass flow kg/hr",feed.getFlowRate("kg/hr")-rate,1e-6);
        return process;
    }
    static double outlet(neqsim.process.processmodel.ProcessSystem process,neqsim.process.util.optimizer.MultiScenarioVFPGenerator gen) {
        return ((neqsim.process.equipment.stream.StreamInterface)process.getUnit((String)field(gen,"outletStreamName"))).getPressure("bara");
    }
    static void table(neqsim.process.util.optimizer.MultiScenarioVFPGenerator.VFPTable table,neqsim.process.util.optimizer.MultiScenarioVFPGenerator gen) {
        BookSolutionChecks.close("complete declared 3 by 2 by 1 by 2 table",table.getTotalPoints()-12,0);
        BookSolutionChecks.check("table flow axis uses declared mass unit",table.getFlowRateUnit().equals("kg/hr"),0,0);
        double tol=(Double)field(gen,"pressureTolerance"),pmin=(Double)field(gen,"minInletPressure"),pmax=(Double)field(gen,"maxInletPressure");
        int accepted=0;
        for(int r=0;r<3;r++) {for(int p=0;p<2;p++) {for(int g=0;g<2;g++) {
            double rate=table.getFlowRates()[r],target=table.getOutletPressures()[p],wc=table.getWaterCuts()[0],gor=table.getGORs()[g],pin=table.getBHP(r,p,0,g);
            String tag="cell "+r+","+p+",0,"+g+" ";
            if(table.isFeasible(r,p,0,g)) {
                accepted++;BookSolutionChecks.check(tag+"finite bounded required inlet pressure",Double.isFinite(pin)&&pin>=pmin&&pin<=pmax,pin,pmax);
                neqsim.process.processmodel.ProcessSystem actual=replay(gen,rate,wc,gor,pin);
                double pout=outlet(actual,gen);BookSolutionChecks.check(tag+"fresh replay satisfies outlet pressure",Double.isFinite(pout)&&pout>=target-1e-6&&pout<pin,pout-target,1e-6);
                BookSolutionChecks.process(actual);
                double lower=outlet(replay(gen,rate,wc,gor,Math.max(pmin,pin-tol-1e-8)),gen);
                BookSolutionChecks.check(tag+"lower inlet brackets minimum required pressure",Double.isFinite(lower)&&lower<target+1e-6,lower-target,1e-6);
            } else {
                BookSolutionChecks.check(tag+"unavailable pressure retained as NaN",Double.isNaN(pin),0,0);
                double maximum=Double.NaN;try{maximum=outlet(replay(gen,rate,wc,gor,pmax),gen);}catch(Exception e){}
                BookSolutionChecks.check(tag+"maximum pressure cannot reach outlet target",!Double.isFinite(maximum)||maximum<target,Double.isFinite(maximum)?maximum:-1,0);
            }
        }}}
        BookSolutionChecks.close("accepted cell count exact",accepted-table.getFeasibleCount(),0);
    }
}

BookSolutionChecks.destination=Paths.get("C:\\Users\\solbraa\\OneDrive - NTNU\\Documents\\GitHub\\neqsim\\neqsim-paperlab\\books\\production_optimization_oil_gas_2026\\.build\\java_solution_runs\\ch28_field_development\\checks.json");
BookSolutionChecks.fence=2;
import neqsim.process.util.optimizer.FluidMagicInput;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;


SystemInterface refFluid = new SystemSrkEos(273.15 + 80.0, 200.0);
refFluid.addComponent("nitrogen", 0.5);
refFluid.addComponent("CO2", 2.0);
refFluid.addComponent("methane", 65.0);
refFluid.addComponent("ethane", 8.0);
refFluid.addComponent("propane", 5.0);
refFluid.addComponent("i-butane", 1.5);
refFluid.addComponent("n-butane", 3.0);
refFluid.addComponent("n-pentane", 2.0);
refFluid.addComponent("n-hexane", 1.5);
refFluid.addComponent("n-heptane", 4.0);
refFluid.addComponent("n-octane", 3.5);
refFluid.addComponent("n-decane", 2.0);
refFluid.addComponent("water", 2.0);
refFluid.setMixingRule("classic");
refFluid.setMultiPhaseCheck(true);


FluidMagicInput input = FluidMagicInput.builder().referenceFluid(refFluid).gorRange(200, 8000).waterCutRange(0.02, 0.50).numberOfGORPoints(6).numberOfWaterCutPoints(5).build();

input.separateToStandardConditions();
BookSolutionChecks.check("reference separated into gas oil water",input.getGasPhase()!=null&&input.getOilPhase()!=null&&input.getWaterPhase()!=null,3,0);
BookSolutionChecks.fence=3;
import neqsim.process.util.optimizer.RecombinationFlashGenerator;

RecombinationFlashGenerator flashGen = new RecombinationFlashGenerator(input);


SystemInterface fluid = flashGen.generateFluid(
    1500.0,     
    0.20,       
    10000.0,    
    353.15,     
    50.0);      


String stats = flashGen.getCacheStatistics();
Chapter28Checks.fluid(fluid,input,1500,.20,10000,353.15,50);
BookSolutionChecks.fence=4;
import neqsim.process.util.optimizer.MultiScenarioVFPGenerator;
import neqsim.process.processmodel.ProcessSystem;
import java.util.function.Supplier;


Supplier<ProcessSystem> processFactory = () -> {
    
    SystemInterface fluid = new SystemSrkEos(273.15 + 80.0, 200.0);
    fluid.addComponent("methane", 70.0);
    fluid.addComponent("ethane", 8.0);
    fluid.addComponent("propane", 4.0);
    fluid.addComponent("n-butane", 2.0);
    fluid.addComponent("n-heptane", 8.0);
    fluid.addComponent("n-decane", 5.0);
    fluid.addComponent("water", 3.0);
    fluid.setMixingRule("classic");
    fluid.setMultiPhaseCheck(true);

    Stream feed = new Stream("Feed", fluid);
    feed.setFlowRate(10000.0, "kg/hr");
    PipeBeggsAndBrills tubing = new PipeBeggsAndBrills("Tubing", feed);
    tubing.setLength(2500.0);
    tubing.setAngle(90.0);
    tubing.setDiameter(0.1016);
    tubing.setNumberOfIncrements(30);

    PipeBeggsAndBrills flowline = new PipeBeggsAndBrills("Flowline", tubing.getOutletStream());
    flowline.setLength(10000.0);
    flowline.setAngle(0.0);
    flowline.setDiameter(0.2032);
    flowline.setNumberOfIncrements(20);

    ProcessSystem process = new ProcessSystem();
    process.add(feed);
    process.add(tubing);
    process.add(flowline);
    process.add(new Stream("Export Outlet", flowline.getOutletStream()));
    return process;
};


MultiScenarioVFPGenerator vfpGen = new MultiScenarioVFPGenerator(
    processFactory,
    "Feed",        
    "Export Outlet" 
);


vfpGen.setFlashGenerator(flashGen);


vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});





vfpGen.setMinInletPressure(20.0);    
vfpGen.setMaxInletPressure(350.0);   
vfpGen.setPressureTolerance(0.5);    


vfpGen.setEnableParallel(false);
vfpGen.setNumberOfWorkers(8);


MultiScenarioVFPGenerator.VFPTable table = vfpGen.generateVFPTable(); Chapter28Checks.table(table,vfpGen);
BookSolutionChecks.fence=5;

double requiredInletPressure = table.getBHP(2, 1, 0, 1);



int feasible = table.getFeasibleCount();
int total = table.getTotalPoints();
logger.info(String.format("Feasible: %d/%d (%.1f%%)%n",
    feasible, total, 100.0 * feasible / total));


table.printSlice(0, 1);  
BookSolutionChecks.close("indexed required pressure matches underlying array",requiredInletPressure-table.getBHPTable()[2][1][0][1],0);
BookSolutionChecks.close("reported feasibility percentage",100.0*feasible/total-100.0*table.getFeasibleCount()/table.getTotalPoints(),0);
BookSolutionChecks.fence=6;

java.nio.file.Files.write(Paths.get("production_screening.txt"),
    vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
BookSolutionChecks.check("diagnostic export exact UTF-8 content",new String(Files.readAllBytes(Paths.get("production_screening.txt")),java.nio.charset.StandardCharsets.UTF_8).equals(vfpGen.toDiagnosticString()),0,0);
BookSolutionChecks.check("diagnostic table is not reservoir deck",!vfpGen.toDiagnosticString().contains("VFPEXP")&&!vfpGen.toDiagnosticString().contains("VFPPROD"),0,0);
BookSolutionChecks.fence=7;

input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);
input.setGORRange(200, 10000);
input.setNumberOfGORPoints(8);

double[] gorGrid=input.generateGORValues(); for(int k=0;k<8;k++){BookSolutionChecks.close("geometric GOR grid node "+k,(gorGrid[k]-200*Math.pow(10000.0/200,k/7.0))/gorGrid[k],1e-12);}
BookSolutionChecks.fence=8;
input.setWaterCutRange(0.02, 0.60);
input.setNumberOfWaterCutPoints(5);

double[] wcGrid=input.generateWaterCutValues(); for(int k=0;k<5;k++){BookSolutionChecks.close("linear watercut grid node "+k,wcGrid[k]-(.02+k*(.60-.02)/4),1e-12);}
BookSolutionChecks.fence=9;
vfpGen.setMinInletPressure(15.0);     
vfpGen.setMaxInletPressure(400.0);    
vfpGen.setPressureTolerance(0.5);     
BookSolutionChecks.close("configured lower pressure bound",(Double)Chapter28Checks.field(vfpGen,"minInletPressure")-15,0);
BookSolutionChecks.close("configured upper pressure bound",(Double)Chapter28Checks.field(vfpGen,"maxInletPressure")-400,0);
BookSolutionChecks.close("configured bracket width bar",(Double)Chapter28Checks.field(vfpGen,"pressureTolerance")-.5,0);
BookSolutionChecks.fence=10;

ProcessSystem testProcess = processFactory.get();
testProcess.run(); BookSolutionChecks.process(testProcess);
double testPressure = ((StreamInterface) testProcess.getUnit("Export Outlet")).getPressure("bara");
logger.info("Test outlet pressure: " + testPressure + " bara");


SystemInterface testFluid = flashGen.generateFluid(1000.0, 0.20, 10000.0, 353.15, 50.0);
testFluid.initProperties();
logger.info("Test fluid components: " + testFluid.getNumberOfComponents());
logger.info("Test fluid density: " + testFluid.getDensity("kg/m3") + " kg/m3");
Chapter28Checks.fluid(testFluid,input,1000,.20,10000,353.15,50);
BookSolutionChecks.fence=11;

for (double diameter : new double[]{0.076, 0.102}) {
    ProcessSystem diameterCase = processFactory.get();
    ((PipeBeggsAndBrills) diameterCase.getUnit("Tubing")).setDiameter(diameter);
    MultiScenarioVFPGenerator diameterGenerator = new MultiScenarioVFPGenerator(diameterCase, "Feed", "Export Outlet");
    diameterGenerator.setFlashGenerator(flashGen);
    diameterGenerator.setFlowRateUnit("kg/hr");
    diameterGenerator.setInletTemperature(358.15);
    diameterGenerator.setFlowRates(new double[]{5000.0,10000.0,20000.0});
    diameterGenerator.setOutletPressures(new double[]{30.0,50.0});
    diameterGenerator.setWaterCuts(new double[]{0.05});
    diameterGenerator.setGORs(new double[]{300.0,1000.0});
    diameterGenerator.setMinInletPressure(20.0);
    diameterGenerator.setMaxInletPressure(350.0);
    diameterGenerator.setEnableParallel(false);
    MultiScenarioVFPGenerator.VFPTable diameterTable = diameterGenerator.generateVFPTable(); Chapter28Checks.table(diameterTable,diameterGenerator);
    logger.info("Internal diameter {} m: {} of {} feasible sampled points", diameter,
        diameterTable.getFeasibleCount(), diameterTable.getTotalPoints());
}
BookSolutionChecks.fence=12;
import neqsim.process.util.optimizer.FluidMagicInput;
import neqsim.process.util.optimizer.RecombinationFlashGenerator;
import neqsim.process.util.optimizer.MultiScenarioVFPGenerator;
import neqsim.process.equipment.stream.Stream;
import neqsim.process.equipment.pipeline.PipeBeggsAndBrills;
import neqsim.process.processmodel.ProcessSystem;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;
import java.util.function.Supplier;

public class VFPGenerationExample {
    private static final org.apache.logging.log4j.Logger logger = org.apache.logging.log4j.LogManager.getLogger(VFPGenerationExample.class);

    /** Process factory that creates a fresh well + flowline model. */
    static Supplier<ProcessSystem> createProcessFactory() {
        return () -> {
            SystemInterface fluid = new SystemSrkEos(273.15 + 85.0, 200.0);
            fluid.addComponent("nitrogen", 0.4);
            fluid.addComponent("CO2", 1.8);
            fluid.addComponent("methane", 68.0);
            fluid.addComponent("ethane", 7.5);
            fluid.addComponent("propane", 4.5);
            fluid.addComponent("i-butane", 1.0);
            fluid.addComponent("n-butane", 2.5);
            fluid.addComponent("n-pentane", 1.5);
            fluid.addComponent("n-hexane", 1.2);
            fluid.addComponent("n-heptane", 4.5);
            fluid.addComponent("n-octane", 3.5);
            fluid.addComponent("n-decane", 2.1);
            fluid.addComponent("water", 1.5);
            fluid.setMixingRule("classic");
            fluid.setMultiPhaseCheck(true);

            Stream feed = new Stream("Feed", fluid);
    feed.setFlowRate(10000.0, "kg/hr");
            feed.setFlowRate(30000.0, "kg/hr");
            feed.setTemperature(85.0, "C");
            feed.setPressure(200.0, "bara");

            
            PipeBeggsAndBrills tubing =
                new PipeBeggsAndBrills("Tubing", feed);
            tubing.setLength(2800.0);
            tubing.setAngle(90.0);
            tubing.setDiameter(0.1016);
            tubing.setPipeWallRoughness(2.5e-5);
            tubing.setNumberOfIncrements(25);

            
            PipeBeggsAndBrills flowline =
                new PipeBeggsAndBrills("Export", tubing.getOutletStream());
            flowline.setLength(12000.0);
            flowline.setAngle(0.0);
            flowline.setDiameter(0.2032);
            flowline.setPipeWallRoughness(4.5e-5);
            flowline.setNumberOfIncrements(20);

            ProcessSystem process = new ProcessSystem();
            process.add(feed);
            process.add(tubing);
            process.add(flowline);
    process.add(new Stream("Export Outlet", flowline.getOutletStream()));
            return process;
        };
    }

    public static void main(String[] args) throws Exception {
        
        SystemInterface refFluid = new SystemSrkEos(273.15 + 85.0, 200.0);
        refFluid.addComponent("nitrogen", 0.4);
        refFluid.addComponent("CO2", 1.8);
        refFluid.addComponent("methane", 68.0);
        refFluid.addComponent("ethane", 7.5);
        refFluid.addComponent("propane", 4.5);
        refFluid.addComponent("i-butane", 1.0);
        refFluid.addComponent("n-butane", 2.5);
        refFluid.addComponent("n-pentane", 1.5);
        refFluid.addComponent("n-hexane", 1.2);
        refFluid.addComponent("n-heptane", 4.5);
        refFluid.addComponent("n-octane", 3.5);
        refFluid.addComponent("n-decane", 2.1);
        refFluid.addComponent("water", 1.5);
        refFluid.setMixingRule("classic");
        refFluid.setMultiPhaseCheck(true);

        
        FluidMagicInput input = new FluidMagicInput(refFluid);
        input.setGORRange(300, 8000);
        input.setWaterCutRange(0.05, 0.55);
        input.setNumberOfGORPoints(6);
        input.setNumberOfWaterCutPoints(5);
        input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);
        input.separateToStandardConditions();

        
        RecombinationFlashGenerator flashGen =
            new RecombinationFlashGenerator(input);

        
        MultiScenarioVFPGenerator vfpGen = new MultiScenarioVFPGenerator(
            createProcessFactory(), "Feed", "Export Outlet");
        vfpGen.setFlashGenerator(flashGen);

        vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});
        
        
        

        vfpGen.setMinInletPressure(20.0);
        vfpGen.setMaxInletPressure(350.0);
        vfpGen.setPressureTolerance(0.5);
        vfpGen.setEnableParallel(false);
        vfpGen.setNumberOfWorkers(8);

        
        MultiScenarioVFPGenerator.VFPTable table =
            vfpGen.generateVFPTable(); Chapter28Checks.table(table,vfpGen);

        logger.info(String.format("Feasible: %d/%d%n",
            table.getFeasibleCount(), table.getTotalPoints()));

        
        table.printSlice(0, 1);  

        
        java.nio.file.Files.write(java.nio.file.Paths.get("production_screening.txt"),
            vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
        logger.info("Process screening diagnostics exported to production_screening.txt");
    }
}
VFPGenerationExample.main(new String[0]);

/exit
