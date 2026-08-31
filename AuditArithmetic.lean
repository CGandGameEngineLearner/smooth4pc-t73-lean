import Smooth4PC.Arithmetic

namespace Smooth4PC

theorem exactData_matrixA :
    matrixA = [[0, 269, 1240], [0, 41, 189], [1, 0, 32]] := by
  norm_num [matrixA]

theorem exactData_matrixAMinusI :
    matrixAMinusI = [[-1, 269, 1240], [0, 40, 189], [1, 0, 31]] := by
  norm_num [matrixAMinusI]

theorem exactData_sphereColumns :
    sphereColumns = [[-1311, 8608, -1], [-189, 1241, 0], [41, -269, 1]] := by
  norm_num [sphereColumns]

theorem exactData_oneHandleActualCapH3 : oneHandleActualCapH3 = -59072 := by
  norm_num [oneHandleActualCapH3]

theorem exactData_degree : degree = [0, 494] := by
  norm_num [degree]

theorem exactData_detAExpected : detAExpected = 1 := by
  norm_num [detAExpected]

theorem exactData_detAMinusIExpected : detAMinusIExpected = 1 := by
  norm_num [detAMinusIExpected]

theorem exactData_sphereDetExpected : sphereDetExpected = 1 := by
  norm_num [sphereDetExpected]

theorem exactData_th1Sigma0Scalar : th1Sigma0Scalar = 0 := by
  norm_num [th1Sigma0Scalar]

theorem exactData_th1Sigma1MinusIdScalar : th1Sigma1MinusIdScalar = 0 := by
  norm_num [th1Sigma1MinusIdScalar]

theorem exactData_th2Sigma0Scalar : th2Sigma0Scalar = 0 := by
  norm_num [th2Sigma0Scalar]

theorem exactData_th2Sigma1MinusIdScalar : th2Sigma1MinusIdScalar = 0 := by
  norm_num [th2Sigma1MinusIdScalar]

theorem exactData_thxySigma0Scalar : thxySigma0Scalar = 0 := by
  norm_num [thxySigma0Scalar]

theorem exactData_thxySigma1MinusIdScalar : thxySigma1MinusIdScalar = 0 := by
  norm_num [thxySigma1MinusIdScalar]

theorem matrixA_rowMajor_entry_0_1 : matrixEntry matrixA 0 1 = 269 := by
  norm_num [matrixEntry, matrixA]

theorem det_matrixA_eq_one : det3 matrixA = 1 := by
  norm_num [det3, matrixA]

theorem det_matrixAMinusI_eq_one : det3 matrixAMinusI = 1 := by
  norm_num [det3, matrixAMinusI]

theorem det_sphereColumns_eq_one : det3 sphereColumns = 1 := by
  norm_num [det3, sphereColumns]

theorem cubic_factor_times_epsilon_eq_h3 :
    (-8 : Int) * 7384 = oneHandleActualCapH3 := by
  norm_num [oneHandleActualCapH3]

theorem oneHandleActualCapH3_ne_zero : oneHandleActualCapH3 ≠ 0 := by
  norm_num [oneHandleActualCapH3]

theorem th1Sigma0_eq_zero : th1Sigma0Scalar = 0 := by
  norm_num [th1Sigma0Scalar]

theorem th1Sigma1MinusId_eq_zero : th1Sigma1MinusIdScalar = 0 := by
  norm_num [th1Sigma1MinusIdScalar]

theorem th2Sigma0_eq_zero : th2Sigma0Scalar = 0 := by
  norm_num [th2Sigma0Scalar]

theorem th2Sigma1MinusId_eq_zero : th2Sigma1MinusIdScalar = 0 := by
  norm_num [th2Sigma1MinusIdScalar]

theorem thxySigma0_eq_zero : thxySigma0Scalar = 0 := by
  norm_num [thxySigma0Scalar]

theorem thxySigma1MinusId_eq_zero : thxySigma1MinusIdScalar = 0 := by
  norm_num [thxySigma1MinusIdScalar]

theorem degree_subtraction_eq_494 : (498 : Int) - 4 = 494 := by
  norm_num

theorem degree_494_ne_zero : (494 : Int) ≠ 0 := by
  norm_num

theorem certificate_degree_eq : degree = [0, 494] := by
  norm_num [degree]

end Smooth4PC
