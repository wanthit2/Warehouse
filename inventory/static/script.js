document.addEventListener("DOMContentLoaded", function() {
    const showCategoriesButton = document.getElementById("showCategoriesButton");
    const categoryList = document.getElementById("categoryList");

    showCategoriesButton.addEventListener("click", function() {
        if (categoryList.style.display === "none") {
            categoryList.style.display = "block";
        } else {
            categoryList.style.display = "none";
        }
    });
});
