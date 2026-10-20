from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Local validation only: this container does not have Flask installed.
# Provide a tiny stub so the PDF-building functions can be imported and tested.
flask_stub = types.ModuleType("flask")
class DummyFlask:
    def __init__(self, *a, **kw): pass
    def get(self, *a, **kw): return lambda f: f
    def post(self, *a, **kw): return lambda f: f
flask_stub.Flask = DummyFlask
flask_stub.render_template = lambda *a, **kw: None
flask_stub.request = None
flask_stub.send_file = lambda *a, **kw: None
flask_stub.jsonify = lambda *a, **kw: None
sys.modules["flask"] = flask_stub

from app import build_pdf

# 검증 전용 예시 데이터입니다. 웹페이지에서는 사용하거나 표시하지 않습니다.
data = {
    "group_no": "3",
    "group_name": "부산정책탐험대",
    "members": "김하늘, 박서준, 이지우, 최민서, 정윤호, 한소라",
    "role_leader": "김하늘",
    "role_schedule": "박서준",
    "role_budget": "이지우",
    "role_photo_1": "최민서",
    "role_photo_2": "정윤호",
    "role_insight_1": "한소라",
    "role_insight_2": "",
    "role_report_1": "박서준",
    "role_report_2": "김하늘",
    "schedule_01_place": "부산근현대역사관",
    "schedule_01_activity": "지역 역사자원의 시민 체험형 운영 방식 탐색",
    "schedule_02_place": "전포 카페거리",
    "schedule_02_activity": "골목상권과 생활인구 유입 요소 관찰",
    "schedule_03_place": "F1963",
    "schedule_03_activity": "유휴공간을 문화공간으로 전환한 사례 탐방",
    "schedule_04_place": "부산시민공원",
    "schedule_04_activity": "도심 공원의 운영 및 시민 이용 방식 조사",
    "goal": "부산의 정책 사례를 탐방하고 정읍시에 적용할 아이디어를 발굴한다.",
}

pdf = build_pdf(data, ["01", "03"])
out = ROOT / "tests" / "sample_output.pdf"
out.write_bytes(pdf.read())
print(out)
