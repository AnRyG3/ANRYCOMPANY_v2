import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(path.join(process.cwd(), "tools", "spreadsheet_work", "index.js"));
const { chromium } = require("playwright");

const root = process.cwd();
const outDir = path.join(root, "01_ショート動画_リール_YouTubeShorts", "CTを怖がる前に_3部作");
const frameDir = path.join(outDir, "frames");
const audioDir = path.join(outDir, "audio");
const videoDir = path.join(outDir, "videos");
const docDir = path.join(outDir, "投稿文");
for (const dir of [outDir, frameDir, audioDir, videoDir, docDir]) fs.mkdirSync(dir, { recursive: true });

const ffmpeg = path.join(root, "tools", "ffmpeg", "bin", "ffmpeg.exe");
const W = 1080;
const H = 1920;

const episodes = [
  {
    id: "01",
    order: "Day 1",
    title: "“念のためCT”って\n本当に安心？",
    label: "CT、受ける前に知ってほしいこと 1/3",
    hook: "撮れば安心、\nとは限らない。",
    narration: [
      "念のためCTを撮っておけば安心。",
      "そう思う方もいるかもしれません。",
      "もちろんCTは、とても優れた検査です。",
      "体の中を短時間で詳しく確認できます。",
      "でも、CTには負担もあります。",
      "放射線被ばく。検査費用。",
      "そして、病気とは限らない小さな異常が見つかり、追加検査につながることもあります。",
      "つまりCTは、撮れば必ず安心、という単純なものではありません。",
      "大切なのは、検査に目的があること。",
      "CTは便利な検査です。だからこそ、必要性を考えて使われます。"
    ],
    beats: [
      { k: "不安", t: "念のため撮れば安心？", sub: "その気持ちは自然です", icon: "?" },
      { k: "有用", t: "CTは優れた検査", sub: "短時間で体の中を詳しく確認", icon: "CT" },
      { k: "負担", t: "でも、負担もある", sub: "被ばく・費用・追加検査", icon: "!" },
      { k: "偶発", t: "小さな異常が見つかることも", sub: "病気とは限らない所見が次の検査へ", icon: "●" },
      { k: "結論", t: "大切なのは目的", sub: "CTは必要性を考えて使う検査", icon: "✓" }
    ],
    caption: "“念のためCT”が必ず安心につながるとは限りません。CTはとても有用な検査ですが、被ばく・費用・偶発所見・追加検査といった負担もあります。大切なのは、検査の目的を理解することです。\n\n#CT検査 #医療知識 #救急医療 #放射線 #健康リテラシー",
    filename: "day1_nen_no_tame_ct.mp4"
  },
  {
    id: "02",
    order: "Day 2",
    title: "CTは危険？\nでも救急で必要なことがあります",
    label: "CT、受ける前に知ってほしいこと 2/3",
    hook: "必要なCTは、\n命を守る検査。",
    narration: [
      "CTは放射線があるから危険。",
      "そう聞くと、不安になりますよね。",
      "でも、救急ではCTが診断に大きく役立つ場面があります。",
      "特に、重症外傷や複数の損傷が疑われる場合には、頭から体幹まで広く確認する全身CTが選択されることがあります。",
      "頭の出血、胸やお腹の損傷、骨盤まわりの出血。",
      "命に関わる異常を、短時間で確認できるからです。",
      "ただし、すべての外傷で全身CTを撮るわけではありません。",
      "状態、年齢、けがの状況を見て、必要性を判断します。",
      "CTはただ危険な検査ではなく、必要な場面では命を守るための大切な検査です。"
    ],
    beats: [
      { k: "不安", t: "放射線があるから不安", sub: "まず不安になるのは自然です", icon: "?" },
      { k: "救急", t: "救急で役立つ場面", sub: "重症外傷・複数損傷が疑われる場合", icon: "+" },
      { k: "確認", t: "頭・胸・お腹・骨盤", sub: "命に関わる異常を短時間で確認", icon: "CT" },
      { k: "判断", t: "全員に撮るわけではない", sub: "状態・年齢・けがの状況から判断", icon: "✓" },
      { k: "結論", t: "必要な場面では大切", sub: "CTは命を守るための検査にもなる", icon: "心" }
    ],
    caption: "CTには放射線被ばくがあります。一方で、救急では診断や治療方針の決定に大きく役立つ場面があります。特に重症外傷や複数損傷が疑われる場合、必要性を判断したうえで全身CTが選択されることがあります。\n\n#CT検査 #救急医療 #外傷 #医療知識 #放射線",
    filename: "day2_kyukyu_ct.mp4"
  },
  {
    id: "03",
    order: "Day 3",
    title: "CTは悪者じゃない。\n目的が大事",
    label: "CT、受ける前に知ってほしいこと 3/3",
    hook: "大切なのは、\n“なぜ撮るのか”。",
    narration: [
      "CTは危険だからダメ。",
      "逆に、CTを撮れば安心。",
      "このどちらも極端です。",
      "救急や重い症状がある場面では、CTが診断や治療方針の決定に大きく役立ちます。",
      "一方で、CTには放射線被ばく、費用、偶然見つかる異常、追加検査といった負担もあります。",
      "だから大切なのは、CTを怖がることでも、何となく希望することでもありません。",
      "医師から必要性や注意点の説明を受け、理解したうえで検査を受けることです。",
      "CTは悪者ではありません。",
      "大切なのは、なぜ撮るのかです。"
    ],
    beats: [
      { k: "両極", t: "怖い / 撮れば安心", sub: "どちらも少し極端です", icon: "↔" },
      { k: "必要", t: "必要な場面では強い検査", sub: "診断や治療方針の決定に役立つ", icon: "CT" },
      { k: "負担", t: "負担も理解する", sub: "被ばく・費用・偶発所見・追加検査", icon: "!" },
      { k: "理解", t: "説明を受けて理解する", sub: "必要性と注意点を確認", icon: "✓" },
      { k: "結論", t: "なぜ撮るのか", sub: "目的があってこそ意味がある", icon: "?" }
    ],
    caption: "CTは悪者ではありません。ただし、何となく受ける検査でもありません。必要な場面では強力な検査。大切なのは、必要性や注意点を理解したうえで受けることです。\n\n#CT検査 #医療知識 #健康リテラシー #放射線 #検査",
    filename: "day3_ct_mokuteki.mp4"
  }
];

