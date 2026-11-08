using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Ninely.SudokuEngine;

namespace PackGenerator
{
    class Program
    {
        static void Main(string[] args)
        {
            var generator = new SudokuGenerator();
            var solver = new SmartHintSolver();

            var pack = new Dictionary<string, object>();
            pack["sourceCommit"] = "4fa5c68";
            pack["schemaVersion"] = 1;
            pack["generatedAt"] = DateTime.UtcNow.ToString("o");

            var days = new Dictionary<string, object>();
            var startDate = new DateTime(2026, 11, 8);

            for (int i = 0; i < 30; i++)
            {
                var curDate = startDate.AddDays(i);
                string dateKey = curDate.ToString("yyyy-MM-dd");
                int seed = int.Parse(curDate.ToString("yyyyMMdd"));

                SudokuPuzzle puzzle = null;
                // Try Medium first, then try with seed perturbations if needed
                int attemptSeed = seed;
                while (puzzle == null)
                {
                    if (generator.TryGenerate(DifficultyLevel.Medium, attemptSeed, out var p))
                    {
                        // Check uniqueness
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

                // Compute SmartHint
                int[] grid = new int[81];
                for (int c = 0; c < 81; c++) grid[c] = puzzle.Givens[c] - '0';
                var hint = solver.FindNextStep(grid, teaching: true) ?? solver.FindNextStep(grid, teaching: false);

                var hintData = new Dictionary<string, object>();
                if (hint != null)
                {
                    hintData["targetRow"] = hint.TargetCell.Row;
                    hintData["targetCol"] = hint.TargetCell.Col;
                    hintData["targetDigit"] = hint.TargetDigit;
                    hintData["technique"] = hint.Technique.ToString();
                    hintData["localizationKey"] = hint.LocalizationKey;
                    
                    var highlights = new List<object>();
                    foreach (var h in hint.HighlightCells)
                    {
                        highlights.Add(new { row = h.Row, col = h.Col });
                    }
                    hintData["highlights"] = highlights;
                }

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
                Console.WriteLine($"Day {dateKey} (seed {seed}): clues={puzzle.ClueCount}, tech={hintData["technique"]}");
            }

            pack["days"] = days;

            // Evergreen fallback puzzle
            SudokuPuzzle fallbackPuzzle = null;
            if (generator.TryGenerate(DifficultyLevel.Medium, 100001, out var fb))
            {
                fallbackPuzzle = fb;
            }
            int[] fbGrid = new int[81];
            for (int c = 0; c < 81; c++) fbGrid[c] = fallbackPuzzle.Givens[c] - '0';
            var fbHint = solver.FindNextStep(fbGrid, teaching: true);
            var fbHintData = new Dictionary<string, object>();
            if (fbHint != null)
            {
                fbHintData["targetRow"] = fbHint.TargetCell.Row;
                fbHintData["targetCol"] = fbHint.TargetCell.Col;
                fbHintData["targetDigit"] = fbHint.TargetDigit;
                fbHintData["technique"] = fbHint.Technique.ToString();
                fbHintData["localizationKey"] = fbHint.LocalizationKey;
                var highlights = new List<object>();
                foreach (var h in fbHint.HighlightCells) highlights.Add(new { row = h.Row, col = h.Col });
                fbHintData["highlights"] = highlights;
            }

            var fallbackEntry = new Dictionary<string, object>();
            fallbackEntry["id"] = "practice-fallback";
            fallbackEntry["difficulty"] = fallbackPuzzle.Difficulty.ToString();
            fallbackEntry["puzzle"] = fallbackPuzzle.Givens;
            fallbackEntry["solution"] = fallbackPuzzle.Solution;
            fallbackEntry["clueCount"] = fallbackPuzzle.ClueCount;
            fallbackEntry["hardestTechnique"] = fallbackPuzzle.HardestTechnique.ToString();
            fallbackEntry["hint"] = fbHintData;

            pack["fallback"] = fallbackEntry;

            string outputPath = args.Length > 0 ? Path.GetFullPath(args[0]) : Path.GetFullPath("ninely/play/daily-pack.json");
            var options = new JsonSerializerOptions { WriteIndented = true };
            string json = JsonSerializer.Serialize(pack, options);
            File.WriteAllText(outputPath, json); ExportFixtures.Run("tools/golden_duel_fixtures.json");
            Console.WriteLine($"\nSuccessfully wrote daily-pack.json to {outputPath} ({json.Length} bytes)");
        }
    }
}
