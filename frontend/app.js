const form = document.getElementById("essay-form");
const essaysContainer = document.getElementById("essays");
const refreshButton = document.getElementById("refresh");


async function loadEssays() {
    const response = await fetch("/api/essays");

    const essays = await response.json();

    essaysContainer.replaceChildren();

    for (const essay of essays) {
        const element = document.createElement("article");
        const title = document.createElement("h3");
        const text = document.createElement("p");
        const score = document.createElement("strong");

        title.textContent = essay.title;
        text.textContent = essay.text;
        score.textContent = `Nota: ${essay.score ?? "Não informada"}`;

        element.append(title, text, score);

        essaysContainer.appendChild(element);
    }
}


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = document.getElementById("title").value;
    const text = document.getElementById("text").value;
    const scoreValue = document.getElementById("score").value;

    const score = scoreValue
        ? Number(scoreValue)
        : null;

    const response = await fetch("/api/essays", {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
        },

        body: JSON.stringify({
            title,
            text,
            score,
        }),
    });

    if (!response.ok) {
        alert("Erro ao cadastrar redação.");
        return;
    }

    form.reset();

    await loadEssays();
});


refreshButton.addEventListener("click", loadEssays);


loadEssays();
