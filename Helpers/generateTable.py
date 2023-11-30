import sys
import os
import glob
import re
from jinja2 import Template


def ReadVDMPPFile(path: str, dist: str = "./"):
    functions = {}
    document = ""
    regex_match = r"(?:(:?\s)|(:?^))(\S)*(?=(\s*:[^=]*==>))"
    with open(path, "r", encoding="utf-8") as file:
        document = file.read()
        file.seek(0, 0)
        for num, line in enumerate(file.readlines()):
            if path == "Environment.vdmpp":
                print(line, end="")
            result = re.search(regex_match, line.strip())
            print(result)
            if result:
                print(f"{num}: {result.group(0)}")
                functions[num] = result.group(0)
        print(functions)
    if len(glob.glob(".generated/coverage/*")) > 0:
        covPath = glob.glob(".generated/coverage/*")[0].replace("\\", "/")
        lastPart = path.lstrip(".").replace("\\", "/")  # For now just take the first.
        coverage = {}
        with open(f"{covPath}/{lastPart}.covtbl", "r", encoding="utf-8") as file:
            for num, line in enumerate(file.readlines()):
                wasRan = line.strip()[0] == "+"
                temp0 = line.split(" ")
                temp1 = temp0[1].split("-")
                lineNum = int(temp0[0][1:])
                if not lineNum in coverage.keys():
                    coverage[lineNum] = (0, 0, 0)
                temp2 = temp1[1].split("=")
                temp1[1] = temp2[0]
                temp2 = temp2[1]
                charNums = [int(x) for x in temp1]
                called = int(temp2)
                if wasRan:
                    coverage[lineNum] = (
                        coverage[lineNum][0] + charNums[1] - charNums[0] + 1,
                        coverage[lineNum][1],
                        called,
                    )
                else:
                    coverage[lineNum] = (
                        coverage[lineNum][0],
                        coverage[lineNum][1] + charNums[1] - charNums[0] + 1,
                        coverage[lineNum][2],
                    )
        print(coverage)
        funcLines = list(functions.keys())
        funcLines.sort()
        coverageLines = list(coverage.keys())
        coverageLines.sort()
        if len(coverageLines) > 0:
            funcLines.append(coverageLines[-1] + 1)
        aggregate = {}
        for num, line in enumerate(funcLines[:-1]):
            funcName = functions[line]
            for k in range(funcLines[num], funcLines[num + 1]):
                if not k in coverage.keys():
                    continue
                if funcName not in aggregate:
                    aggregate[funcName] = (line, 0, 0, coverage[k][2])
                aggregate[funcName] = (
                    aggregate[funcName][0],
                    aggregate[funcName][1] + coverage[k][0],
                    aggregate[funcName][2] + coverage[k][1],
                    aggregate[funcName][3],
                )
        data = [
            (key, line, (pos / (pos + neg) * 100) if (pos + neg) > 0 else 100, calls)
            for key, (line, pos, neg, calls) in aggregate.items()
        ]
        totPos = sum([pos for _, (_, pos, _, _) in aggregate.items()])
        totNeg = sum([neg for _, (_, _, neg, _) in aggregate.items()])
        totCov = (
            int(round(totPos / (totPos + totNeg) * 100, 0))
            if (totPos + totNeg) > 0
            else 100
        )
        data = [
            (fun, line, int(round(cov, 0)), calls) for (fun, line, cov, calls) in data
        ]
        totCalls = sum([x for (_, _, _, x) in data])
        temp = ""
        with open(
            f"{os.path.dirname(__file__)}/tex.template", "r", encoding="utf-8"
        ) as file:
            temp = file.read()
        t = Template(temp)
        toWrite = t.render(
            data=data,
            filename=os.path.basename(path),
            totCov=totCov,
            totCalls=totCalls,
            document=document,
        )
        with open(
            f"{dist}{os.path.splitext((os.path.basename(path)))[0]}.tex",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(toWrite)


BASE_LOCATION = "../latex/prj"

APP_LOCATION = "coverage"

LOCATION = f"{BASE_LOCATION}/{APP_LOCATION}/"

APPENDIX = """
%TC:ignore
\\chapter{Appedix}
{% for app in apps %}
\\input{ {{app}} }
\\clearpage{% endfor %}
%TC:endignore
"""

if __name__ == "__main__":
    os.makedirs(LOCATION, exist_ok=True)
    for file in glob.glob("*.vdmpp"):
        print(file)
        ReadVDMPPFile(file, LOCATION)
    t = Template(APPENDIX)
    with open(f"{BASE_LOCATION}/appendix.tex", "w", encoding="utf-8") as file:
        file.write(
            t.render(
                apps=[
                    f"{'/'.join(LOCATION.split('/')[2:])}{os.path.splitext(os.path.basename(x))[0]}"
                    for x in glob.glob("*.vdmpp")
                ]
            )
        )
