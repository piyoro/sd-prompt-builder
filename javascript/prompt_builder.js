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
});
