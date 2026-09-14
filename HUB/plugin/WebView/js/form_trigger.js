(async () => {
    window.pywebview.api.log("Start form trigger service");

    const sleep = (ms) =>
        new Promise(resolve => setTimeout(resolve, ms));

    const data = FORM_DATA;
    const type = FORM_TYPE;

    // =====================================================
    // Tạo box điều khiển
    // =====================================================

    function createFormTriggerBox() {

        // Không tạo trùng
        if (document.getElementById("pywebview-form-trigger")) {
            return;
        }

        const box = document.createElement("div");
        box.id = "pywebview-form-trigger";

        Object.assign(box.style, {
            position: "fixed",
            bottom: "10px",
            left: "10px",
            zIndex: "999999",
            backgroundColor: "#ffffff",
            border: "1px solid #d9d9d9",
            borderRadius: "8px",
            padding: "10px 12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            fontFamily: "Arial, sans-serif",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            gap: "10px"
        });

        // Text
        const text = document.createElement("span");
        text.textContent = "Nhấn 'Bắt đầu nhập' để điền form tự động, khi form đã sẵn sàng";

        Object.assign(text.style, {
            color: "#333",
            fontWeight: "500"
        });

        // Button
        const button = document.createElement("button");
        button.textContent = "Bắt đầu nhập";
        let formWasFilled = false;

        Object.assign(button.style, {
            border: "none",
            backgroundColor: "#1677ff",
            color: "#fff",
            padding: "6px 12px",
            borderRadius: "5px",
            cursor: "pointer",
            fontSize: "13px",
            transition: "all 0.2s ease"
        });

        // Hover
        button.onmouseenter = () => {
            button.style.backgroundColor = "#4096ff";
            button.style.transform = "translateY(-1px)";
            button.style.boxShadow = "0 2px 6px rgba(0,0,0,0.15)";
        };

        button.onmouseleave = () => {
            button.style.backgroundColor = "#1677ff";
            button.style.transform = "translateY(0)";
            button.style.boxShadow = "none";
        };

        // Click
        button.onclick = async () => {

            if (formWasFilled) {
                await window.pywebview.api.reset_form_fill();
                formWasFilled = false;
            }

            button.disabled = true;
            button.textContent = "Đang nhập...";

            button.style.opacity = "0.7";
            button.style.cursor = "default";

            try {

                window.pywebview.api.log(
                    "User kích hoạt nhập form"
                );

                const fillResult = await window.pywebview.api.form_fill(
                    data,
                    type
                );

                if (fillResult !== true) {
                    throw new Error("Python không thể nhập lại form");
                }

                text.textContent = "Đã nhập form. Kiểm tra lại thông tin và điền nốt các thông tin còn thiếu nếu có.";

                button.textContent = "Nhập lại";
                button.disabled = false;
                button.style.opacity = "1";
                button.style.cursor = "pointer";
                formWasFilled = true;

                showFormMessage(
                    "Đã nhập form",
                    "Kiểm tra lại thông tin và điền nốt các thông tin còn thiếu nếu có. Sau đó bấm 'Xem trước' để tiếp tục."
                );

                window.pywebview.api.log(
                    "Form fill hoàn thành"
                );

            } catch (error) {

                console.error(error);

                text.textContent = "Lỗi khi nhập form";

                button.disabled = false;
                button.textContent = "Thử lại";

                button.style.opacity = "1";
                button.style.cursor = "pointer";

                window.pywebview.api.log(
                    "Form fill lỗi: " + error
                );
            }
        };

        function showFormMessage(title, message) {
            const overlay = document.createElement("div");
            Object.assign(overlay.style, {
                position: "fixed",
                inset: "0",
                zIndex: "1000000",
                backgroundColor: "rgba(0, 0, 0, 0.45)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px",
                fontFamily: "Arial, sans-serif"
            });

            const dialog = document.createElement("div");
            Object.assign(dialog.style, {
                width: "min(480px, 100%)",
                backgroundColor: "#ffffff",
                border: "3px solid #1677ff",
                borderRadius: "10px",
                padding: "24px",
                boxShadow: "0 10px 30px rgba(0, 0, 0, 0.3)",
                color: "#1f1f1f",
                fontSize: "18px",
                lineHeight: "1.5"
            });

            const heading = document.createElement("div");
            heading.textContent = title;
            Object.assign(heading.style, {
                color: "#0958d9",
                fontSize: "24px",
                fontWeight: "700",
                marginBottom: "12px"
            });

            const content = document.createElement("div");
            content.textContent = message;
            content.style.fontWeight = "600";

            const closeButton = document.createElement("button");
            closeButton.textContent = "Đã hiểu";
            Object.assign(closeButton.style, {
                display: "block",
                margin: "20px 0 0 auto",
                border: "none",
                borderRadius: "6px",
                backgroundColor: "#1677ff",
                color: "#fff",
                padding: "10px 18px",
                cursor: "pointer",
                fontSize: "16px",
                fontWeight: "700"
            });

            closeButton.onclick = () => overlay.remove();
            overlay.onclick = event => {
                if (event.target === overlay) {
                    overlay.remove();
                }
            };

            dialog.appendChild(heading);
            dialog.appendChild(content);
            dialog.appendChild(closeButton);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
            closeButton.focus();
        }

        box.appendChild(text);
        box.appendChild(button);

        document.body.appendChild(box);
    }

    // =====================================================
    // Kiểm tra form đã sẵn sàng
    // =====================================================

    async function waitUntilReady() {

        while (true) {

            const h2Elements = [
                ...document.querySelectorAll("h2")
            ].find(
                h2 =>
                    h2.textContent.includes(
                        "Thông tin định danh"
                    )
            );

            const viewButton = [
                ...document.querySelectorAll("button")
            ].find(
                button =>
                    button.textContent.includes(
                        "Xem trước"
                    )
            );

            // Form đã sẵn sàng
            if (!h2Elements && viewButton) {

                window.pywebview.api.log(
                    "Form đã sẵn sàng - chờ người dùng kích hoạt"
                );

                createFormTriggerBox();
                return;
            }

            await sleep(2000);
        }
    }

    // =====================================================
    // Start
    // =====================================================

    await waitUntilReady();

})();