import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "F:/ANRYCAMPANY";
const inputPath = path.join(root, "tools", "spreadsheet_work", "google_short_script_raw.csv");
const outputDir = path.join(root, "tools", "spreadsheet_work", "outputs", "google_sheet_deduped");
await fs.mkdir(outputDir, { recursive: true });

const raw = await fs.readFile(inputPath, "utf8");
const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
const splitIndex = lines.findIndex((line) => line === "繝輔ャ繧ｯ,譛ｬ鬘・陦悟虚蝟夊ｵｷ");

const topLines = lines.slice(1, splitIndex).filter((line) => !line.startsWith(",,"));
const bottomLines = lines.slice(splitIndex + 1);

const topItems = topLines.map((line) => {
  const cleaned = line.replace(/,,\s*$/, "");
  const parts = cleaned.split(/\s+/);
  return {
    source: "荳頑ｮｵ",
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
    source: "荳区ｮｵ",
    originalNo: idx + 1,
    title: hook.replace(/[・・・・]$/g, ""),
    hook,
    content,
    cta,
  };
});

function category(text) {
  if (/MRI/.test(text)) return "MRI";
  if (/CT/.test(text)) return "CT";
  if (/繝ｬ繝ｳ繝医ご繝ｳ|X邱嘶鬪ｨ謚・謦ｮ蠖ｱ|蜀咏悄|鬪ｨ/.test(text)) return "繝ｬ繝ｳ繝医ご繝ｳ";
  if (/繝舌Μ繧ｦ繝|閭・き繝｡繝ｩ/.test(text)) return "繝舌Μ繧ｦ繝";
  if (/謚蟶ｫ/.test(text)) return "謚蟶ｫ縺ゅｋ縺ゅｋ";
  if (/謾ｾ蟆・ｷ嘶陲ｫ縺ｰ縺楯貂ｩ豕榎繝舌リ繝・.test(text)) return "謾ｾ蟆・ｷ夐尅蟄ｦ";
  return "蛹ｻ逋る尅蟄ｦ";
}

function formatType(text) {
  if (/蜊ｱ髯ｺ|諤翻荳榊ｮ榎螯雁ｨ|驥大ｱ桍騾蠖ｱ蜑､|蟄舌←繧・髢画園|繧ｿ繝医ぇ繝ｼ|逞・.test(text)) return "荳榊ｮ芽ｧ｣豸・;
  if (/菫晏ｭ・讀懈渊蜑鋼豕ｨ諢楯繧ｳ繝・.test(text)) return "菫晏ｭ伜梛";
  if (/逅・罰|縺ｪ縺忿縺ｩ縺・繝昴う繝ｳ繝・驕輔＞|縺ｩ繧後￥繧峨＞|譎る俣/.test(text)) return "隗｣隱ｬ";
  if (/謚蟶ｫ|閨ｷ讌ｭ逞・陬丞・|縺ゅｋ縺ゅｋ|縺ゅｊ縺後→縺・諢溯ｬ・.test(text)) return "蜈ｱ諢・;
  return "髮大ｭｦ";
}

