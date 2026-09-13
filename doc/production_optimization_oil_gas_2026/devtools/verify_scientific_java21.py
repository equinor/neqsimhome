"""Literal Ch21 Java execution plus dimensional/engineering hooks; current workspace classes."""
from pathlib import Path
import os,re,json,hashlib,subprocess,datetime,sys
sys.stdout.reconfigure(encoding='utf-8')
B=Path(__file__).resolve().parents[1];S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
p=B/'chapters/ch21_debottlenecking/chapter.md';t=p.read_text(encoding='utf-8');blocks=list(re.finditer(r'^```java\n(.*?)^```',t,re.M|re.S))
w=B/'.build/scientific_java21';w.mkdir(exist_ok=True,parents=True)
helper=(B/'devtools/optimization_java_solution_helpers.jsh').read_text(encoding='utf-8')
(w/'shared_helpers_snapshot.jsh').write_text(helper,encoding='utf-8')
# Extend the local copy for Pump shaft work; canonical shared helper is unchanged.
helper=helper.replace('if(unit instanceof neqsim.process.equipment.heatexchanger.Heater)', 'if(unit instanceof neqsim.process.equipment.pump.Pump) { work=((neqsim.process.equipment.pump.Pump)unit).getPower(); }\n            if(unit instanceof neqsim.process.equipment.heatexchanger.Heater)')
extra=r'''
class Ch21Checks {
 static void ck(String n,boolean p,double x,double tol) {BookSolutionChecks.check(n,p,x,tol);}
 static void close(String n,double x,double tol) {BookSolutionChecks.close(n,x,tol);}
 static void positive(String n,double x) {ck(n,Double.isFinite(x)&&x>0,x,0);}
 static void process(ProcessSystem p) {BookSolutionChecks.process(p); summary(p);}
 static void summary(ProcessSystem p) {
   double max=0; CapacityConstraint worst=null;
   Map<String,Double> s=p.getCapacityUtilizationSummary();
   for(ProcessEquipmentInterface u:p.getUnitOperations()) {
    if(u instanceof ProcessEquipmentBaseClass && !((ProcessEquipmentBaseClass)u).isCapacityAnalysisEnabled()) {ck("excluded equipment absent from summary",!s.containsKey(u.getName()),0,0);continue;}
    double manual=0;
    for(CapacityConstraint c:u.getCapacityConstraints().values()) {
      if(!c.isEnabled())continue;
      double value=c.getCurrentValue();
      ck(u.getName()+" "+c.getName()+" finite observed measurement",Double.isFinite(value),value,0);
      double ratio=(c.getMinValue()>0 && c.getDesignValue()==Double.MAX_VALUE)?(value>0?Math.min(9.99,c.getMinValue()/value):9.99):((c.getDesignValue()>0 && c.getDesignValue()!=Double.MAX_VALUE)?Math.min(9.99,value/c.getDesignValue()):0);
      close(u.getName()+" "+c.getName()+" dimensional utilization",c.getUtilization()-ratio,1e-10);
      if(ratio>manual)manual=ratio;
      if(ratio>max){max=ratio;worst=c;}
    }
    if(manual>0) {ck("positive native utilization present in summary",s.containsKey(u.getName()),manual,0);close("summary percent equals 100 times manual fraction "+u.getName(),s.get(u.getName())-100*manual,1e-8);}
   }
   BottleneckResult r=p.findBottleneck();
   close("global bottleneck equals enumerated maximum",r.getUtilization()-max,1e-10);
   if(worst!=null)ck("global bottleneck names an enabled maximum",r.getConstraint().isEnabled()&&Math.abs(r.getConstraint().getUtilization()-max)<1e-10,max,1e-10);
 }
 static void separator(Separator s) {
  double d=s.getInternalDiameter(),l=s.getSeparatorLength();positive("separator diameter m",d);positive("separator length m",l);
  SystemInterface f=s.getThermoSystem();f.initProperties();
  ck("dry fixture has gas/oil phases",f.hasPhaseType("gas")&&f.hasPhaseType("oil")&&!f.hasPhaseType("aqueous"),f.getNumberOfPhases(),2);
  double rhog=f.getPhase("gas").getDensity("kg/m3"),rhol=f.getPhase("oil").getDensity("kg/m3");
  positive("liquid denser than gas",rhol-rhog);
  double q=f.getPhase("gas").getFlowRate("m3/sec"),v=s.getGasSuperficialVelocity();
  double k=v*Math.sqrt(rhog/(rhol-rhog));
  close("Souders Brown density correction m/s",s.getGasLoadFactor()-k,1e-10);
  ck("effective gas area positive bounded by vessel area",q/v>0&&q/v<=Math.PI*d*d/4+1e-9,q/v,Math.PI*d*d/4);
  Map<String,CapacityConstraint> c=s.getCapacityConstraints();
  Set<String> expected=new HashSet<String>(Arrays.asList("gasLoadFactor","kValue","dropletCutSize","inletMomentum","oilRetentionTime","waterRetentionTime"));
  ck("separator exact six native keys",c.keySet().equals(expected),c.size(),6);
  close("oil residence current in minutes",c.get("oilRetentionTime").getCurrentValue()-s.calcOilRetentionTime(),1e-10);
  ck("oil retention has minimum-good direction",c.get("oilRetentionTime").isMinimumConstraint(),0,0);
  close("absent water sentinel not physical retention",c.get("waterRetentionTime").getCurrentValue()-999,1e-10);
 }
 static void compressor(Compressor c) {
  positive("compressor pressure rise bar",c.getOutletStream().getPressure()-c.getInletStream().getPressure());
  positive("compressor shaft work W",c.getPower());
  close("compressor kW W identity",c.getPower()-1000*c.getPower("kW"),1e-7);
  ck("generated chart activated",c.getCompressorChart().isUseCompressorChart(),0,0);
  Set<String> keys=c.getCapacityConstraints().keySet();
  ck("compressor native six keys and no implicit temperature/head",keys.equals(new HashSet<String>(Arrays.asList("speed","minSpeed","power","ratedPower","surgeMargin","stonewallMargin"))),keys.size(),6);
  close("power percent normalized by design kW",c.getCapacityConstraints().get("power").getCurrentValue()-100*c.getPower("kW")/c.getMechanicalDesign().maxDesignPower,1e-8);
  ck("compressor power unit percent",c.getCapacityConstraints().get("power").getUnit().equals("%"),0,0);
 }
 static void tier(ProcessSystem p,List<String> actual,double percent) {
   Set<String> e=new HashSet<String>();
   for(ProcessEquipmentInterface u:p.getUnitOperations())if(u.getMaxUtilization()>percent/100)e.add(u.getName());
   ck("percent filter "+percent,new HashSet<String>(actual).equals(e),actual.size(),e.size());
 }
}
'''
hooks={
1:'Ch21Checks.process(process); Ch21Checks.separator(separator); Ch21Checks.compressor(compressor); BookSolutionChecks.fluid(feed.getFluid(),10000,303.15,70);',
2:'Ch21Checks.close("speed supplier RPM",speedConstraint.getCurrentValue()-compressor.getSpeed(),1e-10); Ch21Checks.close("speed configured utilization",speedConstraint.getUtilization()-compressor.getSpeed()/10000,1e-10); Ch21Checks.close("speed absolute max RPM",speedConstraint.getMaxValue()-11000,0);',
3:'Ch21Checks.close("assumed shadow-price scalar roundtrip",price-250,0);',
4:'Ch21Checks.ck("eighteen registered strategy contracts",registry.getStrategyCount()==18,registry.getStrategyCount(),18); Ch21Checks.ck("registered separator handler selected",registry.findStrategy(separator).supports(separator),0,0);',
5:'Ch21Checks.ck("analysis flag enabled",equipment.isCapacityAnalysisEnabled(),0,0); for(CapacityConstraint c:equipment.getCapacityConstraints().values())Ch21Checks.ck("all native separator checks enabled",c.isEnabled(),0,0);',
6:'Ch21Checks.process(process);',
7:'Ch21Checks.close("legacy fractional utilization",utilization-process.findBottleneck().getUtilization(),1e-10); Ch21Checks.ck("legacy current all-enabled fixture identity",bottleneck.getName().equals(process.findBottleneck().getEquipmentName()),0,0);',
8:'Ch21Checks.summary(process); for(Map.Entry<String,Double> e:utilization.entrySet())Ch21Checks.close("display percent",e.getValue()-100*process.getUnit(e.getKey()).getMaxUtilization(),1e-10);',
9:'for(ProcessEquipmentInterface u:process.getUnitOperations())Ch21Checks.ck("warning membership "+u.getName(),nearLimit.contains(u.getName())==u.isNearCapacityLimit(),0,0);',
10:'Ch21Checks.tier(process,above80,80);',
11:'boolean expectedOver=false,expectedHard=false; for(ProcessEquipmentInterface u:process.getUnitOperations()){expectedOver|=u.isCapacityExceeded();expectedHard|=u.isHardLimitExceeded();}Ch21Checks.ck("overload aggregate",overloaded==expectedOver,0,0);Ch21Checks.ck("hard-limit aggregate",hardViolation==expectedHard,0,0);',
12:'Ch21Checks.ck("nonempty constrained equipment enumeration",constrained.contains(separator)&&constrained.contains(compressor),constrained.size(),2);',
13:'Ch21Checks.process(process); Ch21Checks.ck("warning list retained",nearLimit.equals(process.getEquipmentNearCapacityLimit()),0,0);',
14:r'''double peak=0; int changes=0;String prior=null; for(BottleneckTracker.Snapshot s:tracker.getSnapshots()){peak=Math.max(peak,s.getUtilizationPercent());if(prior!=null&&!prior.equals(s.getIdentity()))changes++;prior=s.getIdentity();Ch21Checks.ck("snapshot exceeded direction",s.isExceeded()==(s.getUtilizationPercent()>100),s.getUtilizationPercent(),100);}Ch21Checks.close("tracker peak percent",tracker.getPeakUtilizationPercent()-peak,1e-10);Ch21Checks.close("tracker migration identities",tracker.getMigrationCount()-changes,0);Ch21Checks.ck("sweep both endpoints 17 points",tracker.getSnapshots().size()==17,tracker.getSnapshots().size(),17);''',
15:'Ch21Checks.process(process);Ch21Checks.separator(hpSep);Ch21Checks.close("separator flow margin",hpSep.getMechanicalDesign().getVolumeSafetyFactor()-1.20,1e-12);',
16:'Ch21Checks.process(process);Ch21Checks.compressor(comp);Ch21Checks.close("compressor design kW multiplicative factor",comp.getMechanicalDesign().maxDesignPower-referencePowerKW*1.15,1e-8);',
17:r'''Ch21Checks.process(process);Ch21Checks.close("valve declared outlet bara",valve.getOutletStream().getPressure()-60,1e-8);Ch21Checks.positive("valve installed Cv",valve.getCv());Ch21Checks.close("Cv stored/design convention",cvUtil.getUtilization()-valve.getCv()/valve.getMechanicalDesign().maxDesignCv,1e-10);Ch21Checks.close("valve design-volume multiplier",valve.getMechanicalDesign().maxDesignVolumeFlow-valve.getOutletStream().getFlowRate("m3/hr")*1.20,1e-8);for(CapacityConstraint c:constraints.values())Ch21Checks.ck("valve autoSize leaves constraints disabled",!c.isEnabled(),0,0);''',
18:r'''Ch21Checks.process(process);Ch21Checks.positive("positive sized pipeline diameter",pipeline.getDiameter());Ch21Checks.close("teaching line length m",pipeline.getLength()-1000,0);for(double pp:pipeline.getPressureProfile())Ch21Checks.positive("positive pipeline profile bar",pp);Ch21Checks.close("pipeline assigned volume-flow factor",pipeline.getMechanicalDesign().maxDesignVolumeFlow-pipeline.getOutletStream().getFlowRate("m3/hr")*1.15,1e-8);Ch21Checks.close("pipeline assigned pressure-drop factor",pipeline.getMechanicalDesign().maxDesignPressureDrop-pipeline.getPressureDrop()*1.15,1e-10);''',
19:r'''Ch21Checks.process(process);Ch21Checks.ck("liquid pump inlet",!oilStream.getFluid().hasPhaseType("gas"),oilStream.getFluid().getNumberOfPhases(),1);Ch21Checks.positive("pump positive work",pump.getPower());Ch21Checks.positive("pump pressure rise",pump.getOutletStream().getPressure()-oilStream.getPressure());Ch21Checks.close("pump design-flow factor",pump.getMechanicalDesign().maxDesignVolumeFlow-oilStream.getFlowRate("m3/hr")*1.20,1e-8);Ch21Checks.close("pump design-power heuristic",pump.getMechanicalDesign().maxDesignPower-pump.getPower()*1.20*1.20,1e-7);Ch21Checks.ck("pump default keys",pump.getCapacityConstraints().keySet().equals(new HashSet<String>(Arrays.asList("power","flowRate"))),pump.getCapacityConstraints().size(),2);''',
20:'Ch21Checks.process(process);Ch21Checks.separator(hpSep);Ch21Checks.compressor(comp);',
21:'Ch21Checks.process(process);Ch21Checks.ck("relaxed constraint inactive",!limitingConstraint.isEnabled(),0,0);Ch21Checks.ck("reported next constraint differs",newBottleneck.getConstraint()!=limitingConstraint,0,0);Ch21Checks.close("mask leaves imposed flow kg/hr",feed.getFlowRate("kg/hr")-10000,1e-8);',
22:'for(CapacityConstraint c:bottleneckEquip.getCapacityConstraints().values())Ch21Checks.ck("equipment checks disabled",!c.isEnabled(),0,0);Ch21Checks.close("disabled count",disabled-bottleneckEquip.getCapacityConstraints().size(),0);',
23:'Ch21Checks.process(process);Ch21Checks.close("reporting masks leave flow kg/hr",imposedFeedRate-10000,1e-8);Ch21Checks.ck("all reporting absent",process.getCapacityUtilizationSummary().isEmpty()&&!process.findBottleneck().hasBottleneck(),totalDisabled,0);',
24:'Ch21Checks.summary(process);Ch21Checks.ck("analysis flag disabled",!equipment.isCapacityAnalysisEnabled(),0,0);',
25:'Ch21Checks.summary(process);',
26:'Ch21Checks.tier(process,tier1,95);Ch21Checks.tier(process,tier2,85);Ch21Checks.tier(process,tier3,75);',
27:'Ch21Checks.ck("broader separator preset six enabled",separator.getCapacityConstraints().values().stream().filter(c->c.isEnabled()).count()==6,0,0);',
28:'Set<String> enabled=new HashSet<String>();for(CapacityConstraint c:separator.getCapacityConstraints().values())if(c.isEnabled())enabled.add(c.getName());Ch21Checks.ck("API-named preset four exact enabled keys",enabled.equals(new HashSet<String>(Arrays.asList("gasLoadFactor","kValue","oilRetentionTime","waterRetentionTime"))),enabled.size(),4);',
29:'Ch21Checks.close("custom K supplier dimensional",customGasLoad.getCurrentValue()-separator.getGasLoadFactor(),1e-10);Ch21Checks.close("custom K utilization",customGasLoad.getUtilization()-separator.getGasLoadFactor()/0.12,1e-10);Ch21Checks.ck("same-key replacement identity",separator.getCapacityConstraints().get("gasLoadFactor")==customGasLoad,0,0);',
30:r'''double last=Double.MAX_VALUE; for(DebottleneckingAdvisor.Recommendation r:ranked){double capex=r.getCandidate().getCapexNok(),annual=r.getCandidate().getAnnualIncrementalValueNok();double pv=annual*(1-Math.pow(1.08,-10))/0.08,pc=capex/1.08;Ch21Checks.close("independent discounted benefits NOK",r.getPvBenefitsNok()-pv,1e-5);Ch21Checks.close("NPV with CAPEX firstYear1",r.getNpvNok()-(pv-pc),1e-5);Ch21Checks.close("benefit cost ratio",r.getBenefitCostRatio()-pv/pc,1e-10);Ch21Checks.close("simple payback years",r.getPaybackYears()-capex/annual,1e-10);Ch21Checks.ck("descending NPV",r.getNpvNok()<=last,r.getNpvNok(),last);last=r.getNpvNok();}int updated=advisor.applyShadowPrices();Ch21Checks.close("one attached economic constraint",updated-1,0);Ch21Checks.close("annual value stored not marginal derivative",compressor.getCapacityConstraints().get("power").getShadowPrice()-190e6,0);''',
31:'Ch21Checks.process(topside);Ch21Checks.separator(hpSep);Ch21Checks.compressor(hpComp);Ch21Checks.close("topside declared feed kg/hr",wellStream.getFlowRate("kg/hr")-100000,1e-7);'
}
imports,body=blocks[0][1].split('public class CapacityExample {',1);prefix=body[:body.index('    public static void main(')]
methods=[]
for i,m in enumerate(blocks,1):
 code='' if i==1 else m[1]
 if i==16:code=code.replace('comp.autoSize(1.15);','double referencePowerKW=comp.getPower("kW");\ncomp.autoSize(1.15);')
 if i==14:code=code.replace('tracker.record(rate, "rate=" + rate, process.findBottleneck());','tracker.record(rate, "rate=" + rate, process.findBottleneck());\n    Ch21Checks.process(process);\n    Ch21Checks.close("tracker captured percent",tracker.getSnapshots().get(tracker.getSnapshots().size()-1).getUtilizationPercent()-100*process.findBottleneck().getUtilization(),1e-8);')
 methods.append('private static void example%02d() throws Exception {\n%s\n%s\n}'%(i,code,hooks[i]))
