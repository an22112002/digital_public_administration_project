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
        const styleButton = (button, tooltip, bg_color, text_color, font_size) => {
            Object.assign(button.style, {
                border: "1px solid #d9d9d9",
                backgroundColor: bg_color || "#fff",
                color:  text_color || "#333",
                padding: "6px 12px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: font_size || "14px",
                transition: "all 0.2s ease",
                outline: "none"
            });
            button.dataset.tooltip = tooltip;

            button.onmouseenter = () => {
                button.style.backgroundColor = bg_color || "#f0f0f0";
                button.style.borderColor = "#999";
                button.style.transform = "translateY(-1px)";
                button.style.boxShadow = "0 2px 5px rgba(0,0,0,0.15)";
            };

            button.onmouseleave = () => {
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
        // Back
        // =========================
        const btnBack = document.createElement("button");
        btnBack.textContent = "⟵"; // "Back"

        styleButton(btnBack, "Trang trước", "#fff", "#333", "16px");

        btnBack.onclick = () => {
            window.history.back();
        };

        // =========================
        // Forward
        // =========================
        const btnForward = document.createElement("button");
        btnForward.textContent = "⟶"; // "Forward"

        styleButton(btnForward, "Trang tiếp theo", "#fff", "#333", "16px");

        btnForward.onclick = () => {
            window.history.forward();
        };

        // =========================
        // Reload
        // =========================
        const btnReload = document.createElement("button");
        btnReload.dataset.tooltip = "Làm mới trang"; // Thêm tooltip cho nút Reload
        btnReload.textContent = "↻"; // "Reload"

        styleButton(btnReload, "Làm mới trang", "#fff", "#333", "16px");

        btnReload.onclick = () => {
            window.location.reload();
        };

        // =========================
        // Close
        // =========================
        const btnClose = document.createElement("button");
        btnClose.textContent = "Dừng nộp hồ sơ";

        styleButton(btnClose, "Đóng cửa sổ", "#ff4d4f", "#fff");

        btnClose.onclick = () => {
            window.pywebview.api.destroy();
        };

        tools.appendChild(btnBack);
        tools.appendChild(btnForward);
        tools.appendChild(btnReload);
        tools.appendChild(btnClose);

        document.body.appendChild(tools);

    }, 100);
})();