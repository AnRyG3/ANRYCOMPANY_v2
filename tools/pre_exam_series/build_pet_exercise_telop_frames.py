from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(r"F:\ANRYCAMPANY")
UNIT=ROOT/'reel_assets'/'pre_exam_series'/'23_pet_exercise_v1'
FONT=ROOT/'reel_assets'/'fonts'/'M_PLUS_Rounded_1c'/'MPLUSRounded1c-Bold.ttf'
OUT=UNIT/'telop'
W,H=1080,1920
BOX={'top':(82,252,998,488),'center':(82,842,998,1078),'bottom':(82,1248,998,1484)}
NAVY=(12,34,64,255); BLUE=(0,112,185,255)
frames=[
('samples/sample_01_hook_after_running_v2.png','telop_01_hook.png',[['明日PETなのに…'],[('ランニング','blue'),'しちゃった']], 'center'),
('images/frame_02_instruction_and_contact.png','telop_02_instruction.png',[['まず'],[('案内書','blue'),'と予約先を確認']], 'center'),
('images/frame_03_exercise_guidance.png','telop_03_guidance.png',[[('前日・当日','blue'),'の激しい運動は'],['案内に従って控える']], 'center'),
('images/frame_04_used_muscles.png','telop_04_fdg.png',[[('使った筋肉','blue'),'に'],['FDGが集まりやすいことも']], 'center'),
('images/frame_05_facility_variation.png', 'telop_05_facility.png',[[('激しい運動','blue'),'の範囲は'],[('施設ごと','blue'),'に異なります']], 'top'),
('images/frame_06_contact_reservation.png','telop_06_contact.png',[[('運動の内容','blue'),'と',('時間','blue'),'を'],[('予約先','blue'),'へ伝えてください']], 'top'),
('samples/sample_02_pet_waiting_rest_v2.png','telop_07_rest.png',[[('注射後','blue'),'も'],['撮影までは安静に']], 'center'),
('images/frame_08_medicine_instruction.png','telop_08_medicine.png',[[('糖尿病薬','blue'),'・',('インスリン','blue'),'は'],[('自己判断','blue'),'で変えない']], 'center'),
('images/frame_09_call_and_confirm.png','telop_09_confirm.png',[['自分を責めず'],[('予約先','blue'),'に確認しましょう']], 'top'),
('images/frame_10_save_checklist_v2.png','telop_10_save.png',[[('検査前日の夜','blue'),'に'],[('保存','blue'),'して見返す']], 'bottom'),
('images/frame_11_save_checklist_background.png','telop_11_checklist.png',[[('確認する','blue'),'のは3つ'],['運動・絶食開始・糖分入り飲み物']], 'center'),
]
def f(size): return ImageFont.truetype(str(FONT),size)
def t(s): return s[0] if isinstance(s,tuple) else s
def draw_telop(img, lines, pos):
 x0,y0,x1,y1=BOX[pos]; layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
 d.rounded_rectangle((x0+8,y0+10,x1+8,y1+10),34,fill=(8,18,32,58)); img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12)))
 d=ImageDraw.Draw(img,'RGBA'); d.rounded_rectangle((x0,y0,x1,y1),34,fill=(255,255,255,179)); d.rounded_rectangle((x0+7,y0+7,x1-7,y1-7),28,outline=(255,255,255,220),width=4)
 font=f(58); gap=15
 def wh(line):
  return sum(d.textbbox((0,0),t(s),font=font)[2] for s in line)
 hs=[d.textbbox((0,0),'あ',font=font)[3] for _ in lines]; y=y0+((y1-y0)-sum(hs)-gap*(len(lines)-1))//2
 for line,h in zip(lines,hs):
  x=x0+((x1-x0)-wh(line))//2
  for s in line:
   text,color=s if isinstance(s,tuple) else (s,NAVY); d.text((x,y),text,font=font,fill=BLUE if color=='blue' else color); x+=d.textbbox((0,0),text,font=font)[2]
  y+=h+gap
def cover(p):
 im=Image.open(p).convert('RGB'); scale=max(W/im.width,H/im.height); im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS); l=(im.width-W)//2; u=(im.height-H)//2; return im.crop((l,u,l+W,u+H)).convert('RGBA')
OUT.mkdir(exist_ok=True)
for source,name,lines,pos in frames:
 im=cover(UNIT/source); draw_telop(im,lines,pos); im.convert('RGB').save(OUT/name,quality=95)
print('created',len(frames),'telop frames')
