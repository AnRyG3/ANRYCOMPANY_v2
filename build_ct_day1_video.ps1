$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$Root = (Get-Location).Path
$AssetDir = Join-Path $Root "reel_assets\ct_day1_images_v1"
$OutDir = Join-Path $Root "reel_assets\ct_day1_video_v1"
$FrameDir = Join-Path $OutDir "frames"
$AudioDir = Join-Path $OutDir "audio"
$VideoDir = Join-Path $OutDir "video"
@($OutDir,$FrameDir,$AudioDir,$VideoDir) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

$Ffmpeg = Join-Path $Root "tools\ffmpeg\bin\ffmpeg.exe"
$Voicevox = "http://127.0.0.1:50021"
$Speaker = 8
$W = 1080
$H = 1920

$Cuts = @(
  [PSCustomObject]@{
    image="01_worried_patient_exam_guide.png"
    telop="念のためCT、`n本当に安心？"
    voice="念のためCTを撮っておけば安心。そう思うかたもいるかもしれません。"
  },
  [PSCustomObject]@{
    image="02_ct_monitor_useful_test.png"
    telop="CTは、`nとても優れた検査"
    voice="もちろんCTは、とても優れた検査です。体の中を短時間で詳しく確認できます。"
  },
  [PSCustomObject]@{
    image="03_ct_burden_icons.png"
    telop="でも、`n負担もあります"
    voice="でも、CTには負担もあります。放射線被ばく。検査費用。"
  },
  [PSCustomObject]@{
    image="04_incidental_small_spot_magnified.png"
    telop="小さな影から`n追加検査へ"
    voice="そして、偶然見つかった小さな影をきっかけに、追加検査につながることもあります。"
  },
  [PSCustomObject]@{
    image="05_title_toreba_anshin_toha_kagiranai.png"
    telop=""
    voice="つまりCTは、撮れば必ず安心、という単純なものではありません。大切なのは、検査に目的があること。CTは便利な検査です。だからこそ、必要性を考えて使われます。"
  }
)

function Font($size,$style="Bold") {
  New-Object System.Drawing.Font("Yu Gothic", $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel)
}
function Brush($r,$g,$b,$a=255) {
  New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb($a,$r,$g,$b))
}
function RoundRect($g,$x,$y,$w,$h,$r,$brush) {
  $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $r * 2
  $gp.AddArc($x,$y,$d,$d,180,90); $gp.AddArc($x+$w-$d,$y,$d,$d,270,90)
  $gp.AddArc($x+$w-$d,$y+$h-$d,$d,$d,0,90); $gp.AddArc($x,$y+$h-$d,$d,$d,90,90)
  $gp.CloseFigure(); $g.FillPath($brush,$gp); $gp.Dispose()
}
function CenterText($g,$txt,$x,$y,$w,$h,$font,$brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Center"; $fmt.LineAlignment = "Center"
  $g.DrawString($txt,$font,$brush,(New-Object System.Drawing.RectangleF($x,$y,$w,$h)),$fmt)
  $fmt.Dispose()
}
function FitCover($img,$canvasW,$canvasH) {
  $scale = [Math]::Max($canvasW / $img.Width, $canvasH / $img.Height)
  $nw = [int]($img.Width * $scale); $nh = [int]($img.Height * $scale)
  $x = [int](($canvasW - $nw) / 2); $y = [int](($canvasH - $nh) / 2)
  New-Object System.Drawing.Rectangle($x,$y,$nw,$nh)
}
function Save-TelopFrame($cut,$idx) {
  $src = Join-Path $AssetDir $cut.image
  $file = Join-Path $FrameDir ("day1_cut_{0:D2}.png" -f $idx)
  $bmp = New-Object System.Drawing.Bitmap($W,$H)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = "AntiAlias"
  $g.InterpolationMode = "HighQualityBicubic"
  $g.TextRenderingHint = "AntiAliasGridFit"
  $img = [System.Drawing.Image]::FromFile($src)
  $g.DrawImage($img, (FitCover $img $W $H))

  if ($cut.telop -ne "") {
    $box = Brush 15 23 42 222
    $white = Brush 255 255 255
    RoundRect $g 80 112 920 240 34 $box
    CenterText $g $cut.telop 120 132 840 200 (Font 68) $white
    $box.Dispose(); $white.Dispose()
  }

  $shade = New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Rectangle(0,1560,$W,360)), [System.Drawing.Color]::FromArgb(0,15,23,42), [System.Drawing.Color]::FromArgb(170,15,23,42), 90)
  $g.FillRectangle($shade,0,1560,$W,360)
  $small = Brush 255 255 255 235
  CenterText $g "※個別の判断は医療機関でご相談ください" 70 1810 940 60 (Font 28 "Regular") $small
  $small.Dispose(); $shade.Dispose()

  $bmp.Save($file,[System.Drawing.Imaging.ImageFormat]::Png)
  $img.Dispose(); $g.Dispose(); $bmp.Dispose()
  return $file
}
function Synth-Voicevox($text,$out) {
  $query = Invoke-RestMethod -Method Post -Uri "$Voicevox/audio_query?text=$([uri]::EscapeDataString($text))&speaker=$Speaker"
  $query.speedScale = 1.12
  $query.pitchScale = 0.01
  $query.intonationScale = 1.12
  $query.volumeScale = 1.0
  $query.prePhonemeLength = 0.06
  $query.postPhonemeLength = 0.08
  $json = $query | ConvertTo-Json -Depth 50
  Invoke-WebRequest -Method Post -Uri "$Voicevox/synthesis?speaker=$Speaker" -ContentType "application/json" -Body $json -OutFile $out | Out-Null
}
function Get-Duration($file) {
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  $txt = (& $Ffmpeg -hide_banner -i $file 2>&1 | Out-String)
  $ErrorActionPreference = $oldPreference
  if ($txt -match "Duration:\s*(\d+):(\d+):(\d+\.\d+)") {
    return ([double]$Matches[1] * 3600 + [double]$Matches[2] * 60 + [double]$Matches[3])
  }
  return 4.0
}
function Get-ShortPath($Path) {
  $item=Get-Item -LiteralPath $Path; $fso=New-Object -ComObject Scripting.FileSystemObject
  if($item.PSIsContainer){ return $fso.GetFolder($item.FullName).ShortPath }
  return $fso.GetFile($item.FullName).ShortPath
}

