import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "F:/ANRYCAMPANY";
const outputDir = path.join(root, "tools", "spreadsheet_work", "outputs", "short_video_script");
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();

const overview = workbook.worksheets.add("蜿ｰ譛ｬ荳隕ｧ");
const script = workbook.worksheets.add("螳梧・蜿ｰ譛ｬ");
const captions = workbook.worksheets.add("繝・Ο繝・・");
const edit = workbook.worksheets.add("邱ｨ髮・Γ繝｢");

for (const sheet of [overview, script, captions, edit]) {
  sheet.showGridLines = false;
}

const palette = {
  navy: "#1F3A5F",
  blue: "#DDEBFF",
  green: "#E7F5EC",
  yellow: "#FFF3C4",
  gray: "#F4F6F8",
  border: "#D9E2EC",
  text: "#1F2933",
  white: "#FFFFFF",
};

function title(sheet, range, text, sub) {
  const r = sheet.getRange(range);
  r.merge();
  r.values = [[text]];
  r.format = {
    fill: palette.navy,
    font: { bold: true, color: palette.white, size: 16 },
    horizontalAlignment: "left",
    verticalAlignment: "middle",
  };
  r.format.rowHeightPx = 40;
  if (sub) {
    const s = sheet.getRange("A2:F2");
    s.merge();
    s.values = [[sub]];
    s.format = {
      fill: palette.blue,
      font: { color: palette.text, size: 10 },
      wrapText: true,
      verticalAlignment: "middle",
    };
    s.format.rowHeightPx = 30;
  }
}

function styleHeader(range) {
  range.format = {
    fill: palette.navy,
    font: { bold: true, color: palette.white },
    horizontalAlignment: "center",
    verticalAlignment: "middle",
    wrapText: true,
  };
}

