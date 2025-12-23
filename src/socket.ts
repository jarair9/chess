import { Server, Socket } from "socket.io";
import { Server as HTTPServer } from "http";
import { v4 as generateUUID } from "uuid";
import { existsSync, mkdirSync } from "fs";
import { readdir, readFile, writeFile, unlink } from "fs/promises";
import path from "path";

import { ShortType } from "./lib/types/short";
import { ClientboundEvent, ServerboundEvent } from "./lib/types/socket";

import { produceTriviaShort } from "./lib/videos/trivia";
import { producePuzzleShort } from "./lib/videos/puzzle";

export function createSocketServer(httpServer: HTTPServer) {

    const io = new Server(httpServer);

    io.on("connection", socket => {
        socket.on(ServerboundEvent.PRODUCE_SHORT, (type?: ShortType, data?: string) => {
            if (!type) return;
            console.log(`received a request to produce a ${type} short.`);

            try {
                produceShort(type, socket, data);
            } catch {
                socket.emit(
                    ClientboundEvent.RENDER_INFO,
                    "Short rendering process failed."
                );
            }
        });



        socket.on(ServerboundEvent.LIST_PLAYERS, async () => {
            try {
                const { listPlayers } = await import("./lib/pgn/library");
                socket.emit(ClientboundEvent.PLAYERS_LIST, listPlayers());
            } catch (err) {
                console.error("Library Error:", err);
            }
        });

        socket.on(ServerboundEvent.GET_RANDOM_GAME, async (player: string) => {
            console.log(`received a request to get random game for: ${player} `);
            try {
                const { getRandomGame } = await import("./lib/pgn/library");
                socket.emit(ClientboundEvent.RANDOM_GAME_PGN, getRandomGame(player));
            } catch (err: any) {
                console.error("Library Error:", err);
                socket.emit(ClientboundEvent.RENDER_INFO, `Library Error: ${err.message} `);
            }
        });

        socket.on("list videos", async () => {
            await broadcastVideoList(socket);
        });

        socket.on("delete video", async (filename: string) => {
            console.log(`Deleting video: ${filename}`);
            const videos = await loadDatabase();
            const videoIndex = videos.findIndex(v => v.filename === filename);

            if (videoIndex !== -1) {
                // Delete file from disk
                try {
                    const filePath = path.resolve("out", filename);
                    if (existsSync(filePath)) {
                        await unlink(filePath);
                    }
                } catch (e) {
                    console.error("Error deleting file:", e);
                }

                // Remove from DB
                videos.splice(videoIndex, 1);
                await saveDatabase(videos);

                // Broadcast update
                await broadcastVideoList(io); // Update everyone
            }
        });
    });

}

async function produceShort(
    type: ShortType, // The type of short to be produced
    socket: Socket, // The websocket client to send logs to
    data?: string // Extra required parameters (like a PGN)
) {

    if (!existsSync("out")) {
        mkdirSync("out");
    }

    const outputDirectory = "out";
    const outputFilename = `${generateUUID()}.mp4`;
    const outputPath = `${outputDirectory}/${outputFilename}`;

    switch (type) {
        case ShortType.TRIVIA:
            await produceTriviaShort(outputPath, socket);
            break;
        case ShortType.CHESS_PUZZLE:
            if (data) {
                await producePuzzleShort(outputPath, socket, data);
            }
            break;
    }

    socket.emit(
        ClientboundEvent.RENDER_DONE,
        outputFilename
    );

    // Save to DB
    const videos = await loadDatabase();
    videos.push({
        id: generateUUID(),
        filename: outputFilename,
        type: type,
        date: new Date().toISOString(),
        title: `${type === ShortType.TRIVIA ? "Trivia" : "Chess Puzzle"} Short`
    });
    await saveDatabase(videos);

    // Auto-refresh the gallery
    await broadcastVideoList(socket.nsp);

}



const DB_PATH = path.resolve("data/db.json");

interface Video {
    id: string;
    filename: string;
    type: string; // 'trivia', 'chess/puzzle'
    date: string; // ISO string
    title: string; // Display title
}

async function loadDatabase(): Promise<Video[]> {
    if (!existsSync(DB_PATH)) return [];
    try {
        const data = await readFile(DB_PATH, "utf-8");
        return JSON.parse(data);
    } catch (e) {
        console.error("Failed to load DB:", e);
        return [];
    }
}

async function saveDatabase(videos: Video[]) {
    try {
        await writeFile(DB_PATH, JSON.stringify(videos, null, 2));
    } catch (e) {
        console.error("Failed to save DB:", e);
    }
}

async function broadcastVideoList(io: any) {
    // Sync Step: Populate DB with files found in disk but missing in DB
    const outDir = path.resolve("out");
    if (existsSync(outDir)) {
        try {
            const files = await readdir(outDir);
            const mp4Files = files.filter(f => f.endsWith(".mp4"));

            let dbVideos = await loadDatabase();
            let dbChanged = false;

            for (const file of mp4Files) {
                // If file is not in DB, add it
                if (!dbVideos.find(v => v.filename === file)) {
                    dbVideos.push({
                        id: generateUUID(),
                        filename: file,
                        type: "legacy", // Mark as legacy or unknown
                        date: new Date().toISOString(), // Use current time as fallback (real mtime would be better but this is sufficient for migration)
                        title: "Legacy Video"
                    });
                    dbChanged = true;
                }
            }

            // Also cleanup: If file is in DB but NOT on disk, remove from DB?
            // Optional/Safe to run to ensure consistency
            const newDbVideos = dbVideos.filter(v => mp4Files.includes(v.filename));
            if (newDbVideos.length !== dbVideos.length) {
                dbVideos = newDbVideos;
                dbChanged = true;
            }

            if (dbChanged) {
                await saveDatabase(dbVideos);
            }
        } catch (e) {
            console.error("Error migrating videos:", e);
        }
    }

    const videos = await loadDatabase();
    // Sort by date descending (newest first)
    videos.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    io.emit("videos list", videos);
}
