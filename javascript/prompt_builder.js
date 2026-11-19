// 페이지가 열리면 빌더의 기본값을 상단 Prompt / Negative prompt 칸에 채워 넣습니다.
// Gradio 이벤트 연결이 늦게 끝나는 경우가 있어, 채워질 때까지 몇 번 다시 시도합니다.
onUiLoaded(function () {
    ["txt2img", "img2img"].forEach(function (tab) {
        var tries = 0;
        var timer = setInterval(function () {
            tries += 1;
            var app = gradioApp();
            var btn = app.querySelector("#" + tab + "_prompt_builder_sync");
            var enabled = app.querySelector("#" + tab + "_prompt_builder_enabled input");
            var prompt = app.querySelector("#" + tab + "_prompt textarea");

            var done = !btn || !prompt || (enabled && !enabled.checked) || prompt.value.trim() !== "";
            if (done || tries > 30) {
                clearInterval(timer);
                return;
            }
            btn.click();
        }, 1000);
    });

    ["txt2img", "img2img"].forEach(function (tab) {
        var builder = gradioApp().querySelector("#" + tab + "_prompt_builder");
        if (builder) builder.addEventListener("paste", function (e) { onBuilderPaste(tab, e); }, true);
    });
});

// "hair: red hair" 처럼 영역 key 로 시작하는 줄이 하나라도 있으면 빌더용 붙여넣기로 봅니다.
function isBuilderPaste(tab, text) {
    var app = gradioApp();
    return text.split(/\r?\n/).some(function (line) {
        var m = line.match(/^\s*\[?\s*([a-z_]+)\s*\]?\s*[:=]/);
        return m && app.querySelector("#" + tab + "_pb_" + m[1]);
    });
}

// 빌더의 아무 칸에 붙여넣어도 → 붙여넣기 칸에 넣고 "영역에 반영" 을 누름
function onBuilderPaste(tab, e) {
    var text = (e.clipboardData || window.clipboardData).getData("text");
    if (!text || !isBuilderPaste(tab, text)) return;

    var app = gradioApp();
    var box = app.querySelector("#" + tab + "_prompt_builder_paste textarea");
    var btn = app.querySelector("#" + tab + "_prompt_builder_paste_apply");
    if (!box || !btn) return;

    e.preventDefault();
    e.stopPropagation();
    box.value = text;
    box.dispatchEvent(new Event("input", {bubbles: true}));
    // Gradio 가 값을 받은 뒤에 버튼을 눌러야 함
    setTimeout(function () { btn.click(); }, 150);
}
