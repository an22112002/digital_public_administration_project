(async () => {
    window.pywebview.api.log("Start auto pass select service");

    window.setInputValue = (element, value) => {
        const setter = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            "value"
        ).set;

        setter.call(element, value);

        element.dispatchEvent(
            new Event("input", {
                bubbles: true
            })
        );

        element.dispatchEvent(
            new Event("change", {
                bubbles: true
            })
        );
    };

    function clickAtElement(element) {
        const rect = element.getBoundingClientRect();

        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        element.dispatchEvent(new MouseEvent("mousemove", {
            bubbles: true,
            clientX: x,
            clientY: y,
            view: window
        }));

        element.dispatchEvent(new MouseEvent("mousedown", {
            bubbles: true,
            cancelable: true,
            clientX: x,
            clientY: y,
            view: window
        }));

        element.dispatchEvent(new MouseEvent("mouseup", {
            bubbles: true,
            cancelable: true,
            clientX: x,
            clientY: y,
            view: window
        }));

        element.dispatchEvent(new MouseEvent("click", {
            bubbles: true,
            cancelable: true,
            clientX: x,
            clientY: y,
            view: window
        }));
    }

    const button_send_documents_position = parseInt(BUTTON_SEND_DOCUMENTS_POSITION); // bắt đầu từ 1
    const province = PROVINCE;
    const commune = COMMUNE;

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    const cancel = (text) => {
        window.pywebview.api.log("Cancel auto pass select service");
        
        window.alert(text + ` Tự đóng sau 3 giây sau khi nhấn OK.`);

        setTimeout(() => {
            window.pywebview.api.close_window();
        }, 3000);
    }

    async function foundTriggerElement() {
        const e1 = [...window.document.querySelectorAll("div")].find(div => div.textContent.trim() === "Chọn cơ quan thực hiện");
        const e2 = [...window.document.querySelectorAll("div")].find(div => div.textContent.trim() === "Danh sách dịch vụ công");
        return e1 && e2;
    }

    async function findServiceInputElement() {
        // có input có id = "_r_1_" có placeholder = "Nhập từ khóa tìm kiếm dịch vụ công"
        // có button "Tìm kiếm"
        const input = [...window.document.querySelectorAll("input[id='_r_1_']")]
            .find((input) => input.getAttribute("placeholder") === "Nhập từ khóa tìm kiếm dịch vụ công");
        const searchButton = [...window.document.querySelectorAll("button")]
            .find((button) =>
                [...button.querySelectorAll("div")]
                    .some((div) => div.textContent.trim() === "Tìm kiếm")
            );
        return { input, searchButton };
    }

    async function waitUntilReady() {
        while (true) {
            // tìm các dấu hiệu render xong

            const triggerElement = await foundTriggerElement();

            if (triggerElement) {
                break;
            }
            
            await sleep(2000);
        }
        window.pywebview.api.log("Form bắt đầu tự động chọn dịch vụ công");
        await autoPassSelectService();
    }
    // async function findAndClickService() {

    //     const liElements = [
    //         ...document.querySelectorAll("li.transition")
    //     ];

    //     if (liElements.length === 0) {
    //         cancel(`Không tìm thấy dịch vụ công "${service_name}"`);
    //         return false;
    //     }

    //     const targetLi = liElements[service_position - 1];

    //     if (!targetLi) {
    //         cancel(
    //             `Không tìm thấy dịch vụ công "${service_name}" thứ ${service_position}`
    //         );
    //         return false;
    //     }

    //     const targetDiv = [
    //         ...targetLi.querySelectorAll("div")
    //     ].find(
    //         div => div.textContent.trim() === service_name
    //     );

    //     if (!targetDiv) {
    //         cancel(
    //             `Không tìm thấy "${service_name}" trong dịch vụ thứ ${service_position}`
    //         );
    //         return false;
    //     }
    //     window.pywebview.api.log(
    //         `Found service "${service_name}" at position ${service_position}, clicking...`
    //     );
    //     // click
    //     targetDiv.dispatchEvent(new MouseEvent("click", {
    //         bubbles: true,
    //         cancelable: true,
    //         view: window,
    //         button: 0
    //     }));

    //     return true;
    // }
    async function findAndSelectPosition(buttonText, selectedText) {
        // 1. Tìm button
        let button;

        while (!button) {
            button = [...window.document.querySelectorAll(
                'button[aria-haspopup="listbox"]'
            )].find(button => {
                const span = button.querySelector("span");
                return span?.textContent.trim() === buttonText;
            });

            if (!button) {
                await sleep(100);
            }
        }
        // 2. Click button
        button.click();

        await sleep(100);

        return true;
    }
    async function waitAndClickOption(text) {
        pywebview.api.log(`Waiting for option: ${text}`);
        while (true) {
            window.pywebview.api.log(`Looking for option: ${text}`);
            const option = [...window.document.querySelectorAll(
                'ul[role="listbox"] li[role="option"]'
            )].find(li =>
                li.textContent.trim() === text
            );

            if (option) {
                // TÌM THẤY OPTION
                option.dispatchEvent(new MouseEvent("mousedown", {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
                window.pywebview.api.log(`Clicked option: ${text}`);

                // Chờ dropdown biến mất
                while (document.querySelector('ul[role="listbox"]')) {
                    // window.pywebview.api.log(`Waiting for dropdown to close after selecting: ${text}`);
                    await sleep(100);
                }

                return true;
            }

            await sleep(100);
        }
    }
    async function clickDongYButton() {
        while (true) {
            const targetButtons = [
                ...window.document.querySelectorAll("button")
            ].filter((button) => {
                const span = button.querySelector("span");
                return (
                    span &&
                    span.textContent.trim().includes("Đồng ý")
                );
            });
            if (targetButtons.length > 0) {
                const targetButton = targetButtons[0];
                window.pywebview.api.log(
                    `Click "Đồng ý" button`
                );
                targetButton.click();
                return true;
            }

            await sleep(100);
        }
    }
    async function clickNopTrucTuyenButton() {
        while (true) {
            const targetButtons = [
                ...window.document.querySelectorAll("button")
            ].filter((button) => {
                const span = button.querySelector("span");

                return (
                    span &&
                    span.textContent.trim().includes("Nộp trực tuyến")
                );
            });

            if (targetButtons.length >= button_send_documents_position) {
                const targetButton =
                    targetButtons[button_send_documents_position - 1];

                window.pywebview.api.log(
                    `Click "Nộp trực tuyến" position ${button_send_documents_position}`
                );

                targetButton.click();

                return true;
            }

            await sleep(100);
        }
    }

    // main
    async function autoPassSelectService() {
        // const {input, searchButton} = await findServiceInputElement();
        // window.setInputValue(input, service_name);
        // await sleep(1000);
        // searchButton.click();
        // await sleep(2000);
        // const result = await findAndClickService();
        // if (!result) {
        //     return;
        // }
        await sleep(2000);
        const resultProvince = await findAndSelectPosition("-- Chọn Tỉnh/ Thành phố --");
        const resultSelectedProvince = await waitAndClickOption(province);
        const resultCommune = await findAndSelectPosition("-- Chọn Phường/ Xã --");
        const resultSelectedCommune = await waitAndClickOption(commune);
        await sleep(1000);
        // if (!resultProvince && !resultCommune) {
        //     cancel("Không tìm thấy tỉnh hoặc xã phù hợp với dữ liệu đã nhập");
        //     return;
        // }
        await sleep(1000);
        await clickDongYButton();
        await sleep(1000);
        const resultSendDocuments = await clickNopTrucTuyenButton();
        // if (!resultSendDocuments) {
        //     cancel("Không tìm thấy button Nộp trực tuyến");
        //     return;
        // }
    }

    await waitUntilReady();
})();