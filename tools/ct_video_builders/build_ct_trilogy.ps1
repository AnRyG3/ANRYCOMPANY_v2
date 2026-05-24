$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Speech

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$OutDir = Join-Path $Root "reel_assets\ct_series\ct_trilogy_3part"
$FrameDir = Join-Path $OutDir "frames"
$AudioDir = Join-Path $OutDir "audio"
$VideoDir = Join-Path $OutDir "videos"
$DocDir = Join-Path $OutDir "投稿文"
@($OutDir,$FrameDir,$AudioDir,$VideoDir,$DocDir) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
$Ffmpeg = Join-Path $Root "tools\ffmpeg\bin\ffmpeg.exe"
$W = 1080
$H = 1920

function Get-ShortPath($Path) {
  $item = Get-Item -LiteralPath $Path
  $shell = New-Object -ComObject Scripting.FileSystemObject
  if ($item.PSIsContainer) {
    return $shell.GetFolder($item.FullName).ShortPath
  }
  return $shell.GetFile($item.FullName).ShortPath
}

function New-Beat($k,$t,$sub,$icon) {
  [PSCustomObject]@{ k=$k; t=$t; sub=$sub; icon=$icon }
}

$Episodes = @(
  [PSCustomObject]@{
    id="01"; order="Day 1"; filename="day1_nen_no_tame_ct.mp4"
    label="CT、受ける前に知ってほしいこと 1/3"
    title="「念のためCT」って`n本当に安心？"
    hook="撮れば安心、`nとは限らない。"
    narration=@(
      "念のためCTを撮っておけば安心。","そう思う方もいるかもしれません。","もちろんCTは、とても優れた検査です。","体の中を短時間で詳しく確認できます。","でも、CTには負担もあります。","放射線被ばく。検査費用。","そして、病気とは限らない小さな異常が見つかり、追加検査につながることもあります。","つまりCTは、撮れば必ず安心、という単純なものではありません。","大切なのは、検査に目的があること。","CTは便利な検査です。だからこそ、必要性を考えて使われます。"
    )
    beats=@(
      (New-Beat "不安" "念のため撮れば安心？" "その気持ちは自然です" "?"),
      (New-Beat "有用" "CTは優れた検査" "短時間で体の中を詳しく確認" "CT"),
      (New-Beat "負担" "でも、負担もある" "被ばく・費用・追加検査" "!"),
      (New-Beat "偶発" "小さな異常が見つかることも" "病気とは限らない所見が次の検査へ" "●"),
      (New-Beat "結論" "大切なのは目的" "CTは必要性を考えて使う検査" "✓")
    )
    caption="「念のためCT」が必ず安心につながるとは限りません。CTはとても有用な検査ですが、被ばく・費用・偶発所見・追加検査といった負担もあります。大切なのは、検査の目的を理解すること。`n`n#CT検査 #医療知識 #救急医療 #放射線 #健康リテラシー"
  },
  [PSCustomObject]@{
    id="02"; order="Day 2"; filename="day2_kyukyu_ct.mp4"
    label="CT、受ける前に知ってほしいこと 2/3"
    title="CTは危険？`nでも救急で必要なことがあります"
    hook="必要なCTは、`n命を守る検査。"
    narration=@(
      "CTは放射線があるから危険。","そう聞くと、不安になりますよね。","でも、救急ではCTが診断に大きく役立つ場面があります。","特に、重症外傷や複数の損傷が疑われる場合には、頭から体幹まで広く確認する全身CTが選択されることがあります。","頭の出血、胸やお腹の損傷、骨盤まわりの出血。","命に関わる異常を、短時間で確認できるからです。","ただし、すべての外傷で全身CTを撮るわけではありません。","状態、年齢、けがの状況を見て、必要性を判断します。","CTはただ危険な検査ではなく、必要な場面では命を守るための大切な検査です。"
    )
    beats=@(
      (New-Beat "不安" "放射線があるから不安" "まず不安になるのは自然です" "?"),
      (New-Beat "救急" "救急で役立つ場面" "重症外傷・複数損傷が疑われる場合" "+"),
      (New-Beat "確認" "頭・胸・お腹・骨盤" "命に関わる異常を短時間で確認" "CT"),
      (New-Beat "判断" "全員に撮るわけではない" "状態・年齢・けがの状況から判断" "✓"),
      (New-Beat "結論" "必要な場面では大切" "CTは命を守るための検査にもなる" "♥")
    )
    caption="CTには放射線被ばくがあります。一方で、救急では診断や治療方針の決定に大きく役立つ場面があります。特に重症外傷や複数損傷が疑われる場合、必要性を判断したうえで全身CTが選択されることがあります。`n`n#CT検査 #救急医療 #外傷 #医療知識 #放射線"
  },
  [PSCustomObject]@{
    id="03"; order="Day 3"; filename="day3_ct_mokuteki.mp4"
    label="CT、受ける前に知ってほしいこと 3/3"
    title="CTは悪者じゃない。`n目的が大事"
    hook="大切なのは、`n「なぜ撮るのか」。"
    narration=@(
      "CTは危険だからダメ。","逆に、CTを撮れば安心。","このどちらも極端です。","救急や重い症状がある場面では、CTが診断や治療方針の決定に大きく役立ちます。","一方で、CTには放射線被ばく、費用、偶然見つかる異常、追加検査といった負担もあります。","だから大切なのは、CTを怖がることでも、何となく希望することでもありません。","医師から必要性や注意点の説明を受け、理解したうえで検査を受けることです。","CTは悪者ではありません。","大切なのは、なぜ撮るのかです。"
    )
    beats=@(
      (New-Beat "両極" "怖い / 撮れば安心" "どちらも少し極端です" "↔"),
      (New-Beat "必要" "必要な場面では強い検査" "診断や治療方針の決定に役立つ" "CT"),
      (New-Beat "負担" "負担も理解する" "被ばく・費用・偶発所見・追加検査" "!"),
      (New-Beat "理解" "説明を受けて理解する" "必要性と注意点を確認" "✓"),
      (New-Beat "結論" "なぜ撮るのか" "目的があってこそ意味がある" "?")
    )
    caption="CTは悪者ではありません。ただし、何となく受ける検査でもありません。必要な場面では強力な検査。大切なのは、必要性や注意点を理解したうえで受けることです。`n`n#CT検査 #医療知識 #健康リテラシー #放射線 #検査"
  }
)

