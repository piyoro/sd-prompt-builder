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

1. 품질 / 형식 (`quality`)
2. 구도 / 앵글 (`composition`)
3. 주제 (누가 / 무엇을) (`subject`)
4. 머리 (`hair`)
5. 눈 (`eyes`)
6. 의상 (`clothing`)
7. 소품 / 액세서리 (`accessory`)
8. 자세 (`pose`)
9. 손 / 동작 (`hands`)
10. 시선 (`gaze`)
11. 표정 (`expression`)
12. 배경 / 장소 (`setting`)
13. 조명 / 분위기 (`lighting`)
14. 렌즈 / 촬영 효과 (`camera`)
15. 스타일 / 질감 (`style`)
16. 기타 (LoRA, 임베딩 등) (`extra`) — 기본값 없음

구도 / 앵글을 주제 앞에 두는 이유: SD 1.5 는 프롬프트를 75토큰 단위로 끊어 읽기 때문에
뒤쪽 단어일수록 영향력이 약해집니다. 그림 전체의 틀을 정하는 구도 단어는 앞에 둡니다.

괄호 안의 key 는 변환기(sd-prompt-translator)가 돌려주는 `section` 값과 같습니다.

Negative

1. 배제할 스타일
2. 품질 문제
3. 인체 오류
4. 구도 / 기타

## 붙여넣기 (변환기 랜덤 생성기 연동)

`영역key: 태그` 형식의 텍스트를 붙여넣으면 해당 영역 칸에 나눠서 반영합니다.

```
# sd-prompt-builder
hair: short hair, red hair   # 짧은 머리, 빨간 머리
eyes: blue eyes
pose: standing
```

- 빌더의 **아무 칸에나** 붙여넣어도 자동으로 나눠 들어갑니다
  (`영역key:` 로 시작하는 줄이 하나라도 있을 때만, 평범한 태그 붙여넣기는 그대로).
- **붙여넣기** 아코디언의 칸에 넣고 **영역에 반영** 을 눌러도 됩니다.
- `#` 으로 시작하는 줄과, 줄 끝의 `# ...` (한글 뜻 등)는 무시합니다.
- key 대신 한글 영역 이름(`머리`, `눈`, `의상`, `소품`, `액세서리` ...)도 받습니다.
- 기본은 해당 영역을 덮어쓰고, **기존 내용 뒤에 추가** 를 켜면 뒤에 붙입니다.
- 형식에 없는 영역은 그대로 둡니다.

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
