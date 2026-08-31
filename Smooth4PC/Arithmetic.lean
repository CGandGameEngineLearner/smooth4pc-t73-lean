import Mathlib
import Smooth4PC.CertificateData

namespace Smooth4PC

/-- Entry lookup with a zero fallback, using `(row, column)` order. -/
def matrixEntry (matrix : List (List Int)) (row column : Nat) : Int :=
  (matrix.getD row []).getD column 0

/-- Row-major 3 x 3 determinant. Non-3 x 3 inputs return zero. -/
def det3 : List (List Int) → Int
  | [[a, b, c], [d, e, f], [g, h, i]] =>
      a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
  | _ => 0

end Smooth4PC
