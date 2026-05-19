$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$Root = (Get-Location).Path
$OutDir = Join-Path $Root "reel_assets\common"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Out = Join-Path $OutDir "reel_end_card_comment_save_share.png"

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
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Center"
  $fmt.LineAlignment = "Center"
  $g.DrawString($txt, $font, $brush, (New-Object System.Drawing.RectangleF($x, $y, $w, $h)), $fmt)
  $fmt.Dispose()
}

function DrawText($g, [string]$txt, [float]$x, [float]$y, [float]$w, [float]$h, $font, $brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = "Near"
  $fmt.LineAlignment = "Center"
  $g.DrawString($txt, $font, $brush, (New-Object System.Drawing.RectangleF($x, $y, $w, $h)), $fmt)
  $fmt.Dispose()
}

function DrawCommentIcon($g, [float]$x, [float]$y, [string]$hex) {
  $pen = PenC $hex 12
  $g.DrawEllipse($pen, $x, $y, 145, 112)
  $pts = @(
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 48)), ([float]($y + 106))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 28)), ([float]($y + 148))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 85)), ([float]($y + 116)))
  )
  $g.DrawLines($pen, $pts)
}

function DrawBookmarkIcon($g, [float]$x, [float]$y, [string]$hex) {
  $pen = PenC $hex 12
  $pts = @(
    (New-Object System.Drawing.PointF -ArgumentList ([float]$x), ([float]$y)),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 118)), ([float]$y)),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 118)), ([float]($y + 158))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 59)), ([float]($y + 116))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]$x), ([float]($y + 158))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]$x), ([float]$y))
  )
  $g.DrawLines($pen, $pts)
}

function DrawShareIcon($g, [float]$x, [float]$y, [string]$hex) {
  $pen = PenC $hex 12
  $pts = @(
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 10)), ([float]($y + 70))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 160)), ([float]($y + 10))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 105)), ([float]($y + 160))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 76)), ([float]($y + 92))),
    (New-Object System.Drawing.PointF -ArgumentList ([float]($x + 10)), ([float]($y + 70)))
  )
  $g.DrawLines($pen, $pts)
}

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = "AntiAlias"
$g.TextRenderingHint = "AntiAliasGridFit"

$rect = New-Object System.Drawing.Rectangle 0, 0, $W, $H
$bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush $rect, (Color "#fff7cc"), (Color "#e8fff0"), 70
$g.FillRectangle($bg, $rect)
$bg.Dispose()

$stripe = Brush "#ffffff" 54
for ($i=-$H; $i -lt $W; $i += 74) {
  $pen = PenC "#ffffff" 8 48
  $g.DrawLine($pen, $i, 0, $i + $H, $H)
  $pen.Dispose()
}

CenterText $g "見てくれてありがとうございます" 90 190 900 80 (FontJ 42) (Brush "#0f172a")
CenterText $g "次も一緒に学ぼう" 80 275 920 120 (FontJ 72) (Brush "#0f172a")

$cards = @(
  @{ y=510; color="#facc15"; icon="comment"; accent="#111827"; l1="感想・質問を"; l2="コメントしてね！"; hi="コメント" },
  @{ y=840; color="#16a34a"; icon="save"; accent="#16a34a"; l1="保存して"; l2="あとで見返そう！"; hi="保存" },
  @{ y=1170; color="#f43f5e"; icon="share"; accent="#f43f5e"; l1="シェアして"; l2="みんなに教えよう！"; hi="シェア" }
)

foreach ($c in $cards) {
  RoundRect $g 96 $c.y 888 250 36 (Brush "#ffffff" 232)
  RoundRect $g 96 $c.y 18 250 9 (Brush $c.color)
  if ($c.icon -eq "comment") { DrawCommentIcon $g 172 ($c.y + 54) $c.accent }
  if ($c.icon -eq "save") { DrawBookmarkIcon $g 188 ($c.y + 45) $c.accent }
  if ($c.icon -eq "share") { DrawShareIcon $g 170 ($c.y + 47) $c.accent }
  DrawText $g $c.l1 400 ($c.y + 35) 470 82 (FontJ 54) (Brush "#0f172a")
  DrawText $g $c.l2 400 ($c.y + 112) 510 88 (FontJ 48) (Brush "#0f172a")
}

$yellow = PenC "#facc15" 16
$yellow.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$yellow.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$g.DrawLine($yellow, 455, 690, 835, 690)
$green = PenC "#16a34a" 16
$green.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$green.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$g.DrawLine($green, 455, 1020, 832, 1020)
$pink = PenC "#f43f5e" 16
$pink.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$pink.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$g.DrawLine($pink, 455, 1350, 850, 1350)

CenterText $g "気軽に参加してください" 120 1540 840 70 (FontJ 44) (Brush "#334155")
CenterText $g "※個別の医療相談は医療機関へ" 120 1648 840 48 (FontJ 28 "Regular") (Brush "#64748b")

$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Host $Out
