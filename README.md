# unam.fi.compilers.g5.02 — Hand-crafted Lexical Analyzer

Lexical analyzer (lexer) written in Python **from scratch**, without FLEX or regular-expression libraries, using deterministic finite automaton (DFA) state functions.

- **Course:** Compilers — Facultad de Ingeniería, UNAM
- **Group / Team:** 5 / 02
- **Branch:** `feature/lexer`
- **Recognized tokens:** 40 internal token types, reported in 5 categories: `keyword`, `identifier`, `operator`, `constant`, `punctuation`
- **Error handling:** Panic Mode recovery (multiple lexical errors are reported without stopping the scan)

You can use the lexer in two ways: through the **web interface** (Flask) or through the **command line (CLI)**. If the web interface fails for any reason, the CLI does not need Flask and works on its own (see [Section 4](#4-command-line-fallback-no-web-interface-needed)).

---

## 1. Requirements

| Requirement | Notes |
|---|---|
| Python 3.9 or newer | Tested with Python 3.12 |
| Flask 3.1.3 | **Only** for the web interface. The CLI uses the standard library only. |
| Git | To clone the repository |

---

## 2. Installation

```bash
# 1. Clone the repository and select the lexer branch
git clone -b feature/lexer https://github.com/AnemixHearts/Compilers-Project-ACME.git
cd Compilers-Project-ACME

# 2. (Recommended) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate            # Linux / macOS
# .venv\Scripts\activate             # Windows (cmd / PowerShell)

# 3. Install the dependencies (Flask, needed only for the web interface)
pip install -r requirements.txt

# 4. Move to the project folder that contains the `unam` package
cd MX/UNAM/FI/COMPILER/GP05/develop
```

> **Important:** every command below must be executed from the `develop` folder (step 4).
> The package is named `unam.fi.compilers.g5.02`. Because `02` is not a valid Python identifier for a normal `import`, the modules must be launched with `python -m ...`. Running `python main.py` directly will **not** work.
>
> On Windows, use `py` instead of `python3` if `python3` is not recognized.

---

## 3. Running the web interface

From the `develop` folder:

```bash
python3 -m unam.fi.compilers.g5.02.web.app
```

Then open your browser at:

```
http://127.0.0.1:5000
```

How to use it:

1. Paste or type the source code in the text area.
2. Submit the form.
3. The page shows the token table (token type, category, lexeme, line and column), the symbol table, the lexical errors with their position, and the catalog of the 40 supported tokens.

To stop the server, press `Ctrl + C` in the terminal.

**Quick check:** paste the mandatory reading example below. The result must be **10 tokens** and **0 lexical errors**.

```
printf("This is an example");
int a = 10;
```

### If the web interface does not start

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Flask is not installed in the active environment. Activate the virtual environment and run `pip install -r requirements.txt` from the repository root. |
| `ModuleNotFoundError: No module named 'unam'` | You are not in the `develop` folder. Run `cd MX/UNAM/FI/COMPILER/GP05/develop`. |
| `Address already in use` (port 5000) | Another program is using port 5000 (on macOS it is often *AirPlay Receiver*). Close that program and run the command again. |
| The page does not load in the browser | Check that the terminal shows `Running on http://127.0.0.1:5000` and that you typed the address exactly as shown. |

If none of these solve it, use the CLI described in the next section.

---

## 4. Command-line fallback (no web interface needed)

The CLI does not require Flask. It accepts **one** input source (a string or a file) and an optional output file.

```text
python3 -m unam.fi.compilers.g5.02.main [-s CODE | -f FILE] [-o OUTPUT]
```

| Option | Description |
|---|---|
| `-s`, `--string` | Source code written directly as a string |
| `-f`, `--file` | Path of a source-code file to scan |
| `-o`, `--output` | Optional path where the report is also saved |

`-s` and `-f` are mutually exclusive.

### 4.1 Scan a string

```bash
python3 -m unam.fi.compilers.g5.02.main -s 'printf("This is an example"); int a = 10;'
```

Expected result (the report is printed in Spanish):

```text
- ANALIZADOR LÉXICO -

keyword punctuation constant punctuation punctuation keyword identifier operator constant punctuation

Total de tokens: 10
```

followed by the `DETALLE DE TOKENS` table (token, category, lexeme, line, column) and the `ERRORES LÉXICOS` section, which reports no errors for this input.

### 4.2 Scan a file

Create a text file, for example `examples/reading_example.txt`, with the two reading examples of the project:

```text
printf("This is an example");
int a = 10;
```

and scan it:

```bash
python3 -m unam.fi.compilers.g5.02.main -f examples/reading_example.txt
```

The repository also includes a larger sample, `examples/ejemplo.txt` (29 tokens):

```bash
python3 -m unam.fi.compilers.g5.02.main -f examples/ejemplo.txt
```

> **Windows PowerShell:** quoting double quotes inside `-s '...'` is unreliable in some versions. Use `-f` with a file instead.

### 4.3 Save the report to a file

```bash
python3 -m unam.fi.compilers.g5.02.main -f examples/reading_example.txt -o report.txt
```

### 4.4 Quick test cases

| Input | Command | Expected result |
|---|---|---|
| Keyword `print` | `... main -s 'print'` | 1 token, category `keyword` |
| Case sensitivity | `... main -s 'Print'` | 1 token, category `identifier` |
| Longest match | `... main -s 'printed'` | 1 token, category `identifier` |
| Real number | `... main -s 'x == 3.14'` | 3 tokens: `identifier operator constant` |
| Illegal character | `... main -s '@'` | 0 tokens, 1 lexical error |
| Unclosed string | `... main -s '"abc'` | 0 tokens, 1 lexical error |
| Malformed real | `... main -s '3.'` | 0 tokens, 1 lexical error |
| Panic Mode recovery | `... main -s 'int a=3.; b=! @ $'` | 6 valid tokens and 4 lexical errors (columns 7, 13, 15 and 17) |

(`...` stands for `python3 -m unam.fi.compilers.g5.02`.)

> **Note:** the exit code of the program is `0` even when lexical errors are found. Check the `ERRORES LÉXICOS` section of the report to see them.

---

## 5. Running the unit tests

The tests are launched module by module (not with `pytest`), from the `develop` folder:

```bash
for t in test_40_tokens test_scanner test_dfa test_symtab test_writer \
         test_reader test_reader_scanner test_full_pipeline test_main; do
    echo "== $t"
    python3 -m unam.fi.compilers.g5.02.tests.$t
done
```

---

## 6. Project structure

```text
develop/
├── examples/
│   └── ejemplo.txt                  # Sample source file
└── unam/fi/compilers/g5/02/
    ├── main.py                      # CLI entry point (argparse)
    ├── io/
    │   ├── reader.py                # Reads a string or a UTF-8 file
    │   └── writer.py                # Builds the report and maps 40 token types to 5 categories
    ├── lexer/
    │   ├── scanner.py               # Main scanning loop, line/column tracking, Panic Mode
    │   └── dfa.py                   # DFA state functions (maximal munch)
    ├── models/
    │   └── token.py                 # Immutable Token model and token types
    ├── symbol_table/
    │   └── symtab.py                # Booleans, reserved words and identifiers
    ├── web/
    │   ├── app.py                   # Flask web interface
    │   ├── templates/index.html
    │   └── static/style.css
    └── tests/                       # Unit tests
```

Data flow: raw text → `Reader` → `Scanner` (uses `DFA` and `SymbolTable`) → `Token` objects → `Writer` (CLI report) or `web/app.py` (web page).

---

## 7. Notes

- The web server runs in Flask **debug mode** (`debug=True`). It is meant for local use and the project demonstration only, not for production.
- The report labels (`ANALIZADOR LÉXICO`, `Total de tokens`, `ERRORES LÉXICOS`) are currently printed in Spanish.