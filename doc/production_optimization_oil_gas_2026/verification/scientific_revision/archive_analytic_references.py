from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import urllib.request
ROOT=Path(__file__).resolve().parent
manifest_path=ROOT/'references/collection_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
sources=[
 ('nasa','compressor_thermodynamics.html','https://www.grc.nasa.gov/www/k-12/airplane/compth.html','NASA Glenn','Constant-cp ideal compressor equation and shaft first law. The source prose equates adiabatic with isentropic; our benchmark correctly distinguishes ideal isentropic reference from irreversible eta=0.8 compression.'),
 ('nasa','hydrostatic_pressure.html','https://www.grc.nasa.gov/www/k-12/WindTunnel/Activities/fluid_pressure.html','NASA Glenn','Hydrostatic pressure rho*g*h, with absolute versus gauge pressure distinction.'),
 ('nist','codata_constants.txt','https://physics.nist.gov/cuu/Constants/Table/allascii.txt','NIST CODATA','Exact molar gas constant and standard gravity used in analytical limits.'),
 ('nist','reference_properties_method.html','https://www.nist.gov/publications/thermophysical-properties-fluids','NIST','Reference tables are calculated with reference-fluid models; distinguish them from raw experimental measurements.')]
for folder,name,url,source,purpose in sources:
    path=ROOT/'references'/folder/name;path.parent.mkdir(exist_ok=True)
    # Native Windows HTTPS retrieval can use the managed system certificate
    # store when the bundled Python CA set lacks an enterprise trust anchor.
    # Never disable certificate verification to obtain primary references.
    if path.exists():
        data=path.read_bytes()
    else:
        data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read()
        path.write_bytes(data)
    entry={'source':source,'url':url,'file':str(path.relative_to(ROOT)),
           'sha256':hashlib.sha256(data).hexdigest(),'retrieved_utc':datetime.now(timezone.utc).isoformat(),
           'data_type':'Primary educational equation/constant provenance','purpose':purpose}
    manifest=[m for m in manifest if m['file']!=entry['file']]+[entry]
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
lines=['# Primary reference archive','','All retrieved data stay with the book. NIST fluid values are reference-EOS calculations, not new experimental measurements.','']
for entry in manifest:
    lines += [f"- [{Path(entry['file']).name}]({entry['url']}) — {entry['source']}.",
              f"  - {entry['purpose']}",f"  - Local: `{entry['file']}`; retrieved {entry['retrieved_utc']}; SHA-256 `{entry['sha256']}`."]
lines+=['','Data gaps: no independent mixture PVT, hydrate/MEG/TEG, field hydraulic, vendor map, facility dynamic, production-history or cost data were supplied. Those domains remain explicitly uncalibrated.']
(ROOT/'references/SOURCES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
