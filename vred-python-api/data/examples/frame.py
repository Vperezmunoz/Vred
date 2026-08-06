# vrFrame demo
# source: frame.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing frame script!")

newScene()

loadGeometry("$VRED_EXAMPLES/geo/car.osb")

html1="""
<TABLE border="1">
<CAPTION>A TABLE</CAPTION>
<TR><TH>This
<TR><TH>is
<TR><TH>a
<TR><TH>table
</TABLE>
"""

html2="""
<table border="0" width="80" height="40" align="left" cellspacing="0" cellpadding="0">
  <tr>
    <td>
      <font color='ffff00'>Hello World!</font><br>
    </td>
  </tr>
</table>
"""

frame1 = vrFrame(html1, 0.2, 0.4, 0.6, 0.8)
frame2 = vrFrame(html2, 0.1, 0.1, 0.6, 0.5)

class Mover():

    def __init__(self, frame, s):
        self.frame = frame
        x1, y1, x2, y2 = frame.getFrame()
        self.x = x1
        self.y = y1
        self.w = x2 - x1
        self.h = y2 - y1
        self.s = s
        self.sx = s
        self.sy = s
    def move(self):
        self.frame.setFrame(self.x, self.y, self.x + self.w, self.y + self.w)
        self.x += self.sx;
        self.y += self.sy;
        if self.x + self.w > 1.0:
            self.sx = self.sx * -1.0
            self.x += self.sx;
        if self.x < 0.0:
            self.sx = self.sx * -1.0
            self.x += self.sx;
        if self.y + self.h > 1.0:
            self.sy = self.sy * -1.0
            self.y += self.sy;
        if self.y < 0.0:
            self.sy = self.sy * -1.0
            self.y += self.sy;

mover1 = Mover(frame1, 0.001)
mover2 = Mover(frame2, 0.002)

timer = vrTimer(0.01)
timer.connect(mover1.move)
timer.connect(mover2.move)
timer.setActive(true)
