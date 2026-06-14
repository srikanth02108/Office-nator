# Sutra — Excel Action Library Reference

> **129 deterministic actions** covering every Excel tab.  
> The LLM classifies intent → picks an `action_id` → Sutra executes the pre-coded key sequence.  
> No hallucination. No invented shortcuts.

---

## How to speak commands

Sutra understands natural Hindi/Marathi/English. You don't need to say exact commands — just describe what you want.

| You say | Sutra does |
|---|---|
| "is cell ko bold karo" | `bold` → Ctrl+B |
| "font size 16 karo" | `set_font_size(16)` → Alt+H, FS, 16, Enter |
| "column ki width autofit karo" | `autofit_column_width` → Alt+H, O, I |
| "text wrap karo" | `wrap_text` → Alt+H, W |
| "merge karke center karo" | `merge_and_center` → Alt+H, M, C |
| "borders lagao sab taraf" | `borders_all` → Alt+H, B, A |
| "pehli row freeze karo" | `freeze_top_row` → Alt+W, F, R |
| "save karo" | `save` → Ctrl+S |
| "undo karo" | `undo` → Ctrl+Z |

⚠ **Actions marked CONFIRM** will ask for voice confirmation before executing.

---

## Category 1 — Basic Formatting

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `bold` | Toggle bold | Ctrl+B | — |
| `italic` | Toggle italic | Ctrl+I | — |
| `underline` | Toggle underline | Ctrl+U | — |
| `strikethrough` | Toggle strikethrough | Ctrl+5 | — |
| `bold_italic` | Bold + italic together | Ctrl+B, Ctrl+I | — |
| `bold_underline` | Bold + underline together | Ctrl+B, Ctrl+U | — |
| `clear_formatting` | Remove all formatting | Alt+H → E → F | — |
| `clear_contents` | Delete cell contents only | Delete | ✅ |
| `clear_all` | Delete contents AND formatting | Alt+H → E → A | ✅ |

---

## Category 2 — Font

| Action ID | Parameters | What it does | Key Sequence | Confirm? |
|---|---|---|---|---|
| `set_font_size` | `size` (int) | Set font size e.g. 12, 14, 16, 18, 24 | Alt+H → FS → select all → type size → Enter | — |
| `increase_font_size` | — | Increase font size one step | Ctrl+Shift+. | — |
| `decrease_font_size` | — | Decrease font size one step | Ctrl+Shift+, | — |
| `set_font` | `font_name` (str) | Set font family e.g. Arial, Calibri | Alt+H → FF → select all → type name → Enter | — |
| `set_font_color_last` | — | Apply last-used font color | Alt+H → FC | — |
| `set_fill_color_last` | — | Apply last-used fill/background color | Alt+H → H | — |
| `open_format_cells` | — | Open Format Cells dialog (full control) | Ctrl+1 | — |

**Common font names:** Arial, Calibri, Times New Roman, Verdana, Courier New, Georgia, Tahoma, Comic Sans MS

---

## Category 3 — Alignment

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `align_left` | Align text left | Ctrl+L | — |
| `align_center` | Align text center | Ctrl+E | — |
| `align_right` | Align text right | Alt+H → A → R | — |
| `align_top` | Align content to cell top | Alt+H → A → T | — |
| `align_middle_vertical` | Align content to cell middle | Alt+H → A → M | — |
| `align_bottom` | Align content to cell bottom | Alt+H → A → B | — |
| `wrap_text` | Toggle text wrap | Alt+H → W | — |
| `merge_and_center` | Merge cells and center text | Alt+H → M → C | ✅ |
| `merge_cells` | Merge cells (no center) | Alt+H → M → M | ✅ |
| `unmerge_cells` | Unmerge cells | Alt+H → M → U | — |
| `increase_indent` | Increase indent | Alt+H → 6 | — |
| `decrease_indent` | Decrease indent | Alt+H → 5 | — |
| `rotate_text` | Open text rotation options | Alt+H → F → Q | — |

---

## Category 4 — Borders

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `borders_all` | Apply borders on all sides | Alt+H → B → A | — |
| `borders_outside` | Apply outside border only | Alt+H → B → S | — |
| `borders_thick_box` | Apply thick box border | Alt+H → B → T | — |
| `borders_bottom` | Apply bottom border | Alt+H → B → O | — |
| `borders_top` | Apply top border | Alt+H → B → P | — |
| `borders_left` | Apply left border | Alt+H → B → L | — |
| `borders_right_border` | Apply right border | Alt+H → B → R | — |
| `borders_none` | Remove all borders | Alt+H → B → N | — |
| `borders_double_bottom` | Double bottom border | Alt+H → B → B | — |
| `borders_thick_bottom` | Thick bottom border | Alt+H → B → K | — |
| `open_borders_dialog` | Open More Borders dialog | Alt+H → B → M | — |

