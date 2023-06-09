import preppy

from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.lib.colors import PCMYKColor, toColor, Whiter
from reportlab.lib.validators import Auto
from rlextra.rml2pdf import rml2pdf

from .functions import generate_monthly_insights, generate_time_info, set_metadata
from .log import log, Log
from .enums import Bank


def commit_to_pdf(
    data: dict,
    outfile: str,
    statement: list[dict],
    bank: Bank,
    verbose: bool = False,
):
    data["period"] = generate_time_info(statement)

    if verbose == True:
        data["transactions"] = statement

    colours = {
        "stdFG": "#000000",
        "bannerBG": "#0173B5",
        "bannerFG": "#E8E8E8",
        "tblBG": "#DDDDDD",
        "tblBGAlt": "#F2F2F2",
    }

    match (bank):
        case Bank.SCOTIA:
            bank_info = {"name": "Scotia", "bannerBG": "#EA0E18"}
        case Bank.BMO:
            bank_info = {"name": "BMO", "bannerBG": "#0173B5"}
        case Bank.TD:
            bank_info = {"name": "TD Bank", "bannerBG": "#006E00"}
        case _:
            bank_info = {"name": "", "bannerBG": "#808080"}

    data["bank"] = bank_info
    data["month"] = generate_monthly_insights(data)

    template = preppy.getModule("finance/insight_report.prep")
    rmlText = template.get(data, colours, verbose)

    rml2pdf.go(rmlText, outputFileName=outfile)
    try:
        set_metadata(
            outfile,
            title=f"Transaction Insights",
            subject=f"This document summarizes transactions from ({data['period']['fTrnsDate'].strftime('%b %d, %Y')} to {data['period']['lTrnsDate'].strftime('%b %d, %Y')})",
        )
    except UnicodeDecodeError as error:
        log(Log.WARNING, f"Could not set metadata, reason: {error}")


class AssetPie2dp(_DrawingEditorMixin, Drawing):
    def __init__(self, width=238, height=108, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self._fontName = "Helvetica"
        fontSize = 8
        self._add(self, Pie(), name="pie", validate=None, desc=None)
        self._add(self, Legend(), name="legend", validate=None, desc=None)
        self._colors = [
            PCMYKColor(60, 47, 0, 30),
            PCMYKColor(72, 98, 0, 0),
            PCMYKColor(0, 100, 46, 23),
            PCMYKColor(0, 96, 64, 4),
            PCMYKColor(0, 76, 84, 5),
            PCMYKColor(0, 59, 100, 0),
            PCMYKColor(0, 22, 90, 0),
            PCMYKColor(52, 0, 100, 28),
            PCMYKColor(51, 0, 45, 59),
            PCMYKColor(0, 12, 18, 56),
            PCMYKColor(0, 6, 12, 31),
            PCMYKColor(100, 0, 8, 13),
            PCMYKColor(70, 0, 38, 8),
            PCMYKColor(0, 43, 97, 17),
            PCMYKColor(45, 0, 100, 24),
            PCMYKColor(0, 0, 0, 40),
            PCMYKColor(65, 64, 0, 30),
            PCMYKColor(72, 98, 0, 0, density=50),
            PCMYKColor(0, 100, 46, 23, density=50),
            PCMYKColor(52, 0, 100, 28, density=50),
            PCMYKColor(51, 0, 45, 59, density=50),
            PCMYKColor(70, 0, 38, 8, density=50),
        ]
        self._labels = [
            "a fairly long label",
            "b fairly long label",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j fairly long label",
        ]
        self.width = 238
        self.height = 108
        self.legend.alignment = "right"
        self.legend.fontSize = fontSize
        self.legend.dy = 6.5
        self.legend.yGap = 0
        self.legend.deltay = 10
        self.legend.strokeColor = PCMYKColor(0, 0, 0, 0)
        self.legend.strokeWidth = 0
        self.legend.colorNamePairs = []
        self.legend.dx = 15
        self.legend.variColumn = 1
        self.legend.dxTextSpace = 2
        self.legend.boxAnchor = "e"
        self.legend.x = self.width - 5
        self.legend.y = self.height * 0.5
        self.legend.deltax = 90
        self.legend.columnMaximum = 20
        self.pie.sameRadii = 1
        self.pie.slices.strokeColor = PCMYKColor(0, 0, 0, 0)
        self.pie.slices.strokeWidth = 0.5
        self.pie.width = 230 - 143
        self.pie.x = 15
        self.pie.y = 15
        self.pie.innerRadiusFraction = 0.6
        self.pie.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.pie.slices.fontName = "Helvetica"
        self.pie.slices.fontSize = 6
        self.pie.slices.labelRadius = 1.2
        self.pie.height = self.pie.width
        self.pie.sideLabels = 0
        self._force_100 = 0

    def getContents(self):
        pie = self.pie
        data = [100 * v for v in pie.data]
        total = sum(data)
        ndata = len(data)
        lv = [" %.2f%%" % v for v in data]
        labels = self._labels[:]
        labels += max(len(lv) - len(labels), 0) * [""]
        labels = [lab + lv[i] for i, lab in enumerate(labels)]
        fontName = self._fontName
        legend = self.legend
        legend.fontName = fontName
        colors = list(map(toColor, self._colors))
        ncolors = len(colors)
        colors += [
            Whiter(colors[i % ncolors], 0.7 ** (1 + i // ncolors))
            for i in range(max(ndata - ncolors, 0))
        ]
        for i in range(ndata):
            self.pie.slices[i].fillColor = colors[i]
        for i in range(ndata):
            legend.colorNamePairs.append((colors[i], labels[i]))
        if total < 99.9:
            data.append(100 - total)
        if total < 99.9:
            self.pie.slices[ndata].fillColor = None
        if total < 99.9:
            legend.colorNamePairs.append(
                (Auto(obj=self.pie), "Unknown %.2f%%" % (100 - total))
            )
        self.pie.data = data
        return Drawing.getContents(self)
