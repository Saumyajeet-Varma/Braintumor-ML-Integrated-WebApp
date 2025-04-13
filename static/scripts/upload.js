const fileInput = document.getElementById("image");
const label = document.querySelector(".custom-file-input");

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        label.textContent = fileInput.files[0].name;
    }
});