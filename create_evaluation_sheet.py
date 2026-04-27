import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "部内貢献度評価"

# ── 列幅設定 ──────────────────────────────────────────────
col_widths = {
    "A": 4, "B": 22, "C": 18, "D": 18, "E": 18,
    "F": 12, "G": 14, "H": 18,
}
for col, width in col_widths.items():
    ws.column_dimensions[col].width = width

# ── 行高設定 ──────────────────────────────────────────────
row_heights = {
    1: 8, 2: 36, 3: 28, 4: 28, 5: 28, 6: 28, 7: 16,
    8: 28,
    9: 24, 10: 28, 11: 28, 12: 28, 13: 28, 14: 28,
    15: 24, 16: 28, 17: 28, 18: 28, 19: 28, 20: 28,
    21: 24, 22: 28, 23: 28, 24: 28, 25: 28, 26: 28,
    27: 16,
    28: 34, 29: 34,
    30: 16,
}
for r, h in row_heights.items():
    ws.row_dimensions[r].height = h

# ── スタイル定義 ──────────────────────────────────────────
def side(style="thin", color="AAAAAA"):
    return Side(style=style, color=color)

border_all = Border(
    left=side(), right=side(), top=side(), bottom=side()
)
border_thick = Border(
    left=side("medium","555555"), right=side("medium","555555"),
    top=side("medium","555555"), bottom=side("medium","555555")
)
border_header = Border(
    left=side("medium","555555"), right=side("medium","555555"),
    top=side("medium","555555"), bottom=side("medium","555555")
)

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, size=10, color="000000", name="Meiryo UI"):
    return Font(bold=bold, size=size, color=color, name=name)

