-- Generated from the committed E12/E13 certificates.
-- Regenerate with scripts/generate_t73_lean_geometry.py --write; do not edit.

import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-!
Index data for the E12 empty-link reduction and the E13 Johnson CS handle
picture.  These definitions record certificate digests and integer counts.
They do not inhabit `ExternalGeometry`, `CSExternalGeometry`, or
`CSTopologyData`.
-/

def e12S4ReductionSha256 : String :=
  "F402BA82E98238A8990A6B552CDC6B3E9CB4CCB9C35E8AF8895DED14AD3A468D"

def e13CloseSha256 : String :=
  "0EBF95B31ACF84ED33732B089BB79CA3D0503EBDC3B8DBE8D6D95C1FCB120E53"

def e13IdentificationSha256 : String :=
  "9344845E53F50B86C5D1BE297290CCB8FF9A93FB31A9679F99EF315C5A60FDC2"

def e13RailroadPdSha256 : String :=
  "4D1D71FB1B63C5E53C7D0007BD7D5631F00C43996AAD164728F9846A33666C8C"

def e13AlphaMovieSha256 : String :=
  "DBE744C045104CE01860EC925C34A07CCB44C9B398CFB828AFE6562DBE050A19"

def p3FourHandleSha256 : String :=
  "26B5677C5C39A3F39C4D19FCFF015F5AD0FF1102CE1CE447E916ACC8291FAE76"

def linkingM2Ryz : Int := 0

def selectedWicketCount : Nat := 44

def johnsonPsiSupportCount : Nat := 93

def railroadPdCrossingCount : Nat := 1958

theorem linkingM2Ryz_eq_zero : linkingM2Ryz = 0 := rfl

theorem selectedWicketCount_eq_44 : selectedWicketCount = 44 := rfl

theorem johnsonPsiSupportCount_eq_93 : johnsonPsiSupportCount = 93 := rfl

theorem railroadPdCrossingCount_eq_1958 :
    railroadPdCrossingCount = 1958 :=
  rfl

end Smooth4PC.T73
