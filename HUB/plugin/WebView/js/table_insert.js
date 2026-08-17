(async () => {

    const papers = PAPERS_DATA;

    const sleep = (ms) => new Promise(r => setTimeout(r, ms));

    async function waitUntilReady() {{
        while (true) {{
            const btn = [...document.querySelectorAll("button")]
                .find(b => b.textContent.trim() === "Thêm thành phần hồ sơ");
            if (btn)
                return;

            await sleep(100);
        }}
    }}

    async function waitAndClickButton(text) {
        while (true) {
            const btn = [...document.querySelectorAll("button")]
                .find(b => b.textContent.trim() === text);
            if (btn) {
                btn.click();
                return;
            }

            await sleep(100);
        }
    }

    function getRows() {{
        return [...document.querySelectorAll("tbody tr")]
            .filter(r => !r.innerText.includes("Thêm thành phần hồ sơ"));
    }}

    function getAddButton() {{
        return [...document.querySelectorAll("button")]
            .find(b => b.textContent.trim() === "Thêm thành phần hồ sơ");
    }}

    function getRowName(row) {{

        const input = row.querySelector('input[maxlength="1000"]');

        // Dòng mới
        if (input)
            return input.value.trim();

        const p = row.querySelector("td:nth-child(2) p.text-justify");

        if (!p)
            return "";

        return [...p.childNodes]
            .filter(n => n.nodeType === Node.TEXT_NODE)
            .map(n => n.textContent)
            .join("")
            .trim();
    }}

    async function addRow() {{

        const before = getRows().length;

        getAddButton().click();

        while (getRows().length === before)
            await sleep(100);

        return getRows().at(-1);
    }}

    async function fillName(row, name) {{

        const input = row.querySelector('input[maxlength="1000"]');

        if (!input)
            return;

        const setter = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            "value"
        ).set;

        setter.call(input, name);

        input.dispatchEvent(new Event("input", {
            bubbles: true
        }));

        input.dispatchEvent(new Event("change", {
            bubbles: true
        }));

        await sleep(100);
    }}

    async function findRowByName(name) {{
        while (true) {{
            const row = [...document.querySelectorAll("tbody tr")]
                .find(tr => {{

                    // Nếu là dòng đang edit
                    const input = tr.querySelector('input[maxlength="1000"]');

                    if (input)
                        return input.value.trim() === name;

                    // Nếu là dòng đã lưu
                    const p = tr.querySelector("td:nth-child(2) p.text-justify");

                    if (!p)
                        return false;

                    const text = [...p.childNodes]
                        .filter(n => n.nodeType === Node.TEXT_NODE)
                        .map(n => n.textContent)
                        .join("")
                        .trim();

                    return text === name;
                }});
            if (row)
                return row;
            await sleep(100);
        }}
    }}

    async function clickUploadButton(row) {
        while (true) {

            const btn = [...row.querySelectorAll("button")]
                .find(b => {
                    const text = b.textContent
                        .replace(/\s+/g, " ")
                        .trim();

                    return text === "Chọn tệp đính kèm";
                });

            if (btn) {
                window.pywebview.api.log(
                    "Found upload button:",
                    btn.textContent
                );

                btn.click();
                return;
            }

            await sleep(100);
        }
    }

    async function waitUploadModalClosed() {
        while (true) {

            const modalTitle = [...document.querySelectorAll("div")]
                .find(div =>
                    div.textContent.trim() === "Danh sách tài liệu điện tử"
                );

            if (!modalTitle) {
                window.pywebview.api.log(
                    "Upload modal closed"
                );
                return;
            }

            await sleep(100);
        }
    }

    async function uploadFile(paper) {{
        window.pywebview.api.log("UPLOAD:", paper.name, paper.file);
        if (paper.file === "") {
            // Nếu không có file, bỏ qua
            window.pywebview.api.log("No file to upload, skipping:", paper.name);
            return;
        }
        // 1. Click "Chọn tệp đính kèm"
        const row = await findRowByName(paper.name);

        await clickUploadButton(row);

        // 2. Click "Tải lên từ thiết bị"
        await waitAndClickButton("Tải lên từ thiết bị");

        // 3. Click tiếp "Tải lên từ thiết bị"
        await waitAndClickButton("Tải lên từ thiết bị");

        // 4. Python xử lý hộp thoại Open
        await window.pywebview.api.upload_file(paper.file);

        window.pywebview.api.log("Upload file done:");

        // 6. Click "Thêm vào ví & Chọn", upload file
        await waitAndClickButton("Thêm vào ví & Chọn");
            
        // 7. Chờ nút "Đang tải lên" biến mất -> upload xong
        await waitUploadModalClosed();
    }}

    // kiểu tài liệu (ko dùng)
    // async function selectType(row, type) {{

    //     await window.pywebview.api.log("SELECT:", type);

    //     // TODO:
    //     // click combobox
    //     // chọn option
    // }}

    async function syncTable() {{

        await waitUntilReady();

        const existed = new Map();

        // =========================
        // Quét các dòng hiện có
        // =========================

        for (const row of getRows()) {{

            const name = getRowName(row);

            if (name)
                existed.set(name, row);
        }}

        // =========================
        // Phase 1: Thêm các dòng còn thiếu
        // =========================

        for (const paper of papers) {{

            if (existed.has(paper.name))
                continue;

            window.pywebview.api.log("Thêm:", paper.name);

            const row = await addRow();

            await fillName(row, paper.name);

            existed.set(paper.name, row);
        }}

        // Chờ React render ổn định
        await sleep(1000);

        // =========================
        // Phase 2: Upload
        // =========================

        for (const paper of papers) {{

            await uploadFile(paper);

        }}

        await window.pywebview.api.log("DONE");
    }}
    await syncTable();

})();