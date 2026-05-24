import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "F:/ANRYCAMPANY";
const inputPath = path.join(root, "tools", "spreadsheet_work", "google_short_script_raw.csv");
const outputDir = path.join(root, "tools", "spreadsheet_work", "outputs", "google_sheet_cleaned");
await fs.mkdir(outputDir, { recursive: true });

const raw = await fs.readFile(inputPath, "utf8");
const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);

const splitIndex = lines.findIndex((line) => line === "繝輔ャ繧ｯ,譛ｬ鬘・陦悟虚蝟夊ｵｷ");
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
  if (/繝ｬ繝ｳ繝医ご繝ｳ|X邱嘶鬪ｨ謚・謦ｮ蠖ｱ|蜀咏悄/.test(text)) return "繝ｬ繝ｳ繝医ご繝ｳ";
  if (/繝舌Μ繧ｦ繝|閭・き繝｡繝ｩ/.test(text)) return "繝舌Μ繧ｦ繝";
  if (/謚蟶ｫ/.test(text)) return "謚蟶ｫ縺ゅｋ縺ゅｋ";
  if (/謾ｾ蟆・ｷ嘶陲ｫ縺ｰ縺楯貂ｩ豕榎繝舌リ繝・.test(text)) return "謾ｾ蟆・ｷ夐尅蟄ｦ";
  return "蛹ｻ逋る尅蟄ｦ";
}

function typeFromText(text) {
  if (/蜊ｱ髯ｺ|諤翻荳榊ｮ榎螯雁ｨ|驥大ｱ桍騾蠖ｱ蜑､|蟄舌←繧・髢画園/.test(text)) return "荳榊ｮ芽ｧ｣豸・;
  if (/逅・罰|縺ｪ縺忿縺ｩ縺・繝昴う繝ｳ繝・繧ｳ繝л驕輔＞/.test(text)) return "隗｣隱ｬ";
  if (/菫晏ｭ・讀懈渊蜑鋼豕ｨ諢・.test(text)) return "菫晏ｭ伜梛";
  if (/謚蟶ｫ|閨ｷ讌ｭ逞・陬丞・|縺ゅｋ縺ゅｋ|縺ゅｊ縺後→縺・.test(text)) return "蜈ｱ諢・;
  return "髮大ｭｦ";
}

