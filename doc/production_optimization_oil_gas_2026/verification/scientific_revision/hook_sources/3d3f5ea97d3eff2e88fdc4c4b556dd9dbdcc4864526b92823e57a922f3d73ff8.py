"""Supplement exact Java fences with numerical conservation/contract checks."""
from pathlib import Path
import argparse,ast,hashlib,json,os,re,subprocess
B=Path(__file__).resolve().parents[1]
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
source=(B/'devtools/audit_optimization_java.py').read_text(encoding='utf-8')
PREFIX=next(ast.literal_eval(node.value) for node in ast.parse(source).body if isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='PREFIX' for v in node.targets))
helper=B/'devtools/optimization_java_solution_helpers.jsh'
TARGETS={24:[12,14,22,24,40,42,43,61,63,64,65],28:[2,3,4,5,6,10,11,12],29:[7,9],30:[24,25,26,27]}
parser=argparse.ArgumentParser();parser.add_argument('--chapter',type=int,required=True);args=parser.parse_args();n=args.chapter
chapter=next((B/'chapters').glob(f'ch{n:02d}_*'));text=(chapter/'chapter.md').read_text(encoding='utf-8-sig')
work=B/'.build/java_solution_runs'/chapter.name;work.mkdir(parents=True,exist_ok=True)
data=work/'checks.json';data.write_text('[]')
cp=str(S/'target/classes')+os.pathsep+str(S/'src/main/resources')+os.pathsep+os.pathsep.join(
    value for value in (S/'target/neqsim-dev-classpath.txt').read_text().strip().split(os.pathsep) if value.lower().endswith('.jar'))
script=PREFIX+'\n'+helper.read_text(encoding='utf-8')+'\nBookSolutionChecks.destination=Paths.get('+json.dumps(str(data))+');\n'
entries=[]
for i,m in enumerate(P.finditer(text),1):
 lang,ann,code=m.groups()
 if lang!='java' or 'pattern' in ann:continue
 entries.append({'number':i,'sha256':hashlib.sha256(code.encode()).hexdigest(),'targeted':i in TARGETS[n]})
 lines=[]
 for line in code.splitlines():
  quoted=False;escape=False;stop=len(line)
  for k,ch in enumerate(line):
   if ch=='"' and not escape:quoted=not quoted
   if not quoted and line[k:k+2]=='//':stop=k;break
   escape=(ch=='\\' and not escape)
  lines.append(line[:stop])
 joined=re.sub(r'\n\s*\.', '.', '\n'.join(lines))
 joined=re.sub(r'\b(process|testProcess|diameterCase)\.run\(\);',r'\1.run(); BookSolutionChecks.process(\1);',joined)
 if n==28:
  joined=re.sub(r'(\b(?:table|diameterTable)\s*=\s*\w+\.generateVFPTable\(\);)',r'\1 BookSolutionChecks.table('+('diameterTable' if i==11 else 'table')+');',joined)
 script+=f'BookSolutionChecks.fence={i};\n'+joined+'\n'
 if re.search(r'public class (\w+).*public static void main',joined,re.S):
  name=re.search(r'public class (\w+)',joined)[1];script+=name+'.main(new String[0]);\n'
 extra=''
 if n==24:
  if i in [12,14,22,24,40,42,43,61]:extra+='BookSolutionChecks.process(process);\n'
  if i in [22,24]:extra+='BookSolutionChecks.optimizer(result);\n'
  if i==40:extra+='BookSolutionChecks.pareto(pareto,process,new String[]{"throughput","power"},new boolean[]{true,false});\n'
  if i==42:extra+='BookSolutionChecks.pareto(threeObjectiveResult,process,new String[]{"oil_rate","gas_rate","power"},new boolean[]{true,true,false});\n'
  if i==43:extra+='for(ScenarioRequest request:scenarios){BookSolutionChecks.process(request.getProcess());}\n'
  if i==61:extra+='BookSolutionChecks.close("SQP bounded linear throughput optimum",sqpResult.getOptimalPoint()[0]-3.0,1e-4);\nBookSolutionChecks.check("SQP independently replayed power constraint",comp.getPower("MW")<=25.00001,comp.getPower("MW"),25.00001);\n'
  if i==63:extra+='BookSolutionChecks.check("constant synthetic detector signal accepted",steady.isAtSteadyState(),0,0);\n'
  if i in [64,65]:extra+='for(double r:reconciliation.getConstraintResidualsAfter()){BookSolutionChecks.close("reconciled mass constraint",r,1e-6);}\n'
  if i==64:extra+='double[] measuredValues={200000,150000,48000,5000}; double[] variances={4000000,2250000,1000000,250000}; double[] signs={1,-1,-1,-1}; String[] variableNames={"feed","gas","oil","water"}; for(int k=0;k<4;k++){double expected=measuredValues[k]+variances[k]*signs[k]*3000.0/7500000.0; BookSolutionChecks.close("closed-form weighted reconciliation "+variableNames[k],reconciler.getVariable(variableNames[k]).getReconciledValue()-expected,1e-6);}\nBookSolutionChecks.close("chi-square from normalized independent residual",reconciliation.getChiSquareStatistic()-1.2,1e-8);\n'
 if n==28:
  if i==2:extra+='BookSolutionChecks.close("reference standard pressure",input.getReferenceFluid().getPressure()-1.01325,1e-8);\n' if False else 'BookSolutionChecks.check("configured reference is retained",refFluid.getNumberOfComponents()==13,refFluid.getNumberOfComponents(),0);\n'
  if i==3:extra+='BookSolutionChecks.fluid(fluid,10000,353.15,50);\n'
  if i in [4,5]:extra+='BookSolutionChecks.table(table);\n'
  if i==6:extra+='BookSolutionChecks.check("diagnostic export contains content",Files.size(Paths.get("production_screening.txt"))>100,Files.size(Paths.get("production_screening.txt")),0);\n'
  if i==10:extra+='BookSolutionChecks.fluid(testFluid,10000,353.15,50);\n'
 if n==29 and i in [7,9]:extra+='BookSolutionChecks.process(process);\n'
 if n==29 and i==9:extra+='BookSolutionChecks.close("Celsius automation readback",T-separator.getGasOutStream().getTemperature("C"),1e-8);BookSolutionChecks.close("pressure automation readback",P-separator.getGasOutStream().getPressure("bara"),1e-8);BookSolutionChecks.close("flow automation readback kg/hr",flow-separator.getGasOutStream().getFlowRate("kg/hr"),1e-6);\n'
 if n==30:
  if i==24:extra+='BookSolutionChecks.process(process); BookSolutionChecks.check("lifecycle serialized state schema valid",result.isValid(),0,0);\n'
  if i==25:extra+='BookSolutionChecks.check("multi-area saved state exists",Files.size(Paths.get("platform_x_v3.json"))>100,0,0);\n'
  if i==26:extra+='BookSolutionChecks.check("metadata-only version comparison preserves equipment",diff.getAddedEquipment().isEmpty()&&diff.getRemovedEquipment().isEmpty(),0,0);\n'
  if i==27:extra+='BookSolutionChecks.check("compressed state roundtrip semantic JSON",new com.google.gson.JsonParser().parse(modelState.toJson()).equals(new com.google.gson.JsonParser().parse(restored.toJson())),0,0);\n'
 script+=extra
