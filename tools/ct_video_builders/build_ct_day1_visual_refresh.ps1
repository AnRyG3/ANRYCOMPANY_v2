$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$AssetDir = Join-Path $Root "reel_assets\ct_trilogy_v2_voicevox"
$FrameDir = Join-Path $AssetDir "frames\01"
$VideoDir = Join-Path $AssetDir "videos"
$Audio = Join-Path $AssetDir "audio\01_voicevox.wav"
$Ffmpeg = Join-Path $Root "tools\ffmpeg\bin\ffmpeg.exe"
$BackupDir = Join-Path $AssetDir ("frames_backup\01_before_visual_refresh_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
$W = 1080
$H = 1920

New-Item -ItemType Directory -Force -Path $FrameDir, $VideoDir | Out-Null
if (Test-Path -LiteralPath $FrameDir) {
  New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
  Get-ChildItem -LiteralPath $FrameDir -Filter "cut_*.png" -File | Copy-Item -Destination $BackupDir -Force
}

function Color([string]$hex, [int]$a = 255) {
  $h = $hex.TrimStart("#")
  return [System.Drawing.Color]::FromArgb($a, [Convert]::ToInt32($h.Substring(0,2),16), [Convert]::ToInt32($h.Substring(2,2),16), [Convert]::ToInt32($h.Substring(4,2),16))
}

function Brush([string]$hex, [int]$a = 255) { New-Object System.Drawing.SolidBrush (Color $hex $a) }
function PenC([string]$hex, [float]$w = 6, [int]$a = 255) { New-Object System.Drawing.Pen ((Color $hex $a), $w) }
function FontJ([int]$size, [string]$style = "Bold") { New-Object System.Drawing.Font("Yu Gothic", $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel) }

function RoundRect($g, [float]$x, [float]$y, [float]$w, [float]$h, [float]$r, $brush) {
  $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $r * 2
  $gp.AddArc($x, $y, $d, $d, 180, 90)
  $gp.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
  $gp.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
  $gp.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
  $gp.CloseFigure()
  $g.FillPath($brush, $gp)
  $gp.Dispose()
}

function StrokeRoundRect($g, [float]$x, [float]$y, [float]$w, [float]$h, [float]$r, $pen) {
  $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $r * 2
  $gp.AddArc($x, $y, $d, $d, 180, 90)
  $gp.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
  $gp.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
  $gp.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
  $gp.CloseFigure()
  $g.DrawPath($pen, $gp)
  $gp.Dispose()
}

function CenterText($g, [string]$txt, [float]$x, [float]$y, [float]$w, [float]$h, $font, $brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Center"
  $fmt.LineAlignment = "Center"
  $g.DrawString($txt, $font, $brush, (New-Object System.Drawing.RectangleF($x, $y, $w, $h)), $fmt)
  $fmt.Dispose()
}

function LeftText($g, [string]$txt, [float]$x, [float]$y, [float]$w, [float]$h, $font, $brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Near"
  $fmt.LineAlignment = "Center"
  $g.DrawString($txt, $font, $brush, (New-Object System.Drawing.RectangleF($x, $y, $w, $h)), $fmt)
  $fmt.Dispose()
}

function DrawLinearBg($g, [string]$a, [string]$b) {
  $rect = New-Object System.Drawing.Rectangle 0, 0, $W, $H
  $lb = New-Object System.Drawing.Drawing2D.LinearGradientBrush $rect, (Color $a), (Color $b), 58
  $g.FillRectangle($lb, $rect)
  $lb.Dispose()
}

function DrawNoiseDots($g, [int]$count, [string]$hex, [int]$alpha) {
  $rnd = New-Object System.Random 17
  $br = Brush $hex $alpha
  for ($i=0; $i -lt $count; $i++) {
    $x = $rnd.Next(0, $W)
    $y = $rnd.Next(0, $H)
    $s = $rnd.Next(2, 8)
    $g.FillEllipse($br, $x, $y, $s, $s)
  }
  $br.Dispose()
}

function DrawHeader($g, [int]$idx) {
  RoundRect $g 64 72 952 92 46 (Brush "#ffffff" 236)
  CenterText $g "CT、受ける前に知ってほしいこと 01/3" 78 82 924 72 (FontJ 31) (Brush "#0f766e")
  RoundRect $g 126 1700 828 18 9 (Brush "#dbeafe" 210)
  RoundRect $g 126 1700 ([int](828 * $idx / 6)) 18 9 (Brush "#0f766e")
  CenterText $g "※個別の判断は医療機関でご相談ください" 90 1810 900 48 (FontJ 27 "Regular") (Brush "#94a3b8")
}

function Get-ShortPath([string]$Path) {
  $item = Get-Item -LiteralPath $Path
  $fso = New-Object -ComObject Scripting.FileSystemObject
  if ($item.PSIsContainer) { return $fso.GetFolder($item.FullName).ShortPath }
  return $fso.GetFile($item.FullName).ShortPath
}

function DrawBottom($g, [string]$txt) {
  RoundRect $g 96 1342 888 250 30 (Brush "#0f172a" 246)
  CenterText $g $txt 140 1378 800 178 (FontJ 50) (Brush "#ffffff")
}

function DrawCTScanner($g, [float]$cx, [float]$cy, [float]$scale, [bool]$glow = $true) {
  if ($glow) {
    $glowBrush = Brush "#22d3ee" 32
    $g.FillEllipse($glowBrush, $cx - 360*$scale, $cy - 260*$scale, 720*$scale, 520*$scale)
    $glowBrush.Dispose()
  }
  $body = Brush "#f8fafc"
  $edge = PenC "#0f766e" (16*$scale)
  $g.FillEllipse($body, $cx - 270*$scale, $cy - 210*$scale, 540*$scale, 420*$scale)
  $g.DrawEllipse($edge, $cx - 270*$scale, $cy - 210*$scale, 540*$scale, 420*$scale)
  $g.FillEllipse((Brush "#e0f2fe"), $cx - 150*$scale, $cy - 112*$scale, 300*$scale, 224*$scale)
  $g.FillEllipse((Brush "#ffffff"), $cx - 118*$scale, $cy - 82*$scale, 236*$scale, 164*$scale)
  RoundRect $g ($cx - 170*$scale) ($cy + 155*$scale) (340*$scale) (94*$scale) (24*$scale) (Brush "#0f766e")
  CenterText $g "CT" ($cx - 170*$scale) ($cy + 150*$scale) (340*$scale) (98*$scale) (FontJ ([int](54*$scale))) (Brush "#ffffff")
}

function DrawScanScreen($g, [float]$x, [float]$y, [float]$w, [float]$h) {
  RoundRect $g $x $y $w $h 34 (Brush "#0b1120")
  StrokeRoundRect $g $x $y $w $h 34 (PenC "#1e293b" 4)
  for ($i=0; $i -lt 9; $i++) {
    $yy = $y + 75 + $i * 48
    $g.DrawLine((PenC "#134e4a" 2 120), $x + 70, $yy, $x + $w - 70, $yy)
  }
  $g.DrawLine((PenC "#22d3ee" 5), $x + 80, $y + $h * 0.55, $x + $w - 80, $y + $h * 0.55)
  $g.FillEllipse((Brush "#38bdf8"), $x + $w * 0.58, $y + $h * 0.37, 64, 64)
  $g.FillEllipse((Brush "#7dd3fc" 70), $x + $w * 0.58 - 26, $y + $h * 0.37 - 26, 116, 116)
}

function DrawFrame1($g) {
  DrawLinearBg $g "#08111f" "#0f766e"
  DrawNoiseDots $g 140 "#67e8f9" 38
  DrawCTScanner $g 540 760 1.1 $true
  RoundRect $g 76 212 928 300 38 (Brush "#020617" 212)
  CenterText $g "そのCT、`n本当に必要？" 108 224 864 270 (FontJ 82) (Brush "#ffffff")
  RoundRect $g 220 1120 640 130 26 (Brush "#dc2626")
  CenterText $g "念のため が迷いになることも" 244 1130 592 110 (FontJ 42) (Brush "#ffffff")
  DrawBottom $g "撮れば終わり、`nではないことも"
}

function DrawFrame2($g) {
  DrawLinearBg $g "#ecfeff" "#dbeafe"
  RoundRect $g 110 300 860 880 44 (Brush "#ffffff" 245)
  DrawCTScanner $g 540 745 1.05 $false
  $scan = PenC "#22d3ee" 8
  $g.DrawLine($scan, 220, 740, 860, 740)
  $g.FillEllipse((Brush "#22d3ee"), 512, 712, 56, 56)
  CenterText $g "CTはすごく有用" 110 194 860 130 (FontJ 78) (Brush "#0f172a")
  CenterText $g "短時間で体の中を確認できます" 130 1080 820 72 (FontJ 42) (Brush "#334155")
  DrawBottom $g "短時間で体の中を`n確認できます"
}

function DrawFrame3($g) {
  DrawLinearBg $g "#fff7ed" "#fee2e2"
  CenterText $g "でも、負担もある" 90 205 900 128 (FontJ 76) (Brush "#0f172a")
  $items = @(
    @("被ばく", "⚡", "#dc2626"),
    @("費用", "¥", "#d97706"),
    @("偶発所見", "●", "#0f766e"),
    @("追加検査", "+", "#2563eb")
  )
  for ($i=0; $i -lt 4; $i++) {
    $x = 100 + ($i % 2) * 450
    $y = 440 + [Math]::Floor($i / 2) * 330
    RoundRect $g $x $y 430 265 34 (Brush "#ffffff" 246)
    StrokeRoundRect $g $x $y 430 265 34 (PenC $items[$i][2] 5)
    CenterText $g $items[$i][1] $x ($y + 28) 430 86 (FontJ 62) (Brush $items[$i][2])
    CenterText $g $items[$i][0] $x ($y + 120) 430 92 (FontJ 47) (Brush "#0f172a")
  }
  DrawBottom $g "被ばく・費用・`n追加検査"
}

function DrawFrame4($g) {
  DrawLinearBg $g "#e0f2fe" "#f8fafc"
  CenterText $g "小さな影＝病気`nとは限らない" 92 192 896 178 (FontJ 70) (Brush "#0f172a")
  DrawScanScreen $g 138 455 804 580
  RoundRect $g 255 1085 570 102 24 (Brush "#ffffff" 236)
  CenterText $g "偶然見つかる所見もあります" 275 1092 530 84 (FontJ 37) (Brush "#0f172a")
  DrawBottom $g "偶然見つかる所見も`nあります"
}

function DrawFrame5($g) {
  DrawLinearBg $g "#f8fafc" "#dcfce7"
  CenterText $g "撮れば安心、`nとは限らない" 78 192 924 178 (FontJ 72) (Brush "#0f172a")
  RoundRect $g 120 460 840 235 32 (Brush "#dc2626")
  CenterText $g "撮れば安心？" 140 462 800 230 (FontJ 78) (Brush "#ffffff")
  RoundRect $g 120 775 840 235 32 (Brush "#0f766e")
  CenterText $g "目的が大事" 140 776 800 230 (FontJ 82) (Brush "#ffffff")
  $arrow = PenC "#0f172a" 16
  $arrow.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
  $g.DrawLine($arrow, 540, 705, 540, 760)
  DrawBottom $g "大切なのは目的です"
}

function DrawFrame6($g) {
  DrawLinearBg $g "#ecfeff" "#ccfbf1"
  CenterText $g "なぜ撮るのか`nここが大事" 80 194 920 178 (FontJ 72) (Brush "#0f172a")
  CenterText $g "CT" 190 500 700 260 (FontJ 180) (Brush "#0f766e")
  $targetPen = PenC "#0f766e" 10
  $g.DrawEllipse($targetPen, 385, 820, 310, 310)
  $g.DrawEllipse($targetPen, 440, 875, 200, 200)
  $g.DrawEllipse($targetPen, 495, 930, 90, 90)
  $arrow = PenC "#dc2626" 12
  $arrow.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
  $g.DrawLine($arrow, 720, 805, 585, 940)
  RoundRect $g 160 1160 760 108 26 (Brush "#ffffff" 238)
  CenterText $g "なぜ撮るのか" 180 1160 720 108 (FontJ 58) (Brush "#0f172a")
  DrawBottom $g "必要性を考えて使う検査"
}

$drawers = @("DrawFrame1", "DrawFrame2", "DrawFrame3", "DrawFrame4", "DrawFrame5", "DrawFrame6")
$durations = @(3.0, 3.0, 4.2, 4.0, 4.0, 3.6)
$frames = @()
for ($i=0; $i -lt $drawers.Count; $i++) {
  $file = Join-Path $FrameDir ("cut_{0:D2}.png" -f ($i + 1))
  $bmp = New-Object System.Drawing.Bitmap($W, $H)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = "AntiAlias"
  $g.TextRenderingHint = "AntiAliasGridFit"
  & $drawers[$i] $g
  DrawHeader $g ($i + 1)
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose()
  $bmp.Dispose()
  $frames += $file
}

$list = Join-Path $VideoDir "01_frames.txt"
$lines = @()
for ($i=0; $i -lt $frames.Count; $i++) {
  $lines += "file '../frames/01/cut_$('{0:D2}' -f ($i + 1)).png'"
  $lines += ("duration {0:N2}" -f $durations[$i])
}
$lines += "file '../frames/01/cut_06.png'"
[System.IO.File]::WriteAllText($list, ($lines -join "`n"), [System.Text.Encoding]::ASCII)

$out = Join-Path $VideoDir "day1_nen_no_tame_ct_voicevox.mp4"
Push-Location $VideoDir
try {
  & $Ffmpeg -y -f concat -safe 0 -i "01_frames.txt" -vf "fps=30,format=yuv420p" -c:v libx264 -pix_fmt yuv420p "01_silent.mp4"
  if ($LASTEXITCODE -ne 0) { throw "silent video failed" }

  & $Ffmpeg -y -i "01_silent.mp4" -i "../audio/01_voicevox.wav" -f lavfi -i "sine=frequency=174.61:duration=90" -f lavfi -i "sine=frequency=220:duration=90" -filter_complex "[2:a]volume=0.010[a2];[3:a]volume=0.008[a3];[a2][a3]amix=inputs=2:duration=first,lowpass=f=900[bgm];[1:a]volume=1.05[voice];[voice][bgm]amix=inputs=2:duration=first[a]" -map "0:v" -map "[a]" -shortest -c:v copy -c:a aac -b:a 192k "day1_nen_no_tame_ct_voicevox.mp4"
  if ($LASTEXITCODE -ne 0) { throw "audio mux failed" }
}
finally {
  Pop-Location
}

Write-Host "Day1 visual refresh complete"
Write-Host "Frames: $FrameDir"
Write-Host "Video: $out"
Write-Host "Backup: $BackupDir"

