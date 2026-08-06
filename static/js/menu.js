// Simple animation effect when adding to cart
document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(".add-form");

    forms.forEach(f => {
        f.addEventListener("submit", () => {
            alert("Item added to your order!");
        });
    });
});
