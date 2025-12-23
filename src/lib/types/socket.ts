export enum ServerboundEvent {
    PRODUCE_SHORT = "produce",
    GENERATE_PGN = "generate pgn",
    LIST_PLAYERS = "list players",
    GET_RANDOM_GAME = "get random game"
}

export enum ClientboundEvent {
    RENDER_INFO = "render info",
    RENDER_DONE = "render done",
    PGN_GENERATED = "pgn generated",
    PLAYERS_LIST = "players list",
    RANDOM_GAME_PGN = "random game pgn"
}