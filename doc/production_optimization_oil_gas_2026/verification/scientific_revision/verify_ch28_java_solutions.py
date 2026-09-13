"""Chapter 28 exact Java plus source-preserving observed-state checks."""
from pathlib import Path
import ast,hashlib,json,os,re,subprocess,shutil,sys
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
shared=B/'devtools/optimization_java_solution_helpers.jsh';helper=OUT/'ch28_base_java_checks.jsh'
if not helper.exists():shutil.copy2(shared,helper)
extra=OUT/'ch28_java_extra_checks.jsh'
source=(B/'devtools/audit_optimization_java.py').read_text(encoding='utf-8')
PREFIX=next(ast.literal_eval(node.value) for node in ast.parse(source).body if isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='PREFIX' for v in node.targets))
chapter=next((B/'chapters').glob('ch28_*'));text=(chapter/'chapter.md').read_text(encoding='utf-8-sig')
work=B/'.build/java_solution_runs'/chapter.name;work.mkdir(parents=True,exist_ok=True)
data=work/'checks.json';data.write_text('[]')
cp=str(S/'target/classes')+os.pathsep+str(S/'src/main/resources')+os.pathsep+os.pathsep.join(v for v in (S/'target/neqsim-dev-classpath.txt').read_text().strip().split(os.pathsep) if v.lower().endswith('.jar'))
script=PREFIX+'\n'+helper.read_text(encoding='utf-8')+'\n'+extra.read_text(encoding='utf-8')+'\nBookSolutionChecks.destination=Paths.get('+json.dumps(str(data))+');\n'
entries=[]
for i,m in enumerate(P.finditer(text),1):
 lang,ann,code=m.groups()
 if lang!='java' or 'pattern' in ann:continue
 entries.append({'number':i,'sha256':hashlib.sha256(code.encode()).hexdigest(),'targeted':True})
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
 joined=re.sub(r'(\b(table|diameterTable)\s*=\s*(\w+)\.generateVFPTable\(\);)',r'\1 Chapter28Checks.table(\2,\3);',joined)
 script+=f'BookSolutionChecks.fence={i};\n'+joined+'\n'
 if re.search(r'public class (\w+).*public static void main',joined,re.S):
  name=re.search(r'public class (\w+)',joined)[1];script+=name+'.main(new String[0]);\n'
 add=''
 if i==2:add='BookSolutionChecks.check("reference separated into gas oil water",input.getGasPhase()!=null&&input.getOilPhase()!=null&&input.getWaterPhase()!=null,3,0);\n'
 if i==3:add='Chapter28Checks.fluid(fluid,input,1500,.20,10000,353.15,50);\n'
 if i==5:add='BookSolutionChecks.close("indexed required pressure matches underlying array",requiredInletPressure-table.getBHPTable()[2][1][0][1],0);\nBookSolutionChecks.close("reported feasibility percentage",100.0*feasible/total-100.0*table.getFeasibleCount()/table.getTotalPoints(),0);\n'
 if i==6:add='BookSolutionChecks.check("diagnostic export exact UTF-8 content",new String(Files.readAllBytes(Paths.get("production_screening.txt")),java.nio.charset.StandardCharsets.UTF_8).equals(vfpGen.toDiagnosticString()),0,0);\nBookSolutionChecks.check("diagnostic table is not reservoir deck",!vfpGen.toDiagnosticString().contains("VFPEXP")&&!vfpGen.toDiagnosticString().contains("VFPPROD"),0,0);\n'
 if i==7:add='double[] gorGrid=input.generateGORValues(); for(int k=0;k<8;k++){BookSolutionChecks.close("geometric GOR grid node "+k,(gorGrid[k]-200*Math.pow(10000.0/200,k/7.0))/gorGrid[k],1e-12);}\n'
 if i==8:add='double[] wcGrid=input.generateWaterCutValues(); for(int k=0;k<5;k++){BookSolutionChecks.close("linear watercut grid node "+k,wcGrid[k]-(.02+k*(.60-.02)/4),1e-12);}\n'
 if i==9:add='BookSolutionChecks.close("configured lower pressure bound",(Double)Chapter28Checks.field(vfpGen,"minInletPressure")-15,0);\nBookSolutionChecks.close("configured upper pressure bound",(Double)Chapter28Checks.field(vfpGen,"maxInletPressure")-400,0);\nBookSolutionChecks.close("configured bracket width bar",(Double)Chapter28Checks.field(vfpGen,"pressureTolerance")-.5,0);\n'
 if i==10:add='Chapter28Checks.fluid(testFluid,input,1000,.20,10000,353.15,50);\n'
 script+=add
script+='\n/exit\n';(work/'solutions.jsh').write_text(script,encoding='utf-8')
try:
 run=subprocess.run(['jshell','--execution','local','-J--add-modules=ALL-SYSTEM','-J-Xmx512m','--class-path',cp,str(work/'solutions.jsh')],cwd=work,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',timeout=1500);log=run.stdout
except subprocess.TimeoutExpired as ex:log=str(ex.stdout)+'\nTIMEOUT'
(OUT/'ch28_java_solution_checks.log').write_text(log,encoding='utf-8')
checks=json.loads(data.read_text(encoding='utf-8'))
for row in entries:
 row['checks']=[v for v in checks if v['fence']==row['number']]
 row['classification']='configuration_dimensions_verified' if row['number']==9 else 'numerical_solution_check'
 row['status']='passed' if row['checks'] and all(c['passed'] for c in row['checks']) else 'failed_or_missing_checks'
files=[Path(__file__),helper,extra,S/'src/main/java/neqsim/process/util/optimizer/RecombinationFlashGenerator.java',S/'src/main/java/neqsim/process/util/optimizer/MultiScenarioVFPGenerator.java']
report={'chapter':chapter.name,'source_commit':subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip(),'python_executable':sys.executable,'entries':entries,'bound_sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'scope':'Exact Java fences; independent component mixing and dimensional contracts, fresh physical-pressure replay of every VFP cell, phase/mass/component checks. Hydraulic thermal duty unspecified and field calibration not established.','diagnostic_errors':log.count('Error:')+log.count('Exception '),'all_targeted_checks_passed':all(r['status']=='passed' for r in entries) and not any(s in log for s in ['Error:','Exception ','TIMEOUT'])}
(OUT/'ch28_java_solution_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(len(checks),'checks',report['all_targeted_checks_passed'],report['diagnostic_errors'])
