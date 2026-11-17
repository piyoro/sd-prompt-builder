"""
Prompt Builder (영역별 프롬프트 입력기)

- UI 프리셋이 sd / xl 일 때만 표시됩니다.
- 영역별로 입력한 내용을 정해진 순서대로 ", " 로 합쳐서
  상단 Prompt / Negative prompt 칸에 실시간으로 채워 넣습니다.
- Generate 는 평소처럼 상단 프롬프트 칸의 내용으로 요청됩니다.
- 페이지를 열면 기본값이 상단 프롬프트 칸에 자동으로 채워집니다.
"""

import re

import gradio as gr

from modules import scripts, script_callbacks, shared


# (key, 라벨, 기본값) — 이 순서대로 합쳐집니다. 기본값은 placeholder 로도 쓰입니다.
# 외형/표정 순서: 머리 -> 눈 -> 옷 -> 소품 -> 자세 -> 손 -> 시선 -> 표정
POSITIVE_SECTIONS = [
    ("quality", "1. 품질 / 형식", "RAW photo, 8k uhd, high quality"),
    ("subject", "2. 주제 (누가 / 무엇을)", "portrait of a young woman"),
    ("hair", "3. 머리", "brown hair"),
    ("eyes", "4. 눈", "brown eyes"),
    ("clothing", "5. 의상", "casual sweater"),
    ("accessory", "6. 소품 / 액세서리", "silver necklace"),
    ("pose", "7. 자세", "sitting"),
    ("hands", "8. 손 / 동작", "holding a coffee cup"),
    ("gaze", "9. 시선", "looking at viewer"),
    ("expression", "10. 표정", "soft smile"),
    ("setting", "11. 배경 / 장소", "in a cozy cafe"),
    ("lighting", "12. 조명 / 분위기", "natural window light"),
    ("camera", "13. 구도 / 카메라", "shallow depth of field, bokeh background, dslr"),
    ("style", "14. 스타일 / 질감", "film grain, Fujifilm XT3"),
    ("extra", "15. 기타 (LoRA, 임베딩 등)", "<lora:name:0.8>"),
]

# 기본값을 채우지 않고 placeholder 로만 보여줄 칸
NO_DEFAULT = {"extra"}

NEGATIVE_SECTIONS = [
    ("n_style", "1. 배제할 스타일",
     "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime)"),
    ("n_quality", "2. 품질 문제", "worst quality, low quality, jpeg artifacts, ugly, blurry, morbid"),
    ("n_anatomy", "3. 인체 오류",
     "mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, "
     "bad anatomy, bad proportions, extra limbs, disfigured, missing arms, missing legs, extra arms, "
     "extra legs, fused fingers, too many fingers, long neck"),
    ("n_frame", "4. 구도 / 기타", "text, cropped, out of frame, duplicate"),
]

# 두 칸씩 한 줄에 배치 (key 기준)
POSITIVE_ROWS = [
    ("quality", "subject"),
    ("hair", "eyes"),
    ("clothing", "accessory"),
    ("pose", "hands"),
    ("gaze", "expression"),
    ("setting", "lighting"),
    ("camera", "style"),
    ("extra",),
]
NEGATIVE_ROWS = [("n_style", "n_quality"), ("n_anatomy", "n_frame")]

VISIBLE_PRESETS = ("sd", "xl")

# elem_id -> component (상단 프롬프트 칸을 찾기 위해 사용)
_components = {}
# 프리셋에 따라 보이기/숨기기 할 아코디언들
_accordions = []
_preset_radio = None


def default_value(key, text):
    return "" if key in NO_DEFAULT else text


def _clean(text):
    """줄바꿈은 쉼표로 바꾸고, 앞뒤 공백과 쉼표를 정리합니다."""
    text = (text or "").replace("\r", "")
    text = re.sub(r"\s*\n\s*", ", ", text)
    text = re.sub(r"\s*,\s*(,\s*)+", ", ", text)
    return text.strip().strip(",").strip()


def combine(*parts):
    return ", ".join(p for p in (_clean(x) for x in parts) if p)


def _preset_visible():
    return getattr(shared.opts, "forge_preset", "sd") in VISIBLE_PRESETS


def _no_save(component):
    """ui-config.json 에 값이 저장되지 않게 함 (저장되면 코드의 기본값을 덮어씀)."""
    component.do_not_save_to_config = True
    return component