function styleBody(range) {
  range.format = {
    font: { color: palette.text },
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

title(overview, "A1:F1", "繧ｷ繝ｧ繝ｼ繝亥虚逕ｻ逕ｨ蜿ｰ譛ｬ 邂｡逅・｡ｨ", "蜿ｰ譛ｬ縺ｮ逶ｮ逧・∵ｧ区・縲∽ｿ晏ｭ倅ｾ｡蛟､繧偵・縺ｨ逶ｮ縺ｧ遒ｺ隱阪〒縺阪ｋ謨ｴ逅・沿縺ｧ縺吶・);
overview.getRange("A4:F4").values = [["謚慕ｨｿID", "繝・・繝・, "蟇ｾ雎｡", "蟆ｺ", "逶ｮ逧・, "迥ｶ諷・]];
overview.getRange("A5:F5").values = [[
  "REEL-20260513-001",
  "繝ｬ繝ｳ繝医ご繝ｳ讀懈渊蜑阪↓螟悶☆繧ゅ・",
  "荳闊ｬ縺ｮ謔｣閠・＆繧・,
  "邏・8遘・,
  "謦ｮ繧顔峩縺励ｒ髦ｲ縺弱∵､懈渊蜑阪・荳榊ｮ峨ｒ貂帙ｉ縺・,
  "螳梧・蜿ｰ譛ｬ",
]];
styleHeader(overview.getRange("A4:F4"));
styleBody(overview.getRange("A5:F5"));
overview.getRange("A7:B11").values = [
  ["蜍慕判繧ｿ繧､繝・, "菫晏ｭ伜梛 + 荳榊ｮ芽ｧ｣豸・],
  ["荳ｻ縺ｪ險ｴ豎・, "讀懈渊蜑阪↓隕玖ｿ斐○繧句ｮ溽畑諠・ｱ"],
  ["繝輔ャ繧ｯ", "謦ｮ繧顔峩縺励↓縺ｪ繧九％縺ｨ縺後≠繧翫∪縺・],
  ["螳牙ｿ・・逹蝨ｰ", "霑ｷ縺｣縺溘ｉ繧ｹ繧ｿ繝・ヵ縺ｸ閨槭＞縺ｦOK"],
  ["繧ｳ繝｡繝ｳ繝郁ｪ伜ｰ・, "莉悶↓荳榊ｮ峨↑讀懈渊繧定◇縺・],
];
styleHeader(overview.getRange("A7:B7"));
styleBody(overview.getRange("A7:B11"));
overview.getRange("A:F").format.columnWidthPx = 150;
overview.getRange("E:E").format.columnWidthPx = 260;
overview.freezePanes.freezeRows(4);

title(script, "A1:E1", "螳梧・蜿ｰ譛ｬ", "遘呈焚縺斐→縺ｫ縲∝ｽｹ蜑ｲ繝ｻ繝翫Ξ繝ｼ繧ｷ繝ｧ繝ｳ繝ｻ逕ｻ髱｢陦ｨ遉ｺ繧貞・縺代※縺・∪縺吶・);
script.getRange("A4:E4").values = [["遘呈焚", "蠖ｹ蜑ｲ", "繝翫Ξ繝ｼ繧ｷ繝ｧ繝ｳ", "逕ｻ髱｢繝・Ο繝・・", "縺ｭ繧峨＞"]];
script.getRange("A5:E10").values = [
  ["0縲・遘・, "繝輔ャ繧ｯ", "繝ｬ繝ｳ繝医ご繝ｳ蜑阪√％繧御ｻ倥￠縺溘∪縺ｾ縺縺ｨ謦ｮ繧顔峩縺励↓縺ｪ繧九％縺ｨ縺後≠繧翫∪縺吶・, "繝ｬ繝ｳ繝医ご繝ｳ蜑・縺薙ｌ豕ｨ諢十n謦ｮ繧顔峩縺励↓縺ｪ繧九°繧・, "譛蛻昴↓荳榊ｮ峨〒縺ｯ縺ｪ縺乗ｳｨ諢丞繭襍ｷ縺ｨ縺励※蠑輔″縺､縺代ｋ"],
  ["3縲・遘・, "邨占ｫ・, "貉ｿ蟶・・繧ｫ繧､繝ｭ繝ｻ驥大ｱ槭・繧｢繧ｯ繧ｻ繧ｵ繝ｪ繝ｼ縺ｯ螟悶☆縺薙→縺後≠繧翫∪縺吶・, "貉ｿ蟶・/ 繧ｫ繧､繝ｭ / 驥大ｱ・/ 繧｢繧ｯ繧ｻ", "蜈医↓遲斐∴繧貞・縺励※髮｢閼ｱ繧帝亟縺・],
  ["7縲・4遘・, "逅・罰", "逕ｻ蜒上↓逋ｽ縺丞・縺｣縺溘ｊ縲∬ｦ九◆縺・ｴ謇繧帝國縺励※縺励∪縺・％縺ｨ縺後≠繧九°繧峨〒縺吶・, "逕ｻ蜒上↓蜀吶ｋ縺薙→縺後≠繧翫∪縺兔n隕九◆縺・ｴ謇縺碁國繧後ｋ縺薙→繧・, "縺ｪ縺懷､悶☆縺ｮ縺九ｒ荳闊ｬ蜷代￠縺ｫ隱ｬ譏・],
  ["14縲・0遘・, "蟆る摩螳ｶ隕也せ", "謾ｾ蟆・ｷ壽橿蟶ｫ縺ｯ縲∫羅豌励ｄ繧ｱ繧ｬ繧定ｦ九ｋ縺溘ａ縺ｫ菴呵ｨ医↑蜀吶ｊ霎ｼ縺ｿ縺後↑縺・°遒ｺ隱阪＠縺ｦ縺・∪縺吶・, "謚蟶ｫ縺悟・繧願ｾｼ縺ｿ繧堤｢ｺ隱阪＠縺ｦ縺・∪縺・, "謾ｾ蟆・ｷ壽橿蟶ｫ縺ｮ蟆る摩諤ｧ繧定・辟ｶ縺ｫ蜃ｺ縺・],
  ["20縲・4遘・, "螳牙ｿ・▼縺・, "霑ｷ縺｣縺溘ｉ縲∝､悶☆蜑阪↓繧ｹ繧ｿ繝・ヵ縺ｸ閨槭＞縺ｦOK縺ｧ縺吶・, "霑ｷ縺｣縺溘ｉ繧ｹ繧ｿ繝・ヵ縺ｸ閨槭＞縺ｦOK", "謔｣閠・＆繧薙・荳榊ｮ峨ｒ荳九￡繧・],
  ["24縲・8遘・, "陦悟虚蝟夊ｵｷ", "讀懈渊蜑阪↓隕玖ｿ斐○繧九ｈ縺・↓菫晏ｭ倥＠縺ｦ縺ｭ縲ゆｻ悶↓荳榊ｮ峨↑讀懈渊縲√さ繝｡繝ｳ繝医〒謨吶∴縺ｦ縺上□縺輔＞縲・, "讀懈渊蜑阪↓菫晏ｭ禄n荳榊ｮ峨↑讀懈渊縺ｯ繧ｳ繝｡繝ｳ繝医∈", "菫晏ｭ倥→繧ｳ繝｡繝ｳ繝医↓縺､縺ｪ縺偵ｋ"],
];
styleHeader(script.getRange("A4:E4"));
styleBody(script.getRange("A5:E10"));
script.getRange("A:A").format.columnWidthPx = 80;
script.getRange("B:B").format.columnWidthPx = 110;
script.getRange("C:C").format.columnWidthPx = 360;
script.getRange("D:D").format.columnWidthPx = 240;
script.getRange("E:E").format.columnWidthPx = 260;
script.getRange("A5:E10").format.rowHeightPx = 64;
script.freezePanes.freezeRows(4);

title(captions, "A1:D1", "繝・Ο繝・・荳隕ｧ", "邱ｨ髮・凾縺ｫ縺昴・縺ｾ縺ｾ蜈･繧後ｉ繧後ｋ遏ｭ繧√・逕ｻ髱｢譁・ｭ励〒縺吶・);
captions.getRange("A4:D4").values = [["逡ｪ蜿ｷ", "繝・Ο繝・・", "陦ｨ遉ｺ繧ｿ繧､繝溘Φ繧ｰ", "邱ｨ髮・・繧､繝ｳ繝・]];
captions.getRange("A5:D11").values = [
  [1, "繝ｬ繝ｳ繝医ご繝ｳ蜑・縺薙ｌ豕ｨ諢・, "0縲・遘・, "螟ｧ縺阪￥陦ｨ遉ｺ"],
  [2, "莉倥￠縺溘∪縺ｾ縺縺ｨ謦ｮ繧顔峩縺暦ｼ・, "1縲・遘・, "蟆代＠蠑ｷ繧√↓蠑輔″縺､縺代ｋ"],
  [3, "貉ｿ蟶・/ 繧ｫ繧､繝ｭ / 驥大ｱ・/ 繧｢繧ｯ繧ｻ", "3縲・遘・, "4蛻・牡縺ｧ繝・Φ繝昴ｈ縺剰｡ｨ遉ｺ"],
  [4, "逕ｻ蜒上↓蜀吶ｋ縺薙→縺後≠繧翫∪縺・, "7縲・0遘・, "逋ｽ縺丞・繧九う繝｡繝ｼ繧ｸ繧貞・繧後ｋ"],
  [5, "隕九◆縺・ｴ謇縺碁國繧後ｋ縺薙→繧・, "10縲・4遘・, "髫繧後ｋ逅・罰繧偵す繝ｳ繝励Ν縺ｫ"],
  [6, "霑ｷ縺｣縺溘ｉ繧ｹ繧ｿ繝・ヵ縺ｸ閨槭＞縺ｦOK", "20縲・4遘・, "螳牙ｿ・─縺ｮ縺ゅｋ濶ｲ縺ｫ縺吶ｋ"],
  [7, "讀懈渊蜑阪↓菫晏ｭ・, "24縲・8遘・, "菫晏ｭ倥・繧ｿ繝ｳ鬚ｨ縺ｮ隕九○譁ｹ"],
];
styleHeader(captions.getRange("A4:D4"));
styleBody(captions.getRange("A5:D11"));
captions.getRange("A:A").format.columnWidthPx = 60;
captions.getRange("B:B").format.columnWidthPx = 260;
captions.getRange("C:C").format.columnWidthPx = 120;
captions.getRange("D:D").format.columnWidthPx = 260;
captions.freezePanes.freezeRows(4);

title(edit, "A1:C1", "邱ｨ髮・Γ繝｢", "蜍慕判蛻ｶ菴懈凾縺ｫ霑ｷ繧上↑縺・◆繧√・豕ｨ諢冗せ縺ｧ縺吶・);
edit.getRange("A4:C4").values = [["鬆・岼", "蜀・ｮｹ", "逅・罰"]];
edit.getRange("A5:C10").values = [
  ["繧ｵ繝繝・, "繝｡繧､繝ｳ: 讀懈渊蜑阪↓螟悶☆繧ゅ・\n繧ｵ繝・ 謦ｮ繧顔峩縺励ｒ髦ｲ縺・, "菫晏ｭ倥＠縺溘￥縺ｪ繧句ｮ溽畑繝・・繝槭↓隕九○繧・],
  ["蜀帝ｭ", "1遘堤岼縺ｫ縲梧聴繧顔峩縺励阪ｒ螟ｧ縺阪￥蜃ｺ縺・, "隕冶・閠・・謇九ｒ豁｢繧√ｋ"],
  ["隕九○譁ｹ", "貉ｿ蟶・・繧ｫ繧､繝ｭ繝ｻ驥大ｱ槭・繧｢繧ｯ繧ｻ繧ｵ繝ｪ繝ｼ縺ｯ4蛻・牡陦ｨ遉ｺ", "荳隕ｧ諤ｧ縺碁ｫ倥￥菫晏ｭ倥＆繧後ｄ縺吶＞"],
  ["繝医・繝ｳ", "諤悶′繧峨○縺吶℃縺壹∵怙蠕後・螳牙ｿ・↓逹蝨ｰ", "蛹ｻ逋らｳｻ繧｢繧ｫ繧ｦ繝ｳ繝医→縺励※菫｡鬆ｼ諢溘ｒ菫昴▽"],
  ["髻ｳ", "BGM縺ｯ荳ｭ縺上ｉ縺・ょ柑譫憺浹縺ｯ繝√ぉ繝・け陦ｨ遉ｺ遞句ｺｦ", "隱ｬ譏弱・驍ｪ鬲斐ｒ縺励↑縺・],
  ["險縺・屓縺・, "縲悟､悶＠縺ｦ縺上□縺輔＞縲阪〒縺ｯ縺ｪ縺上悟､悶☆縺薙→縺後≠繧翫∪縺吶・, "讀懈渊驛ｨ菴阪ｄ譁ｽ險ｭ蟾ｮ縺ｫ蟇ｾ蠢懊＠繧・☆縺・],
];
styleHeader(edit.getRange("A4:C4"));
styleBody(edit.getRange("A5:C10"));
edit.getRange("A:A").format.columnWidthPx = 110;
edit.getRange("B:B").format.columnWidthPx = 340;
edit.getRange("C:C").format.columnWidthPx = 300;
edit.getRange("A5:C10").format.rowHeightPx = 58;
edit.freezePanes.freezeRows(4);

for (const sheet of [overview, script, captions, edit]) {
  const used = sheet.getUsedRange();
  used.format.font = { name: "Yu Gothic", color: palette.text };
}

const preview = await workbook.render({ sheetName: "螳梧・蜿ｰ譛ｬ", autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(outputDir, "preview_completed_script.png"), new Uint8Array(await preview.arrayBuffer()));

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const outPath = path.join(outputDir, "繧ｷ繝ｧ繝ｼ繝亥虚逕ｻ逕ｨ蜿ｰ譛ｬ_謨ｴ逅・沿.xlsx");
await xlsx.save(outPath);
console.log(outPath);