main='''public static void main(String[] args) throws Exception {
 BookSolutionChecks.destination=java.nio.file.Paths.get("checks.json");
 List<String> outcomes=new ArrayList<String>();
 for(int n=1;n<=COUNT;n++) { try {setup();BookSolutionChecks.fence=n;CapacityExample.class.getDeclaredMethod(String.format("example%02d",n)).invoke(null);outcomes.add("PASS "+n);}catch(Throwable e){outcomes.add("FAIL "+n+" "+e+" cause="+e.getCause());}}
 java.nio.file.Files.write(java.nio.file.Paths.get("outcomes.txt"),outcomes,java.nio.charset.StandardCharsets.UTF_8);
}
'''.replace('COUNT',str(len(blocks)))
script=imports+'\n'+helper+'\n'+extra+'\npublic class CapacityExample {\n'+prefix+'\n'.join(methods)+main+'}\nCapacityExample.main(new String[0]);\n/exit\n'
(w/'examples.jsh').write_text(script,encoding='utf-8')
for f in ['outcomes.txt','checks.json']:
 if (w/f).exists():(w/f).unlink()
deps=[x for x in (S/'target/neqsim-dev-classpath.txt').read_text().strip().split(os.pathsep) if x.lower().endswith('.jar')];cp=os.pathsep.join([str(S/'target/classes'),str(S/'src/main/resources')]+deps)
r=subprocess.run(['jshell','-J--add-modules=ALL-SYSTEM','-J-Xmx512m','--execution','local','--class-path',cp,str(w/'examples.jsh')],cwd=w,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
(w/'execution.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
checks=json.loads((w/'checks.json').read_text()) if (w/'checks.json').exists() else []
outcomes=(w/'outcomes.txt').read_text() if (w/'outcomes.txt').exists() else ''
entries=[]
for i,m in enumerate(blocks,1):
 cs=[x for x in checks if x['fence']==i];entries.append({'java_index':i,'code_sha256':hashlib.sha256(m[1].encode()).hexdigest(),'classification':'engineering_numerical_solution_check' if i not in [2,3,4,5,9,11,12,22,24,27,28,29] else 'API_configuration_or_reporting_contract','status':'pass' if re.search(r'^PASS '+str(i)+r'$',outcomes,re.M) and cs and all(x['passed'] for x in cs) else 'fail','checks':cs})
report={'chapter':p.parent.name,'status':'pass' if all(e['status']=='pass' for e in entries) else 'fail','source_sha256':hashlib.sha256(t.encode()).hexdigest(),'python':sys.executable,'source_root':str(S),'executed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'shared_helper_sha256':hashlib.sha256((w/'shared_helpers_snapshot.jsh').read_bytes()).hexdigest(),'entries':entries,'outcomes':outcomes,'check_count':len(checks),'scope':'Exact Java operation fragments with fresh literal fixture; supplemental checks after each fragment and inside tracker sweep. Component/mass relative tolerance1e-6, energy1e-5; API percentages independently reconstructed. Local helper adds pump work. Synthetic charts and ratings are screening data; no vendor/field/cavitation/erosion/AIV calibration.'}
(B/'verification/scientific_revision/ch21_java_solution_checks.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
print(report['status'],len(entries),'fences',len(checks),'checks');print(outcomes)
if not checks:print((r.stdout+'\n'+r.stderr)[-15000:])
sys.exit(0 if report['status']=='pass' else 1)