def _bind_preset():
    """프리셋 라디오가 바뀌면 빌더 아코디언을 보이거나 숨깁니다."""
    if _preset_radio is None or not _accordions:
        return
    accordions = list(_accordions)
    _accordions.clear()
    _preset_radio.change(
        fn=lambda preset: [gr.update(visible=preset in VISIBLE_PRESETS) for _ in accordions],
        inputs=[_preset_radio],
        outputs=accordions,
        queue=False,
        show_progress=False,
    )


def _on_after_component(component, **kwargs):
    global _preset_radio
    elem_id = kwargs.get("elem_id") or getattr(component, "elem_id", None)
    if not elem_id:
        return
    _components[elem_id] = component
    if elem_id == "forge_ui_preset":
        _preset_radio = component
        _bind_preset()


script_callbacks.on_after_component(_on_after_component)


def _make_boxes(tab, sections, rows):
    by_key = {key: (label, text) for key, label, text in sections}
    boxes = {}
    for row in rows:
        with gr.Row():
            for key in row:
                label, text = by_key[key]
                boxes[key] = _no_save(gr.Textbox(
                    label=label,
                    placeholder=text,
                    value=default_value(key, text),
                    lines=1,
                    max_lines=4,
                    elem_id=f"{tab}_pb_{key}",
                ))
    # 합치는 순서는 sections 순서를 따름
    return [boxes[key] for key, _, _ in sections]


class PromptBuilderScript(scripts.Script):
    def title(self):
        return "Prompt Builder"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        tab = "img2img" if is_img2img else "txt2img"
        prompt_box = _components.get(f"{tab}_prompt")
        neg_box = _components.get(f"{tab}_neg_prompt")

        with gr.Accordion("Prompt Builder (영역별 프롬프트)", open=True, visible=_preset_visible(),
                          elem_id=f"{tab}_prompt_builder") as accordion:
            enabled = _no_save(gr.Checkbox(
                label="사용 (입력할 때마다 상단 프롬프트 칸을 자동으로 덮어씀)",
                value=True,
                elem_id=f"{tab}_prompt_builder_enabled",
            ))

            with gr.Tabs():
                with gr.Tab("Prompt"):
                    pos_boxes = _make_boxes(tab, POSITIVE_SECTIONS, POSITIVE_ROWS)
                with gr.Tab("Negative"):
                    neg_boxes = _make_boxes(tab, NEGATIVE_SECTIONS, NEGATIVE_ROWS)

            with gr.Row():
                default_btn = gr.Button("기본값으로 되돌리기", size="sm")
                clear_btn = gr.Button("모두 비우기", size="sm")
            # 페이지 로드 시 JS 가 눌러서 기본값을 상단 칸에 채움 (화면에는 숨김)
            load_sync_btn = gr.Button("sync", elem_id=f"{tab}_prompt_builder_sync",
                                      elem_classes=["prompt-builder-hidden"])

        _accordions.append(accordion)
        _bind_preset()

        if prompt_box is None or neg_box is None:
            print("[Prompt Builder] prompt textbox not found; sync disabled.")
            return []

        def sync(is_on, *parts):
            return gr.update(value=combine(*parts)) if is_on else gr.update()

        # 상단 칸의 토큰 카운터(0/75)가 갱신되도록 input 이벤트를 한 번 발생시킴
        def refresh_tokens_js(elem_id):
            return ("() => { const t = gradioApp().querySelector('#%s textarea');"
                    " if (t) t.dispatchEvent(new Event('input', {bubbles: true})); }" % elem_id)

        targets = [
            (pos_boxes, prompt_box, f"{tab}_prompt"),
            (neg_boxes, neg_box, f"{tab}_neg_prompt"),
        ]
        for boxes, target, target_id in targets:
            # 체크박스를 다시 켰을 때, 페이지 로드 시에도 바로 반영
            for trigger in boxes + [enabled]:
                trigger.change(
                    sync, inputs=[enabled] + boxes, outputs=[target], queue=False, show_progress=False
                ).then(fn=None, js=refresh_tokens_js(target_id), queue=False, show_progress=False)
            load_sync_btn.click(
                sync, inputs=[enabled] + boxes, outputs=[target], queue=False, show_progress=False
            ).then(fn=None, js=refresh_tokens_js(target_id), queue=False, show_progress=False)

        sections = POSITIVE_SECTIONS + NEGATIVE_SECTIONS
        all_boxes = pos_boxes + neg_boxes
        default_btn.click(lambda: [default_value(k, t) for k, _, t in sections], outputs=all_boxes,
                          queue=False, show_progress=False)
        clear_btn.click(lambda: ["" for _ in sections], outputs=all_boxes, queue=False, show_progress=False)

        return []
