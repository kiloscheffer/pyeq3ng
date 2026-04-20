"""One-shot fixture generator: runs the current scipy.odr-backed pyeq3
over a spread of fit types and datasets, captures solvedCoefficients
and sum-square residuals to JSON. Test_OdrEquivalence in the port
branch then checks the odrpack-ported code produces matching values.

Delete this file and _odr_baseline_fixture.json along with
Test_OdrEquivalence.py once the port is validated and merged. Leading
underscore keeps RunAllTests.py from auto-discovering it.
"""
import json
import os
import sys

import numpy

# Same path-setup as Test_*.py uses
if os.path.join(sys.path[0][: sys.path[0].rfind(os.sep)], "..") not in sys.path:
    sys.path.append(os.path.join(sys.path[0][: sys.path[0].rfind(os.sep)], ".."))

import pyeq3
import DataForUnitTests


def _fit_odr_2d():
    model = pyeq3.Models_2D.Polynomial.Linear("ODR")
    pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
        DataForUnitTests.asciiDataInColumns_2D, model, False)
    coeffs = pyeq3.solverService().SolveUsingODR(model)
    return model, coeffs


def _fit_odr_3d():
    model = pyeq3.Models_3D.Polynomial.Linear("ODR")
    model.estimatedCoefficients = numpy.array([0.2, -1.0, 1.0])
    pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
        DataForUnitTests.asciiDataInColumns_3D, model, False)
    coeffs = pyeq3.solverService().SolveUsingODR(model)
    return model, coeffs


def _fit_lm_2d_ssqabs():
    model = pyeq3.Models_2D.Polynomial.Linear("SSQABS")
    model.estimatedCoefficients = numpy.array([-4.0, 2.0])
    pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
        DataForUnitTests.asciiDataInColumns_2D, model, False)
    coeffs = pyeq3.solverService().SolveUsingSelectedAlgorithm(
        model, inAlgorithmName="Levenberg-Marquardt")
    return model, coeffs


def _fit_lm_3d_ssqabs():
    model = pyeq3.Models_3D.Polynomial.Linear("SSQABS")
    model.estimatedCoefficients = numpy.array([0.2, -1.0, 1.0])
    pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
        DataForUnitTests.asciiDataInColumns_3D, model, False)
    coeffs = pyeq3.solverService().SolveUsingSelectedAlgorithm(
        model, inAlgorithmName="Levenberg-Marquardt")
    return model, coeffs


CASES = [
    ("poly2D_ODR", _fit_odr_2d),
    ("poly3D_ODR", _fit_odr_3d),
    ("poly2D_SSQABS_LM", _fit_lm_2d_ssqabs),
    ("poly3D_SSQABS_LM", _fit_lm_3d_ssqabs),
]


def _capture(case_name, fit_fn):
    try:
        model, coeffs = fit_fn()
        model.solvedCoefficients = numpy.asarray(coeffs)
        try:
            model.CalculateCoefficientAndFitStatistics()
            cov_beta = (numpy.asarray(model.cov_beta).tolist()
                        if model.cov_beta is not None else None)
        except Exception as e:
            cov_beta = {"error": f"{type(e).__name__}: {e}"}
        return {
            "case": case_name,
            "solvedCoefficients": numpy.asarray(coeffs).tolist(),
            "sum_square_abs": float(
                model.CalculateAllDataFittingTarget(coeffs)),
            "cov_beta": cov_beta,
        }
    except Exception as e:
        return {"case": case_name,
                "error": f"{type(e).__name__}: {e}"}


def main():
    out = []
    for name, fn in CASES:
        entry = _capture(name, fn)
        out.append(entry)
        if "error" in entry:
            print(f"[{name}] FAILED: {entry['error']}")
        else:
            print(f"[{name}] coeffs={entry['solvedCoefficients']}  "
                  f"SSQ={entry['sum_square_abs']:.6g}")

    fixture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "_odr_baseline_fixture.json")
    with open(fixture_path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nWrote {fixture_path} with {len(out)} entries")


if __name__ == "__main__":
    main()
