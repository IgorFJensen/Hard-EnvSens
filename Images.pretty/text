for item in pcbnew.GetBoard().GetDrawings():
    if item.GetClass() == "PCB_TEXT":
        if item.GetLayer() == pcbnew.F_SilkS:
            item.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(1.0)))
pcbnew.Refresh()
