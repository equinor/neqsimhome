"""Apply reviewable source corrections in chapters 19--35 only."""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parents[1]
for chapter in sorted((BOOK / "chapters").glob("ch*")):
    number = int(chapter.name[2:4])
    if not 19 <= number <= 35:
        continue
    path = chapter / "chapter.md"
    text = path.read_text(encoding="utf-8-sig")
    heading = re.search(r"^## (\d+)\.\d+", text, re.M)
    if heading:
        old = heading.group(1)
        text = re.sub(r"^(#{2,6}\s+)" + old + r"\.(?=\d)",
                      lambda m: m[1] + str(number) + ".", text, flags=re.M)
        text = re.sub(r"\b(Figure|Table|Equation|Eq\.|Section|Example|Exercise) " + old + r"\.(?=\d)",
                      lambda m: m[1] + " " + str(number) + ".", text)
        text = re.sub(r"\*\*" + old + r"\.(\d+)\*\*", lambda m: f"**{number}.{m[1]}**", text)
    text = text.replace("from neqsim import jneqsim", "import jpype\njneqsim = jpype.JPackage(\"neqsim\")")
    # Java examples follow the repository's Log4j2-only output convention.
    text = text.replace("System.out.println(", "logger.info(")
    text = text.replace("System.err.println(", "logger.error(")
    text = re.sub(r"System\.out\.printf\((.*?)(?<!\\)\);", r"logger.info(String.format(\1));", text, flags=re.S)
    if number == 19:
        text = re.sub(r'(iso6976\.getValue\("(?:Superior|Inferior)(?:CalorificValue|WobbeIndex)"\))(?!\s*/)', r'\1 / 1000.0', text)
        text = text.replace('pipeline.setLength(200.0)', 'pipeline.setLength(200000.0)')
        text = text.replace('pipe.setLength(300.0)', 'pipe.setLength(300000.0)')
        text = text.replace('pipeline.setLength(250.0)', 'pipeline.setLength(250000.0)')
        text = text.replace('**Hydrocarbon dew point** — the cricondentherm of the hydrocarbon dew point curve (the maximum temperature at which any liquid hydrocarbon can form, regardless of pressure).',
                            '**Hydrocarbon dew point** is the temperature at which liquid hydrocarbon first forms at a specified pressure. The **cricondentherm** is the maximum temperature on the full hydrocarbon phase envelope; these are different specifications and must not be interchanged.')
        text = text.replace('and $Z_{\\text{mix}}$ is the compressibility factor of the mixture at metering conditions',
                            'and $Z_{\\text{mix}}$ is the compressibility factor of the mixture at the stated volume reference conditions')
        text = text.replace('The following example calculates the complete set of gas quality parameters:',
                            'The following example calculates gas quality at explicitly stated reference conditions. The volume-basis getter returns kJ/Sm³, so calorific values and Wobbe indices are divided by 1000 before reporting MJ/Sm³. The source implementation, rather than a display label, establishes this unit conversion \\cite{neqsim2026update}:')
    path.write_text(text, encoding="utf-8")
