from __future__ import annotations
import json, re, subprocess, urllib.parse, urllib.request, wave
from pathlib import Path
ROOT=Path(r'F:\ANRYCAMPANY'); UNIT=ROOT/'reel_assets'/'pre_exam_series'/'23_pet_exercise_v1'
TELOP=UNIT/'telop'; AUDIO=UNIT/'audio'; WORK=UNIT/'_video_work'; VIDEO=UNIT/'video'
FFMPEG=ROOT/'tools'/'ffmpeg'/'bin'/'ffmpeg.exe'; BGM=ROOT/'01_ショート動画_リール_YouTubeShorts'/'インスタリール用'/'BGM フリー素材'/'Kind_Heart.mp3'
VOICEVOX='http://127.0.0.1:50021'; SPEAKER=20; SPEED=1.2; OUT=VIDEO/'PET検査前日の運動_20261005.mp4'
FRAMES=['telop_01_hook.png','telop_02_instruction.png','telop_03_guidance.png','telop_04_fdg.png','telop_05_facility.png','telop_06_contact.png','telop_07_rest.png','telop_08_medicine.png','telop_09_confirm.png','telop_10_save.png','telop_11_checklist.png']
VOICE=[
'明日ペットなのに、今日ランニングしちゃった。',
'まずは案内書を確認して、予約先へ連絡してください。',
'FDGペット、またはペットCTでは、前日と当日の激しい運動を控える案内があります。',
'運動した筋肉に、FDGが集まりやすくなることがあるためです。',
'激しい運動の範囲は、施設によって異なります。',
'運動していたら、内容と時間を予約先へ伝えてください。',
'注射後も、撮影までは施設の案内に沿って安静にします。',
'糖尿病薬やインスリンは、自己判断で変えず、主治医か施設の案内を確認してください。',
'自分を責めず、検査を受けられるかは予約先に確認しましょう。',
'検査前日の夜に見返せるよう、保存しておいてください。',
'確認するのは三つ。運動制限、絶食の開始時刻、糖分入り飲み物です。']
def run(c): subprocess.run([str(x) for x in c],check=True)
def post(path,params=None,payload=None):
 q=urllib.parse.urlencode(params or {}); req=urllib.request.Request(VOICEVOX+path+('?' + q if q else ''),data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),method='POST')
 if payload is not None: req.add_header('Content-Type','application/json')
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()
def synth(text,out):
 q=json.loads(post('/audio_query',{'text':text,'speaker':SPEAKER})); q.update({'speedScale':SPEED,'pitchScale':0,'intonationScale':0.95,'prePhonemeLength':0,'postPhonemeLength':0}); out.write_bytes(post('/synthesis',{'speaker':SPEAKER},q))
def dur(p):
 with wave.open(str(p),'rb') as w:return w.getnframes()/w.getframerate()
def listfile(ps,p):p.write_text(''.join("file '"+x.as_posix()+"'\n" for x in ps),encoding='utf-8')
def main():
 sources=re.findall(r'`([A-Za-z]:\\[^`]+\.png)`',(UNIT/'production_manifest.md').read_text(encoding='utf-8'))[:11]
 outs=[TELOP/x for x in FRAMES]
 if len(sources)!=11 or not all(x.exists() for x in outs):raise RuntimeError('Manifest and telop frames do not map one-to-one.')
 for d in (AUDIO,WORK,VIDEO):d.mkdir(exist_ok=True)
 wavs=[]; segs=[]; cuts=[]; raw=[]
 for i,text in enumerate(VOICE,1):
  w=AUDIO/f'voice_{i:02d}.wav'; synth(text,w); raw.append(dur(w)); cut=raw[-1]+(1.0 if i==len(VOICE) else 0.03); cuts.append(cut); padded=WORK/f'voice_{i:02d}.wav'
  run([FFMPEG,'-y','-i',w,'-af',f'apad=pad_dur={cut:.3f},atrim=duration={cut:.3f}','-ar','44100','-ac','2',padded]); wavs.append(padded)
  s=WORK/f'segment_{i:02d}.mp4';run([FFMPEG,'-y','-loop','1','-t',f'{cut:.3f}','-i',outs[i-1],'-vf','scale=1080:1920,format=yuv420p','-r','30','-c:v','libx264','-tune','stillimage','-pix_fmt','yuv420p',s]);segs.append(s)
 listfile(wavs,WORK/'voice.txt');listfile(segs,WORK/'video.txt');allwav=AUDIO/'voice_all.wav';silent=WORK/'silent.mp4'
 run([FFMPEG,'-y','-f','concat','-safe','0','-i',WORK/'voice.txt','-c','copy',allwav]);run([FFMPEG,'-y','-f','concat','-safe','0','-i',WORK/'video.txt','-c','copy',silent])
 run([FFMPEG,'-y','-i',silent,'-i',allwav,'-stream_loop','-1','-i',BGM,'-filter_complex','[1:a]volume=1.45[v];[2:a]volume=-27dB[b];[v][b]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]','-map','0:v','-map','[a]','-shortest','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT])
 (VIDEO/'video_manifest.json').write_text(json.dumps({'voice_speed':SPEED,'voice_text':VOICE,'telop_frames':[str(x) for x in outs],'source_images':sources,'voice_durations':raw,'cut_durations':cuts,'pacing':'0.03-second tail between cuts; 1.0-second BGM-only final hold','video':str(OUT)},ensure_ascii=False,indent=2),encoding='utf-8-sig')
 print(OUT)
if __name__=='__main__':main()
