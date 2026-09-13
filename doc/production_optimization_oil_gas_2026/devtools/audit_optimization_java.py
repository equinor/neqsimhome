"""Execute Java manuscript fragments in a chapter-scoped JShell context.

JShell is the host execution harness, not a claim of Java 8 compilation.
The manuscript remains restricted to Java 8 syntax/API. Errors are retained.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import argparse
BOOK = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("NEQSIM_PROJECT_ROOT", r"C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim"))
FENCES = re.compile(r"^```(python|java)([^\n]*)\n(.*?)^```", re.M | re.S)
PREFIX = """import java.util.*;
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
"""

classpath = str(SOURCE / "target/classes") + os.pathsep + str(SOURCE / "src/main/resources")
classpath += os.pathsep + os.pathsep.join(
    entry for entry in (SOURCE / "target/neqsim-dev-classpath.txt").read_text().strip().split(os.pathsep)
    if entry.lower().endswith('.jar'))
parser=argparse.ArgumentParser()
parser.add_argument('--chapters', default='24,28,29,30,32')
arguments=parser.parse_args()
selected=set(map(int, arguments.chapters.split(',')))
for chapter in sorted((BOOK / "chapters").glob("ch*")):
    if not 19 <= int(chapter.name[2:4]) <= 35:
        continue
    if int(chapter.name[2:4]) not in selected:
        continue
    text = (chapter / "chapter.md").read_text(encoding="utf-8-sig")
    fragments = [(n, m) for n, m in enumerate(FENCES.finditer(text), 1) if m[1] == "java"]
    if not fragments:
        continue
    work = BOOK / ".build/fence_runs" / chapter.name
    work.mkdir(parents=True, exist_ok=True)
    script = work / "manuscript_java.jsh"
    content = PREFIX
    for number, match in fragments:
        if 'pattern' in match[2]:
            continue
        # JShell otherwise ends a constructor expression at its line break and
        # parses the following fluent '.method' as a new statement.
        # Preserve string literals while removing line comments before joining.
        uncommented=[]
        for line in match[3].splitlines():
            quoted=False; escaped=False; stop=len(line)
            for pos,char in enumerate(line):
                if char == '"' and not escaped: quoted=not quoted
                if not quoted and line[pos:pos+2] == '//': stop=pos;break
                escaped=(char == '\\' and not escaped)
            uncommented.append(line[:stop])
        joined = re.sub(r'\n\s*\.', '.', '\n'.join(uncommented))
        content += f'String bookFence = "BOOK_FENCE_{number}";\n' + joined + "\n"
        if re.search(r'public class (\w+).*public static void main', joined, re.S):
            name=re.search(r'public class (\w+)', joined)[1]
            content+=f'{name}.main(new String[0]);\n'
    content += 'String bookFence = "BOOK_FENCE_END";\n/exit\n'
    script.write_text(content, encoding="utf-8")
    try:
        process = subprocess.run(["jshell", "--execution", "local", "-J--add-modules=ALL-SYSTEM", "-J-Xmx512m", "--class-path", classpath, str(script)],
                                 cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 encoding="utf-8", errors="replace", timeout=600)
        output = process.stdout
        status = "executed_with_diagnostics" if process.returncode == 0 else "harness_failed"
    except subprocess.TimeoutExpired as error:
        output = str(error.stdout or "") + str(error.stderr or "")
        status = "timeout"
    (BOOK / "verification" / (chapter.name + "_java.log")).write_text(output, encoding="utf-8")
    rows = []
    # JShell returns zero for individual compile errors. Preserve and count those
    # explicitly instead of treating the process exit status as success.
    for number, match in fragments:
        row = {"number": number, "line": text.count("\n", 0, match.start()) + 1,
               "sha256": hashlib.sha256(match[3].encode()).hexdigest(),
               "status": "attempted_in_chapter_context", "language": "java"}
        if 'pattern' in match[2]:
            row['status']='integration_pattern'
            row['reason']=match[2].strip()
            rows.append(row)
            continue
        marker=re.search(r'BOOK_FENCE_'+str(number)+r'\b(.*?)(?=BOOK_FENCE_|\Z)',output,re.S)
        if marker:
            diagnostics=marker[1]
            row['status']='failed' if ('Error:' in diagnostics or 'Exception ' in diagnostics) else 'passed'
            row['output']=diagnostics[-12000:]
        elif status == 'executed_with_diagnostics' and 'Error:' not in output and 'Exception ' not in output:
            row['status']='passed'
            row['scope']='Executed in a chapter context with zero compile/runtime diagnostics.'
        rows.append(row)
    result = {"chapter": chapter.name, "harness": "JShell, current source classpath",
              "status": status, "error_diagnostics": output.count("Error:"),
              "examples": rows,
              "scope": "Java snippets are API fragments; missing caller fixtures and unsupported APIs remain explicit in log. Exit code is not a compilation pass."}
    (BOOK / "verification" / (chapter.name + "_java.json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(chapter.name, len(rows), status, result["error_diagnostics"], flush=True)
