import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/Users/maruk/OneDrive/デスクトップ/Anry campany";
const inputPath = path.join(root, "tools", "spreadsheet_work", "google_short_script_raw.csv");
const outputDir = path.join(root, "tools", "spreadsheet_work", "outputs", "google_sheet_cleaned");
await fs.mkdir(outputDir, { recursive: true });

const raw = await fs.readFile(inputPath, "utf8");
const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);

const splitIndex = lines.findIndex((line) => line === "フック,本題,行動喚起");
const ideaLines = lines.slice(1, splitIndex).filter((line) => !line.startsWith(",,"));
const scriptLines = lines.slice(splitIndex + 1);

const ideas = ideaLines.map((line) => {
  const cleaned = line.replace(/,,\s*$/, "");
  const parts = cleaned.split(/\s+/);
  return {
    no: Number(parts[0]),
    title: parts[1] ?? "",
    hook: parts[2] ?? "",
    content: parts[3] ?? "",
    cta: parts.slice(4).join(" "),
  };
});

const scripts = scriptLines.map((line, idx) => {
  const [hook = "", body = "", action = ""] = line.split(",");
  return {
    no: idx + 1,
    hook,
    body,
    action,
  };
});

function categoryFromText(text) {
  if (/MRI/.test(text)) return "MRI";
  if (/CT/.test(text)) return "CT";
  if (/レントゲン|X線|骨折|撮影|写真/.test(text)) return "レントゲン";
  if (/バリウム|胃カメラ/.test(text)) return "バリウム";
  if (/技師/.test(text)) return "技師あるある";
  if (/放射線|被ばく|温泉|バナナ/.test(text)) return "放射線雑学";
  return "医療雑学";
}

function typeFromText(text) {
  if (/危険|怖|不安|妊娠|金属|造影剤|子ども|閉所/.test(text)) return "不安解消";
  if (/理由|なぜ|どう|ポイント|コツ|違い/.test(text)) return "解説";
  if (/保存|検査前|注意/.test(text)) return "保存型";
  if (/技師|職業病|裏側|あるある|ありがとう/.test(text)) return "共感";
  return "雑学";
}

const workbook = Workbook.create();
const summary = workbook.worksheets.add("概要");
const ideaSheet = workbook.worksheets.add("ネタ一覧_整理");
const scriptSheet = workbook.worksheets.add("台本案_整理");
const checkSheet = workbook.worksheets.add("改善ポイント");

const palette = {
  dark: "#1F3A5F",
  blue: "#E8F1FF",
  green: "#EAF7EF",
  yellow: "#FFF4CC",
  gray: "#F5F7FA",
  border: "#D8E0EA",
  text: "#1F2933",
  white: "#FFFFFF",
};

for (const sheet of [summary, ideaSheet, scriptSheet, checkSheet]) {
  sheet.showGridLines = false;
}

function heading(sheet, range, text) {
  const r = sheet.getRange(range);
  r.merge();
  r.values = [[text]];
  r.format = {
    fill: palette.dark,
    font: { bold: true, color: palette.white, size: 15, name: "Yu Gothic" },
    verticalAlignment: "middle",
  };
  r.format.rowHeightPx = 38;
}

function headers(range) {
  range.format = {
    fill: palette.dark,
    font: { bold: true, color: palette.white, name: "Yu Gothic" },
    horizontalAlignment: "center",
    verticalAlignment: "middle",
    wrapText: true,
  };
}

function body(range) {
  range.format = {
    font: { color: palette.text, name: "Yu Gothic" },
    verticalAlignment: "top",
    wrapText: true,
    borders: {
      insideHorizontal: { style: "Continuous", color: palette.border },
      insideVertical: { style: "Continuous", color: palette.border },
      edgeTop: { style: "Continuous", color: palette.border },
      edgeBottom: { style: "Continuous", color: palette.border },
      edgeLeft: { style: "Continuous", color: palette.border },
      edgeRight: { style: "Continuous", color: palette.border },
    },
  };
}

heading(summary, "A1:F1", "ショート動画用台本スプレッドシート 整理版");
summary.getRange("A3:B8").values = [
  ["確認した内容", "上段に30本のネタ一覧、下段に30本の台本案が入っていました。"],
  ["主な問題", "列区切りが崩れていて、1つのシートに別形式の表が混在していました。"],
  ["整理方針", "ネタ一覧と台本案を別シートに分け、カテゴリと型を追加しました。"],
  ["ネタ一覧", `${ideas.length}件`],
  ["台本案", `${scripts.length}件`],
  ["おすすめ", "今後は1シート1用途にすると、管理と投稿化がかなり楽になります。"],
];
headers(summary.getRange("A3:B3"));
body(summary.getRange("A3:B8"));
summary.getRange("A:A").format.columnWidthPx = 150;
summary.getRange("B:B").format.columnWidthPx = 560;

