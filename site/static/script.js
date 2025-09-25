document.getElementById("taskForm").addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevent normal form submission

    const taskInput = document.getElementById("task").value;
    const userId = prompt("Enter your Habitica user ID:");
    const apiToken = prompt("Enter your Habitica API token:");

    try {
        const response = await fetch("/add_task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                api_token: apiToken,
                task: taskInput
            })
        });

        const data = await response.json();

        if (response.ok) {
            console.log('Task created: ${data.data.data.text}');
        } else {
            console.log('Error: ${data.detail || data.error}');
        }
    } catch (err) {
        console.log('Error: ${err.message}');
    }
});