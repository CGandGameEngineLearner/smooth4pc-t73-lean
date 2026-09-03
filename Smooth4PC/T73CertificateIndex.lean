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
  "E7EB5367D63B0D590F850CFAF8878BFBE9094AB98669AD2FD5384E6CD4885069"

def e13CloseSha256 : String :=
  "42309427FB78FCFD3208E7F9537C2C7B2B3AFF5484D9E373A69336ABB856B00F"

def e13IdentificationSha256 : String :=
  "F497862B2E116D2993C721FB92979A0AD45ACA9E69863AF6B6DD3B910C859F0F"

def e13RailroadPdSha256 : String :=
  "E8C0B066D2FC2C7CD01C58BEE404B8063C72C6D7D3E2A937FE3ED99D9298F92A"

def e13AlphaMovieSha256 : String :=
  "DBE744C045104CE01860EC925C34A07CCB44C9B398CFB828AFE6562DBE050A19"

def p3FourHandleSha256 : String :=
  "B9ED5F7122D69D623F179089EE76B95468EA481863F04C270227E251EE07C7B2"

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
