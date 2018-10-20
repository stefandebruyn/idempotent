import re
import sys


# Usage check
if len(sys.argv) != 2:
    raise ValueError("Usage: py idempotent.py <src>")


# Globals
SRC = open(sys.argv[1], "r")
CLASS_NAME = sys.argv[1][0:sys.argv[1].index(".")].title() + "Tester"
DEST = open(CLASS_NAME + ".java", "w")
RE_ARG_SPLITTER = r"[^A-Za-z]+"
EQUATOR_INTERFACE_DEFINITION = [
    "private interface Equator {",
    "\tpublic abstract boolean equate(Object a, Object b);",
    "}"
]
TRANSLATOR_INTERFACE_DEFINITION = [
    "private interface Translator {",
    "\tpublic abstract String translate(Object obj);",
    "}"
]
DEFAULT_EQUATOR_DEFINITION = [
    "private static Equator defaultEquator = new Equator() {",
    "\t@Override public boolean equate(Object a, Object b) {",
    "\t\treturn a.equals(b);",
    "\t}",
    "};"
]
DEFAULT_TRANSLATOR_DEFINITION = [
    "private static Translator defaultTranslator = new Translator() {",
    "\t@Override public String translate(Object obj) {",
    "\t\treturn obj.toString();",
    "\t}",
    "};"
]
LAMBDA_EQUATOR_DEFINITION = [
    "private static Equator <NAME> = new Equator() {",
    "\t@Override public boolean <HEADER>",
    "\t\t<BODY>",
    "\t}",
    "};"
]
LAMBDA_TRANSLATOR_DEFINITION = [
    "private static Translator <NAME> = new Translator() {",
    "\t@Override public String <HEADER>",
    "\t\t<BODY>",
    "\t}",
    "};"
]
MAIN_METHOD_DEFINITION = "public static void main(String[] args) {"
MAIN_METHOD_REFERENCES = [
    "Object expected, actual;",
    "String testName = \"\";",
    "double testNum = 1;"
]
RUN_TEST_METHOD_DEFINITION = [
    "private static void runTest(double testNum, String testName, Object expected, Object actual, Equator equator, Translator translator) {",
    "\tboolean equivalent = equator.equate(expected, actual);",
    '\tString testLevel = "" + (testNum % 1 == 0 ? (int)testNum : testNum);',
    '\tString result = (equivalent ? "Passed" : "**FAILED") + " Test " + testLevel;',
    "",
    "\t" + r'System.out.println("Test " + testLevel + ": " + testName + "\n" +',
    "\t\t" + r'"Expected value: " + translator.translate(expected) + "\n" +',
    "\t\t" + r'"Received value: " + translator.translate(actual) + "\n" +',
    "\t\tresult);",
    "}"
]


# Parser memory
last_parse = None
tab_level = 0
defined_default_lambdas = False
defined_header = False
current_equator = "defaultEquator"
current_translator = "defaultTranslator"
current_testgroup = None


# Gets a string of tab_level tabs; used for indenting
def get_tabs():
    return "".join(["\t"] * tab_level)


# Writes a string or a list of strings to DEST, indented according to get_tabs()
def write(out):
    tabs = get_tabs()

    if isinstance(out, list):
        for l in out:
            DEST.write(tabs + l + "\n")
    else:
        DEST.write(get_tabs() + out)


# Compiling algorithm proper
for line in SRC.readlines():
    args = re.split(RE_ARG_SPLITTER, line)
    print(args)

    # Imports
    if args[0] == "import":
        DEST.write(line)
        last_parse = "import"
        continue

    # Class definition
    if args[0] != "import" and last_parse == "import":
        write("\n")
        write("public class " + CLASS_NAME + " {\n")
        tab_level += 1
        last_parse = "class"
        continue

    # Equator and translator definitions
    if args[0] == "equator" or args[0] == "translator":
        # This is an equator declaration
        if not defined_header:
            # Make sure the functional interfaces are defined first
            if not defined_default_lambdas:
                write(EQUATOR_INTERFACE_DEFINITION)
                write(TRANSLATOR_INTERFACE_DEFINITION)
                write(DEFAULT_EQUATOR_DEFINITION)
                write(DEFAULT_TRANSLATOR_DEFINITION)
                defined_default_lambdas = True

            lambda_def = line[line.index("=")+1:len(line)].strip()
            lambda_header = lambda_def[0:lambda_def.index("{")+1].strip()
            lambda_body = lambda_def[lambda_def.index("{")+1:lambda_def.index("}")].strip()
            lambda_name = args[1]
            lambda_type = "Equator" if args[0] == "equator" else "Translator"
            lambda_frame = LAMBDA_EQUATOR_DEFINITION if args[0] == "equator" else LAMBDA_TRANSLATOR_DEFINITION
            lambda_frame = lambda_frame[:]

            # Insert the name, header, and body into the lambda declaration
            for i in range(len(lambda_frame)):
                lambda_frame[i] = lambda_frame[i].replace("<NAME>", lambda_name)
                lambda_frame[i] = lambda_frame[i].replace("<HEADER>", lambda_header)
                lambda_frame[i] = lambda_frame[i].replace("<BODY>", lambda_body)

            write(lambda_frame)

            last_parse = "equator"
        # This is an assignment of an equator to a particular test
        else:
            if args[0] == "equator":
                current_equator = args[1]
            else:
                current_translator = args[1]
        continue

    # Testgroup definition
    if args[0] == "testgroup":
        # Conclude the class/state header by writing the main method header
        if not defined_header:
            write("\n")
            write(MAIN_METHOD_DEFINITION + "\n")
            tab_level += 1

            for ref in MAIN_METHOD_REFERENCES:
                write(ref + "\n")

            defined_header = True

        current_testgroup = args[1]
        write("\n")
        write("// " + current_testgroup + " tests\n")
        write("testName = \"" + current_testgroup + "\";\n")
        write("testNum = Math.floor(testNum) + 1;\n")
        continue

    # Individual test definition
    if args[0] == "expected":
        value = line[line.index("=")+1:len(line)].strip()
        write("\n")
        write("expected = " + value + ";\n")
        continue

    if args[0] == "actual":
        method_args = line[line.index("=")+1:len(line)].strip()
        method_call = current_testgroup + "(" + method_args + ")"
        write("actual = " + method_call + ";\n")
        write("runTest(testNum, testName, expected, actual, " + current_equator + ", " + current_translator + ");\n")
        write("testNum += 0.1;\n")

# Add closing brackets
while tab_level > 0:
    tab_level -= 1

    write("}\n")

    # Add runTest method definition after main
    if tab_level == 1:
        write("\n")
        write(RUN_TEST_METHOD_DEFINITION)

SRC.close()
DEST.close()
