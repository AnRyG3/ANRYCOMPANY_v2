$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$Root = (Get-Location).Path
$OutDir = Join-Path $Root "reel_assets\common"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$W = 1080
$H = 1920

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

function CenterText($g, [string]$txt, [float]$x, [float]$y, [float]$w, [float]$h, $font, $brush) {
  $lines = $txt -split "`n"
  $lineHeight = $font.GetHeight($g) * 1.16
  $totalHeight = $lineHeight * $lines.Count
  $yy = $y + (($h - $totalHeight) / 2)
  foreach ($line in $lines) {
    $size = $g.MeasureString($line, $font)
    $xx = $x + (($w - $size.Width) / 2)
    $g.DrawString($line, $font, $brush, $xx, $yy)
    $yy += $lineHeight
  }
}

function DrawIcon($g, [string]$type, [float]$cx, [float]$cy, [string]$hex) {
  $pen = PenC $hex 18
  if ($type -eq "save") {
    $x = $cx - 85; $y = $cy - 110
    $pts = @(
      (New-Object System.Drawing.PointF -ArgumentList ([float]$x), ([float]$y)),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 170)), ([float]$y)),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 170)), ([float]($y + 220))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 85)), ([float]($y + 160))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]$x), ([float]($y + 220))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]$x), ([float]$y))
    )
    $g.DrawLines($pen, $pts)
  }
  elseif ($type -eq "comment") {
    $g.DrawEllipse($pen, $cx - 118, $cy - 88, 236, 176)
    $pts = @(
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx - 45)), ([float]($cy + 80))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx - 78)), ([float]($cy + 148))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx + 14)), ([float]($cy + 94)))
    )
    $g.DrawLines($pen, $pts)
  }
  else {
    $pts = @(
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx - 120)), ([float]($cy - 10))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx + 115)), ([float]($cy - 110))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx + 34)), ([float]($cy + 132))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx - 12)), ([float]($cy + 25))),
      (New-Object System.Drawing.PointF -ArgumentList ([float]($cx - 120)), ([float]($cy - 10)))
    )
    $g.DrawLines($pen, $pts)
  }
  $pen.Dispose()
}

function DrawVariant([string]$file, [string]$type, [string]$accent, [string]$bgA, [string]$bgB, [string]$small, [string]$main, [string]$sub) {
  $bmp = New-Object System.Drawing.Bitmap($W, $H)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = "AntiAlias"
  $g.TextRenderingHint = "AntiAliasGridFit"

  $rect = New-Object System.Drawing.Rectangle 0, 0, $W, $H
  $bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush $rect, (Color $bgA), (Color $bgB), 70
  $g.FillRectangle($bg, $rect)
  $bg.Dispose()

  for ($i=-$H; $i -lt $W; $i += 74) {
    $pen = PenC "#ffffff" 8 52
    $g.DrawLine($pen, $i, 0, $i + $H, $H)
    $pen.Dispose()
  }

  CenterText $g $small 90 250 900 80 (FontJ 42) (Brush "#0f172a")
  CenterText $g $main 80 385 920 220 (FontJ 82) (Brush "#0f172a")

  RoundRect $g 140 720 800 570 44 (Brush "#ffffff" 244)
  RoundRect $g 140 720 800 20 10 (Brush $accent)
  DrawIcon $g $type 540 930 $accent
  CenterText $g $sub 200 1070 680 145 (FontJ 54) (Brush "#0f172a")
  $line = PenC $accent 18
  $line.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
  $line.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
  $g.DrawLine($line, 300, 1240, 780, 1240)
  $line.Dispose()

  $out = Join-Path $OutDir $file
  $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose()
  $bmp.Dispose()
  Write-Host $out
}

DrawVariant "reel_end_card_save.png" "save" "#16a34a" "#fff7cc" "#e8fff0" "あとで見返せるように" "保存して`nまた見よう" "大事なポイントは`n保存がおすすめ"
DrawVariant "reel_end_card_comment.png" "comment" "#facc15" "#fff7cc" "#fff7ed" "あなたの声も聞かせてください" "感想・質問を`nコメントしてね" "気になったことを`n気軽にどうぞ"
DrawVariant "reel_end_card_share.png" "share" "#f43f5e" "#fff1f2" "#f0f9ff" "知っておくと安心です" "大切な人に`nシェアしよう" "家族や友人にも`n教えてあげてね"