heading(ideaSheet, "A1:H1", "ネタ一覧 整理");
ideaSheet.getRange("A3:H3").values = [["番号", "カテゴリ", "型", "タイトル", "冒頭フック", "内容", "CTA", "次の作業"]];
ideaSheet.getRange(`A4:H${ideas.length + 3}`).values = ideas.map((item) => {
  const text = `${item.title} ${item.hook} ${item.content} ${item.cta}`;
  return [
    item.no,
    categoryFromText(text),
    typeFromText(text),
    item.title,
    item.hook,
    item.content,
    item.cta,
    "30秒台本化",
  ];
});
headers(ideaSheet.getRange("A3:H3"));
body(ideaSheet.getRange(`A4:H${ideas.length + 3}`));
ideaSheet.getRange("A:A").format.columnWidthPx = 58;
ideaSheet.getRange("B:C").format.columnWidthPx = 100;
ideaSheet.getRange("D:D").format.columnWidthPx = 220;
ideaSheet.getRange("E:E").format.columnWidthPx = 300;
ideaSheet.getRange("F:F").format.columnWidthPx = 260;
ideaSheet.getRange("G:G").format.columnWidthPx = 220;
ideaSheet.getRange("H:H").format.columnWidthPx = 110;
ideaSheet.freezePanes.freezeRows(3);
ideaSheet.tables.add(`A3:H${ideas.length + 3}`, true, "IdeaList");

heading(scriptSheet, "A1:G1", "台本案 整理");
scriptSheet.getRange("A3:G3").values = [["番号", "カテゴリ", "型", "フック", "本題", "行動喚起", "改善メモ"]];
scriptSheet.getRange(`A4:G${scripts.length + 3}`).values = scripts.map((item) => {
  const text = `${item.hook} ${item.body} ${item.action}`;
  return [
    item.no,
    categoryFromText(text),
    typeFromText(text),
    item.hook,
    item.body,
    item.action,
    "秒数分け・テロップ化すると投稿に使いやすい",
  ];
});
headers(scriptSheet.getRange("A3:G3"));
body(scriptSheet.getRange(`A4:G${scripts.length + 3}`));
scriptSheet.getRange("A:A").format.columnWidthPx = 58;
scriptSheet.getRange("B:C").format.columnWidthPx = 100;
scriptSheet.getRange("D:D").format.columnWidthPx = 330;
scriptSheet.getRange("E:E").format.columnWidthPx = 430;
scriptSheet.getRange("F:F").format.columnWidthPx = 300;
scriptSheet.getRange("G:G").format.columnWidthPx = 260;
scriptSheet.freezePanes.freezeRows(3);
scriptSheet.tables.add(`A3:G${scripts.length + 3}`, true, "ScriptDrafts");

heading(checkSheet, "A1:C1", "改善ポイント");
checkSheet.getRange("A3:C3").values = [["優先度", "改善内容", "理由"]];
checkSheet.getRange("A4:C9").values = [
  ["高", "上段と下段を別シートに分ける", "ネタ管理と台本作成が混ざると、あとで探しにくくなります。"],
  ["高", "カテゴリ列を追加する", "MRI、CT、レントゲンなどで投稿バランスを見やすくなります。"],
  ["中", "型を追加する", "不安解消、保存型、共感などで狙いを分けられます。"],
  ["中", "次の作業列を作る", "ネタのまま止まっているものを台本化しやすくなります。"],
  ["中", "CTAを保存・コメント・フォローで分類する", "投稿目的に合わせて最後の一言を調整できます。"],
  ["低", "完成台本は別シートで秒数ごとに管理する", "編集時にCapCutやVrewへ移しやすくなります。"],
];
headers(checkSheet.getRange("A3:C3"));
body(checkSheet.getRange("A4:C9"));
checkSheet.getRange("A:A").format.columnWidthPx = 80;
checkSheet.getRange("B:B").format.columnWidthPx = 280;
checkSheet.getRange("C:C").format.columnWidthPx = 520;

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
});
console.log(errors.ndjson);

const preview = await workbook.render({ sheetName: "ネタ一覧_整理", autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(outputDir, "preview.png"), new Uint8Array(await preview.arrayBuffer()));

const outPath = path.join(outputDir, "ショート動画用台本スプレッドシート_整理版.xlsx");
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outPath);
console.log(outPath);
