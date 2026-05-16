import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/Users/maruk/OneDrive/デスクトップ/Anry campany";
const inputPath = path.join(root, "tools", "spreadsheet_work", "google_short_script_raw.csv");
const outputDir = path.join(root, "tools", "spreadsheet_work", "outputs", "google_sheet_deduped");
await fs.mkdir(outputDir, { recursive: true });

const raw = await fs.readFile(inputPath, "utf8");
const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
const splitIndex = lines.findIndex((line) => line === "フック,本題,行動喚起");

const topLines = lines.slice(1, splitIndex).filter((line) => !line.startsWith(",,"));
const bottomLines = lines.slice(splitIndex + 1);

const topItems = topLines.map((line) => {
  const cleaned = line.replace(/,,\s*$/, "");
  const parts = cleaned.split(/\s+/);
  return {
    source: "上段",
    originalNo: Number(parts[0]),
    title: parts[1] ?? "",
    hook: parts[2] ?? "",
    content: parts[3] ?? "",
    cta: parts.slice(4).join(" "),
  };
});

const bottomItems = bottomLines.map((line, idx) => {
  const [hook = "", content = "", cta = ""] = line.split(",");
  return {
    source: "下段",
    originalNo: idx + 1,
    title: hook.replace(/[！!？?]$/g, ""),
    hook,
    content,
    cta,
  };
});

function category(text) {
  if (/MRI/.test(text)) return "MRI";
  if (/CT/.test(text)) return "CT";
  if (/レントゲン|X線|骨折|撮影|写真|骨/.test(text)) return "レントゲン";
  if (/バリウム|胃カメラ/.test(text)) return "バリウム";
  if (/技師/.test(text)) return "技師あるある";
  if (/放射線|被ばく|温泉|バナナ/.test(text)) return "放射線雑学";
  return "医療雑学";
}

function formatType(text) {
  if (/危険|怖|不安|妊娠|金属|造影剤|子ども|閉所|タトゥー|痛/.test(text)) return "不安解消";
  if (/保存|検査前|注意|コツ/.test(text)) return "保存型";
  if (/理由|なぜ|どう|ポイント|違い|どれくらい|時間/.test(text)) return "解説";
  if (/技師|職業病|裏側|あるある|ありがとう|感謝/.test(text)) return "共感";
  return "雑学";
}

function dedupeKey(item) {
  const text = `${item.title} ${item.hook} ${item.content}`;
  if (/レントゲン1回|X線検査で被ばく|X線で身体に悪い影響|胸部X線/.test(text)) return "xray-dose-basic";
  if (/CT.*レントゲン|レントゲン.*CT/.test(text)) return "ct-xray-difference";
  if (/CT.*被ばく|部位ごとの線量/.test(text)) return "ct-dose";
  if (/温泉|ラドン/.test(text)) return "radon-onsen";
  if (/バナナ|カリウム40/.test(text)) return "banana-radiation";
  if (/息.*止め|息止め/.test(text)) return "breath-hold";
  if (/MRI.*金属|金属.*MRI/.test(text)) return "mri-metal";
  if (/造影剤/.test(text)) return "contrast-agent";
  if (/妊娠中レントゲン/.test(text)) return "pregnancy-xray";
  if (/MRI.*妊婦|妊婦.*MRI/.test(text)) return "pregnancy-mri";
  if (/MRI.*音/.test(text)) return "mri-noise";
  if (/MRI.*閉所/.test(text)) return "mri-claustrophobia";
  if (/MRI.*時間/.test(text)) return "mri-duration";
  if (/MRI.*放射線|被ばくゼロ/.test(text)) return "mri-no-radiation";
  if (/MRI.*痛み|針も痛み/.test(text)) return "mri-no-pain";
  if (/MRI.*体も診断|全身/.test(text)) return "mri-whole-body";
  if (/MRI.*CT.*得意|CT.*MRI.*得意/.test(text)) return "mri-ct-strength";
  if (/湿布/.test(text)) return "mri-or-xray-shippu";
  if (/バリウム.*白い液体|なぜ白い液体/.test(text)) return "barium-why";
  if (/バリウム.*下剤|下剤/.test(text)) return "barium-laxative";
  if (/バリウム.*コツ|少しずつ飲む/.test(text)) return "barium-tips";
  if (/バリウム.*苦手|対処法/.test(text)) return "barium-anxiety";
  if (/バリウム.*食事|消化の良い/.test(text)) return "barium-food";
  if (/胃カメラ.*バリウム|バリウム.*どっち/.test(text)) return "gastroscopy-barium";
  if (/痛い場所.*何回|何回も痛い場所/.test(text)) return "pain-location-repeat";
  if (/痛い場所.*骨折場所|関連痛/.test(text)) return "pain-location-different";
  if (/歩け.*骨折/.test(text)) return "walking-fracture";
  if (/撮影前.*歩き方|跛行/.test(text)) return "gait-before-xray";
  if (/X線写真.*骨折以外|肺炎|腸閉塞/.test(text)) return "xray-other-disease";
  if (/X線.*体の中|白黒/.test(text)) return "xray-how-see";
  if (/虫歯|歯/.test(text)) return "dental-xray";
  if (/子ども.*X線/.test(text)) return "child-xray";
  if (/CT.*時間/.test(text)) return "ct-duration";
  if (/CT.*3D/.test(text)) return "ct-3d";
  if (/CT.*心臓/.test(text)) return "ct-heart";
  if (/CT.*水分制限/.test(text)) return "ct-water-restriction";
  if (/CT.*意外な病気|健康診断/.test(text)) return "ct-incidental";
  return `${category(text)}:${item.title}`;
}

