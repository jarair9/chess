const socket = io({ reconnection: false });
const feedContainer = $("#videoFeed");

function renderFeed(videos) {
    feedContainer.empty();

    if (videos.length === 0) {
        feedContainer.html("<div class='no-videos'>No videos generated yet. Go create some!</div>");
        return;
    }

    // Sort videos by newest first (assuming filename contains uuid, we might rely on listing order from server, 
    // but ideally server sends modification time. For now, just reverse or serve as is. 
    // UUIDs aren't time ordered. We'll display as received.)
    // Note: To truly show newest first, backend should sort by mtime. 
    // For now, let's just display what we get.

    videos.forEach(video => {
        // video is now an object: { id, filename, type, date, title }
        // Ensure backward compatibility if database is empty but files exist (optional, but good practice. 
        // Actually, our loadDatabase only loads from DB. Files not in DB won't show. That's fine for now.)

        const videoCard = $(`
            <div class="video-card" id="card-${video.filename}">
                <video src="/media/${video.filename}" controls preload="metadata"></video>
                <div class="video-info">
                    <div class="video-details">
                        <span class="video-title">${video.title}</span>
                        <span class="video-date">${new Date(video.date).toLocaleString()}</span>
                    </div>
                    <div class="video-controls">
                        <a href="/media/${video.filename}" download class="btn download-btn">⬇</a>
                        <button class="btn delete-btn" data-filename="${video.filename}">🗑</button>
                    </div>
                </div>
            </div>
        `);

        videoCard.find(".delete-btn").on("click", function () {
            const filename = $(this).data("filename");
            if (confirm("Are you sure you want to delete form database?")) {
                socket.emit("delete video", filename);
                showToast("Video deleted", "success");
            }
        });

        feedContainer.append(videoCard);
    });
}

socket.on("connect", () => {
    console.log("Connected to feed socket");
    socket.emit("list videos");
});

socket.on("videos list", (videos) => {
    console.log("Received videos:", videos);
    renderFeed(videos);
});