script+='\n/exit\n';(work/'solutions.jsh').write_text(script,encoding='utf-8')
try:
 run=subprocess.run(['jshell','--execution','local','-J--add-modules=ALL-SYSTEM','-J-Xmx512m','--class-path',cp,str(work/'solutions.jsh')],cwd=work,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',timeout=900)
 log=run.stdout
except subprocess.TimeoutExpired as ex:log=str(ex.stdout)+'\nTIMEOUT'
(B/f'verification/scientific_revision/ch{n:02d}_java_solution_checks.log').write_text(log,encoding='utf-8')
checks=json.loads(data.read_text(encoding='utf-8'))
for row in entries:
 row['checks']=[v for v in checks if v['fence']==row['number']]
 row['classification']='numerical_solution_check' if row['checks'] else 'executed_api_configuration'
 row['status']='passed' if (not row['targeted'] or row['checks']) and all(c['passed'] for c in row['checks']) else 'failed_or_missing_checks'
report={'chapter':chapter.name,'source_commit':subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip(),
 'entries':entries,'helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),
 'scope':'Exact Java code executed with conservation, domain, optimizer or data-contract hooks; fixtures are not field validation.',
 'diagnostic_errors':log.count('Error:')+log.count('Exception '),'all_targeted_checks_passed':all(r['status']=='passed' for r in entries) and 'Error:' not in log and 'Exception ' not in log and 'TIMEOUT' not in log}
archive=B/'verification/scientific_revision/hook_sources';archive.mkdir(exist_ok=True)
for item in [helper,Path(__file__),work/'solutions.jsh']:
 payload=item.read_bytes();digest=hashlib.sha256(payload).hexdigest();dest=archive/(digest+item.suffix);dest.write_bytes(payload)
 report.setdefault('verification_source_snapshots',[]).append({'source':str(item),'sha256':digest,'snapshot':str(dest.relative_to(B))})
(B/f'verification/scientific_revision/ch{n:02d}_java_solution_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(n,len(checks),'checks',report['all_targeted_checks_passed'],report['diagnostic_errors'])