$frames = @()
$segments = @()
for ($i=0; $i -lt $Cuts.Count; $i++) {
  $frames += Save-TelopFrame $Cuts[$i] ($i+1)
  $wav = Join-Path $AudioDir ("voice_{0:D2}.wav" -f ($i+1))
  Synth-Voicevox $Cuts[$i].voice $wav
  $segments += [PSCustomObject]@{ wav=$wav; sec=(Get-Duration $wav) + 0.35 }
}

$concatAudio = Join-Path $AudioDir "voice_concat.txt"
$audioLines = @()
foreach($s in $segments){ $audioLines += "file '$((Get-ShortPath $s.wav).Replace('\','/'))'" }
Set-Content -Path $concatAudio -Value ($audioLines -join "`n") -Encoding ASCII
$voiceAll = Join-Path (Get-ShortPath $AudioDir) "day1_voicevox.wav"
& $Ffmpeg -y -f concat -safe 0 -i (Get-ShortPath $concatAudio) -c copy $voiceAll
if($LASTEXITCODE -ne 0){ throw "voice concat failed" }

$list = Join-Path $VideoDir "frames.txt"
$lines = @()
for($i=0;$i -lt $frames.Count;$i++){
  $lines += "file '$((Get-ShortPath $frames[$i]).Replace('\','/'))'"
  $lines += ("duration {0:N2}" -f $segments[$i].sec)
}
$lines += "file '$((Get-ShortPath $frames[-1]).Replace('\','/'))'"
Set-Content -Path $list -Value ($lines -join "`n") -Encoding ASCII

$silent = Join-Path (Get-ShortPath $VideoDir) "day1_silent.mp4"
$out = Join-Path (Get-ShortPath $VideoDir) "day1_ct_nen_no_tame_voicevox.mp4"
& $Ffmpeg -y -f concat -safe 0 -i (Get-ShortPath $list) -vf "fps=30,format=yuv420p" -c:v libx264 -pix_fmt yuv420p $silent
if($LASTEXITCODE -ne 0){ throw "silent video failed" }
& $Ffmpeg -y -i $silent -i $voiceAll -f lavfi -i "sine=frequency=174.61:duration=90" -f lavfi -i "sine=frequency=220:duration=90" -filter_complex "[2:a]volume=0.018[a2];[3:a]volume=0.012[a3];[a2][a3]amix=inputs=2:duration=first,lowpass=f=850[bgm];[1:a]volume=1.05[voice];[voice][bgm]amix=inputs=2:duration=first[a]" -map "0:v" -map "[a]" -shortest -c:v copy -c:a aac -b:a 192k $out
if($LASTEXITCODE -ne 0){ throw "mux failed" }

Set-Content -Path (Join-Path $OutDir "narration.txt") -Value (($Cuts | ForEach-Object { $_.voice }) -join "`r`n") -Encoding UTF8
Set-Content -Path (Join-Path $OutDir "README.txt") -Value "DAY1 CT video. Minimal telops + VOICEVOX speaker 8. Final: video/day1_ct_nen_no_tame_voicevox.mp4" -Encoding UTF8
Write-Host "Done: $OutDir"