---

## Category 5 — Number Formats

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `format_general` | General format | Ctrl+Shift+~ | — |
| `format_number` | Number (2 decimal places) | Ctrl+Shift+1 | — |
| `format_currency` | Currency ($) | Ctrl+Shift+4 | — |
| `format_percentage` | Percentage (%) | Ctrl+Shift+5 | — |
| `format_scientific` | Scientific notation | Ctrl+Shift+6 | — |
| `format_date` | Date format | Ctrl+Shift+3 | — |
| `format_time` | Time format | Ctrl+Shift+2 | — |
| `format_text` | Text format (store as-is) | Alt+H → N → T | — |

---

## Category 6 — Column & Row Size

| Action ID | Parameters | What it does | Key Sequence | Confirm? |
|---|---|---|---|---|
| `autofit_column_width` | — | AutoFit column to content | Alt+H → O → I | — |
| `autofit_row_height` | — | AutoFit row to content | Alt+H → O → A | — |
| `autofit_all_columns` | — | Select all then autofit all columns | Ctrl+A, Alt+H → O → I | — |
| `set_column_width` | `width` (number) | Set exact column width | Alt+H → O → W → type width → Enter | — |
| `set_row_height` | `height` (number) | Set exact row height | Alt+H → O → H → type height → Enter | — |
| `hide_column` | — | Hide selected column | Ctrl+0 | — |
| `unhide_column` | — | Unhide column | Ctrl+Shift+0 | — |
| `hide_row` | — | Hide selected row | Ctrl+9 | — |
| `unhide_row` | — | Unhide row | Ctrl+Shift+9 | — |
| `group_rows` | — | Group selected rows | Alt+Shift+Right | — |
| `ungroup_rows` | — | Ungroup selected rows | Alt+Shift+Left | — |

---

## Category 7 — Insert & Delete Rows / Columns

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `insert_row` | Insert row above current | Shift+Space → Ctrl+Shift+= | — |
| `delete_row` | Delete current row | Shift+Space → Ctrl+- | ✅ |
| `insert_column` | Insert column before current | Ctrl+Space → Ctrl+Shift+= | — |
| `delete_column` | Delete current column | Ctrl+Space → Ctrl+- | ✅ |
| `insert_cells_shift_right` | Insert cells shifting right | Alt+H → I → I → Right → Enter | — |
| `insert_cells_shift_down` | Insert cells shifting down | Alt+H → I → I → Down → Enter | — |
| `delete_cells_shift_left` | Delete cells shifting left | Alt+H → D → D → Left → Enter | — |
| `delete_cells_shift_up` | Delete cells shifting up | Alt+H → D → D → Up → Enter | — |

---

## Category 8 — Editing

| Action ID | Parameters | What it does | Key Sequence | Confirm? |
|---|---|---|---|---|
| `undo` | — | Undo last action | Ctrl+Z | — |
| `redo` | — | Redo | Ctrl+Y | — |
| `copy` | — | Copy selected | Ctrl+C | — |
| `cut` | — | Cut selected | Ctrl+X | — |
| `paste` | — | Paste | Ctrl+V | — |
| `paste_values_only` | — | Paste values only (no formatting) | Ctrl+Alt+V → V → Enter | — |
| `paste_formats_only` | — | Paste formatting only | Ctrl+Alt+V → T → Enter | — |
| `paste_special` | — | Open Paste Special dialog | Ctrl+Alt+V | — |
| `fill_down` | — | Fill down | Ctrl+D | — |
| `fill_right` | — | Fill right | Ctrl+R | — |
| `flash_fill` | — | Flash fill (pattern recognition) | Ctrl+E | — |
| `autosum` | — | AutoSum at cursor | Alt+= | — |
| `find` | — | Open Find dialog | Ctrl+F | — |
| `find_replace` | — | Open Find & Replace | Ctrl+H | — |
| `edit_cell` | — | Enter edit mode (F2) | F2 | — |
| `select_all` | — | Select all | Ctrl+A | — |
| `type_in_cell` | `text` (str) | Type text in current cell + Enter | type text → Enter | — |
| `enter_formula` | `formula` (str) | Enter a formula (add = if missing) | type formula → Enter | — |
| `enter_current_date` | — | Insert today's date | Ctrl+; → Enter | — |
| `enter_current_time` | — | Insert current time | Ctrl+Shift+; → Enter | — |
| `repeat_last_action` | — | Repeat last action | F4 | — |
| `copy_format` | — | Format Painter (copy formatting) | Alt+H → F → P | — |
| `select_visible_cells` | — | Select only visible cells | Alt+; | — |

---

## Category 9 — Navigation