def align(h="center", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

# ── カラーパレット ─────────────────────────────────────────
TITLE_BG      = "1F3864"   # 濃紺
TITLE_FG      = "FFFFFF"
HEADER_BG     = "2E4A7A"
HEADER_FG     = "FFFFFF"
LABEL_BG      = "F2F2F2"

# 基本行動 = 青系
CAT1_HEAD     = "1565C0"
CAT1_HEAD_FG  = "FFFFFF"
CAT1_LABEL    = "BBDEFB"
CAT1_INPUT    = "E3F2FD"
CAT1_SCORE    = "90CAF9"

# 支援行動 = 緑系
CAT2_HEAD     = "2E7D32"
CAT2_HEAD_FG  = "FFFFFF"
CAT2_LABEL    = "C8E6C9"
CAT2_INPUT    = "E8F5E9"
CAT2_SCORE    = "A5D6A7"

# 付加価値 = オレンジ系
CAT3_HEAD     = "E65100"
CAT3_HEAD_FG  = "FFFFFF"
CAT3_LABEL    = "FFE0B2"
CAT3_INPUT    = "FFF3E0"
CAT3_SCORE    = "FFCC80"

TOTAL_BG      = "263238"
TOTAL_FG      = "FFFFFF"
RANK_A_BG     = "1B5E20"
RANK_B_BG     = "1565C0"
RANK_C_BG     = "F57F17"
RANK_D_BG     = "B71C1C"
RANK_FG       = "FFFFFF"
WARN_BG       = "FFCCCC"

# ── ユーティリティ ────────────────────────────────────────
def cell(row, col_letter):
    return ws[f"{col_letter}{row}"]

def merge_fill_font(
    r1, c1, r2, c2,
    text="", bg=None, fg="000000",
    bold=False, sz=10, h="center", v="center",
    wrap=False, bdr=None
):
    ref = f"{c1}{r1}:{c2}{r2}"
    ws.merge_cells(ref)
    c = ws[f"{c1}{r1}"]
    c.value = text
    if bg:
        c.fill = fill(bg)
    c.font = font(bold=bold, size=sz, color=fg)
    c.alignment = align(h=h, v=v, wrap=wrap)
    if bdr:
        # apply border to every cell in range
        from openpyxl.utils import range_boundaries
        min_col, min_row, max_col, max_row = range_boundaries(f"{c1}{r1}:{c2}{r2}")
        for row in ws.iter_rows(min_row=min_row, max_row=max_row,
                                 min_col=min_col, max_col=max_col):
            for cell_ in row:
                cell_.border = bdr

def apply_border_range(r1, c1, r2, c2, bdr):
    from openpyxl.utils import range_boundaries
    min_col, min_row, max_col, max_row = range_boundaries(f"{c1}{r1}:{c2}{r2}")
    for row in ws.iter_rows(min_row=min_row, max_row=max_row,
                             min_col=min_col, max_col=max_col):
        for c in row:
            c.border = bdr

# ════════════════════════════════════════════════════════
# ROW 2: タイトル
# ════════════════════════════════════════════════════════
merge_fill_font(2,"A",2,"H",
    text="部内貢献度評価シート　─　トヨオカ電気",
    bg=TITLE_BG, fg=TITLE_FG, bold=True, sz=16,
    bdr=border_thick)

# ════════════════════════════════════════════════════════
# ROW 3-6: 基本情報
# ════════════════════════════════════════════════════════
info_items = [
    (3, "社員名",   "C3"),
    (4, "所　属",   "C4"),
    (5, "評価期間", "C5"),
    (6, "評価者",   "C6"),
]

for row, label, val_cell in info_items:
    # ラベル B
    ws.merge_cells(f"B{row}:B{row}")
    c = ws[f"B{row}"]
    c.value = label
    c.fill = fill(HEADER_BG)
    c.font = font(bold=True, size=10, color="FFFFFF")
    c.alignment = align()
    c.border = border_all

    # 入力セル C-E
    ws.merge_cells(f"C{row}:E{row}")
    c2 = ws[f"C{row}"]
    c2.fill = fill("FFFFFF")
    c2.font = font(size=11)
    c2.alignment = align(h="left")
    c2.border = border_all

    # 右側 F-H
    ws.merge_cells(f"F{row}:H{row}")
    c3 = ws[f"F{row}"]
    c3.fill = fill(LABEL_BG)
    c3.border = border_all

# A列 基本情報エリア装飾
for r in range(2, 7):
    c = ws[f"A{r}"]
    c.fill = fill(TITLE_BG)
    c.border = border_all

# ════════════════════════════════════════════════════════
# 評価エリア共通ヘッダー（ROW 8）
# ════════════════════════════════════════════════════════
ws.merge_cells("A8:H8")
c = ws["A8"]
c.value = "　▼　評価入力エリア（各項目：1〜5点で入力してください）"
c.fill = fill(HEADER_BG)
c.font = font(bold=True, size=10, color="FFFFFF")
c.alignment = align(h="left")
c.border = border_thick

# ────────────────────────────────────────────────────────
# カテゴリブロック描画ヘルパー
# ────────────────────────────────────────────────────────
def draw_category(
    start_row, cat_num, cat_name, multiplier, max_score,
    items,
    head_bg, head_fg, label_bg, input_bg, score_bg
):
    """
    start_row : カテゴリヘッダー行
    items     : 評価項目名リスト（3項目）
    multiplier: スコア換算係数
    max_score : カテゴリ最大点
    """
    # --- カテゴリヘッダー行 ---
    ws.merge_cells(f"A{start_row}:H{start_row}")
    c = ws[f"A{start_row}"]
    c.value = f"  ■ カテゴリ {cat_num}：{cat_name}（配点 {max_score}点）"
    c.fill = fill(head_bg)
    c.font = font(bold=True, size=11, color=head_fg)
    c.alignment = align(h="left")
    apply_border_range(start_row,"A",start_row,"H", border_thick)

    # --- 列ヘッダー行 ---
    h_row = start_row + 1
    headers = [
        ("A", ""),
        ("B", "評価項目"),
        ("C", "評価基準（参考）"),
        ("D", "スコア\n（1〜5）"),
        ("E", ""),
        ("F", ""),
        ("G", ""),
        ("H", ""),
    ]
    col_header_items = [
        ("B", "評価項目",     label_bg,  "000000", False),
        ("C", "評価基準（参考）", label_bg, "000000", False),
        ("D", "スコア\n（1〜5）", head_bg,  head_fg, True),
    ]
    # 空セル
    for col in ["A","E","F","G","H"]:
        cc = ws[f"{col}{h_row}"]
        cc.fill = fill(label_bg)
        cc.border = border_all
    # 項目ヘッダー
    ws[f"B{h_row}"].value = "評価項目"
    ws[f"B{h_row}"].fill = fill(head_bg)
    ws[f"B{h_row}"].font = font(bold=True, size=10, color=head_fg)
    ws[f"B{h_row}"].alignment = align()
    ws[f"B{h_row}"].border = border_all

    ws.merge_cells(f"C{h_row}:F{h_row}")
    ws[f"C{h_row}"].value = "評価基準（参考）"
    ws[f"C{h_row}"].fill = fill(head_bg)
    ws[f"C{h_row}"].font = font(bold=True, size=10, color=head_fg)
    ws[f"C{h_row}"].alignment = align()
    ws[f"C{h_row}"].border = border_all

    ws[f"G{h_row}"].value = "スコア（1〜5）"
    ws[f"G{h_row}"].fill = fill(head_bg)
    ws[f"G{h_row}"].font = font(bold=True, size=10, color=head_fg)
    ws[f"G{h_row}"].alignment = align(wrap=True)
    ws[f"G{h_row}"].border = border_all

    ws[f"H{h_row}"].value = "換算点"
    ws[f"H{h_row}"].fill = fill(head_bg)
    ws[f"H{h_row}"].font = font(bold=True, size=10, color=head_fg)
    ws[f"H{h_row}"].alignment = align()
    ws[f"H{h_row}"].border = border_all

    # 評価基準テキスト（参考）
    criteria = {
        "期限遵守":   "5:常に守る  4:ほぼ守る  3:概ね守る  2:遅れ有  1:頻繁に遅延",
        "報連相":     "5:適切・迅速  4:ほぼ適切  3:概ね実施  2:不足有  1:ほとんどなし",
        "ルール遵守": "5:完全遵守  4:ほぼ遵守  3:概ね遵守  2:違反有  1:頻繁に違反",
        "他部署応援": "5:積極的に支援  4:求めに応じる  3:指示で動く  2:消極的  1:非協力",
        "部内支援":   "5:率先して支援  4:依頼で快諾  3:指示で動く  2:消極的  1:非協力",
        "教育・フォロー": "5:積極指導  4:依頼対応  3:指示で対応  2:消極的  1:ほぼなし",
        "改善提案":   "5:複数実施・採用  4:提案有  3:1件提出  2:検討中のみ  1:なし",
        "業務効率化": "5:大幅改善  4:改善有  3:一部改善  2:検討中  1:変化なし",
        "付加活動":   "5:複数の貢献  4:1つ以上  3:指示で参加  2:消極的参加  1:なし",
    }

    score_cells = []
    for i, item in enumerate(items):
        r = start_row + 2 + i
        ws[f"A{r}"].fill = fill(label_bg)
        ws[f"A{r}"].border = border_all

        ws[f"B{r}"].value = item
        ws[f"B{r}"].fill = fill(label_bg)
        ws[f"B{r}"].font = font(bold=True, size=10)
        ws[f"B{r}"].alignment = align(h="left", wrap=True)
        ws[f"B{r}"].border = border_all

        ws.merge_cells(f"C{r}:F{r}")
        ws[f"C{r}"].value = criteria.get(item, "")
        ws[f"C{r}"].fill = fill(input_bg)
        ws[f"C{r}"].font = font(size=8, color="444444")
        ws[f"C{r}"].alignment = align(h="left", wrap=True)
        ws[f"C{r}"].border = border_all

        # スコア入力セル
        sc = ws[f"G{r}"]
        sc.fill = fill("FFFFFF")
        sc.font = font(bold=True, size=13)
        sc.alignment = align()
        sc.border = Border(
            left=side("medium", head_bg),
            right=side("medium", head_bg),
            top=side("medium", head_bg),
            bottom=side("medium", head_bg),
        )
        score_cells.append(f"G{r}")

        # 個別換算（参考表示：score/5*max/3 的な表示は不要、平均で行う）
        ws[f"H{r}"].fill = fill(score_bg)
        ws[f"H{r}"].font = font(size=9, color="555555")
        ws[f"H{r}"].alignment = align()
        ws[f"H{r}"].border = border_all
        ws[f"H{r}"].value = "―"

    # --- プルダウン設定 ---
    dv = DataValidation(
        type="list", formula1='"1,2,3,4,5"',
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="入力エラー",
        error="1〜5の整数を選択してください",
        showInputMessage=True,
        promptTitle="スコア入力",
        prompt="1（低）〜5（高）から選択"
    )
    ws.add_data_validation(dv)
    for sc_ref in score_cells:
        dv.add(ws[sc_ref])

    # --- 集計行 ---
    sum_row = start_row + 5
    ws.row_dimensions[sum_row].height = 30
    ws.merge_cells(f"A{sum_row}:B{sum_row}")
    ws[f"A{sum_row}"].value = f"カテゴリ{cat_num} 合計"
    ws[f"A{sum_row}"].fill = fill(score_bg)
    ws[f"A{sum_row}"].font = font(bold=True, size=10)
    ws[f"A{sum_row}"].alignment = align()
    apply_border_range(sum_row,"A",sum_row,"B", border_all)

    avg_formula = (
        f"=IF(COUNTA({score_cells[0]}:{score_cells[2]})=3,"
        f"AVERAGE({score_cells[0]}:{score_cells[2]}),\"未入力\")"
    )
    ws.merge_cells(f"C{sum_row}:D{sum_row}")
    ws[f"C{sum_row}"].value = avg_formula
    ws[f"C{sum_row}"].fill = fill(score_bg)
    ws[f"C{sum_row}"].font = font(bold=True, size=10)
    ws[f"C{sum_row}"].alignment = align()
    ws[f"C{sum_row}"].number_format = "0.00"
    apply_border_range(sum_row,"C",sum_row,"D", border_all)

    ws[f"E{sum_row}"].value = f"　×{multiplier}　="
    ws[f"E{sum_row}"].fill = fill(score_bg)
    ws[f"E{sum_row}"].font = font(bold=True, size=10)
    ws[f"E{sum_row}"].alignment = align()
    ws[f"E{sum_row}"].border = border_all

    score_formula = (
        f'=IF(ISNUMBER(C{sum_row}),'
        f'ROUND(C{sum_row}*{multiplier},1),"―")'
    )
    ws.merge_cells(f"F{sum_row}:H{sum_row}")
    ws[f"F{sum_row}"].value = score_formula
    ws[f"F{sum_row}"].fill = fill(head_bg)
    ws[f"F{sum_row}"].font = font(bold=True, size=14, color=head_fg)
    ws[f"F{sum_row}"].alignment = align()
    apply_border_range(sum_row,"F",sum_row,"H", border_thick)

    return f"F{sum_row}"   # カテゴリスコアセル参照を返す


# ════════════════════════════════════════════════════════
# 3つのカテゴリを描画
# ════════════════════════════════════════════════════════
cat1_score_ref = draw_category(
    start_row=9, cat_num=1,
    cat_name="基本行動", multiplier=8, max_score=40,
    items=["期限遵守","報連相","ルール遵守"],
    head_bg=CAT1_HEAD, head_fg=CAT1_HEAD_FG,
    label_bg=CAT1_LABEL, input_bg=CAT1_INPUT, score_bg=CAT1_SCORE,
)

cat2_score_ref = draw_category(
    start_row=16, cat_num=2,
    cat_name="支援行動", multiplier=6, max_score=30,
    items=["他部署応援","部内支援","教育・フォロー"],
    head_bg=CAT2_HEAD, head_fg=CAT2_HEAD_FG,
    label_bg=CAT2_LABEL, input_bg=CAT2_INPUT, score_bg=CAT2_SCORE,
)

cat3_score_ref = draw_category(
    start_row=23, cat_num=3,
    cat_name="付加価値", multiplier=6, max_score=30,
    items=["改善提案","業務効率化","付加活動"],
    head_bg=CAT3_HEAD, head_fg=CAT3_HEAD_FG,
    label_bg=CAT3_LABEL, input_bg=CAT3_INPUT, score_bg=CAT3_SCORE,
)

# ════════════════════════════════════════════════════════
# ROW 27: スペーサー
# ════════════════════════════════════════════════════════
for col in ["A","B","C","D","E","F","G","H"]:
    ws[f"{col}27"].fill = fill("EEEEEE")
    ws[f"{col}27"].border = border_all

# ════════════════════════════════════════════════════════
# ROW 28: 合計スコア
# ════════════════════════════════════════════════════════
ws.merge_cells("A28:D28")
ws["A28"].value = "　◆　合計スコア（100点満点）"
ws["A28"].fill = fill(TOTAL_BG)
ws["A28"].font = font(bold=True, size=13, color=TOTAL_FG)
ws["A28"].alignment = align(h="left")
apply_border_range(28,"A",28,"D", border_thick)

total_formula = (
    f'=IF(AND(ISNUMBER({cat1_score_ref}),'
    f'ISNUMBER({cat2_score_ref}),'
    f'ISNUMBER({cat3_score_ref})),'
    f'{cat1_score_ref}+{cat2_score_ref}+{cat3_score_ref},"未入力あり")'
)
ws.merge_cells("E28:H28")
ws["E28"].value = total_formula
ws["E28"].fill = fill(TOTAL_BG)
ws["E28"].font = font(bold=True, size=20, color="FFD700")
ws["E28"].alignment = align()
apply_border_range(28,"E",28,"H", border_thick)

# ════════════════════════════════════════════════════════
# ROW 29: 評価ランク
# ════════════════════════════════════════════════════════
ws.merge_cells("A29:D29")
ws["A29"].value = "　◆　評価ランク"
ws["A29"].fill = fill(TOTAL_BG)
ws["A29"].font = font(bold=True, size=13, color=TOTAL_FG)
ws["A29"].alignment = align(h="left")
apply_border_range(29,"A",29,"D", border_thick)

rank_formula = (
    '=IF(NOT(ISNUMBER(E28)),"―",'
    'IF(E28>=80,"A",'
    'IF(E28>=65,"B",'
    'IF(E28>=50,"C","D"))))'
)
ws.merge_cells("E29:H29")
ws["E29"].value = rank_formula
ws["E29"].font = font(bold=True, size=24, color="FFFFFF")
ws["E29"].alignment = align()
apply_border_range(29,"E",29,"H", border_thick)

# 条件付き書式の代わりに、ランク背景は後でVBAなしで固定表示
# ランクセルはデフォルト暗背景に（実際の値で色が変わるのはVBA必要のため濃いめの共通色）
ws["E29"].fill = fill("37474F")

# ════════════════════════════════════════════════════════
# ROW 30: 凡例・注記
# ════════════════════════════════════════════════════════
for col in ["A","B","C","D","E","F","G","H"]:
    ws[f"{col}30"].fill = fill("EEEEEE")

ws.merge_cells("A30:H30")
ws["A30"].value = (
    "【ランク基準】  A：80点以上　B：65〜79点　C：50〜64点　D：49点以下　　"
    "※スコア未入力の場合、合計・ランクは「未入力あり」または「―」と表示されます"
)
ws["A30"].fill = fill("EEEEEE")
ws["A30"].font = font(size=8, color="444444")
ws["A30"].alignment = align(h="left", wrap=True)
ws["A30"].border = border_all
ws.row_dimensions[30].height = 28

# ════════════════════════════════════════════════════════
# 印刷設定
# ════════════════════════════════════════════════════════
ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT
ws.page_setup.fitToPage = True
ws.page_setup.fitToHeight = 1
ws.page_setup.fitToWidth = 1
ws.print_area = "A1:H30"
ws.oddHeader.center.text = "部内貢献度評価シート　トヨオカ電気"
ws.oddFooter.center.text = "Page &P / &N"

# ════════════════════════════════════════════════════════
# 保存
# ════════════════════════════════════════════════════════
out_path = "/home/user/X-/トヨオカ電気_部内貢献度評価シート.xlsx"
wb.save(out_path)
print(f"Saved: {out_path}")
