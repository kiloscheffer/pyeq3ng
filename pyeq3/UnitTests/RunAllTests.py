import argparse
import pathlib
import sys
import unittest
import warnings


def _run_strict_prechecks():
    # Runtime-raised warnings: escalate globally so any deprecation triggered by
    # scipy / matplotlib / numpy etc. during tests fails loudly instead of scrolling by.
    warnings.filterwarnings("error", category=DeprecationWarning)
    warnings.filterwarnings("error", category=PendingDeprecationWarning)
    warnings.filterwarnings("error", category=SyntaxWarning)

    # SyntaxWarnings fire at parse time, so already-imported modules won't re-trigger them.
    # Recompile every .py under the repo root to catch invalid escape sequences exhaustively.
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    skip_parts = {".venv", ".git", "build", "pyeq3.egg-info", "__pycache__"}
    failures = []
    for path in repo_root.rglob("*.py"):
        if any(part in skip_parts for part in path.parts):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", SyntaxWarning)
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, SyntaxWarning) as exc:
            failures.append((path, exc))
    if failures:
        print("--strict: source sweep failed:", file=sys.stderr)
        for path, exc in failures:
            print(f"  {path}: {exc}", file=sys.stderr)
        sys.exit(1)


_parser = argparse.ArgumentParser(description="Run all pyeq3 unit tests.")
_parser.add_argument(
    "--strict",
    action="store_true",
    help="Escalate SyntaxWarning, DeprecationWarning, and PendingDeprecationWarning "
    "to errors, and sweep the repo for invalid escape sequences before running tests.",
)
_args, _ = _parser.parse_known_args()

if _args.strict:
    print("RunAllTests: --strict mode (warnings-as-errors + source sweep)", file=sys.stderr)
    _run_strict_prechecks()

import Test_IndividualPolyFunctions
import Test_OutputSourceCodeService
import Test_DataConverterService
import Test_DataCache
import Test_SolverService
import Test_CalculateCoefficientAndFitStatistics
import Test_ModelSolveMethods
import Test_ExtendedVersionHandlers
import Test_Equations
import Test_NIST


# see http://www.voidspace.org.uk/python/articles/
# introduction-to-unittest.shtml#loaders-runners-and-all-that-stuff

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(Test_CalculateCoefficientAndFitStatistics)
suite.addTests(loader.loadTestsFromModule(Test_DataCache))
suite.addTests(loader.loadTestsFromModule(Test_DataConverterService))
suite.addTests(loader.loadTestsFromModule(Test_ExtendedVersionHandlers))
suite.addTests(loader.loadTestsFromModule(Test_IndividualPolyFunctions))
suite.addTests(loader.loadTestsFromModule(Test_ModelSolveMethods))
suite.addTests(loader.loadTestsFromModule(Test_OutputSourceCodeService))
suite.addTests(loader.loadTestsFromModule(Test_SolverService))
suite.addTests(loader.loadTestsFromModule(Test_Equations))
suite.addTests(loader.loadTestsFromModule(Test_NIST))

runner = unittest.TextTestRunner(verbosity=2)

result = runner.run(suite)