const all = [...topItems, ...bottomItems].map((item) => {
  const text = `${item.title} ${item.hook} ${item.content} ${item.cta}`;
  return {
    ...item,
    category: category(text),
    type: formatType(text),
    key: dedupeKey(item),
  };
});

const unique = [];
const duplicateRows = [];
const seen = new Map();

for (const item of all) {
  if (!seen.has(item.key)) {
    seen.set(item.key, item);
    unique.push(item);
  } else {
    const representative = seen.get(item.key);
    duplicateRows.push({
      source: item.source,
      originalNo: item.originalNo,
      title: item.title,
      duplicateOf: `${representative.source}-${representative.originalNo}: ${representative.title}`,
      reason: "テーマがかなり近いため省略候補",
    });
  }
}

const finalRows = unique.map((item, idx) => ({
  no: idx + 1,
  status: idx < 4 ? "作成済み" : "未作成",
  category: item.category,
  type: item.type,
  title: item.title,
  hook: item.hook,
  content: item.content,
  cta: item.cta,
  source: `${item.source}-${item.originalNo}`,
  next: idx < 4 ? "投稿済み/作成済みとして管理" : "30秒台本化",
}));

const workbook = Workbook.create();
const summary = workbook.worksheets.add("概要");
const master = workbook.worksheets.add("統合リスト");
const omitted = workbook.worksheets.add("省いた重複");
const done = workbook.worksheets.add("作成済み");

for (const sheet of [summary, master, omitted, done]) sheet.showGridLines = false;

const c = {
  dark: "#1F3A5F",
  blue: "#E8F1FF",
  green: "#E8F6EF",
  yellow: "#FFF2C2",
  red: "#FDECEC",
  border: "#D8E0EA",
  text: "#1F2933",
  white: "#FFFFFF",
};

function head(sheet, range, text) {
  const r = sheet.getRange(range);
  r.merge();
  r.values = [[text]];
  r.format = { fill: c.dark, font: { bold: true, color: c.white, size: 15, name: "Yu Gothic" }, verticalAlignment: "middle" };
  r.format.rowHeightPx = 38;
}

function header(range) {
  range.format = { fill: c.dark, font: { bold: true, color: c.white, name: "Yu Gothic" }, horizontalAlignment: "center", verticalAlignment: "middle", wrapText: true };
}

function body(range) {
  range.format = {
    font: { color: c.text, name: "Yu Gothic" },
    verticalAlignment: "top",
    wrapText: true,
    borders: {
      insideHorizontal: { style: "Continuous", color: c.border },
      insideVertical: { style: "Continuous", color: c.border },
      edgeTop: { style: "Continuous", color: c.border },
      edgeBottom: { style: "Continuous", color: c.border },
      edgeLeft: { style: "Continuous", color: c.border },
      edgeRight: { style: "Continuous", color: c.border },
    },
  };
}

