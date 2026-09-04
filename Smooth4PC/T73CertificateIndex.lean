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

def actualArLinkSha256 : String := "E5CD3C2A2AD0650D061CFB730F54F32C1F2860D2FD0813067550D545D02D2853"
def actualCutTangleSha256 : String := "99D86692B5087AC32C87E7CC56EF0AC79C2A07DA63497066E412CDD440E32CF6"
def actualProductRectanglesSha256 : String := "F2C55E7423EC92521D392ADB3593580266A7ABCDAE786B0F33E24A46606152D9"
def actualLeftoverCirclesSha256 : String := "DF6635022DBB39536041B77D9F14FD0EB78007D70B1722504120B8FB8CE9156F"
def actualGeometricBraidSha256 : String := "DE5FFF008614A73955E71EFA2A2D6C007168E93DCE8C2BC37CDF5CF9CC2CEDD9"
def actualDualDiskMovieSha256 : String := "136C440B149624E7763175D5639695C0BEFD374191E5CE26881ED0B47D362435"
def actualThreeHandleSurfacesSha256 : String := "4860CFDABFE62EF2458130995AA80665D0CB1BC310CCF3DE5DB4B3DF8A118B3C"
def actualSphereSystemSha256 : String := "F1EDF5C0969959CE2D99314EAE48C84C68AA50EB67D1DB8C6319EA2D7FB98163"
def actualHemisphereMoviesSha256 : String := "6BD9F0E816A8D54801BAF6C7F910B81FA16EEFB5AEBFB81ACF208F16A0413E7B"

def linkingM2Ryz : Int := 0

def selectedWicketCount : Nat := 44

def johnsonPsiSupportCount : Nat := 93

def railroadPdCrossingCount : Nat := 1958

def actualProductRectangleCount : Nat := 44
def actualLeftoverCircleCount : Nat := 227
def actualDualDiskFactorCount : Nat := 93
def actualThreeHandleCoreCounts : List Nat := [12578, 1824, 409]
def actualTCancellationBandCount : Nat := 6
def actualXCancellationBandCount : Nat := 1513
def actualW2LasagnaMapVerified : Bool := true

theorem linkingM2Ryz_eq_zero : linkingM2Ryz = 0 := rfl

theorem selectedWicketCount_eq_44 : selectedWicketCount = 44 := rfl

theorem johnsonPsiSupportCount_eq_93 : johnsonPsiSupportCount = 93 := rfl

theorem railroadPdCrossingCount_eq_1958 :
    railroadPdCrossingCount = 1958 :=
  rfl

theorem actualProductRectangleCount_eq_44 : actualProductRectangleCount = 44 := rfl
theorem actualLeftoverCircleCount_eq_227 : actualLeftoverCircleCount = 227 := rfl
theorem actualDualDiskFactorCount_eq_93 : actualDualDiskFactorCount = 93 := rfl
theorem actualThreeHandleCoreCounts_eq :
    actualThreeHandleCoreCounts = [12578, 1824, 409] := rfl
theorem actualTCancellationBandCount_eq_6 : actualTCancellationBandCount = 6 := rfl
theorem actualXCancellationBandCount_eq_1513 : actualXCancellationBandCount = 1513 := rfl
theorem actualW2LasagnaMapVerified_eq_true : actualW2LasagnaMapVerified = true := rfl

end Smooth4PC.T73