function dedupeKey(item) {
  const text = `${item.title} ${item.hook} ${item.content}`;
  if (/繝ｬ繝ｳ繝医ご繝ｳ1蝗桍X邱壽､懈渊縺ｧ陲ｫ縺ｰ縺楯X邱壹〒霄ｫ菴薙↓謔ｪ縺・ｽｱ髻ｿ|閭ｸ驛ｨX邱・.test(text)) return "xray-dose-basic";
  if (/CT.*繝ｬ繝ｳ繝医ご繝ｳ|繝ｬ繝ｳ繝医ご繝ｳ.*CT/.test(text)) return "ct-xray-difference";
  if (/CT.*陲ｫ縺ｰ縺楯驛ｨ菴阪＃縺ｨ縺ｮ邱夐㍼/.test(text)) return "ct-dose";
  if (/貂ｩ豕榎繝ｩ繝峨Φ/.test(text)) return "radon-onsen";
  if (/繝舌リ繝掛繧ｫ繝ｪ繧ｦ繝40/.test(text)) return "banana-radiation";
  if (/諱ｯ.*豁｢繧－諱ｯ豁｢繧・.test(text)) return "breath-hold";
  if (/MRI.*驥大ｱ桍驥大ｱ・*MRI/.test(text)) return "mri-metal";
  if (/騾蠖ｱ蜑､/.test(text)) return "contrast-agent";
  if (/螯雁ｨ荳ｭ繝ｬ繝ｳ繝医ご繝ｳ/.test(text)) return "pregnancy-xray";
  if (/MRI.*螯雁ｩｦ|螯雁ｩｦ.*MRI/.test(text)) return "pregnancy-mri";
  if (/MRI.*髻ｳ/.test(text)) return "mri-noise";
  if (/MRI.*髢画園/.test(text)) return "mri-claustrophobia";
  if (/MRI.*譎る俣/.test(text)) return "mri-duration";
  if (/MRI.*謾ｾ蟆・ｷ嘶陲ｫ縺ｰ縺上ぞ繝ｭ/.test(text)) return "mri-no-radiation";
  if (/MRI.*逞帙∩|驥昴ｂ逞帙∩/.test(text)) return "mri-no-pain";
  if (/MRI.*菴薙ｂ險ｺ譁ｭ|蜈ｨ霄ｫ/.test(text)) return "mri-whole-body";
  if (/MRI.*CT.*蠕玲э|CT.*MRI.*蠕玲э/.test(text)) return "mri-ct-strength";
  if (/貉ｿ蟶・.test(text)) return "mri-or-xray-shippu";
  if (/繝舌Μ繧ｦ繝.*逋ｽ縺・ｶｲ菴倒縺ｪ縺懃區縺・ｶｲ菴・.test(text)) return "barium-why";
  if (/繝舌Μ繧ｦ繝.*荳句王|荳句王/.test(text)) return "barium-laxative";
  if (/繝舌Μ繧ｦ繝.*繧ｳ繝л蟆代＠縺壹▽鬟ｲ繧/.test(text)) return "barium-tips";
  if (/繝舌Μ繧ｦ繝.*闍ｦ謇弓蟇ｾ蜃ｦ豕・.test(text)) return "barium-anxiety";
  if (/繝舌Μ繧ｦ繝.*鬟滉ｺ弓豸亥喧縺ｮ濶ｯ縺・.test(text)) return "barium-food";
  if (/閭・き繝｡繝ｩ.*繝舌Μ繧ｦ繝|繝舌Μ繧ｦ繝.*縺ｩ縺｣縺｡/.test(text)) return "gastroscopy-barium";
  if (/逞帙＞蝣ｴ謇.*菴募屓|菴募屓繧ら李縺・ｴ謇/.test(text)) return "pain-location-repeat";
  if (/逞帙＞蝣ｴ謇.*鬪ｨ謚伜ｴ謇|髢｢騾｣逞・.test(text)) return "pain-location-different";
  if (/豁ｩ縺・*鬪ｨ謚・.test(text)) return "walking-fracture";
  if (/謦ｮ蠖ｱ蜑・*豁ｩ縺肴婿|霍幄｡・.test(text)) return "gait-before-xray";
  if (/X邱壼・逵・*鬪ｨ謚倅ｻ･螟翻閧ｺ轤旨閻ｸ髢牙｡・.test(text)) return "xray-other-disease";
  if (/X邱・*菴薙・荳ｭ|逋ｽ鮟・.test(text)) return "xray-how-see";
  if (/陌ｫ豁ｯ|豁ｯ/.test(text)) return "dental-xray";
  if (/蟄舌←繧・*X邱・.test(text)) return "child-xray";
  if (/CT.*譎る俣/.test(text)) return "ct-duration";
  if (/CT.*3D/.test(text)) return "ct-3d";
  if (/CT.*蠢・∮/.test(text)) return "ct-heart";
  if (/CT.*豌ｴ蛻・宛髯・.test(text)) return "ct-water-restriction";
  if (/CT.*諢丞､悶↑逞・ｰ慾蛛･蠎ｷ險ｺ譁ｭ/.test(text)) return "ct-incidental";
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
      reason: "繝・・繝槭′縺九↑繧願ｿ代＞縺溘ａ逵∫払蛟呵｣・,
    });
  }
}

const finalRows = unique.map((item, idx) => ({
  no: idx + 1,
  status: idx < 4 ? "菴懈・貂医∩" : "譛ｪ菴懈・",
  category: item.category,
  type: item.type,
  title: item.title,
  hook: item.hook,
  content: item.content,
  cta: item.cta,
  source: `${item.source}-${item.originalNo}`,
  next: idx < 4 ? "謚慕ｨｿ貂医∩/菴懈・貂医∩縺ｨ縺励※邂｡逅・ : "30遘貞床譛ｬ蛹・,
}));

