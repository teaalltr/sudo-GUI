from PyQt6.QtGui import QColor, QPalette

def mix(c1: QColor, c2: QColor, frac: float) -> QColor:
    """Return a colour that is `frac`% c1 and (1-frac)% c2 in HSV space."""
    h = c1.hsvHueF()   * frac + c2.hsvHueF()   * (1 - frac)
    s = c1.hsvSaturationF() * frac + c2.hsvSaturationF() * (1 - frac)
    v = c1.valueF()    * frac + c2.valueF()    * (1 - frac)
    out = QColor()
    out.setHsvF(h, s, v)
    return out


def changed_bg(pal: QPalette) -> QColor:
    """Soft highlight for *edited* cells; works for light & dark themes."""
    base  = pal.color(QPalette.ColorRole.Base)
    high  = pal.color(QPalette.ColorRole.Highlight)
    # 85 % base + 15 % highlight → subtle tint
    return mix(high, base, 0.15)


def error_bg(pal: QPalette) -> QColor:
    """Red-ish row background for invalid entries."""
    base = pal.color(QPalette.ColorRole.Base)
    err  = QColor(255, 85, 85)  # a pleasant accessible red
    return mix(err, base, 0.35)
