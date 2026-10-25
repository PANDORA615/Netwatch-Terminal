"""Static HUD geometry; no animation, image assets, or simulated telemetry."""

from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class HudCanvas(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#100F19'))
        painter.setPen(QPen(QColor('#14151E'), 1))
        for y in range(0, self.height(), 4):
            painter.drawLine(0, y, self.width(), y)
        painter.setPen(QPen(QColor('#1C1E26'), 1))
        for x in range(230, self.width(), 72):
            painter.drawLine(x, 0, x, self.height())
        painter.setPen(QPen(QColor('#66703F'), 1))
        painter.drawRect(229, 11, max(0, self.width() - 242), max(0, self.height() - 24))
        painter.setPen(QPen(QColor('#DCFA63'), 3))
        for x, y, dx, dy in ((229, 11, 1, 1), (self.width()-13, 11, -1, 1),
                             (229, self.height()-13, 1, -1),
                             (self.width()-13, self.height()-13, -1, -1)):
            painter.drawLine(x, y, x + dx * 22, y)
            painter.drawLine(x, y, x, y + dy * 22)
        painter.end()
