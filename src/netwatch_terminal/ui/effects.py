"""Original synthesized audio and a short, skippable HUD entry animation."""
from pathlib import Path
from PySide6.QtCore import QTimer,QUrl,Qt
from PySide6.QtGui import QPainter,QColor,QFont
from PySide6.QtWidgets import QWidget


class Sounds:
    def __init__(self,settings):self.settings=settings; self.effects={}
    def play(self,name):
        if not self.settings.data.get('sound',True):return
        try:
            if name not in self.effects:
                from PySide6.QtMultimedia import QSoundEffect
                effect=QSoundEffect(); effect.setVolume(.22)
                effect.setSource(QUrl.fromLocalFile(str(Path(__file__).resolve().parents[1]/'assets'/'sounds'/f'{name}.wav')))
                self.effects[name]=effect
            effect=self.effects[name]
            if effect.status().name=='Ready': effect.play()
            else:
                def ready():
                    if effect.status().name=='Ready':
                        effect.statusChanged.disconnect(ready)
                        if self.settings.data.get('sound',True):effect.play()
                effect.statusChanged.connect(ready)
        except (ImportError,RuntimeError):pass
    def stop(self):
        for effect in self.effects.values():effect.stop()


class BootOverlay(QWidget):
    def __init__(self,parent):
        super().__init__(parent); self.frame=0; self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setGeometry(parent.rect()); self.show(); self.raise_(); self.setFocus()
        self.timer=QTimer(self); self.timer.timeout.connect(self.advance); self.timer.start(40)
    def advance(self):
        self.frame+=1; self.setGeometry(self.parentWidget().rect()); self.update()
        if self.frame>=32:self.finish()
    def finish(self):
        self.timer.stop(); self.hide(); self.deleteLater()
    def keyPressEvent(self,event):self.finish()
    def mousePressEvent(self,event):self.finish()
    def paintEvent(self,event):
        p=QPainter(self); p.fillRect(self.rect(),QColor('#100f19')); w,h=self.width(),self.height()
        p.setPen(QColor('#263027'))
        for y in range(0,h,4):p.drawLine(0,y,w,y)
        offset=(self.frame%5-2)*5 if self.frame<16 else 0
        font=QFont('monospace'); font.setPixelSize(max(20,min(54,w//20))); font.setBold(True); p.setFont(font)
        p.setPen(QColor('#6a9f91')); p.drawText(self.rect().translated(offset+3,2),Qt.AlignmentFlag.AlignCenter,'NETWATCH // ONLINE')
        p.setPen(QColor('#dcfa63')); p.drawText(self.rect().translated(offset,0),Qt.AlignmentFlag.AlignCenter,'NETWATCH // ONLINE')
        for i in range(5):
            y=(self.frame*29+i*113)%max(1,h)
            p.fillRect(w//6+(i*43)%120,y,w//2,2,QColor('#45532c'))
        p.fillRect(w//4,h*3//4,int(w/2*self.frame/32),4,QColor('#dcfa63'))
        font.setPixelSize(13); p.setFont(font); p.drawText(25,h-30,'INITIALIZING LOCAL INTERFACE   /   ESC: SKIP')
        p.end()
