using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Ninely.SudokuEngine;

namespace PackGenerator
{
    class Program
    {
        static Dictionary<string, (string en, string he, string ar)> HintTemplates = new()
        {
            ["HINT_FULL_HOUSE_ROW"] = (
                "Only one cell is empty in row {1}. The missing number is {0}.",
                "בשורה {1} נשארה רק משבצת ריקה אחת. המספר החסר הוא {0}.",
                "في الصف {1} بقيت خانة فارغة واحدة فقط. الرقم الناقص هو {0}."
            ),
            ["HINT_FULL_HOUSE_COL"] = (
                "Only one cell is empty in column {1}. The missing number is {0}.",
                "בעמודה {1} נשארה רק משבצת ריקה אחת. המספר החסר הוא {0}.",
                "في العمود {1} بقيت خانة فارغة واحدة فقط. الرقم الناقص هو {0}."
            ),
            ["HINT_FULL_HOUSE_BOX"] = (
                "Only one cell is empty in box {1}. The missing number is {0}.",
                "בריבוע {1} נשארה רק משבצת ריקה אחת. המספר החסר הוא {0}.",
                "في المربع {1} بقيت خانة فارغة واحدة فقط. الرقم الناقص هو {0}."
            ),
            ["HINT_HIDDEN_SINGLE_ROW"] = (
                "In row {1}, {0} can't go in any other cell because of the {0}s that cross it. This is the only place left for it!",
                "בשורה {1}, המספר {0} לא יכול להופיע בשאר המשבצות בגלל חסימות בשורות ובעמודות החוצות. לכן זו המשבצת היחידה שנותרה עבורו!",
                "في الصف {1}، لا يمكن وضع الرقم {0} في الخانات الأخرى بسبب الأرقام {0} المتقاطعة. لذا هذه هي الخانة الوحيدة المتبقية له!"
            ),
            ["HINT_HIDDEN_SINGLE_COL"] = (
                "In column {1}, {0} can't go in any other cell because of the {0}s that cross it. This is the only place left for it!",
                "בעמודה {1}, המספר {0} לא יכול להופיע בשאר המשבצות בגלל חסימות בשורות ובעמודות החוצות. לכן זו המשבצת היחידה שנותרה עבורו!",
                "في العمود {1}، لا يمكن وضع الرقم {0} في الخانات الأخرى بسبب الأرقام {0} المتقاطعة. لذا هذه هي الخانة الوحيدة المتبقية له!"
            ),
            ["HINT_HIDDEN_SINGLE_BOX"] = (
                "In box {1}, {0} can't go in any other cell because of the {0}s that cross it. This is the only place left for it!",
                "בריבוע {1}, המספר {0} לא יכול להופיע בשאר המשבצות בגלל חסימות בשורות ובעמודות החוצות. לכן זו המשבצת היחידה שנותרה עבורו!",
                "في المربع {1}، لا يمكن وضع الرقم {0} في الخانات الأخرى بسبب الأرقام {0} المتقاطعة. لذا هذه هي الخانة الوحيدة المتبقية له!"
            ),
            ["HINT_NAKED_SINGLE"] = (
                "Row {1}, column {2}: every number except {0} already appears in this cell's row, column or box.",
                "שורה {1}, עמודה {2}: כל המספרים מלבד {0} כבר מופיעים בשורה, בעמודה או בריבוע של המשבצת הזו.",
                "الصف {1}، العمود {2}: كل الأرقام ما عدا {0} موجودة بالفعل في صف هذه الخانة أو عمودها أو مربعها."
            ),
            ["HINT_POINTING_PAIR"] = (
                "Pointing pair: inside a box, {3} can only be on {4} {5}, so it is removed from the rest of that line. That leaves {0} at row {1}, column {2}.",
                "זוג מצביע: בתוך ריבוע, {3} יכול להיות רק ב{4} {5}, ולכן הוא יוצא משאר הקו. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "زوج مُشير: داخل مربع، لا يمكن أن يكون {3} إلا في {4} {5}، لذا يُستبعد من باقي هذا الخط. فيبقى {0} في الصف {1}، العمود {2}."
            ),
            ["HINT_BOX_LINE"] = (
                "Box-line: on its line, {3} can only be inside {4} {5}, so it is removed from the other cells of that box. That leaves {0} at row {1}, column {2}.",
                "ריבוע-קו: בקו שלו, {3} יכול להיות רק בתוך {4} {5}, ולכן הוא יוצא משאר המשבצות של הריבוע. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "مربع-خط: على خطه، لا يمكن أن يكون {3} إلا داخل {4} {5}، لذا يُستبعد من باقي خانات هذا المربع. فيبقى {0} في الصف {1}، العمود {2}."
            )
        };

