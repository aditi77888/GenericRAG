(function () {

    function createHistoryPanel() {

        if (document.getElementById("generic-rag-history")) {
            return;
        }

        const panel = document.createElement("div");

        panel.id = "generic-rag-history";

        panel.innerHTML = `
            <div class="grh-title">
                Chat History
            </div>

            <div id="grh-list">
                <div class="grh-empty">
                    No questions yet
                </div>
            </div>
        `;

        document.body.appendChild(panel);
    }


    function updateHistory(history) {

        createHistoryPanel();

        const list = document.getElementById("grh-list");

        if (!list) {
            return;
        }

        if (!history || history.length === 0) {

            list.innerHTML = `
                <div class="grh-empty">
                    No questions yet
                </div>
            `;

            return;
        }

        list.innerHTML = "";

        history.forEach(function (turn, index) {

            const item = document.createElement("div");

            item.className = "grh-item";

            item.innerHTML = `
                <div class="grh-number">
                    ${index + 1}
                </div>

                <div class="grh-question">
                    ${escapeHtml(turn.question)}
                </div>
            `;

            list.appendChild(item);
        });
    }


    function escapeHtml(text) {

        const div = document.createElement("div");

        div.textContent = text || "";

        return div.innerHTML;
    }


    window.addEventListener("message", function (event) {

        if (!event.data) {
            return;
        }

        if (event.data.type === "GENERIC_RAG_HISTORY") {

            updateHistory(
                event.data.history
            );
        }
    });


    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            createHistoryPanel
        );

    } else {

        createHistoryPanel();
    }


    // =====================================================
    // REMOVE "Chainlit" TEXT FROM WELCOME SCREEN
    // KEEP THE CHAINLIT ICON
    // =====================================================
    function replaceChainlitBranding() {

    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT
    );

    const textNodes = [];

    while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
    }

    for (const node of textNodes) {

        if (node.nodeValue.trim() === "Chainlit") {

            node.nodeValue = node.nodeValue.replace(
                "Chainlit",
                "Assistant"
            );
        }
    }
}


function startBrandingReplacement() {

    replaceChainlitBranding();

    const brandingObserver = new MutationObserver(() => {
        replaceChainlitBranding();
    });

    brandingObserver.observe(
        document.body,
        {
            childList: true,
            subtree: true,
            characterData: true
        }
    );
}


if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        startBrandingReplacement
    );

} else {

    startBrandingReplacement();
}

    function startBrandingWatcher() {

        removeChainlitBranding();

        const brandingObserver = new MutationObserver(() => {
            removeChainlitBranding();
        });

        brandingObserver.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );
    }


    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            startBrandingWatcher
        );

    } else {

        startBrandingWatcher();
    }

})();