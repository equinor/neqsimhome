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