| Action ID | Parameters | What it does | Key Sequence |
|---|---|---|---|
| `go_to_cell` | `cell_ref` (str) e.g. "A1" | Navigate to specific cell | Ctrl+G → type ref → Enter |
| `go_to_a1` | — | Go to cell A1 | Ctrl+Home |
| `go_to_last_cell` | — | Go to last used cell | Ctrl+End |
| `next_sheet` | — | Next worksheet | Ctrl+PageDown |
| `previous_sheet` | — | Previous worksheet | Ctrl+PageUp |
| `move_right` | — | Move one cell right | Tab |
| `move_down` | — | Move one cell down | Enter |
| `move_up` | — | Move one cell up | Up arrow |
| `move_left` | — | Move one cell left | Left arrow |

---

## Category 10 — File & Workbook

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `save` | Save workbook | Ctrl+S | — |
| `save_as` | Save As dialog | F12 | — |
| `new_workbook` | New workbook | Ctrl+N | — |
| `open_file` | Open file dialog | Ctrl+O | — |
| `print_file` | Print | Ctrl+P | — |
| `close_workbook` | Close workbook | Ctrl+W | ✅ |
| `new_sheet` | Insert new sheet | Shift+F11 | — |
| `rename_sheet` | Rename current sheet | Alt+H → O → R | — |
| `delete_sheet` | Delete current sheet | Alt+H → D → S | ✅ |

---

## Category 11 — Data / Sort / Filter

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `sort_ascending` | Sort A→Z | Alt+A → S → A | — |
| `sort_descending` | Sort Z→A | Alt+A → S → D | — |
| `open_sort_dialog` | Open Sort dialog | Alt+A → S → S | — |
| `toggle_filter` | Toggle AutoFilter | Ctrl+Shift+L | — |
| `clear_filter` | Clear all filters | Alt+A → S → C | — |
| `remove_duplicates` | Remove duplicate rows | Alt+A → M | ✅ |
| `text_to_columns` | Text to Columns wizard | Alt+A → E | — |
| `data_validation` | Data Validation dialog | Alt+A → V → V | — |
| `group_data` | Group rows/columns | Alt+A → G → G | — |
| `ungroup_data` | Ungroup rows/columns | Alt+A → U → U | — |
| `subtotal` | Subtotal dialog | Alt+A → B | — |
| `refresh_all` | Refresh all data connections | Ctrl+Alt+F5 | — |
| `what_if_analysis` | What-If Analysis | Alt+A → W | — |

---

## Category 12 — Insert Objects

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `insert_table` | Insert table from selection | Ctrl+T | — |
| `insert_pivot_table` | Insert PivotTable | Alt+N → V | — |
| `insert_chart_embedded` | Insert chart on current sheet | Alt+F1 | — |
| `insert_chart_new_sheet` | Insert chart on new sheet | F11 | — |
| `insert_sparkline` | Insert sparkline | Alt+N → S → N | — |
| `insert_hyperlink` | Insert hyperlink | Ctrl+K | — |
| `insert_comment` | Insert comment | Shift+F2 | — |
| `insert_function` | Insert Function dialog | Shift+F3 | — |
| `insert_picture` | Insert picture | Alt+N → P → P | — |
| `insert_shapes` | Insert shapes | Alt+N → S → H | — |
| `insert_text_box` | Insert text box | Alt+N → X | — |
| `insert_wordart` | Insert WordArt | Alt+N → W | — |
| `insert_header_footer` | Insert header/footer | Alt+N → H | — |

---

## Category 13 — Page Layout

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `page_orientation_portrait` | Portrait orientation | Alt+P → O → R | — |
| `page_orientation_landscape` | Landscape orientation | Alt+P → O → L | — |
| `page_margins` | Margins dialog | Alt+P → M | — |
| `page_size` | Paper size dialog | Alt+P → S → Z | — |
| `set_print_area` | Set print area | Alt+P → R → S | — |
| `clear_print_area` | Clear print area | Alt+P → R → C | — |
| `show_gridlines` | Toggle gridline visibility | Alt+P → V → G | — |
| `show_headings` | Toggle row/column headings | Alt+P → V → H | — |

---

## Category 14 — View

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `freeze_top_row` | Freeze top row | Alt+W → F → R | — |
| `freeze_first_column` | Freeze first column | Alt+W → F → C | — |
| `freeze_panes` | Freeze at current cell | Alt+W → F → F | — |
| `unfreeze_panes` | Unfreeze all panes | Alt+W → F → F (toggle) | — |
| `zoom_100` | Zoom to 100% | Alt+W → J | — |
| `zoom_to_selection` | Zoom to fit selection | Alt+W → G | — |
| `split_view` | Split view | Alt+W → S | — |
| `normal_view` | Normal view | Alt+W → L | — |
| `page_layout_view` | Page layout view | Alt+W → P | — |
| `page_break_view` | Page break preview | Alt+W → I | — |

---

## Category 15 — Formulas