        static Dictionary<string, object> BuildHintData(SmartHintStep hint)
        {
            var hintData = new Dictionary<string, object>();
            if (hint == null) return hintData;

            hintData["targetRow"] = hint.TargetCell.Row;
            hintData["targetCol"] = hint.TargetCell.Col;
            hintData["targetDigit"] = hint.TargetDigit;
            hintData["technique"] = hint.Technique.ToString();
            hintData["localizationKey"] = hint.LocalizationKey ?? "";

            var argsList = new List<object>();
            if (hint.LocalizationArgs != null)
            {
                foreach (var a in hint.LocalizationArgs) argsList.Add(a?.ToString() ?? "");
            }
            hintData["localizationArgs"] = argsList;

            if (HintTemplates.TryGetValue(hint.LocalizationKey ?? "", out var tpl) && hint.LocalizationArgs != null)
            {
                hintData["explanation"] = new Dictionary<string, string>
                {
                    ["en"] = string.Format(tpl.en, hint.LocalizationArgs),
                    ["he"] = string.Format(tpl.he, hint.LocalizationArgs),
                    ["ar"] = string.Format(tpl.ar, hint.LocalizationArgs)
                };
            }

            var highlights = new List<object>();
            foreach (var h in hint.HighlightCells)
            {
                highlights.Add(new { row = h.Row, col = h.Col });
            }
            hintData["highlights"] = highlights;
            return hintData;
        }

        static void Main(string[] args)
        {
            var generator = new SudokuGenerator();
            var solver = new SmartHintSolver();

            var pack = new Dictionary<string, object>();
            pack["sourceCommit"] = "4fa5c68";
            pack["schemaVersion"] = 1;
            pack["generatedAt"] = "2026-11-08T13:55:00Z";

            var days = new Dictionary<string, object>();
            var startDate = new DateTime(2026, 11, 8);

            for (int i = 0; i < 30; i++)
            {
                var curDate = startDate.AddDays(i);
                string dateKey = curDate.ToString("yyyy-MM-dd");
                int seed = int.Parse(curDate.ToString("yyyyMMdd"));

                SudokuPuzzle puzzle = null;
                int attemptSeed = seed;
                while (puzzle == null)
                {
                    if (generator.TryGenerate(DifficultyLevel.Medium, attemptSeed, out var p))
                    {
                        int[] g = new int[81];
                        for (int c = 0; c < 81; c++) g[c] = p.Givens[c] - '0';
                        if (SudokuGenerator.CountSolutions(g, 2) == 1)
                        {
                            puzzle = p;
                            break;
                        }
                    }
                    attemptSeed++;
                }

                int[] grid = new int[81];
                for (int c = 0; c < 81; c++) grid[c] = puzzle.Givens[c] - '0';
                var hint = solver.FindNextStep(grid, teaching: true) ?? solver.FindNextStep(grid, teaching: false);
                var hintData = BuildHintData(hint);

                var dayEntry = new Dictionary<string, object>();
                dayEntry["date"] = dateKey;
                dayEntry["seed"] = seed;
                dayEntry["difficulty"] = puzzle.Difficulty.ToString();
                dayEntry["puzzle"] = puzzle.Givens;
                dayEntry["solution"] = puzzle.Solution;
                dayEntry["clueCount"] = puzzle.ClueCount;
                dayEntry["hardestTechnique"] = puzzle.HardestTechnique.ToString();
                dayEntry["hint"] = hintData;

                days[dateKey] = dayEntry;
            }

            pack["days"] = days;

            SudokuPuzzle fallbackPuzzle = null;
            if (generator.TryGenerate(DifficultyLevel.Medium, 100001, out var fb))
            {
                fallbackPuzzle = fb;
            }
            int[] fbGrid = new int[81];
            for (int c = 0; c < 81; c++) fbGrid[c] = fallbackPuzzle.Givens[c] - '0';
            var fbHint = solver.FindNextStep(fbGrid, teaching: true) ?? solver.FindNextStep(fbGrid, teaching: false);

            var fallbackEntry = new Dictionary<string, object>();
            fallbackEntry["id"] = "practice-fallback";
            fallbackEntry["difficulty"] = fallbackPuzzle.Difficulty.ToString();
            fallbackEntry["puzzle"] = fallbackPuzzle.Givens;
            fallbackEntry["solution"] = fallbackPuzzle.Solution;
            fallbackEntry["clueCount"] = fallbackPuzzle.ClueCount;
            fallbackEntry["hardestTechnique"] = fallbackPuzzle.HardestTechnique.ToString();
            fallbackEntry["hint"] = BuildHintData(fbHint);

            pack["fallback"] = fallbackEntry;

            string outputPath = args.Length > 0 ? Path.GetFullPath(args[0]) : Path.GetFullPath("ninely/play/daily-pack.json");
            var options = new JsonSerializerOptions { WriteIndented = true };
            string json = JsonSerializer.Serialize(pack, options);
            File.WriteAllText(outputPath, json);
            ExportFixtures.Run("tools/golden_duel_fixtures.json");
            Console.WriteLine($"Successfully wrote daily-pack.json ({json.Length} bytes) and golden_duel_fixtures.json");
        }
    }
}
