using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Ninely.SudokuEngine;

namespace PackGenerator
{
    public static class ExportFixtures
    {
        public static void Run(string outputPath)
        {
            var generator = new SudokuGenerator();
            var difficulties = new[]
            {
                DifficultyLevel.Easy,
                DifficultyLevel.Medium,
                DifficultyLevel.Hard,
                DifficultyLevel.Expert,
                DifficultyLevel.Master
            };

            int[] testSeeds = new[] { 123456, 20261108, 424242, 999999, 777777 };

            var fixtures = new Dictionary<string, object>();
            fixtures["sourceCommit"] = "4fa5c68";
            fixtures["generator"] = "Ninely.SudokuEngine.SudokuGenerator";

            var tests = new List<object>();

            foreach (var diff in difficulties)
            {
                foreach (var seed in testSeeds)
                {
                    if (generator.TryGenerate(diff, seed, out var puzzle))
                    {
                        tests.Add(new
                        {
                            difficulty = diff.ToString(),
                            difficultyIndex = (int)diff,
                            seed = seed,
                            clueCount = puzzle.ClueCount,
                            givens = puzzle.Givens,
                            solution = puzzle.Solution,
                            hardestTechnique = puzzle.HardestTechnique.ToString()
                        });
                    }
                }
            }

            fixtures["fixtures"] = tests;
            var opts = new JsonSerializerOptions { WriteIndented = true };
            string json = JsonSerializer.Serialize(fixtures, opts);
            File.WriteAllText(outputPath, json);
            Console.WriteLine($"Exported {tests.Count} golden duel fixtures to {outputPath}");
        }
    }
}
