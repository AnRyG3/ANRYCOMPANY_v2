$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$Root = (Get-Location).Path
$OutDir = Join-Path $Root "reel_assets\ct_trilogy_v2_voicevox"
$FrameDir = Join-Path $OutDir "frames"
$AudioDir = Join-Path $OutDir "audio"
$VideoDir = Join-Path $OutDir "videos"
$DocDir = Join-Path $OutDir "投稿文"
@($OutDir,$FrameDir,$AudioDir,$VideoDir,$DocDir) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
$Ffmpeg = Join-Path $Root "tools\ffmpeg\bin\ffmpeg.exe"
$Voicevox = "http://127.0.0.1:50021"
$Speaker = 8
$W = 1080
$H = 1920

function New-Cut($scene,$telop,$sub,$voice,$sec) {
  [PSCustomObject]@{ scene=$scene; telop=$telop; sub=$sub; voice=$voice; sec=$sec }
}

$Episodes = @(
  [PSCustomObject]@{
    id="01"; file="day1_nen_no_tame_ct_voicevox.mp4"; title="念のためCT"
    caption="「念のためCT」が必ず安心につながるとは限りません。CTは有用な検査ですが、被ばく・費用・偶発所見・追加検査といった負担もあります。大切なのは、検査の目的を理解すること。`n`n#CT検査 #医療知識 #放射線 #健康リテラシー"
    cuts=@(
      (New-Cut "question" "念のためCT、`n本当に安心？" "撮れば終わり、ではないことも" "念のためCT。そう聞くと安心に感じますよね。" 3.0),
      (New-Cut "ctroom" "CTはすごく有用" "短時間で体の中を確認できます" "もちろんCTは、とても優れた検査です。" 3.0),
      (New-Cut "icons" "でも負担もある" "被ばく・費用・追加検査" "でも、放射線被ばく、検査費用、追加検査につながることもあります。" 4.2),
      (New-Cut "finding" "小さな影＝病気`nとは限らない" "偶然見つかる所見もあります" "病気とは限らない小さな異常が、偶然見つかることもあります。" 4.0),
      (New-Cut "decision" "撮れば安心、`nとは限らない" "大切なのは目的です" "CTは、撮れば必ず安心、という単純な検査ではありません。" 4.0),
      (New-Cut "end" "CTは便利。`nだから目的が大事。" "必要性を考えて使う検査" "便利な検査だからこそ、必要性を考えて使われます。" 3.6)
    )
  },
  [PSCustomObject]@{
    id="02"; file="day2_kyukyu_ct_voicevox.mp4"; title="救急のCT"
    caption="CTには放射線被ばくがあります。一方で、救急では診断や治療方針の決定に大きく役立つ場面があります。特に重症外傷や複数損傷が疑われる場合、必要性を判断したうえで全身CTが選択されることがあります。`n`n#CT検査 #救急医療 #外傷 #医療知識"
    cuts=@(
      (New-Cut "ambulance" "救急でCT？" "必要な場面があります" "CTは放射線があるから不安。そう感じるのは自然です。" 3.5),
      (New-Cut "trauma" "重症外傷では`n話が変わる" "複数の損傷が疑われる場合" "でも救急では、CTが診断に大きく役立つ場面があります。" 4.0),
      (New-Cut "bodymap" "頭・胸・お腹・骨盤" "短時間で広く確認" "重症外傷や複数の損傷が疑われる場合、広く確認する全身CTが選ばれることがあります。" 5.0),
      (New-Cut "bleeding" "命に関わる異常を探す" "出血・臓器損傷・骨盤周囲" "頭の出血、胸やお腹の損傷、骨盤まわりの出血を確認するためです。" 4.8),
      (New-Cut "checklist" "全員に撮るわけではない" "状態・年齢・けがの状況で判断" "ただし、すべての外傷で全身CTを撮るわけではありません。" 3.8),
      (New-Cut "end" "必要なCTは、`n命を守る検査" "怖がるだけではなく理解する" "必要な場面では、命を守るための大切な検査です。" 3.4)
    )
  },
  [PSCustomObject]@{
    id="03"; file="day3_ct_mokuteki_voicevox.mp4"; title="CTは目的が大事"
    caption="CTは悪者ではありません。ただし、何となく受ける検査でもありません。必要な場面では強力な検査。大切なのは、必要性や注意点を理解したうえで受けることです。`n`n#CT検査 #医療知識 #健康リテラシー #検査"
    cuts=@(
      (New-Cut "split" "CTは危険？`n撮れば安心？" "どちらも極端です" "CTは危険だからだめ。逆に、CTを撮れば安心。このどちらも極端です。" 4.6),
      (New-Cut "ctroom" "必要な場面では強い" "診断や治療方針に役立つ" "救急や重い症状では、CTが診断や治療方針に大きく役立ちます。" 4.0),
      (New-Cut "icons" "一方で負担もある" "被ばく・費用・偶発所見・追加検査" "一方で、被ばく、費用、偶然見つかる異常、追加検査といった負担もあります。" 4.6),
      (New-Cut "doctor" "怖がるでもなく、`n何となくでもなく" "説明を受けて理解する" "大切なのは、怖がることでも、何となく希望することでもありません。" 4.2),
      (New-Cut "decision" "なぜ撮るのか" "ここが一番大事" "必要性や注意点を理解したうえで受けることです。" 3.4),
      (New-Cut "end" "CTは悪者じゃない" "目的があってこそ意味がある" "CTは悪者ではありません。大切なのは、なぜ撮るのかです。" 3.8)
    )
  }
)

