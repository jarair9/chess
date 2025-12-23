function showToast(message, type = "info") {
    // Create container if not exists
    let container = $(".toast-container");
    if (container.length === 0) {
        $("body").append('<div class="toast-container"></div>');
        container = $(".toast-container");
    }

    // Create toast element
    const toast = $(`<div class="toast ${type}"><span>${message}</span></div>`);

    // Add to container
    container.append(toast);

    // Trigger animation
    setTimeout(() => {
        toast.addClass("show");
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.removeClass("show");
        setTimeout(() => {
            toast.remove();
        }, 300); // Wait for transition out
    }, 3000);
}
