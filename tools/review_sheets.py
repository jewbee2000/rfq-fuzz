"""Contact sheets of actual exported PNG regions for retained visual QA."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw

p=argparse.ArgumentParser();p.add_argument("public");p.add_argument("out");p.add_argument("--batch",type=int,default=6);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
files=sorted(Path(a.public).glob("*/drawing.png"))
for index in range(0,len(files),a.batch):
    selected=files[index:index+a.batch];sheet=Image.new("RGB",(2400,1350*((len(selected)+1)//2)),"#edf1f5");draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(selected):
        with Image.open(path) as original:
            # Canonical authored annotation region, cropped from actual shipped
            # PDF-derived PNG. Never a redraw from metadata or expected values.
            crop=original.crop((1110,275,2310,1575))
        x=(j%2)*1200;y=(j//2)*1350
        sheet.paste(crop,(x,y+40));draw.text((x+20,y+10),path.parent.name,fill="black")
    sheet.save(out/f"annotations-{index//a.batch+1:02}.png")
print(f"{len(files)} actual drawing annotation regions in {(len(files)+a.batch-1)//a.batch} sheets")
