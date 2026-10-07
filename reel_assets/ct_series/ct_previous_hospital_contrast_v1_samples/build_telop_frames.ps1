param(
    [string]$ProjectDir = 'F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples'
)

Add-Type -AssemblyName System.Drawing

$fontPath = 'F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf'
$fontCollection = New-Object System.Drawing.Text.PrivateFontCollection
$fontCollection.AddFontFile($fontPath)
$fontFamily = $fontCollection.Families[0]

$navy = [System.Drawing.Color]::FromArgb(18, 45, 88)
$blue = [System.Drawing.Color]::FromArgb(43, 108, 176)
$white = [System.Drawing.Color]::FromArgb(179, 255, 255, 255)
$outputDir = Join-Path $ProjectDir 'telop_frames'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function New-RoundedPath {
    param([System.Drawing.RectangleF]$Rect, [single]$Radius)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $diameter = $Radius * 2
    $path.AddArc($Rect.X, $Rect.Y, $diameter, $diameter, 180, 90)
    $path.AddArc($Rect.Right - $diameter, $Rect.Y, $diameter, $diameter, 270, 90)
    $path.AddArc($Rect.Right - $diameter, $Rect.Bottom - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($Rect.X, $Rect.Bottom - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

function Get-FittedFont {
    param($Graphics, $Lines, [int]$ImageWidth)
    $format = New-Object System.Drawing.StringFormat
    $format.FormatFlags = [System.Drawing.StringFormatFlags]::NoClip
    $maximumWidth = $ImageWidth * 0.82
    $size = [int]($ImageWidth * 0.070)
    while ($size -ge 34) {
        $font = New-Object System.Drawing.Font($fontFamily, [single]$size, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
        $widest = 0
        foreach ($line in $Lines) {
            $lineText = ($line | ForEach-Object { $_.Text }) -join ''
            $width = $Graphics.MeasureString($lineText, $font, [System.Drawing.PointF]::Empty, $format).Width
            if ($width -gt $widest) { $widest = $width }
        }
        if ($widest -le $maximumWidth) {
            $format.Dispose()
            return $font
        }
        $font.Dispose()
        $size -= 2
    }
    $format.Dispose()
    return (New-Object System.Drawing.Font($fontFamily, 34, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel))
}

function Draw-CenteredLine {
    param($Graphics, $Chunks, [single]$Y, $Font)
    $format = New-Object System.Drawing.StringFormat
    $format.FormatFlags = [System.Drawing.StringFormatFlags]::NoClip
    $widths = @()
    foreach ($chunk in $Chunks) {
        $widths += $Graphics.MeasureString($chunk.Text, $Font, [System.Drawing.PointF]::Empty, $format).Width
    }
    $x = ($Graphics.VisibleClipBounds.Width - (($widths | Measure-Object -Sum).Sum)) / 2
    for ($i = 0; $i -lt $Chunks.Count; $i++) {
        $brush = New-Object System.Drawing.SolidBrush($(if ($Chunks[$i].Blue) { $blue } else { $navy }))
        $Graphics.DrawString($Chunks[$i].Text, $Font, $brush, [single]$x, $Y, $format)
        $x += $widths[$i]
        $brush.Dispose()
    }
    $format.Dispose()
}

$frames = @(
    @{ Input='sample_01_hook_patient_ct_room.png'; Output='01_hook_patient_ct_room_telop.png'; Lines=@(@(@{Text='前の病院でCTを撮ったのに';Blue=$false}),@(@{Text='また';Blue=$false},@{Text='造影CT';Blue=$true},@{Text='？';Blue=$false})) },
    @{ Input='sample_02_ct_room_injector.png'; Output='02_ct_room_injector_telop.png'; Lines=@(@(@{Text='単純CTだけでは';Blue=$false}),@(@{Text='分からない';Blue=$true},@{Text='ことも';Blue=$false})) },
    @{ Input='scene_03_injector_detail_v2.png'; Output='03_injector_detail_telop.png'; Lines=@(@(@{Text='造影剤で';Blue=$false}),@(@{Text='見え方';Blue=$true},@{Text='が変わる';Blue=$false})) },
    @{ Input='scene_04_ct_room_wide.png'; Output='04_ct_room_wide_telop.png'; Lines=@(@(@{Text='必要な';Blue=$false},@{Text='情報';Blue=$true},@{Text='に応じて';Blue=$false}),@(@{Text='追加することがあります';Blue=$false})) },
    @{ Input='scene_05_patient_waiting.png'; Output='05_patient_waiting_telop.png'; Lines=@(@(@{Text='前のCTがあっても';Blue=$false}),@(@{Text='追加';Blue=$true},@{Text='することがあります';Blue=$false})) },
    @{ Input='scene_06_patient_corridor.png'; Output='06_patient_corridor_telop.png'; Lines=@(@(@{Text='必要かどうかは';Blue=$false}),@(@{Text='医師';Blue=$true},@{Text='が判断します';Blue=$false})) },
    @{ Input='scene_07_patient_reception.png'; Output='07_patient_reception_telop.png'; Lines=@(@(@{Text='造影剤での気分不良は';Blue=$false}),@(@{Text='事前に';Blue=$true},@{Text='伝えて';Blue=$false})) },
    @{ Input='scene_08_patient_ct_room.png'; Output='08_patient_ct_room_telop.png'; Lines=@(@(@{Text='気になることは';Blue=$false}),@(@{Text='検査前に';Blue=$true},@{Text='確認を';Blue=$false})) }
)

foreach ($frame in $frames) {
    $source = Join-Path $ProjectDir $frame.Input
    $image = [System.Drawing.Image]::FromFile($source)
    $bitmap = New-Object System.Drawing.Bitmap($image.Width, $image.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.DrawImage($image, 0, 0, $image.Width, $image.Height)

    $font = @(Get-FittedFont -Graphics $graphics -Lines $frame.Lines -ImageWidth $bitmap.Width)[-1]
    $lineHeight = $font.GetHeight($graphics) * 1.16
    $paddingX = $bitmap.Width * 0.055
    $paddingY = $bitmap.Width * 0.035
    $cardHeight = ($lineHeight * $frame.Lines.Count) + ($paddingY * 2)
    $cardY = ($bitmap.Height - $cardHeight) / 2
    $cardWidth = [single]($bitmap.Width - ($paddingX * 2))
    $card = [System.Drawing.RectangleF]::new([single]$paddingX, [single]$cardY, $cardWidth, [single]$cardHeight)
    $path = New-RoundedPath -Rect $card -Radius ($bitmap.Width * 0.045)
    $backing = New-Object System.Drawing.SolidBrush($white)
    $graphics.FillPath($backing, $path)
    $backing.Dispose()
    $path.Dispose()

    $firstY = $cardY + $paddingY - ($font.GetHeight($graphics) * 0.06)
    for ($i = 0; $i -lt $frame.Lines.Count; $i++) {
        Draw-CenteredLine -Graphics $graphics -Chunks $frame.Lines[$i] -Y ($firstY + ($lineHeight * $i)) -Font $font
    }

    $bitmap.Save((Join-Path $outputDir $frame.Output), [System.Drawing.Imaging.ImageFormat]::Png)
    $font.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
    $image.Dispose()
}

$fontCollection.Dispose()
