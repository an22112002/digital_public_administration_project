(async () => {
    window.pywebview.api.log("Start form trigger service");
    // ==============================
    // Hỗ trợ
    // ==============================
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    // ==============================
    // Data
    // ==============================
    const data = FORM_DATA;
    const type = FORM_TYPE;
    
    // ==============================
    // Hàm chính
    // ==============================
    async function waitUntilReady() {
        while (true) {
            // tìm các dấu hiệu render xong
            // ko có h2 "Thông tin định danh"
            const h2Elements = [...document.querySelectorAll("h2")]
                .find((h2) => h2.textContent.includes("Thông tin định danh"));
            // có button "Xem trước"
            const viewButton = [...document.querySelectorAll("button")]
                .find((button) => button.textContent.includes("Xem trước"));

            // window.pywebview.api.log(`h2Elements: ${h2Elements ? 'Found' : 'Not found'}, viewButton: ${viewButton ? 'Found' : 'Not found'}`);
            if (!h2Elements && viewButton) {
                break;
            }

            await sleep(5000);
        }

        window.pywebview.api.log("Form bắt đầu nhập");
        await window.pywebview.api.form_fill(data, type);
    }


    // ==============================
    // Start
    // ==============================

    await waitUntilReady();

})();
