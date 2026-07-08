/** @odoo-module **/

/**
 * Clio RAG — Enter triggar sökning.
 */

const SEARCH_FIELDS = ["rag_query"];

document.addEventListener(
    "keydown",
    (ev) => {
        if (ev.key !== "Enter") return;

        const fieldWidget = ev.target.closest(".o_field_widget");
        if (!fieldWidget) return;

        const fieldName = fieldWidget.getAttribute("name");
        if (!SEARCH_FIELDS.includes(fieldName)) return;

        ev.preventDefault();
        ev.stopPropagation();

        const row = fieldWidget.closest(".o_row") || fieldWidget.parentElement;
        const btn = row && row.querySelector("button.btn-primary");
        if (btn) btn.click();
    },
    true,
);
