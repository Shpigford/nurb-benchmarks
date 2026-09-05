from nurb import *

@part
def bundle_holder(draft=False):
    """Wall-mount J-channel for a taped cable bundle.

    bundle_diameter (measured): taped bundle diameter the channel is sized for
    """
    D = measured("bundle_diameter")
    t = 3.0
    W = 10.0
    clearance = 1.0
    nub = 0.8
    hole_dia = 4.5

    lip_inner = t + D + clearance
    outer = 2 * t + D + clearance
    lip_top = t + D + clearance
    plate_top = t + D + 13.0
    hole_z = t + D + 7.0
    nub_apex_z = lip_top - nub
    nub_bot_z = lip_top - 2 * nub

    if D < 2.0:
        reject(
            f"bundle_diameter {D} is too small for a printable channel: raise it above 2.0",
            param="bundle_diameter",
        )

    with BuildSketch(Plane.XZ) as profile:
        with BuildLine():
            Polyline(
                (0, 0),
                (outer, 0),
                (outer, lip_top),
                (lip_inner, lip_top),
                (lip_inner - nub, nub_apex_z),
                (lip_inner, nub_bot_z),
                (lip_inner, t),
                (t, t),
                (t, plate_top),
                (0, plate_top),
                close=True,
            )
        make_face()

    body = extrude(profile.sketch, amount=-W)
    hole = Cylinder(hole_dia / 2, t + 2.0)
    hole = Rot(0, 90, 0) * hole
    hole = Pos(t / 2, W / 2, hole_z) * hole
    body = body - hole
    return body
