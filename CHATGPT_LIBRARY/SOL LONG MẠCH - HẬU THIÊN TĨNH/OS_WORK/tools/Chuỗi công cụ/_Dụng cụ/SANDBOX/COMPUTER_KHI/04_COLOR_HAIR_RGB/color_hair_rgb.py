#!/usr/bin/env python3
"""Color Hail: hair tone code + numerical sRGB/Lab diagnostics, no dye simulation."""
from __future__ import annotations
import argparse,colorsys,json,math,re

TONE={0:'NATURAL',1:'ASH',2:'VIOLET',3:'GOLD',4:'COPPER',5:'MAHOGANY',6:'RED'}
AXES={'SPACE_SOUL':['BLUE','ORANGE'],'MIND_POWER':['YELLOW','VIOLET'],'REALITY_TIME':['RED','GREEN']}

def parse_hair_code(code):
    m=re.fullmatch(r'(10|[1-9])\.([0-6])([0-6])',code)
    if not m:raise ValueError('Must be LEVEL.MAINREFLECTION e.g. 4.32 (LEVEL 1..10, tone digits 0..6)')
    lvl,main,secondary=map(int,m.groups())
    return {'code':code,'level':lvl,'main_tone':TONE[main],'secondary_tone':TONE[secondary],
       'note':'hair level/tone notation; does NOT mathematically determine monitor RGB'}

def parse_hex(x):
    m=re.fullmatch(r'#?([A-Fa-f0-9]{6})',x)
    if not m:raise ValueError('hex must be exactly RRGGBB or #RRGGBB')
    v=m.group(1);return tuple(int(v[i:i+2],16) for i in (0,2,4))

def lin(t):
    t=t/255.0
    return t/12.92 if t<=0.04045 else ((t+0.055)/1.055)**2.4

def xyz(rgb):
    r,g,b=[lin(z) for z in rgb]
    return (100*(.4124564*r+.3575761*g+.1804375*b),
            100*(.2126729*r+.7151522*g+.0721750*b),
            100*(.0193339*r+.1191920*g+.9503041*b))

def lab(rgb):
    X,Y,Z=xyz(rgb);xr,yr,zr=X/95.047,Y/100,Z/108.883
    def f(t):return t**(1/3) if t>0.008856451679 else t/(3*(6/29)**2)+4/29
    x,y,z=map(f,(xr,yr,zr));return (116*y-16,500*(x-y),200*(y-z))

def describe(rgb):
    rf,gf,bf=(x/255 for x in rgb)
    h,s,v=colorsys.rgb_to_hsv(rf,gf,bf);h2,l,s2=colorsys.rgb_to_hls(rf,gf,bf)
    return {'RGB_8bit':list(rgb),'HEX':'#'+''.join(f'{x:02X}' for x in rgb),
      'HSV':{'H_degrees':round(h*360,4),'S_percent':round(s*100,4),'V_percent':round(v*100,4)},
      'HSL':{'H_degrees':round(h2*360,4),'S_percent':round(s2*100,4),'L_percent':round(l*100,4)},
      'CIE_Lab_D65_sRGB':[round(x,5) for x in lab(rgb)], 'CIE_XYZ_D65':[round(x,5) for x in xyz(rgb)],
      'assumption':'sRGB IEC 61966-2-1 white D65; display RGB is not physical dye mixture'}

def delta_E76(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(lab(a),lab(b))))

def main():
    p=argparse.ArgumentParser(description='RGB ↔ hair code evidence parser')
    p.add_argument('--hex',default=None)
    p.add_argument('--compare-hex',default=None)
    p.add_argument('--hair-code',default=None)
    args=p.parse_args()
    out={'axes':AXES,'tone_map':TONE}
    if args.hair_code:out['hair_tone']=parse_hair_code(args.hair_code)
    if args.hex:out['source_color']=describe(parse_hex(args.hex))
    if args.compare_hex:
        if not args.hex:p.error('--compare-hex requires --hex')
        out['comparison_color']=describe(parse_hex(args.compare_hex))
        out['DeltaE_1976']=round(delta_E76(parse_hex(args.hex),parse_hex(args.compare_hex)),4)
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
