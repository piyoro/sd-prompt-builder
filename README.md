# sd-prompt-builder

Stable Diffusion WebUI Forge용 **영역별 프롬프트 입력기** 확장입니다.

긴 한 줄 프롬프트 대신 영역별 칸에 나눠 입력하면, 정해진 순서대로 쉼표로 합쳐서
상단 Prompt / Negative prompt 칸에 실시간으로 채워 넣습니다. Generate는 평소처럼
상단 칸의 내용으로 요청됩니다.

## 기능

- UI 프리셋이 **sd / xl** 일 때만 표시됩니다 (flux, all 에서는 숨김).
- Txt2img, Img2img 탭 모두 지원합니다.
- 페이지를 열면 기본값이 상단 프롬프트 칸에 자동으로 채워집니다.
- 상단 칸의 토큰 카운터(0/75)도 함께 갱신됩니다.
- **사용** 체크박스를 끄면 상단 칸에 직접 입력할 수 있습니다.
- **기본값으로 되돌리기** / **모두 비우기** 버튼.

## 영역 (합쳐지는 순서)

Prompt

1. 품질 / 형식
2. 주제 (누가 / 무엇을)
3. 머리
4. 눈
5. 의상
6. 소품 / 액세서리
7. 자세
8. 손 / 동작
9. 시선
10. 표정
11. 배경 / 장소
12. 조명 / 분위기
13. 구도 / 카메라
14. 스타일 / 질감
15. 기타 (LoRA, 임베딩 등) — 기본값 없음

Negative

1. 배제할 스타일
2. 품질 문제
3. 인체 오류
4. 구도 / 기타

기본값과 영역 구성은 `scripts/prompt_builder.py` 상단의
`POSITIVE_SECTIONS`, `NEGATIVE_SECTIONS` 에서 바꿀 수 있습니다.

## 설치

**URL로 설치 (권장)**

1. Forge 화면에서 **Extensions → Install from URL**
2. 이 저장소 주소를 입력하고 **Install**
3. **Installed** 탭에서 **Apply and restart UI**

**직접 복사**

이 폴더를 Forge의 `extensions/` 아래에 넣고 Forge를 재시작합니다.

```
stable-diffusion-webui-forge/extensions/sd-prompt-builder/
```

## 참고

- 빌더 칸에 입력한 값은 `ui-config.json` 에 저장되지 않으며, 새로고침하면 기본값으로 돌아갑니다.
- Forge `f2.0.1v1.10.1` 에서 테스트했습니다.