const workbook = Workbook.create();
const summary = workbook.worksheets.add("讎りｦ・);
const master = workbook.worksheets.add("邨ｱ蜷医Μ繧ｹ繝・);
const omitted = workbook.worksheets.add("逵√＞縺滄㍾隍・);
const done = workbook.worksheets.add("菴懈・貂医∩");

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

head(summary, "A1:F1", "繧ｷ繝ｧ繝ｼ繝亥虚逕ｻ逕ｨ蜿ｰ譛ｬ 60鬘梧紛逅・沿");
summary.getRange("A3:B9").values = [
  ["蜈・ョ繝ｼ繧ｿ", `荳頑ｮｵ ${topItems.length}莉ｶ / 荳区ｮｵ ${bottomItems.length}莉ｶ`],
  ["邨ｱ蜷亥ｾ・, `${finalRows.length}莉ｶ`],
  ["逵√＞縺滄㍾隍・, `${duplicateRows.length}莉ｶ`],
  ["菴懈・貂医∩", "1縲・逡ｪ繧剃ｽ懈・貂医∩縺ｫ險ｭ螳・],
  ["謨ｴ逅・・螳ｹ", "荳贋ｸ九・谿ｵ繧貞酔縺伜・讒区・縺ｫ邨ｱ荳縺励∬ｿ代＞繝・・繝槭ｒ逵√″縺ｾ縺励◆縲・],
  ["菴ｿ縺・婿", "縺ｾ縺壹・縲檎ｵｱ蜷医Μ繧ｹ繝医阪ｒ隕九ｌ縺ｰ縲∵ｬ｡縺ｫ菴懊ｋ蜍慕判繝阪ち縺悟・縺九ｊ縺ｾ縺吶・],
  ["陬懆ｶｳ", "逵√＞縺溘ユ繝ｼ繝槭・縲檎怐縺・◆驥崎､・阪す繝ｼ繝医↓谿九＠縺ｦ縺ゅｊ縺ｾ縺吶・],
];
header(summary.getRange("A3:B3"));
body(summary.getRange("A3:B9"));
summary.getRange("A:A").format.columnWidthPx = 130;
summary.getRange("B:B").format.columnWidthPx = 540;

head(master, "A1:J1", "邨ｱ蜷医Μ繧ｹ繝・);
master.getRange("A3:J3").values = [["逡ｪ蜿ｷ", "迥ｶ諷・, "繧ｫ繝・ざ繝ｪ", "蝙・, "繧ｿ繧､繝医Ν", "蜀帝ｭ繝輔ャ繧ｯ", "蜀・ｮｹ", "CTA", "蜈・ョ繝ｼ繧ｿ", "谺｡縺ｮ菴懈･ｭ"]];
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

head(omitted, "A1:E1", "逵√＞縺滄㍾隍・);
omitted.getRange("A3:E3").values = [["蜈・ョ繝ｼ繧ｿ", "蜈・分蜿ｷ", "繧ｿ繧､繝医Ν/繝輔ャ繧ｯ", "莉｣陦ｨ縺ｫ縺励◆繝阪ち", "逅・罰"]];
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

head(done, "A1:H1", "菴懈・貂医∩");
const doneRows = finalRows.filter((r) => r.status === "菴懈・貂医∩");
done.getRange("A3:H3").values = [["逡ｪ蜿ｷ", "迥ｶ諷・, "繧ｫ繝・ざ繝ｪ", "蝙・, "繧ｿ繧､繝医Ν", "蜀帝ｭ繝輔ャ繧ｯ", "蜀・ｮｹ", "CTA"]];
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

const preview = await workbook.render({ sheetName: "邨ｱ蜷医Μ繧ｹ繝・, autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(outputDir, "preview.png"), new Uint8Array(await preview.arrayBuffer()));

const outPath = path.join(outputDir, "繧ｷ繝ｧ繝ｼ繝亥虚逕ｻ逕ｨ蜿ｰ譛ｬ_60鬘梧紛逅・驥崎､・怐逡･迚・xlsx");
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outPath);
console.log(outPath);


