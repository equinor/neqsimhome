from pathlib import Path
import re
import shutil

BOOK = Path(__file__).resolve().parents[1]
backup = BOOK / '.build' / 'foundations_originals'
backup.mkdir(parents=True, exist_ok=True)
for path in sorted((BOOK / 'chapters').glob('*/chapter.md'))[:18]:
    original = backup / (path.parent.name + '.md')
    if not original.exists():
        shutil.copy2(path, original)
    text = path.read_text(encoding='utf-8')
    chapter = int(path.parent.name[2:4])
    numbered = re.search(r'^## (\d+)\.', text, re.M)
    if numbered:
        old = numbered[1]
        text = re.sub(r'^(#{2,6}\s+)' + old + r'(?=\.\d)', lambda m: m[1] + str(chapter), text, flags=re.M)
        text = re.sub(r'\b(Figure|Table|Equation|Eq\.|Exercise|Section)\s+' + old + r'(?=\.\d)', lambda m: m[1] + ' ' + str(chapter), text)
    else:
        count = 0
        def section(match):
            global count
            count += 1
            return '## ' + str(chapter) + '.' + str(count) + ' ' + match[1]
        text = re.sub(r'^## (.+)$', section, text, flags=re.M)
    text = text.replace('from neqsim import jneqsim', 'import jpype\njneqsim = jpype.JPackage("neqsim")')
    text = re.sub(r'System\.out\.println\((.*?)\);', r'logger.info(\1);', text, flags=re.S)
    text = re.sub(r'System\.out\.printf\((.*?)\);', r'logger.info(String.format(\1));', text, flags=re.S)
    if '```java' in text and 'Logger logger =' not in text:
        text = text.replace('```java\n', '```java\nimport org.apache.logging.log4j.LogManager;\nimport org.apache.logging.log4j.Logger;\nLogger logger = LogManager.getLogger("BookChapter' + str(chapter) + '");\n', 1)
    note = ('**Running the examples.** Start the source-workspace Python session described in Chapter 1, '
            'then run this chapter\'s Python blocks in reading order. Java blocks form a separate sequence '
            'using the same NeqSim build; carry forward objects from preceding Java blocks. '
            'The release execution records are in `verification/`; a successful run establishes API '
            'compatibility, while physical validation also requires the checks discussed in the text.\n\n')
    if '**Running the examples.**' not in text:
        first = text.index('\n') + 1
        text = text[:first] + '\n' + note + text[first:].lstrip('\n')
    path.write_text(text, encoding='utf-8')

path = BOOK / 'chapters/ch01_introduction/chapter.md'
text = path.read_text(encoding='utf-8')
old = 'import jpype\njneqsim = jpype.JPackage("neqsim")\nprint("NeqSim loaded successfully")'
new = '''import os
import sys
from pathlib import Path

# Set NEQSIM_PROJECT_ROOT to the NeqSim source clone before starting Python.
PROJECT_ROOT = Path(os.environ["NEQSIM_PROJECT_ROOT"]).resolve()
if not (PROJECT_ROOT / "target" / "classes").is_dir():
    raise RuntimeError("Compile the selected NeqSim source checkout first.")
sys.path.insert(0, str(PROJECT_ROOT / "devtools"))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=PROJECT_ROOT, recompile=False, verbose=False)
import jpype
jneqsim = jpype.JPackage("neqsim")
print("NeqSim loaded from", PROJECT_ROOT / "target" / "classes")'''
text = text.replace(old, new)
old = 'plant = ProcessModel()\nplant.add("Separation", separation_system)'
new = '''# Continue from the separator flowsheet created above.
separation_system = process
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
compressor = Compressor("Export compressor", hp_sep.getGasOutStream())
compressor.setOutletPressure(120.0)
compressor.setIsentropicEfficiency(0.75)
compression_system = ProcessSystem()
compression_system.add(compressor)
cooler = Cooler("Export cooler", compressor.getOutletStream())
cooler.setOutTemperature(313.15)
gas_processing_system = ProcessSystem()
gas_processing_system.add(cooler)
plant = ProcessModel()
plant.add("Separation", separation_system)'''
text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
