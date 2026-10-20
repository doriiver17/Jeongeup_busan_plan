# 정읍시청 부산 정책 골목 탐방계획서 v2

새 양식 기준의 Flask + ReportLab PDF 생성 웹앱입니다.

## 필수 입력
- 조 번호(1~5)
- 조 이름
- 조원 이름
- 팀장
- 예산 관리
- 탐방 컨셉 1개 이상
- 일정표 4개 행의 방문지 / 활동 계획
- 탐방 목표

## 글자 수 제한
- 조 이름: 12자
- 방문지: 16자
- 활동 계획: 30자
- 탐방 목표: 45자

웹 화면에 실시간 글자 수가 표시됩니다.

## 예시 데이터
실제 사이트 HTML에는 예시 데이터가 포함되지 않습니다. 검증용 값은 `tests/generate_sample.py`에만 있습니다.

## Render
- Build Command: `bash build.sh`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
- Python: `3.13.7`