head(summary, "A1:F1", "ショート動画用台本 60題整理版");
summary.getRange("A3:B9").values = [
  ["元データ", `上段 ${topItems.length}件 / 下段 ${bottomItems.length}件`],
  ["統合後", `${finalRows.length}件`],
  ["省いた重複", `${duplicateRows.length}件`],
  ["作成済み", "1〜4番を作成済みに設定"],
  ["整理内容", "上下の段を同じ列構成に統一し、近いテーマを省きました。"],
  ["使い方", "まずは「統合リスト」を見れば、次に作る動画ネタが分かります。"],
  ["補足", "省いたテーマは「省いた重複」シートに残してあります。"],
];
header(summary.getRange("A3:B3"));
body(summary.getRange("A3:B9"));
summary.getRange("A:A").format.columnWidthPx = 130;
summary.getRange("B:B").format.columnWidthPx = 540;

head(master, "A1:J1", "統合リスト");
master.getRange("A3:J3").values = [["番号", "状態", "カテゴリ", "型", "タイトル", "冒頭フック", "内容", "CTA", "元データ", "次の作業"]];
master.getRange(`A4:J${finalRows.length + 3}`).values = finalRows.map((r) => [r.no, r.status, r.category, r.type, r.title, r.hook, r.content, r.cta, r.source, r.next]);
header(master.getRange("A3:J3"));
body(master.getRange(`A4:J${finalRows.length + 3}`));
master.getRange(`B4:B7`).format = { fill: c.green, font: { bold: true, color: "#166534", name: "Yu Gothic" }, horizontalAlignment: "center" };
master.getRange(`A8:J${finalRows.length + 3}`).format.fill = c.white;
master.getRange("A:A").format.columnWidthPx = 54;
master.getRange("B:B").format.columnWidthPx = 90;
master.getRange("C:D").format.columnWidthPx = 100;
master.getRange("E:E").format.columnWidthPx = 230;
master.getRange("F:F").format.columnWidthPx = 330;
master.getRange("G:G").format.columnWidthPx = 360;
master.getRange("H:H").format.columnWidthPx = 250;
master.getRange("I:J").format.columnWidthPx = 120;
master.freezePanes.freezeRows(3);
master.tables.add(`A3:J${finalRows.length + 3}`, true, "UnifiedScripts");

head(omitted, "A1:E1", "省いた重複");
omitted.getRange("A3:E3").values = [["元データ", "元番号", "タイトル/フック", "代表にしたネタ", "理由"]];
if (duplicateRows.length) {
  omitted.getRange(`A4:E${duplicateRows.length + 3}`).values = duplicateRows.map((r) => [r.source, r.originalNo, r.title, r.duplicateOf, r.reason]);
  body(omitted.getRange(`A4:E${duplicateRows.length + 3}`));
}
header(omitted.getRange("A3:E3"));
omitted.getRange("A:A").format.columnWidthPx = 80;
omitted.getRange("B:B").format.columnWidthPx = 70;
omitted.getRange("C:C").format.columnWidthPx = 280;
omitted.getRange("D:D").format.columnWidthPx = 340;
omitted.getRange("E:E").format.columnWidthPx = 220;
omitted.freezePanes.freezeRows(3);

head(done, "A1:H1", "作成済み");
const doneRows = finalRows.filter((r) => r.status === "作成済み");
done.getRange("A3:H3").values = [["番号", "状態", "カテゴリ", "型", "タイトル", "冒頭フック", "内容", "CTA"]];
done.getRange(`A4:H${doneRows.length + 3}`).values = doneRows.map((r) => [r.no, r.status, r.category, r.type, r.title, r.hook, r.content, r.cta]);
header(done.getRange("A3:H3"));
body(done.getRange(`A4:H${doneRows.length + 3}`));
done.getRange(`B4:B${doneRows.length + 3}`).format = { fill: c.green, font: { bold: true, color: "#166534", name: "Yu Gothic" }, horizontalAlignment: "center" };
done.getRange("A:A").format.columnWidthPx = 54;
done.getRange("B:D").format.columnWidthPx = 100;
done.getRange("E:E").format.columnWidthPx = 230;
done.getRange("F:F").format.columnWidthPx = 330;
done.getRange("G:G").format.columnWidthPx = 350;
done.getRange("H:H").format.columnWidthPx = 250;

const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 } });
console.log(errors.ndjson);

const preview = await workbook.render({ sheetName: "統合リスト", autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(outputDir, "preview.png"), new Uint8Array(await preview.arrayBuffer()));

const outPath = path.join(outputDir, "ショート動画用台本_60題整理_重複省略版.xlsx");
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outPath);
console.log(outPath);