function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;" }[c]));
}

function textLines(text, x, y, size, weight = 700, fill = "#111827", anchor = "middle", lineGap = 1.18) {
  return text.split("\n").map((line, i) =>
    `<text x="${x}" y="${y + i * size * lineGap}" text-anchor="${anchor}" font-size="${size}" font-weight="${weight}" fill="${fill}" font-family="Yu Gothic, Meiryo, Arial">${esc(line)}</text>`
  ).join("");
}

function card(x, y, w, h, fill = "#ffffff", stroke = "#d7dee8") {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="22" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
}

function iconSvg(icon, cx, cy, r = 86) {
  const label = icon === "心" ? "♥" : icon;
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#0f766e"/>
  <circle cx="${cx}" cy="${cy}" r="${r - 10}" fill="#ecfeff"/>
  <text x="${cx}" y="${cy + 24}" text-anchor="middle" font-family="Yu Gothic, Meiryo, Arial" font-size="${label.length > 1 ? 44 : 72}" font-weight="800" fill="#0f766e">${esc(label)}</text>`;
}

function baseSvg(ep, idx, total) {
  const beat = ep.beats[idx];
  const progressW = 820 * ((idx + 1) / total);
  const palette = idx % 2 === 0 ? ["#f8fafc", "#e0f2fe"] : ["#ffffff", "#ccfbf1"];
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="${palette[0]}"/>
        <stop offset="1" stop-color="${palette[1]}"/>
      </linearGradient>
      <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#0f172a" flood-opacity="0.12"/>
      </filter>
    </defs>
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    <rect x="80" y="96" width="920" height="88" rx="44" fill="#ffffff" opacity="0.88"/>
    ${textLines(ep.label, 540, 152, 34, 700, "#0f766e")}
    ${textLines(ep.title, 540, 330, 72, 800, "#111827")}
    <g filter="url(#shadow)">${card(96, 650, 888, 720)}</g>
    ${iconSvg(beat.icon, 540, 820)}
    ${textLines(beat.t, 540, 1048, 64, 800, "#111827")}
    ${textLines(beat.sub, 540, 1168, 40, 700, "#475569")}
    <g transform="translate(150 1436)">
      <rect x="0" y="0" width="780" height="210" rx="18" fill="#0f172a"/>
      ${textLines(ep.hook, 390, 76, 52, 800, "#ffffff")}
    </g>
    <rect x="130" y="1710" width="820" height="18" rx="9" fill="#dbeafe"/>
    <rect x="130" y="1710" width="${progressW}" height="18" rx="9" fill="#0f766e"/>
    ${textLines(ep.order, 540, 1802, 34, 800, "#334155")}
    ${textLines("※個別の判断は医療機関でご相談ください", 540, 1858, 28, 600, "#64748b")}
  </svg>`;
}

