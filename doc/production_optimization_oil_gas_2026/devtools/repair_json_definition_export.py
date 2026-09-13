from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch32*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
m=list(PAT.finditer(text))[9]
code='''// Copy the definition into standard JSON values; unbounded limits become null.
Object finiteJsonValue(Object value) {
    if (value instanceof Double && !Double.isFinite(((Double) value).doubleValue())) { return null; }
    if (value instanceof Map) {
        Map<String,Object> clean = new LinkedHashMap<String,Object>();
        for (Map.Entry<?,?> entry : ((Map<?,?>) value).entrySet()) {
            clean.put(String.valueOf(entry.getKey()), finiteJsonValue(entry.getValue()));
        }
        return clean;
    }
    if (value instanceof Iterable) {
        List<Object> clean = new ArrayList<Object>();
        for (Object entry : (Iterable<?>) value) { clean.add(finiteJsonValue(entry)); }
        return clean;
    }
    return value;
}
Map<String,Object> definition = evaluator.getProblemDefinition();
definition.put("unboundedLimitEncoding", "null");
String json = new com.google.gson.GsonBuilder().serializeNulls().setPrettyPrinting()
    .create().toJson(finiteJsonValue(definition));
logger.info("Problem definition: {}",json);'''
text=text[:m.start()]+'```java\n'+code+'\n```'+text[m.end():]
p.write_text(text,encoding='utf-8')
