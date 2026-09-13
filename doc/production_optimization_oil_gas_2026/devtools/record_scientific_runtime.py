"""Record the source and compiled-class identity used by the scientific revision."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
B=Path(__file__).resolve().parents[1]
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
git=lambda *args:subprocess.check_output(['git','-C',str(S),*args],text=True).strip()
changes=git('status','--porcelain','--untracked-files=no','--','src/main/java','src/test/java','pom.xml')
assert not changes, 'Source code changed since the recorded scientific basis: '+changes
classes={str(p.relative_to(S/'target/classes')):sha(p) for p in sorted((S/'target/classes').rglob('*.class'))}
assert classes
source={str(p.relative_to(S)):sha(p) for p in sorted((S/'src/main/java').rglob('*.java'))}
r={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'source_root':str(S),'source_commit':git('rev-parse','HEAD'),'tracked_java_and_pom_clean':True,
   'python_executable':sys.executable,'python_version':sys.version,
   'compiled_class_count':len(classes),'compiled_classes':classes,
   'source_java_count':len(source),'source_java_sha256':source,
   'pom_sha256':sha(S/'pom.xml'),
   'interpretation':'Compiled workspace classes and clean source identity retained for reproduction; this manifest does not itself assert physical validity.'}
out=B/'verification/scientific_revision/runtime_artifact_manifest.json'
out.write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in ('compiled_classes','source_java_sha256')},indent=2))
