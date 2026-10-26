"""Generate original low-volume interface sounds; no third-party samples."""
import math
from pathlib import Path
import struct
import wave

ROOT=Path(__file__).resolve().parents[1]/'src/netwatch_terminal/assets/sounds'
ROOT.mkdir(parents=True,exist_ok=True)
for name,tones in {'boot':[220,330,440,660], 'click':[880,660], 'success':[440,660,880], 'error':[180,130]}.items():
    samples=[]; rate=22050; length=.09 if name!='boot' else .17
    for frequency in tones:
        n=int(rate*length)
        for i in range(n):
            t=i/rate; envelope=min(1,i/100)*((n-i)/n)**2
            value=.22*envelope*(math.sin(2*math.pi*frequency*t)+.15*math.sin(2*math.pi*frequency*2.01*t))
            samples.append(struct.pack('<h',int(value*32767)))
    with wave.open(str(ROOT/(name+'.wav')),'wb') as f:
        f.setparams((1,2,rate,len(samples),'NONE','not compressed')); f.writeframes(b''.join(samples))
