const shortExtraDataTitles = {
    "chess/puzzle": "Game PGN"
};

$(".short-type-option").on("change", () => {

    const shortType = $(".short-type-option").val() || "";
    const shortExtraDataTitle = shortExtraDataTitles[shortType];

    if (shortExtraDataTitle) {
        $(".short-extra-data-container").css("display", "flex");
        $(".short-extra-data-title").html(shortExtraDataTitle);
    } else {
        $(".short-extra-data-container").css("display", "none");
    }

});

$(".produce-video").on("click", () => {

    const socket = io({ reconnection: false });

    socket.on("connect", () => {
        $(".short-configuration").css("display", "none");
        $(".production-logs").css("display", "flex");
        $(".production-logs").html("<span>Spawning Python process...</span>");

        socket.emit(
            "produce",
            $(".short-type-option").val() || "",
            $(".short-extra-data").val() || ""
        );

        socket.on("render info", message => {
            $(".production-logs").append(`<span>${message}</span>`);
        });

        socket.on("render done", filename => {
            $(".short-configuration").css("display", "flex");
            $(".short-filename").html(filename);
            $(".short-preview").attr("src", `/media/${filename}`);
        });
    });

});

const logsObserver = new MutationObserver(() => {
    const logsContainer = $(".production-logs").get(0);
    logsContainer.scrollTop = logsContainer.scrollHeight;
});


// Load players on startup
const socket = io({ reconnection: false });

socket.on("connect", () => {
    socket.emit("list players");
});
socket.on("players list", (players) => {
    const select = $(".player-select");
    players.forEach(player => {
        select.append(new Option(player, player));
    });
    // socket.disconnect(); // Keep connection open for gallery updates
});

$(".get-random-game").on("click", () => {
    const player = $(".player-select").val();
    if (!player) {
        showToast("Please select a player first.", "error");
        return;
    }

    const btn = $(".get-random-game");
    const originalText = btn.text();
    btn.prop("disabled", true).text("Loading...");

    const socket = io({ reconnection: false });

    socket.on("connect", () => {
        socket.emit("get random game", player);
    });

    socket.on("random game pgn", (pgn) => {
        $(".short-extra-data").val(pgn);
        btn.prop("disabled", false).text(originalText);
        showToast("Random game loaded!", "success");
        socket.disconnect();
    });

    socket.on("render info", (msg) => {
        if (msg.startsWith("Library Error")) {
            showToast(msg, "error");
            btn.prop("disabled", false).text(originalText);
            socket.disconnect();
        }
    });
});

logsObserver.observe($(".production-logs").get(0), {
    childList: true
});