async function makeFrames(ep, browser) {
  const epFrameDir = path.join(frameDir, ep.id);
  fs.mkdirSync(epFrameDir, { recursive: true });
  const files = [];
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  for (let i = 0; i < ep.beats.length; i++) {
    const file = path.join(epFrameDir, `frame_${String(i + 1).padStart(2, "0")}.png`);
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;width:${W}px;height:${H}px;overflow:hidden;background:#fff}</style></head><body>${baseSvg(ep, i, ep.beats.length)}</body></html>`;
    await page.setContent(html, { waitUntil: "load" });
    await page.screenshot({ path: file, type: "png" });
    files.push(file);
  }
  await page.close();
  return files;
}

function writeNarration(ep) {
  const txt = ep.narration.join("\n");
  fs.writeFileSync(path.join(docDir, `${ep.id}_ナレーション.txt`), txt, "utf8");
  fs.writeFileSync(path.join(docDir, `${ep.id}_投稿文.txt`), ep.caption, "utf8");
  const safe = txt.replace(/'/g, "''");
  const wav = path.join(audioDir, `${ep.id}_narration.wav`);
  const ps = [
    "Add-Type -AssemblyName System.Speech",
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
    "$s.SelectVoice('Microsoft Haruka Desktop')",
    "$s.Rate = -1",
    "$s.Volume = 100",
    `$s.SetOutputToWaveFile('${wav.replace(/'/g, "''")}')`,
    `$s.Speak('${safe}')`,
    "$s.Dispose()"
  ].join("; ");
  execFileSync("powershell", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], { stdio: "inherit" });
  return wav;
}

function duration(file) {
  const out = execFileSync(ffmpeg, ["-i", file], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  return out;
}

function getAudioSeconds(file) {
  try {
    execFileSync(ffmpeg, ["-hide_banner", "-i", file], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  } catch (e) {
    const m = String(e.stderr || "").match(/Duration:\s*(\d+):(\d+):(\d+\.\d+)/);
    if (m) return Number(m[1]) * 3600 + Number(m[2]) * 60 + Number(m[3]);
  }
  return 45;
}

function makeVideo(ep, frames, wav) {
  const sec = getAudioSeconds(wav);
  const per = Math.max(3.2, sec / frames.length);
  const listFile = path.join(videoDir, `${ep.id}_frames.txt`);
  const lines = [];
  for (const f of frames) {
    lines.push(`file '${f.replace(/\\/g, "/").replace(/'/g, "'\\''")}'`);
    lines.push(`duration ${per.toFixed(2)}`);
  }
  lines.push(`file '${frames[frames.length - 1].replace(/\\/g, "/").replace(/'/g, "'\\''")}'`);
  fs.writeFileSync(listFile, lines.join("\n"), "utf8");
  const silent = path.join(videoDir, `${ep.id}_silent.mp4`);
  const out = path.join(videoDir, ep.filename);
  execFileSync(ffmpeg, ["-y", "-f", "concat", "-safe", "0", "-i", listFile, "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-pix_fmt", "yuv420p", silent], { stdio: "inherit" });
  execFileSync(ffmpeg, [
    "-y",
    "-i", silent,
    "-i", wav,
    "-f", "lavfi",
    "-i", `sine=frequency=220:duration=${(sec + 2).toFixed(2)}`,
    "-filter_complex", "[2:a]volume=0.035,aloop=loop=-1:size=2e+09[bgm];[1:a]volume=1.0[voice];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1[a]",
    "-map", "0:v",
    "-map", "[a]",
    "-shortest",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    out
  ], { stdio: "inherit" });
  return out;
}

const manifest = [];
const browser = await chromium.launch({ headless: true });
for (const ep of episodes) {
  const frames = await makeFrames(ep, browser);
  const wav = writeNarration(ep);
  const video = makeVideo(ep, frames, wav);
  manifest.push({ id: ep.id, title: ep.title.replace(/\n/g, " "), video, narration: wav, caption: path.join(docDir, `${ep.id}_投稿文.txt`) });
}
await browser.close();

fs.writeFileSync(path.join(outDir, "manifest.json"), JSON.stringify(manifest, null, 2), "utf8");
fs.writeFileSync(path.join(outDir, "README.txt"), [
  "CT 3部作 連日投稿セット",
  "",
  "videos: 投稿用MP4",
  "audio: ナレーションWAV",
  "frames: 各動画の静止画素材",
  "投稿文: ナレーション原稿とキャプション",
  "",
  "順番:",
  "1. day1_nen_no_tame_ct.mp4",
  "2. day2_kyukyu_ct.mp4",
  "3. day3_ct_mokuteki.mp4"
].join("\n"), "utf8");

console.log(`Done: ${outDir}`);
