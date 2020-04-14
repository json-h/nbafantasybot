def formatFloat(flt):
    if flt.startswith("0."):
        return flt[1:5]
    else:
        return flt + "00"