function New-Font($size, $style) {
  New-Object System.Drawing.Font("Yu Gothic", $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
}

function Draw-CenteredText($g, $text, $x, $y, $w, $h, $font, $brush) {
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = [System.Drawing.StringAlignment]::Center
  $fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
  $rect = New-Object System.Drawing.RectangleF($x,$y,$w,$h)
  $g.DrawString($text, $font, $brush, $rect, $fmt)
  $fmt.Dispose()
}

function Fill-RoundRect($g, $x, $y, $w, $h, $r, $brush) {
  $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $r * 2
  $gp.AddArc($x,$y,$d,$d,180,90); $gp.AddArc($x+$w-$d,$y,$d,$d,270,90)
  $gp.AddArc($x+$w-$d,$y+$h-$d,$d,$d,0,90); $gp.AddArc($x,$y+$h-$d,$d,$d,90,90)
  $gp.CloseFigure()
  $g.FillPath($brush,$gp)
  $gp.Dispose()
}

function Save-Frame($ep, $beat, $index, $total) {
  $epDir = Join-Path $FrameDir $ep.id
  New-Item -ItemType Directory -Force -Path $epDir | Out-Null
  $file = Join-Path $epDir ("frame_{0:D2}.png" -f $index)
  $bmp = New-Object System.Drawing.Bitmap($W,$H)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Rectangle(0,0,$W,$H)), [System.Drawing.Color]::FromArgb(248,250,252), [System.Drawing.Color]::FromArgb(204,251,241), 45)
  $g.FillRectangle($bg,0,0,$W,$H)
  $white = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
  $ink = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(17,24,39))
  $muted = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(71,85,105))
  $teal = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(15,118,110))
  $dark = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(15,23,42))
  $pale = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(236,254,255))
  $blue = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(219,234,254))
  Fill-RoundRect $g 80 96 920 88 44 $white
  Draw-CenteredText $g $ep.label 110 104 860 72 (New-Font 34 ([System.Drawing.FontStyle]::Bold)) $teal
  Draw-CenteredText $g $ep.title 80 238 920 230 (New-Font 68 ([System.Drawing.FontStyle]::Bold)) $ink
  Fill-RoundRect $g 96 650 888 720 22 $white
  $g.FillEllipse($teal,454,734,172,172)
  $g.FillEllipse($pale,464,744,152,152)
  Draw-CenteredText $g $beat.icon 464 744 152 152 (New-Font 64 ([System.Drawing.FontStyle]::Bold)) $teal
  Draw-CenteredText $g $beat.t 126 984 828 130 (New-Font 58 ([System.Drawing.FontStyle]::Bold)) $ink
  Draw-CenteredText $g $beat.sub 126 1132 828 118 (New-Font 38 ([System.Drawing.FontStyle]::Bold)) $muted
  Fill-RoundRect $g 150 1436 780 210 18 $dark
  Draw-CenteredText $g $ep.hook 180 1454 720 176 (New-Font 52 ([System.Drawing.FontStyle]::Bold)) $white
  Fill-RoundRect $g 130 1710 820 18 9 $blue
  $pw = [int](820 * $index / $total)
  Fill-RoundRect $g 130 1710 $pw 18 9 $teal
  Draw-CenteredText $g $ep.order 440 1768 200 52 (New-Font 34 ([System.Drawing.FontStyle]::Bold)) $muted
  Draw-CenteredText $g "※個別の判断は医療機関でご相談ください" 80 1834 920 48 (New-Font 28 ([System.Drawing.FontStyle]::Regular)) $muted
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $bg.Dispose(); $white.Dispose(); $ink.Dispose(); $muted.Dispose(); $teal.Dispose(); $dark.Dispose(); $pale.Dispose(); $blue.Dispose()
  return $file
}

