submitBtn.addEventListener("click", async () => {
    const taskValue = input.value.trim();
    if (!taskValue) return;

    const user_id = document.cookie.replace(/(?:(?:^|.*;\s*)user_id\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    const api_token = document.cookie.replace(/(?:(?:^|.*;\s*)api_token\s*\=\s*([^;]*).*$)|^.*$/, "$1");

    if (!user_id || !api_token) {
        alert("Please enter your credentials first!");
        return;
    }

    try {
        const response = await fetch("/add_task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id, api_token, task: taskValue })
        });
        const result = await response.json();
        console.log(result);
        input.value = ""; // clear input
    } catch (err) {
        console.error("Error submitting task:", err);
    }
});

clearBtn.addEventListener("click", () => {
    input.value = ""; // clear input
});

