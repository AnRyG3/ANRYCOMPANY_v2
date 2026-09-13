param(
    [string]$ProjectDir = 'F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_aftercare_phone_v1_samples'
)

Add-Type -AssemblyName System.Drawing

$fontPath = 'F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf'
$fontCollection = New-Object System.Drawing.Text.PrivateFontCollection
$fontCollection.AddFontFile($fontPath)
$fontFamily = $fontCollection.Families[0]

$navy = [System.Drawing.Color]::FromArgb(18, 45, 88)
$blue = [System.Drawing.Color]::FromArgb(43, 108, 176)
$white = [System.Drawing.Color]::FromArgb(230, 255, 255, 255)
$outputDir = Join-Path $ProjectDir 'telop_frames_mplus'
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
    $size = [int]($ImageWidth * 0.072)
    while ($size -ge 34) {
        $font = New-Object System.Drawing.Font($fontFamily, [single]$size, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
        $widest = 0
        foreach ($line in $Lines) {
            $lineText = ($line | ForEach-Object { $_.Text }) -join ''
            $measured = $Graphics.MeasureString($lineText, $font, [System.Drawing.PointF]::Empty, $format).Width
            if ($measured -gt $widest) { $widest = $measured }
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
        $color = if ($Chunks[$i].Blue) { $blue } else { $navy }
        $brush = New-Object System.Drawing.SolidBrush($color)
        $Graphics.DrawString($Chunks[$i].Text, $Font, $brush, [single]$x, $Y, $format)
        $x += $widths[$i]
        $brush.Dispose()
    }
    $format.Dispose()
}

$frames = @(
    @{ Input='sample_s01_home_question.png'; Output='s01_home_question_telop.png'; Position='bottom'; Lines=@(@(@{Text='造影検査のあと';Blue=$false}),@(@{Text='家で気分が悪い';Blue=$false}),@(@{Text='電話';Blue=$true},@{Text='していい？';Blue=$false})) },
    @{ Input='s02_mild_fatigue_home.png'; Output='s02_mild_fatigue_telop.png'; Position='top'; Lines=@(@(@{Text='帰宅後';Blue=$false}),@(@{Text='なんとなく';Blue=$false},@{Text='だるい';Blue=$true})) },
    @{ Input='sample_s03_call_facility.png'; Output='s03_call_facility_telop.png'; Position='top'; Lines=@(@(@{Text='気になる変化は';Blue=$false}),@(@{Text='施設へ';Blue=$false},@{Text='連絡';Blue=$true},@{Text='して大丈夫';Blue=$false})) },
    @{ Input='s04_time_passes_home.png'; Output='s04_time_passes_telop.png'; Position='top'; Lines=@(@(@{Text='時間が経ってから';Blue=$false}),@(@{Text='症状';Blue=$true},@{Text='が出ることもあります';Blue=$false})) },
    @{ Input='s05_emergency_phone_ready.png'; Output='s05_emergency_119_telop.png'; Position='center'; Lines=@(@(@{Text='呼吸が苦しい・意識がもうろう';Blue=$false}),@(@{Text='→ ';Blue=$false},@{Text='119番';Blue=$true},@{Text='へ';Blue=$false})) },
    @{ Input='s06_reassured_after_call.png'; Output='s06_consultation_telop.png'; Position='top'; Lines=@(@(@{Text='迷う内容でも';Blue=$false}),@(@{Text='遠慮せず';Blue=$false},@{Text='相談';Blue=$true},@{Text='してください';Blue=$false})) },
    @{ Input='s07_instruction_sheet_contact.png'; Output='s07_contact_info_telop.png'; Position='top'; Lines=@(@(@{Text='説明書と';Blue=$false},@{Text='連絡先';Blue=$true},@{Text='を';Blue=$false}),@(@{Text='すぐ見られる場所に';Blue=$false})) },
    @{ Input='s08_save_share_cta.png'; Output='s08_save_share_telop.png'; Position='top'; Lines=@(@(@{Text='帰宅後に見返せるよう';Blue=$false}),@(@{Text='保存';Blue=$true},@{Text='・ご家族にも共有を';Blue=$false})) }
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

    # PrivateFontCollection can emit implementation-specific values on Windows PowerShell.
    # The final emitted value is always the fitted Font object.
    $font = @(Get-FittedFont -Graphics $graphics -Lines $frame.Lines -ImageWidth $bitmap.Width)[-1]
    $lineHeight = $font.GetHeight($graphics) * 1.16
    $paddingX = $bitmap.Width * 0.055
    $paddingY = $bitmap.Width * 0.035
    $cardHeight = ($lineHeight * $frame.Lines.Count) + ($paddingY * 2)
    switch ($frame.Position) {
        'bottom' { $cardY = $bitmap.Height * 0.70 }
        'center' { $cardY = ($bitmap.Height - $cardHeight) / 2 }
        default { $cardY = $bitmap.Height * 0.095 }
    }
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

    $destination = Join-Path $outputDir $frame.Output
    $bitmap.Save($destination, [System.Drawing.Imaging.ImageFormat]::Png)
    $font.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
    $image.Dispose()
}

$fontCollection.Dispose()