function Get-AudioSeconds($file) {
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  $txt = (& $Ffmpeg -hide_banner -i $file 2>&1 | Out-String)
  $ErrorActionPreference = $oldPreference
  if ($txt -match "Duration:\s*(\d+):(\d+):(\d+\.\d+)") {
    return ([double]$Matches[1] * 3600 + [double]$Matches[2] * 60 + [double]$Matches[3])
  }
  return 45
}

$Manifest = @()
foreach ($ep in $Episodes) {
  $frames = @()
  for ($i=0; $i -lt $ep.beats.Count; $i++) { $frames += Save-Frame $ep $ep.beats[$i] ($i+1) $ep.beats.Count }
  $narText = ($ep.narration -join "`r`n")
  Set-Content -Path (Join-Path $DocDir "$($ep.id)_ナレーション.txt") -Value $narText -Encoding UTF8
  Set-Content -Path (Join-Path $DocDir "$($ep.id)_投稿文.txt") -Value $ep.caption -Encoding UTF8
  $wav = Join-Path $AudioDir "$($ep.id)_narration.wav"
  $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $s.SelectVoice("Microsoft Haruka Desktop")
  $s.Rate = -1
  $s.Volume = 100
  $s.SetOutputToWaveFile($wav)
  $s.Speak($narText)
  $s.Dispose()
  $sec = Get-AudioSeconds $wav
  $per = [Math]::Max(3.2, $sec / $frames.Count)
  $list = Join-Path $VideoDir "$($ep.id)_frames.txt"
  $lines = @()
  foreach ($f in $frames) { $lines += "file '$((Get-ShortPath $f).Replace('\','/'))'"; $lines += ("duration {0:N2}" -f $per) }
  $lines += "file '$((Get-ShortPath $frames[-1]).Replace('\','/'))'"
  Set-Content -Path $list -Value ($lines -join "`n") -Encoding ASCII
  $silent = Join-Path $VideoDir "$($ep.id)_silent.mp4"
  $out = Join-Path $VideoDir $ep.filename
  $listShort = Get-ShortPath $list
  $silentShort = (Join-Path (Get-ShortPath $VideoDir) "$($ep.id)_silent.mp4")
  $outShort = (Join-Path (Get-ShortPath $VideoDir) $ep.filename)
  $wavShort = Get-ShortPath $wav
  & $Ffmpeg -y -f concat -safe 0 -i $listShort -vf "fps=30,format=yuv420p" -c:v libx264 -pix_fmt yuv420p $silentShort
  if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while creating silent video for $($ep.id)" }
  $bgmDur = [Math]::Round($sec+2,2)
  & $Ffmpeg -y -i $silentShort -i $wavShort -f lavfi -i "sine=frequency=220:duration=$bgmDur" -f lavfi -i "sine=frequency=277.18:duration=$bgmDur" -f lavfi -i "sine=frequency=329.63:duration=$bgmDur" -filter_complex "[2:a]volume=0.012[a2];[3:a]volume=0.010[a3];[4:a]volume=0.008[a4];[a2][a3][a4]amix=inputs=3:duration=first,lowpass=f=1200[bgm];[1:a]volume=1.0[voice];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1[a]" -map "0:v" -map "[a]" -shortest -c:v copy -c:a aac -b:a 192k $outShort
  if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while adding audio for $($ep.id)" }
  $Manifest += [PSCustomObject]@{ id=$ep.id; title=$ep.title.Replace("`n"," "); video=$out; narration=$wav; caption=(Join-Path $DocDir "$($ep.id)_投稿文.txt") }
}

$Manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $OutDir "manifest.json") -Encoding UTF8
Set-Content -Path (Join-Path $OutDir "README.txt") -Encoding UTF8 -Value @"
CT 3部作 連日投稿セット

videos: 投稿用MP4
audio: ナレーションWAV
frames: 各動画の静止画素材
投稿文: ナレーション原稿とキャプション

順番:
1. day1_nen_no_tame_ct.mp4
2. day2_kyukyu_ct.mp4
3. day3_ct_mokuteki.mp4
"@

Write-Host "Done: $OutDir"








