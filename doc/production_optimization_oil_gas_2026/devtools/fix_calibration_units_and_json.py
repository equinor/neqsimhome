from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch32*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
 code=m[3];old=code
 if n==10:code='''Map<String,Object> definition = evaluator.getProblemDefinition();
// Inequality definitions contain infinite limits. Encode unbounded limits as JSON null.
definition.put("unboundedLimitEncoding", "null");
com.google.gson.JsonSerializer<Double> finiteDouble = new com.google.gson.JsonSerializer<Double>() {
    public com.google.gson.JsonElement serialize(Double value, java.lang.reflect.Type type,
        com.google.gson.JsonSerializationContext context) {
        return Double.isFinite(value) ? new com.google.gson.JsonPrimitive(value) : com.google.gson.JsonNull.INSTANCE;
    }
};
String json = new com.google.gson.GsonBuilder().registerTypeAdapter(Double.class, finiteDouble)
    .serializeNulls().setPrettyPrinting().create().toJson(definition);
logger.info("Problem definition: {}", json);'''
 if n==14:
  code=code.replace('"Compressor.outletStream.temperature","C",1.0', '"Compressor.outletStream.temperature","K",1.0')
  code=code.replace('compressor.getOutletStream().getTemperature("C")','compressor.getOutletStream().getTemperature("K")')
  code=code.replace('// Recovery experiment using synthetic observations generated at known efficiency.', '// Recovery experiment using synthetic observations generated at known efficiency.\n// This estimator path reads native stream-temperature units; observations therefore use kelvin.')
  code=code.replace('if (!Double.isFinite(fit.getEstimate(0))) { throw new IllegalStateException("Non-finite fitted efficiency"); }','if (!Double.isFinite(fit.getEstimate(0)) || Math.abs(fit.getEstimate(0)-0.78)>0.01) {\n    throw new IllegalStateException("Synthetic efficiency recovery failed");\n}')
 if code!=old:text=text[:m.start()]+'```'+m[1]+m[2]+'\n'+code.rstrip()+'\n```'+text[m.end():]
p.write_text(text,encoding='utf-8')