function Font($size,$style="Bold") { New-Object System.Drawing.Font("Yu Gothic", $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel) }
function Brush($r,$g,$b,$a=255) { New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb($a,$r,$g,$b)) }
function PenC($r,$g,$b,$w=6) { New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb($r,$g,$b),$w) }
function CenterText($g,$txt,$x,$y,$w,$h,$font,$brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Center"; $fmt.LineAlignment = "Center"
  $g.DrawString($txt,$font,$brush,(New-Object System.Drawing.RectangleF($x,$y,$w,$h)),$fmt)
  $fmt.Dispose()
}
function LeftText($g,$txt,$x,$y,$w,$h,$font,$brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Near"; $fmt.LineAlignment = "Center"
  $g.DrawString($txt,$font,$brush,(New-Object System.Drawing.RectangleF($x,$y,$w,$h)),$fmt)
  $fmt.Dispose()
}
function RoundRect($g,$x,$y,$w,$h,$r,$brush) {
  $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d=$r*2
  $gp.AddArc($x,$y,$d,$d,180,90); $gp.AddArc($x+$w-$d,$y,$d,$d,270,90)
  $gp.AddArc($x+$w-$d,$y+$h-$d,$d,$d,0,90); $gp.AddArc($x,$y+$h-$d,$d,$d,90,90)
  $gp.CloseFigure(); $g.FillPath($brush,$gp); $gp.Dispose()
}
function Draw-Bg($g,$tone) {
  $c1=[System.Drawing.Color]::FromArgb(248,250,252); $c2=[System.Drawing.Color]::FromArgb(207,250,254)
  if ($tone -eq "dark") { $c1=[System.Drawing.Color]::FromArgb(15,23,42); $c2=[System.Drawing.Color]::FromArgb(20,83,99) }
  $lb=New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Rectangle(0,0,$W,$H)),$c1,$c2,55)
  $g.FillRectangle($lb,0,0,$W,$H); $lb.Dispose()
}
function Draw-Scene($g,$scene) {
  $white=Brush 255 255 255; $ink=Brush 15 23 42; $teal=Brush 15 118 110; $red=Brush 220 38 38; $blue=Brush 37 99 235; $gray=Brush 100 116 139; $pale=Brush 224 242 254
  switch ($scene) {
    "question" { RoundRect $g 170 410 740 740 40 $white; CenterText $g "？" 170 500 740 360 (Font 260) $teal; CenterText $g "安心のつもりが`n迷いになることも" 210 900 660 150 (Font 44) $ink }
    "ctroom" { RoundRect $g 150 430 780 610 40 $white; $g.FillEllipse($pale,265,505,550,360); $g.FillEllipse($white,355,565,370,240); $g.DrawEllipse((PenC 15 118 110 18),265,505,550,360); RoundRect $g 380 835 320 95 24 (Brush 15 118 110); CenterText $g "CT" 380 830 320 100 (Font 54) $white }
    "icons" { $labels=@("被ばく","費用","偶発所見","追加検査"); for($i=0;$i -lt 4;$i++){ $x=130+($i%2)*420; $y=470+[Math]::Floor($i/2)*330; RoundRect $g $x $y 360 250 28 $white; CenterText $g @("⚡","¥","●","+")[$i] $x ($y+25) 360 90 (Font 60) $teal; CenterText $g $labels[$i] $x ($y+115) 360 80 (Font 42) $ink } }
    "finding" { RoundRect $g 170 450 740 520 32 (Brush 15 23 42); $g.DrawLine((PenC 34 211 238 4),230,720,850,720); $g.FillEllipse((Brush 56 189 248),590,640,62,62); CenterText $g "小さな影" 170 1010 740 90 (Font 56) $ink }
    "decision" { RoundRect $g 135 470 810 220 30 (Brush 220 38 38); CenterText $g "撮れば安心？" 135 470 810 220 (Font 70) $white; RoundRect $g 135 760 810 220 30 (Brush 15 118 110); CenterText $g "目的が大事" 135 760 810 220 (Font 72) $white }
    "ambulance" { RoundRect $g 130 590 820 300 34 $white; RoundRect $g 210 660 430 150 20 (Brush 239 68 68); RoundRect $g 640 700 180 110 14 (Brush 37 99 235); CenterText $g "救急" 230 665 380 130 (Font 70) $white; $g.FillEllipse($ink,260,835,90,90); $g.FillEllipse($ink,710,835,90,90) }
    "trauma" { CenterText $g "!" 360 420 360 360 (Font 260) $red; RoundRect $g 185 850 710 170 28 $white; CenterText $g "重症外傷・複数損傷" 185 850 710 170 (Font 56) $ink }
    "bodymap" { $g.FillEllipse($pale,455,430,170,170); RoundRect $g 405 620 270 510 120 $white; $g.DrawRectangle((PenC 15 118 110 8),445,700,190,95); $g.DrawRectangle((PenC 15 118 110 8),430,830,220,125); $g.DrawRectangle((PenC 15 118 110 8),450,990,180,90); CenterText $g "頭  胸  腹  骨盤" 130 1200 820 80 (Font 50) $ink }
    "bleeding" { RoundRect $g 160 440 760 590 30 (Brush 255 255 255); for($i=0;$i -lt 7;$i++){ $g.FillEllipse($red, (230+$i*85), (570+($i%3)*95), 52, 52) }; CenterText $g "見逃せない出血を探す" 160 1080 760 90 (Font 54) $ink }
    "checklist" { $items=@("状態","年齢","けがの状況"); for($i=0;$i -lt 3;$i++){ RoundRect $g 180 (480+$i*210) 720 150 26 $white; CenterText $g "✓" 210 (500+$i*210) 110 100 (Font 58) $teal; LeftText $g $items[$i] 350 (495+$i*210) 480 110 (Font 54) $ink } }
    "split" { RoundRect $g 80 470 430 420 30 (Brush 220 38 38); RoundRect $g 570 470 430 420 30 (Brush 37 99 235); CenterText $g "危険？" 80 470 430 420 (Font 70) $white; CenterText $g "安心？" 570 470 430 420 (Font 70) $white; CenterText $g "どちらも極端" 120 1010 840 90 (Font 58) $ink }
    "doctor" { RoundRect $g 150 470 330 520 34 $white; RoundRect $g 600 470 330 520 34 $white; $g.FillEllipse($pale,245,540,130,130); $g.FillEllipse($pale,695,540,130,130); CenterText $g "説明" 150 760 330 100 (Font 56) $teal; CenterText $g "理解" 600 760 330 100 (Font 56) $blue; $g.DrawLine((PenC 15 118 110 10),500,720,580,720) }
    default { CenterText $g "CT" 200 520 680 280 (Font 180) $teal; RoundRect $g 150 950 780 120 24 $white; CenterText $g "なぜ撮るのか" 150 950 780 120 (Font 58) $ink }
  }
}
function Save-Frame($ep,$cut,$idx,$total) {
  $dir=Join-Path $FrameDir $ep.id; New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $file=Join-Path $dir ("cut_{0:D2}.png" -f $idx)
  $bmp=New-Object System.Drawing.Bitmap($W,$H)
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode="AntiAlias"; $g.TextRenderingHint="AntiAliasGridFit"
  Draw-Bg $g "light"; Draw-Scene $g $cut.scene
  $white=Brush 255 255 255; $ink=Brush 15 23 42; $teal=Brush 15 118 110; $muted=Brush 71 85 105; $dark=Brush 15 23 42
  RoundRect $g 70 86 940 82 41 $white
  CenterText $g "CT、受ける前に知ってほしいこと $($ep.id)/3" 80 88 920 78 (Font 32) $teal
  CenterText $g $cut.telop 80 190 920 220 (Font 72) $ink
  RoundRect $g 112 1345 856 245 30 $dark
  CenterText $g $cut.sub 160 1374 760 180 (Font 50) $white
  RoundRect $g 125 1700 830 18 9 (Brush 219 234 254)
  RoundRect $g 125 1700 ([int](830*$idx/$total)) 18 9 $teal
  CenterText $g "※個別の判断は医療機関でご相談ください" 80 1810 920 50 (Font 28 "Regular") $muted
  $bmp.Save($file,[System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  return $file
}
function Synth-Voicevox($text,$out) {
  $q = Invoke-RestMethod -Method Post -Uri "$Voicevox/audio_query?text=$([uri]::EscapeDataString($text))&speaker=$Speaker"
  $q.speedScale = 1.14; $q.pitchScale = 0.01; $q.intonationScale = 1.12; $q.volumeScale = 1.0; $q.prePhonemeLength = 0.08; $q.postPhonemeLength = 0.08
  $json = $q | ConvertTo-Json -Depth 50
  Invoke-WebRequest -Method Post -Uri "$Voicevox/synthesis?speaker=$Speaker" -ContentType "application/json" -Body $json -OutFile $out | Out-Null
}
function Get-ShortPath($Path) {
  $item=Get-Item -LiteralPath $Path; $fso=New-Object -ComObject Scripting.FileSystemObject
  if($item.PSIsContainer){ return $fso.GetFolder($item.FullName).ShortPath }
  return $fso.GetFile($item.FullName).ShortPath
}

$Manifest=@()
foreach($ep in $Episodes){
  $frames=@(); for($i=0;$i -lt $ep.cuts.Count;$i++){ $frames += Save-Frame $ep $ep.cuts[$i] ($i+1) $ep.cuts.Count }
  $script = ($ep.cuts | ForEach-Object { $_.voice }) -join "`r`n"
  Set-Content -Path (Join-Path $DocDir "$($ep.id)_voicevox_script.txt") -Value $script -Encoding UTF8
  Set-Content -Path (Join-Path $DocDir "$($ep.id)_caption.txt") -Value $ep.caption -Encoding UTF8
  $wav=Join-Path $AudioDir "$($ep.id)_voicevox.wav"; Synth-Voicevox $script $wav
  $list=Join-Path $VideoDir "$($ep.id)_frames.txt"; $lines=@()
  for($i=0;$i -lt $frames.Count;$i++){ $lines += "file '$((Get-ShortPath $frames[$i]).Replace('\','/'))'"; $lines += ("duration {0:N2}" -f $ep.cuts[$i].sec) }
  $lines += "file '$((Get-ShortPath $frames[-1]).Replace('\','/'))'"; Set-Content -Path $list -Value ($lines -join "`n") -Encoding ASCII
  $silent=Join-Path (Get-ShortPath $VideoDir) "$($ep.id)_silent.mp4"; $out=Join-Path (Get-ShortPath $VideoDir) $ep.file
  & $Ffmpeg -y -f concat -safe 0 -i (Get-ShortPath $list) -vf "fps=30,format=yuv420p" -c:v libx264 -pix_fmt yuv420p $silent
  if($LASTEXITCODE -ne 0){ throw "silent video failed $($ep.id)" }
  $wavShort=Get-ShortPath $wav
  & $Ffmpeg -y -i $silent -i $wavShort -f lavfi -i "sine=frequency=174.61:duration=90" -f lavfi -i "sine=frequency=220:duration=90" -filter_complex "[2:a]volume=0.010[a2];[3:a]volume=0.008[a3];[a2][a3]amix=inputs=2:duration=first,lowpass=f=900[bgm];[1:a]volume=1.05[voice];[voice][bgm]amix=inputs=2:duration=first[a]" -map "0:v" -map "[a]" -shortest -c:v copy -c:a aac -b:a 192k $out
  if($LASTEXITCODE -ne 0){ throw "audio mux failed $($ep.id)" }
  $Manifest += [PSCustomObject]@{ id=$ep.id; video=(Join-Path $VideoDir $ep.file); voice=$wav; caption=(Join-Path $DocDir "$($ep.id)_caption.txt") }
}
$Manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $OutDir "manifest.json") -Encoding UTF8
Set-Content -Path (Join-Path $OutDir "README.txt") -Encoding UTF8 -Value "VOICEVOX v2 CT trilogy. Speaker: 春日部つむぎ style id 8. videos folder contains final MP4 files."
Write-Host "Done: $OutDir"

