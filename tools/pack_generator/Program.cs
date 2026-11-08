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
                "في العمود {1}، لا يمكن وضع الرقم {0} في الخانات الأخرى بسبب الأرقام {0} המتقاطعة. لذا هذه هي الخانة الوحيدة المتبقية له!"
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
            ),
            ["HINT_NAKED_PAIR"] = (
                "Naked pair: inside {4} {5}, digits {3} can only be in two cells, eliminating them from the rest of the unit. That leaves {0} at row {1}, column {2}.",
                "זוג גלוי: ב{4} {5}, הספרות {3} יכולות להיות רק בשתי משבצות, ולכן נפסלות משאר היחידה. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "زوج مكشوف: في {4} {5}، لا يمكن أن يكون الرقمان {3} إلا في خانتين، لذا يُستبعدان من باقي الوحدة. فيبقى {0} في الصف {1}، العمود {2}."
            ),
            ["HINT_HIDDEN_PAIR"] = (
                "Hidden pair: inside {4} {5}, digits {3} can only go in two cells, so other candidates are removed. That leaves {0} at row {1}, column {2}.",
                "זוג נסתר: ב{4} {5}, הספרות {3} יכולות להיכנס רק לשתי משבצות, ולכן מועמדים אחרים מוסרים. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "زوج مخفي: في {4} {5}، لا يمكن أن يدخل الرقمان {3} إلا في خانتين، لذا تُستبعد الاحتمالات الأخرى. فيبقى {0} في الصف {1}، العمود {2}."
            ),
            ["HINT_NAKED_TRIPLE"] = (
                "Naked triple: inside {4} {5}, digits {3} lock three cells. That leaves {0} at row {1}, column {2}.",
                "שלשה גלויה: ב{4} {5}, הספרות {3} נועלות שלוש משבצות. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "ثلاثية مكشوفة: في {4} {5}، الأرقام {3} تقفل ثلاث خانات. فيبقى {0} في الصف {1}، العمود {2}."
            ),
            ["HINT_X_WING"] = (
                "X-Wing: candidate {3} forms an X-Wing pattern, eliminating it from other cells. That leaves {0} at row {1}, column {2}.",
                "X-Wing: המועמד {3} יוצר תבנית X-Wing ופוסל אותו ממשבצות מקבילות. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "X-Wing: المرشح {3} يشكل نمط X-Wing ويُستبعد من الخانات المقابلة. فيبقى {0} في الصف {1}، العمود {2}."
            ),
            ["HINT_SWORDFISH"] = (
                "Swordfish: candidate {3} forms a Swordfish pattern across three lines. That leaves {0} at row {1}, column {2}.",
                "Swordfish: המועמד {3} יוצר תבנית Swordfish לאורך שלושה קווים. כך נשאר {0} בשורה {1}, עמודה {2}.",
                "Swordfish: المرشح {3} يشكل نمط Swordfish عبر ثلاثة خطوط. فيبقى {0} في الصف {1}، العمود {2}."
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

            string enStr, heStr, arStr;
            if (HintTemplates.TryGetValue(hint.LocalizationKey ?? "", out var tpl) && hint.LocalizationArgs != null)
            {
                enStr = string.Format(tpl.en, hint.LocalizationArgs);
                heStr = string.Format(tpl.he, hint.LocalizationArgs);
                arStr = string.Format(tpl.ar, hint.LocalizationArgs);
            }
            else
            {
                enStr = $"Look at row {hint.TargetCell.Row + 1}, column {hint.TargetCell.Col + 1}: {hint.TargetDigit} is the next logical step.";
                heStr = $"הבט בשורה {hint.TargetCell.Row + 1}, עמודה {hint.TargetCell.Col + 1}: המספר {hint.TargetDigit} הוא הצעד הבא.";
                arStr = $"انظر إلى الصف {hint.TargetCell.Row + 1}، العمود {hint.TargetCell.Col + 1}: الرقم {hint.TargetDigit} هو الخطوة المنطقية التالية.";
            }

            hintData["explanation"] = new Dictionary<string, string>
            {
                ["en"] = enStr,
                ["he"] = heStr,
                ["ar"] = arStr
            };
            hintData["hint_en"] = enStr;
            hintData["hint_he"] = heStr;
            hintData["hint_ar"] = arStr;

            var highlights = new List<object>();
            foreach (var h in hint.HighlightCells)
            {
                highlights.Add(new { row = h.Row, col = h.Col });
            }
            hintData["highlights"] = highlights;
            return hintData;
        }

        static SudokuPuzzle GenerateDailyPuzzle(int seed, int targetHoles, DifficultyLevel diffLevel, SmartHintSolver solver)
        {
            int attemptSeed = seed;
            while (true)
            {
                var rng = new Random(attemptSeed);
                int[] solution = SudokuGenerator.GenerateSolvedGrid(rng);
                int[] puzzle = (int[])solution.Clone();

                var indices = new List<int>(81);
                for (int c = 0; c < 81; c++) indices.Add(c);
                for (int i = indices.Count - 1; i > 0; i--)
                {
                    int j = rng.Next(i + 1);
                    (indices[i], indices[j]) = (indices[j], indices[i]);
                }

                int holesDug = 0;
                foreach (int idx in indices)
                {
                    int val = puzzle[idx];
                    puzzle[idx] = 0;
                    if (SudokuGenerator.CountSolutions(puzzle, 2) == 1)
                    {
                        holesDug++;
                        if (holesDug == targetHoles) break;
                    }
                    else
                    {
                        puzzle[idx] = val;
                    }
                }

                if (holesDug == targetHoles && SudokuGenerator.CountSolutions(puzzle, 2) == 1)
                {
                    var hint = solver.FindNextStep(puzzle, teaching: true) ?? solver.FindNextStep(puzzle, teaching: false);
                    if (hint != null)
                    {
                        var graded = solver.Solve(puzzle);
                        return new SudokuPuzzle
                        {
                            Givens = SudokuGrid.Format(puzzle),
                            Solution = SudokuGrid.Format(solution),
                            Difficulty = diffLevel,
                            HardestTechnique = graded.HardestTechnique,
                            ClueCount = 81 - targetHoles,
                            Seed = seed
                        };
                    }
                }
                attemptSeed++;
            }
        }

        static void Main(string[] args)
        {
            var solver = new SmartHintSolver();

            var pack = new Dictionary<string, object>();
            pack["sourceCommit"] = "4fa5c68";
            pack["schemaVersion"] = 1;
            pack["generatedAt"] = "2026-11-08T13:55:00Z";

            string outputPath = args.Length > 0 ? Path.GetFullPath(args[0]) : Path.GetFullPath("ninely/play/daily-pack.json");
            int daysCount = args.Length > 1 && int.TryParse(args[1], out int dc) ? dc : 90;

            var days = new Dictionary<string, object>();
            var startDate = new DateTime(2026, 11, 8);

            for (int i = 0; i < daysCount; i++)
            {
                var curDate = startDate.AddDays(i);
                string dateKey = curDate.ToString("yyyy-MM-dd");
                int seed = int.Parse(curDate.ToString("yyyyMMdd"));

                int targetHoles;
                DifficultyLevel diffLevel;
                if (i < 30)
                {
                    targetHoles = 36;
                    diffLevel = DifficultyLevel.Easy;
                }
                else if (i < 60)
                {
                    targetHoles = 46;
                    diffLevel = DifficultyLevel.Medium;
                }
                else
                {
                    targetHoles = 52;
                    diffLevel = DifficultyLevel.Hard;
                }

                SudokuPuzzle puzzle = GenerateDailyPuzzle(seed, targetHoles, diffLevel, solver);

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
                if (hintData.TryGetValue("hint_en", out var heVal)) dayEntry["hint_en"] = heVal;
                if (hintData.TryGetValue("hint_he", out var hhVal)) dayEntry["hint_he"] = hhVal;
                if (hintData.TryGetValue("hint_ar", out var haVal)) dayEntry["hint_ar"] = haVal;

                days[dateKey] = dayEntry;
            }

            pack["days"] = days;

            var generator = new SudokuGenerator();
            SudokuPuzzle fallbackPuzzle = null;
            if (generator.TryGenerate(DifficultyLevel.Medium, 100001, out var fb))
            {
                fallbackPuzzle = fb;
            }
            int[] fbGrid = new int[81];
            for (int c = 0; c < 81; c++) fbGrid[c] = fallbackPuzzle.Givens[c] - '0';
            var fbHint = solver.FindNextStep(fbGrid, teaching: true) ?? solver.FindNextStep(fbGrid, teaching: false);
            var fbHintData = BuildHintData(fbHint);

            var fallbackEntry = new Dictionary<string, object>();
            fallbackEntry["id"] = "practice-fallback";
            fallbackEntry["difficulty"] = fallbackPuzzle.Difficulty.ToString();
            fallbackEntry["puzzle"] = fallbackPuzzle.Givens;
            fallbackEntry["solution"] = fallbackPuzzle.Solution;
            fallbackEntry["clueCount"] = fallbackPuzzle.ClueCount;
            fallbackEntry["hardestTechnique"] = fallbackPuzzle.HardestTechnique.ToString();
            fallbackEntry["hint"] = fbHintData;
            if (fbHintData.TryGetValue("hint_en", out var fbHeVal)) fallbackEntry["hint_en"] = fbHeVal;
            if (fbHintData.TryGetValue("hint_he", out var fbHhVal)) fallbackEntry["hint_he"] = fbHhVal;
            if (fbHintData.TryGetValue("hint_ar", out var fbHaVal)) fallbackEntry["hint_ar"] = fbHaVal;

            pack["fallback"] = fallbackEntry;

            var options = new JsonSerializerOptions { WriteIndented = true };
            string json = JsonSerializer.Serialize(pack, options);
            File.WriteAllText(outputPath, json);
            ExportFixtures.Run("tools/golden_duel_fixtures.json");
            Console.WriteLine($"Successfully wrote {daysCount} days to {outputPath} ({json.Length} bytes) and golden_duel_fixtures.json");
        }
    }
}