const workbook = Workbook.create();
const summary = workbook.worksheets.add("讎りｦ・);
const ideaSheet = workbook.worksheets.add("繝阪ち荳隕ｧ_謨ｴ逅・);
const scriptSheet = workbook.worksheets.add("蜿ｰ譛ｬ譯・謨ｴ逅・);
const checkSheet = workbook.worksheets.add("謾ｹ蝟・・繧､繝ｳ繝・);

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

heading(summary, "A1:F1", "繧ｷ繝ｧ繝ｼ繝亥虚逕ｻ逕ｨ蜿ｰ譛ｬ繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝・謨ｴ逅・沿");
summary.getRange("A3:B8").values = [
  ["遒ｺ隱阪＠縺溷・螳ｹ", "荳頑ｮｵ縺ｫ30譛ｬ縺ｮ繝阪ち荳隕ｧ縲∽ｸ区ｮｵ縺ｫ30譛ｬ縺ｮ蜿ｰ譛ｬ譯医′蜈･縺｣縺ｦ縺・∪縺励◆縲・],
  ["荳ｻ縺ｪ蝠城｡・, "蛻怜玄蛻・ｊ縺悟ｴｩ繧後※縺・※縲・縺､縺ｮ繧ｷ繝ｼ繝医↓蛻･蠖｢蠑上・陦ｨ縺梧ｷｷ蝨ｨ縺励※縺・∪縺励◆縲・],
  ["謨ｴ逅・婿驥・, "繝阪ち荳隕ｧ縺ｨ蜿ｰ譛ｬ譯医ｒ蛻･繧ｷ繝ｼ繝医↓蛻・￠縲√き繝・ざ繝ｪ縺ｨ蝙九ｒ霑ｽ蜉縺励∪縺励◆縲・],
  ["繝阪ち荳隕ｧ", `${ideas.length}莉ｶ`],
  ["蜿ｰ譛ｬ譯・, `${scripts.length}莉ｶ`],
  ["縺翫☆縺吶ａ", "莉雁ｾ後・1繧ｷ繝ｼ繝・逕ｨ騾斐↓縺吶ｋ縺ｨ縲∫ｮ｡逅・→謚慕ｨｿ蛹悶′縺九↑繧頑･ｽ縺ｫ縺ｪ繧翫∪縺吶・],
];
headers(summary.getRange("A3:B3"));
body(summary.getRange("A3:B8"));
summary.getRange("A:A").format.columnWidthPx = 150;
summary.getRange("B:B").format.columnWidthPx = 560;

heading(ideaSheet, "A1:H1", "繝阪ち荳隕ｧ 謨ｴ逅・);
ideaSheet.getRange("A3:H3").values = [["逡ｪ蜿ｷ", "繧ｫ繝・ざ繝ｪ", "蝙・, "繧ｿ繧､繝医Ν", "蜀帝ｭ繝輔ャ繧ｯ", "蜀・ｮｹ", "CTA", "谺｡縺ｮ菴懈･ｭ"]];
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
    "30遘貞床譛ｬ蛹・,
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

heading(scriptSheet, "A1:G1", "蜿ｰ譛ｬ譯・謨ｴ逅・);
scriptSheet.getRange("A3:G3").values = [["逡ｪ蜿ｷ", "繧ｫ繝・ざ繝ｪ", "蝙・, "繝輔ャ繧ｯ", "譛ｬ鬘・, "陦悟虚蝟夊ｵｷ", "謾ｹ蝟・Γ繝｢"]];
scriptSheet.getRange(`A4:G${scripts.length + 3}`).values = scripts.map((item) => {
  const text = `${item.hook} ${item.body} ${item.action}`;
  return [
    item.no,
    categoryFromText(text),
    typeFromText(text),
    item.hook,
    item.body,
    item.action,
    "遘呈焚蛻・￠繝ｻ繝・Ο繝・・蛹悶☆繧九→謚慕ｨｿ縺ｫ菴ｿ縺・ｄ縺吶＞",
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

heading(checkSheet, "A1:C1", "謾ｹ蝟・・繧､繝ｳ繝・);
checkSheet.getRange("A3:C3").values = [["蜆ｪ蜈亥ｺｦ", "謾ｹ蝟・・螳ｹ", "逅・罰"]];
checkSheet.getRange("A4:C9").values = [
  ["鬮・, "荳頑ｮｵ縺ｨ荳区ｮｵ繧貞挨繧ｷ繝ｼ繝医↓蛻・￠繧・, "繝阪ち邂｡逅・→蜿ｰ譛ｬ菴懈・縺梧ｷｷ縺悶ｋ縺ｨ縲√≠縺ｨ縺ｧ謗｢縺励↓縺上￥縺ｪ繧翫∪縺吶・],
  ["鬮・, "繧ｫ繝・ざ繝ｪ蛻励ｒ霑ｽ蜉縺吶ｋ", "MRI縲，T縲√Ξ繝ｳ繝医ご繝ｳ縺ｪ縺ｩ縺ｧ謚慕ｨｿ繝舌Λ繝ｳ繧ｹ繧定ｦ九ｄ縺吶￥縺ｪ繧翫∪縺吶・],
  ["荳ｭ", "蝙九ｒ霑ｽ蜉縺吶ｋ", "荳榊ｮ芽ｧ｣豸医∽ｿ晏ｭ伜梛縲∝・諢溘↑縺ｩ縺ｧ迢吶＞繧貞・縺代ｉ繧後∪縺吶・],
  ["荳ｭ", "谺｡縺ｮ菴懈･ｭ蛻励ｒ菴懊ｋ", "繝阪ち縺ｮ縺ｾ縺ｾ豁｢縺ｾ縺｣縺ｦ縺・ｋ繧ゅ・繧貞床譛ｬ蛹悶＠繧・☆縺上↑繧翫∪縺吶・],
  ["荳ｭ", "CTA繧剃ｿ晏ｭ倥・繧ｳ繝｡繝ｳ繝医・繝輔か繝ｭ繝ｼ縺ｧ蛻・｡槭☆繧・, "謚慕ｨｿ逶ｮ逧・↓蜷医ｏ縺帙※譛蠕後・荳險繧定ｪｿ謨ｴ縺ｧ縺阪∪縺吶・],
  ["菴・, "螳梧・蜿ｰ譛ｬ縺ｯ蛻･繧ｷ繝ｼ繝医〒遘呈焚縺斐→縺ｫ邂｡逅・☆繧・, "邱ｨ髮・凾縺ｫCapCut繧Хrew縺ｸ遘ｻ縺励ｄ縺吶￥縺ｪ繧翫∪縺吶・],
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

const preview = await workbook.render({ sheetName: "繝阪ち荳隕ｧ_謨ｴ逅・, autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(outputDir, "preview.png"), new Uint8Array(await preview.arrayBuffer()));

const outPath = path.join(outputDir, "繧ｷ繝ｧ繝ｼ繝亥虚逕ｻ逕ｨ蜿ｰ譛ｬ繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝・謨ｴ逅・沿.xlsx");
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outPath);
console.log(outPath);


