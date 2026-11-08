import re, sys
s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
s = re.sub(r"\[Stage \d+:[^\]]*\]", "", s)   # bilah progres
for line in re.split(r"[\r\n]+", s):
    line = line.strip()
    if line and "log4j" not in line and "setLogLevel" not in line:
        print(line)
