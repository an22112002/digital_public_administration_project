(() => {
    if (document.getElementById("pywebview-tools")) {
        clearInterval(timer);
        return;
    }

    const timer = setInterval(() => {

        if (!document.body) {
            return;
        }

        if (document.getElementById("pywebview-tools")) {
            clearInterval(timer);
            return;
        }

        clearInterval(timer);

        const tools = document.createElement("div");
        tools.id = "pywebview-tools";

        Object.assign(tools.style, {
            position: "fixed",
            top: "10px",
            right: "10px",
            zIndex: "999999",
            backgroundColor: "#fff",
            padding: "8px",
            border: "1px solid #ccc",
            borderRadius: "6px",
            display: "flex",
            gap: "6px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)"
        });

        // =========================
        // Hàm style chung cho button
        // =========================
        const styleButton = (button) => {
            Object.assign(button.style, {
                border: "1px solid #d9d9d9",
                backgroundColor: "#fff",
                color: "#333",
                padding: "6px 12px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "14px",
                transition: "all 0.2s ease",
                outline: "none"
            });

            button.onmouseenter = () => {
                button.style.backgroundColor = "#f0f0f0";
                button.style.borderColor = "#999";
                button.style.transform = "translateY(-1px)";
                button.style.boxShadow = "0 2px 5px rgba(0,0,0,0.15)";
            };

            button.onmouseleave = () => {
                button.style.backgroundColor = "#fff";
                button.style.borderColor = "#d9d9d9";
                button.style.transform = "translateY(0)";
                button.style.boxShadow = "none";
            };

            button.onmousedown = () => {
                button.style.transform = "translateY(1px) scale(0.97)";
            };

            button.onmouseup = () => {
                button.style.transform = "translateY(-1px)";
            };
        };

        // =========================
        // Reload
        // =========================
        const btnReload = document.createElement("button");
        btnReload.textContent = "Tải lại"; // "Reload" in Vietnamese

        styleButton(btnReload);

        btnReload.onclick = () => {
            window.location.reload();
        };

        // =========================
        // Close
        // =========================
        const btnClose = document.createElement("button");
        btnClose.textContent = "Đóng"; // "Đóng" in Vietnamese

        styleButton(btnClose);

        btnClose.onclick = () => {
            window.pywebview.api.destroy();
        };

        tools.appendChild(btnReload);
        tools.appendChild(btnClose);

        document.body.appendChild(tools);

    }, 100);
})();