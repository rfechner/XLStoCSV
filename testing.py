import re

s = "heyt     here   how   a                 re                            you"
s2 = "hey;how;are"
regex = "\s+|\t+|\s+\t+|\t+\s+"
r2 = ";"

compiled = re.compile(regex)
print(len(compiled.findall(s)) + 1)
o = len(re.findall(regex, s))
print(o)
