from flask import Flask, render_template, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from pathlib import Path
import os
import re

app = Flask(__name__)
BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "assets" / "master_template.png"
W, H = 595.5, 842.25

LIMITS = {
    "group_name": 12,
    "schedule_place": 16,
    "schedule_activity": 30,
    "goal": 45,
}

CONCEPTS = {
    "01": "첨단산업 키우는 성장도시",
    "02": "농촌, 민생 살리는 활력도시",
    "03": "교육문화 누리는 품격도시",
    "04": "건강복지 지키는 행복도시",
    "05": "생활인구 모이는 정주도시",
}

CHECKBOX = {
    "01": (82.3, 391.7),
    "02": (189.4, 391.7),
    "03": (296.4, 391.7),
    "04": (403.2, 391.7),
    "05": (512.4, 391.7),
}

SCHEDULE_ROWS = [
    ("01", 247.6),
    ("02", 216.3),
    ("03", 184.9),
    ("04", 153.3),
]


def register_fonts():
    regular_candidates = []
    bold_candidates = []

    if os.name == "nt":
        fonts_dir = Path(os.environ.get("WINDIR", r"C:\\Windows")) / "Fonts"
        regular_candidates += [fonts_dir / "malgun.ttf", fonts_dir / "NanumGothic.ttf"]
        bold_candidates += [fonts_dir / "malgunbd.ttf", fonts_dir / "NanumGothicBold.ttf"]

    regular_candidates += [
        BASE / "runtime_fonts" / "NanumGothic-Regular.ttf",
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
    ]
    bold_candidates += [
        BASE / "runtime_fonts" / "NanumGothic-Bold.ttf",
        Path("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
    ]

    regular = next((p for p in regular_candidates if p.exists()), None)
    bold = next((p for p in bold_candidates if p.exists()), None)
    if not regular or not bold:
        raise RuntimeError("Korean TrueType fonts are missing. Rebuild the service.")

    pdfmetrics.registerFont(TTFont("Korean", str(regular)))
    pdfmetrics.registerFont(TTFont("KoreanBold", str(bold)))


register_fonts()


def clean(value, limit=500):
    return re.sub(r"[\r\n\t]+", " ", (value or "").strip())[:limit]


def fit_size(text, font, max_width, size, minimum=5.8):
    while size > minimum and pdfmetrics.stringWidth(text, font, size) > max_width:
        size -= 0.2
    return size


def vertical_baseline(font, size, center_y, optical=0.0):
    ascent, descent = pdfmetrics.getAscentDescent(font, size)
    return center_y - (ascent + descent) / 2 + optical


def draw_center(c, text, center_x, center_y, max_width, size=9.0, font="Korean", white=False, optical=0.8):
    text = clean(text)
    if not text:
        return
    size = fit_size(text, font, max_width, size)
    c.setFillColorRGB(*(1, 1, 1) if white else (0.20, 0.20, 0.20))
    c.setFont(font, size)
    c.drawCentredString(center_x, vertical_baseline(font, size, center_y, optical), text)


def draw_left(c, text, x, center_y, max_width, size=8.8, font="Korean", optical=0.8):
    text = clean(text)
    if not text:
        return
    size = fit_size(text, font, max_width, size)
    c.setFillColorRGB(0.20, 0.20, 0.20)
    c.setFont(font, size)
    c.drawString(x, vertical_baseline(font, size, center_y, optical), text)


def build_pdf(data, selected_concepts):
    out = BytesIO()
    c = canvas.Canvas(out, pagesize=(W, H))
    c.drawImage(ImageReader(str(TEMPLATE)), 0, 0, W, H, mask="auto")

    # Header group number
    draw_center(c, data.get("group_no"), 282.0, 758.0, 55, 38, "KoreanBold", True, optical=0.0)

    # 01. Group information
    draw_center(c, data.get("group_name"), 146.3, 633.4, 112, 9.5, "KoreanBold")
    draw_center(c, data.get("members"), 422.3, 634.0, 286, 8.9, "KoreanBold")

    # Roles: first three have one slot; last three have two slots.
    role_single = [
        ("role_leader", 124.9),
        ("role_schedule", 206.2),
        ("role_budget", 287.6),
    ]
    for key, x in role_single:
        draw_center(c, data.get(key), x, 557.2, 50, 7.9, "Korean")

    role_double = [
        ("role_photo_1", "role_photo_2", 369.1),
        ("role_insight_1", "role_insight_2", 450.2),
        ("role_report_1", "role_report_2", 531.6),
    ]
    for key1, key2, x in role_double:
        draw_center(c, data.get(key1), x, 557.2, 50, 7.7, "Korean")
        draw_center(c, data.get(key2), x, 534.5, 50, 7.7, "Korean")

    # 02. Concepts - multiple selections allowed, at least one required.
    for concept in selected_concepts:
        if concept in CHECKBOX:
            cx, cy = CHECKBOX[concept]
            c.setStrokeColorRGB(0.93, 0.48, 0.06)
            c.setLineWidth(1.8)
            c.line(cx - 4.0, cy, cx - 1.0, cy - 3.0)
            c.line(cx - 1.0, cy - 3.0, cx + 4.5, cy + 3.5)

    # 03. Schedule
    for key, y in SCHEDULE_ROWS:
        draw_center(c, data.get(f"schedule_{key}_place"), 210.7, y, 145, 8.5, "KoreanBold")
        draw_center(c, data.get(f"schedule_{key}_activity"), 429.2, y, 270, 8.2, "Korean")

    # 04. Goal
    draw_left(c, data.get("goal"), 142.0, 82.5, 420, 8.8, "Korean")

    c.save()
    out.seek(0)
    return out


def validate(data, selected_concepts):
    no = clean(data.get("group_no"))
    if not no.isdigit() or int(no) < 1:
        return "조 번호는 1 이상의 숫자로 입력해주세요."

    required = {
        "group_name": "조 이름",
        "members": "조원 이름",
        "role_leader": "팀장",
        "role_budget": "예산 관리",
        "goal": "탐방 목표",
    }
    for key, label in required.items():
        if not clean(data.get(key)):
            return f"{label}을(를) 입력해주세요."

    if len(clean(data.get("group_name"), 100)) > LIMITS["group_name"]:
        return f"조 이름은 최대 {LIMITS['group_name']}자까지 입력할 수 있습니다."

    if not selected_concepts:
        return "탐방 컨셉을 1개 이상 선택해주세요."

    for key, _ in SCHEDULE_ROWS:
        place = clean(data.get(f"schedule_{key}_place"), 100)
        activity = clean(data.get(f"schedule_{key}_activity"), 200)
        if not place or not activity:
            return "일정표의 모든 방문지와 활동 계획을 입력해주세요."
        if len(place) > LIMITS["schedule_place"]:
            return f"방문지는 최대 {LIMITS['schedule_place']}자까지 입력할 수 있습니다."
        if len(activity) > LIMITS["schedule_activity"]:
            return f"활동 계획은 최대 {LIMITS['schedule_activity']}자까지 입력할 수 있습니다."

    if len(clean(data.get("goal"), 200)) > LIMITS["goal"]:
        return f"탐방 목표는 최대 {LIMITS['goal']}자까지 입력할 수 있습니다."

    return None


@app.get("/")
def index():
    return render_template("index.html", concepts=CONCEPTS, limits=LIMITS)


@app.post("/generate")
def generate():
    data = request.form.to_dict()
    selected_concepts = [x for x in request.form.getlist("concept") if x in CONCEPTS]

    error = validate(data, selected_concepts)
    if error:
        return jsonify({"error": error}), 400

    no = clean(data.get("group_no"))
    group_name = clean(data.get("group_name"), LIMITS["group_name"])
    safe = re.sub(r'[\\/:*?"<>|]', "", group_name).strip() or "조"

    return send_file(
        build_pdf(data, selected_concepts),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"탐방계획서_{no}조_{safe}.pdf",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
