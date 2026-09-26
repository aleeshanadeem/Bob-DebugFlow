function showToast(message) {
    const toast = document.getElementById("toast");

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}


function startDemo() {
    showToast("DebugFlow session started.");
}


function scrollToWorkflow() {
    document
        .getElementById("workflow")
        .scrollIntoView({ behavior: "smooth" });
}


function showReport() {
    document
        .getElementById("reports")
        .scrollIntoView({ behavior: "smooth" });

    showToast("Reports and evidence available below.");
}


function openReport(fileName) {

    showToast(
        fileName +
        " is available in the reports/ directory."
    );

}