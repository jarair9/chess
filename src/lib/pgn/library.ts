import { readdirSync, readFileSync, existsSync } from "fs";
import { join } from "path";

const GAMES_DIR = "games";

export function listPlayers(): string[] {
    if (!existsSync(GAMES_DIR)) return [];

    return readdirSync(GAMES_DIR)
        .filter(file => file.endsWith(".pgn"))
        .map(file => file.replace(".pgn", ""));
}

export function getRandomGame(player: string): string {
    const filePath = join(GAMES_DIR, `${player}.pgn`);
    if (!existsSync(filePath)) {
        throw new Error(`PGN file for ${player} not found.`);
    }

    const content = readFileSync(filePath, "utf-8");
    // PGN files often separate games with double newlines or just [Event
    // A simple split by [Event " is usually effective to isolate raw games
    // We'll re-add the [Event prefix during processing

    // Normalize newlines
    const rawGames = content.split('[Event "');

    // Filter out empty or too short segments
    const games = rawGames
        .filter(g => g.trim().length > 50)
        .map(g => `[Event "${g}`); // Re-attach the separator

    if (games.length === 0) {
        throw new Error("No games found in file.");
    }

    const randomIndex = Math.floor(Math.random() * games.length);
    return games[randomIndex];
}