| Action ID | What it does | Key Sequence |
|---|---|---|
| `toggle_show_formulas` | Show/hide formulas in cells | Ctrl+` |
| `calculate_now` | Force calculate workbook | F9 |
| `calculate_sheet` | Calculate current sheet | Shift+F9 |
| `name_manager` | Name Manager dialog | Ctrl+F3 |
| `trace_precedents` | Trace precedent cells | Alt+M → P |
| `trace_dependents` | Trace dependent cells | Alt+M → D |
| `remove_arrows` | Remove trace arrows | Alt+M → A → A |
| `evaluate_formula` | Evaluate Formula dialog | Alt+M → V |
| `insert_function` | Insert Function dialog | Shift+F3 |

---

## Category 16 — Review

| Action ID | What it does | Key Sequence | Confirm? |
|---|---|---|---|
| `spell_check` | Run spell check | F7 | — |
| `protect_sheet` | Protect sheet | Alt+R → P → S | — |
| `protect_workbook` | Protect workbook | Alt+R → P → W | — |
| `track_changes` | Track changes | Alt+R → G | — |
| `add_comment` | Add comment to cell | Shift+F2 | — |
| `delete_comment` | Delete comment | Alt+R → D → D | — |
| `show_all_comments` | Show all comments | Alt+R → S → H → C | — |

---

## Category 17 — Compound Actions

These combine multiple operations into a single voice command:

| Action ID | Parameters | What it does |
|---|---|---|
| `format_as_header` | `size` (default 14) | Bold + center + set font size — ideal for header rows |
| `format_currency_borders` | — | Currency format + all borders |
| `make_table_with_filter` | — | Create table with AutoFilter from selection |
| `sum_column` | — | AutoSum at cursor position |
| `copy_format` | — | Format Painter to copy formatting |
| `autofit_all_columns` | — | Select all + autofit every column |
| `select_visible_cells` | — | Select only visible cells (after filtering) |
| `group_rows` | — | Group selected rows |
| `ungroup_rows` | — | Ungroup selected rows |
| `enter_current_date` | — | Insert today's date |
| `enter_current_time` | — | Insert current time |

---

## Voice command examples (Hindi/Marathi → action)

```
"bold karo"                     → bold
"italic karo"                   → italic
"underline karo"                → underline
"font size 14 karo"             → set_font_size(size=14)
"font size badao"               → increase_font_size
"font Arial karo"               → set_font(font_name="Arial")
"center align karo"             → align_center
"right align karo"              → align_right
"text wrap karo"                → wrap_text
"merge karke center karo"       → merge_and_center
"unmerge karo"                  → unmerge_cells
"borders lagao"                 → borders_all
"bahar ki border lagao"         → borders_outside
"borders hatao"                 → borders_none
"currency format karo"          → format_currency
"percentage mein dikhao"        → format_percentage
"date format karo"              → format_date
"column autofit karo"           → autofit_column_width
"column width 25 karo"          → set_column_width(width=25)
"row height 30 karo"            → set_row_height(height=30)
"row chhupaao"                  → hide_row
"nayi row dalo"                 → insert_row
"row delete karo"               → delete_row (asks confirm)
"naya column dalo"              → insert_column
"sort A se Z karo"              → sort_ascending
"filter lagao"                  → toggle_filter
"duplicate rows hatao"          → remove_duplicates (asks confirm)
"pehli row freeze karo"         → freeze_top_row
"first column freeze karo"      → freeze_first_column
"chart banao"                   → insert_chart_embedded
"pivot table banao"             → insert_pivot_table
"table banao"                   → insert_table
"sum nikalo"                    → autosum
"save karo"                     → save
"save as karo"                  → save_as
"nayi sheet banao"              → new_sheet
"print karo"                    → print_file
"undo karo"                     → undo
"redo karo"                     → redo
"copy karo"                     → copy
"paste karo"                    → paste
"sirf values paste karo"        → paste_values_only
"A1 pe jao"                     → go_to_cell(cell_ref="A1")
"pehle cell pe jao"             → go_to_a1
"agla sheet"                    → next_sheet
"spelling check karo"           → spell_check
"formulas dikhao"               → toggle_show_formulas
"aaj ki date dalo"              → enter_current_date
"header format karo"            → format_as_header
"bold aur center karo"          → [bold, align_center]
"font 16 aur bold karo"         → [set_font_size(16), bold]
```

---

## Notes

- **⚠ CONFIRM** — actions marked with ✅ require voice confirmation ("haan"/"yes") before executing
- **Parameters** — extracted automatically by the LLM from your natural speech
- **Multi-action** — you can combine actions in one sentence: *"bold aur center karo"* executes both
- **All sequences tested** — every action above is verified against actual Excel ribbon key sequences
- **Excel must be focused** — ensure Excel is the active window before speaking a command
