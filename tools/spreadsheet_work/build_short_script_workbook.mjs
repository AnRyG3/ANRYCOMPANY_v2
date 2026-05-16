import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/Users/maruk/OneDrive/デスクトップ/Anry campany";
const outputDir = path.join(root, "tools", "spreadsheet_work", "outputs", "short_video_script");
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();

const overview = workbook.worksheets.add("台本一覧");
const script = workbook.worksheets.add("完成台本");
const captions = workbook.worksheets.add("テロップ");
const edit = workbook.worksheets.add("編集メモ");

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

title(overview, "A1:F1", "ショート動画用台本 管理表", "台本の目的、構成、保存価値をひと目で確認できる整理版です。");
overview.getRange("A4:F4").values = [["投稿ID", "テーマ", "対象", "尺", "目的", "状態"]];
overview.getRange("A5:F5").values = [[
  "REEL-20260513-001",
  "レントゲン検査前に外すもの",
  "一般の患者さん",
  "約28秒",
  "撮り直しを防ぎ、検査前の不安を減らす",
  "完成台本",
]];
styleHeader(overview.getRange("A4:F4"));
styleBody(overview.getRange("A5:F5"));
overview.getRange("A7:B11").values = [
  ["動画タイプ", "保存型 + 不安解消"],
  ["主な訴求", "検査前に見返せる実用情報"],
  ["フック", "撮り直しになることがあります"],
  ["安心の着地", "迷ったらスタッフへ聞いてOK"],
  ["コメント誘導", "他に不安な検査を聞く"],
];
styleHeader(overview.getRange("A7:B7"));
styleBody(overview.getRange("A7:B11"));
overview.getRange("A:F").format.columnWidthPx = 150;
overview.getRange("E:E").format.columnWidthPx = 260;
overview.freezePanes.freezeRows(4);

title(script, "A1:E1", "完成台本", "秒数ごとに、役割・ナレーション・画面表示を分けています。");
script.getRange("A4:E4").values = [["秒数", "役割", "ナレーション", "画面テロップ", "ねらい"]];
script.getRange("A5:E10").values = [
  ["0〜3秒", "フック", "レントゲン前、これ付けたままだと撮り直しになることがあります。", "レントゲン前 これ注意\n撮り直しになるかも", "最初に不安ではなく注意喚起として引きつける"],
  ["3〜7秒", "結論", "湿布・カイロ・金属・アクセサリーは外すことがあります。", "湿布 / カイロ / 金属 / アクセ", "先に答えを出して離脱を防ぐ"],
  ["7〜14秒", "理由", "画像に白く写ったり、見たい場所を隠してしまうことがあるからです。", "画像に写ることがあります\n見たい場所が隠れることも", "なぜ外すのかを一般向けに説明"],
  ["14〜20秒", "専門家視点", "放射線技師は、病気やケガを見るために余計な写り込みがないか確認しています。", "技師が写り込みを確認しています", "放射線技師の専門性を自然に出す"],
  ["20〜24秒", "安心づけ", "迷ったら、外す前にスタッフへ聞いてOKです。", "迷ったらスタッフへ聞いてOK", "患者さんの不安を下げる"],
  ["24〜28秒", "行動喚起", "検査前に見返せるように保存してね。他に不安な検査、コメントで教えてください。", "検査前に保存\n不安な検査はコメントへ", "保存とコメントにつなげる"],
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

title(captions, "A1:D1", "テロップ一覧", "編集時にそのまま入れられる短めの画面文字です。");
captions.getRange("A4:D4").values = [["番号", "テロップ", "表示タイミング", "編集ポイント"]];
captions.getRange("A5:D11").values = [
  [1, "レントゲン前 これ注意", "0〜1秒", "大きく表示"],
  [2, "付けたままだと撮り直し？", "1〜3秒", "少し強めに引きつける"],
  [3, "湿布 / カイロ / 金属 / アクセ", "3〜7秒", "4分割でテンポよく表示"],
  [4, "画像に写ることがあります", "7〜10秒", "白く写るイメージを入れる"],
  [5, "見たい場所が隠れることも", "10〜14秒", "隠れる理由をシンプルに"],
  [6, "迷ったらスタッフへ聞いてOK", "20〜24秒", "安心感のある色にする"],
  [7, "検査前に保存", "24〜28秒", "保存ボタン風の見せ方"],
];
styleHeader(captions.getRange("A4:D4"));
styleBody(captions.getRange("A5:D11"));
captions.getRange("A:A").format.columnWidthPx = 60;
captions.getRange("B:B").format.columnWidthPx = 260;
captions.getRange("C:C").format.columnWidthPx = 120;
captions.getRange("D:D").format.columnWidthPx = 260;
captions.freezePanes.freezeRows(4);

title(edit, "A1:C1", "編集メモ", "動画制作時に迷わないための注意点です。");
edit.getRange("A4:C4").values = [["項目", "内容", "理由"]];
edit.getRange("A5:C10").values = [
  ["サムネ", "メイン: 検査前に外すもの\nサブ: 撮り直しを防ぐ", "保存したくなる実用テーマに見せる"],
  ["冒頭", "1秒目に「撮り直し」を大きく出す", "視聴者の手を止める"],
  ["見せ方", "湿布・カイロ・金属・アクセサリーは4分割表示", "一覧性が高く保存されやすい"],
  ["トーン", "怖がらせすぎず、最後は安心に着地", "医療系アカウントとして信頼感を保つ"],
  ["音", "BGMは中くらい。効果音はチェック表示程度", "説明の邪魔をしない"],
  ["言い回し", "「外してください」ではなく「外すことがあります」", "検査部位や施設差に対応しやすい"],
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

const preview = await workbook.render({ sheetName: "完成台本", autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(outputDir, "preview_completed_script.png"), new Uint8Array(await preview.arrayBuffer()));

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const outPath = path.join(outputDir, "ショート動画用台本_整理版.xlsx");
await xlsx.save(outPath);
console.log(outPath);
