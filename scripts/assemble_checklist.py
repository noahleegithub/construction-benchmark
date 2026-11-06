#!/usr/bin/env python3
"""Assemble the translated, deduplicated architecture checklist.

Inputs:
  release_items_full.json   extracted from the 250709 workbook (Korean)
  translate/part*.en.json   translated slices

Outputs (docs/checklists):
  architecture-design-verification-checklist.md
  architecture-design-verification-checklist.csv
  architecture-design-verification-checklist.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

AREA = {
    "표제부": "Title block and general sheets",
    "단지계획": "Site planning",
    "아파트": "Apartment buildings",
    "지하주차장": "Underground parking",
    "부대복리시설": "Auxiliary welfare facilities",
}
STAGE = {
    "초기검토": "Initial review",
    "셀프검증": "Self-verification",
    "본검증": "Main verification",
}
SUBCATEGORY = {
    "법규위반": "Code violation",
    "법규·지침": "Code/guideline",
    "성능미확보": "Performance deficiency",
    "주요하자": "Major defect",
    "일반하자": "General defect",
    "재난안전": "Disaster safety",
    "구조안전": "Structural safety",
    "승인조건": "Approval condition",
    "5대하자": "Five major defects",
    "도면미작성": "Drawing not prepared",
    "사업비 변경": "Project cost change",
    "단순오류": "Simple error",
    "기타제안": "Other recommendation",
}
CATEGORY = {
    "법규·지침": "Code/guideline",
    "주요하자": "Major defect",
    "일반하자": "General defect",
    "재난안전": "Disaster safety",
    "구조안전": "Structural safety",
    "단순오류": "Simple error",
    "기타제안": "Other recommendation",
}
DISCIPLINE = {
    "건축": "Architecture",
    "토목": "Civil",
    "구조": "Structural",
    "전기": "Electrical",
    "조경": "Landscape",
    "기계": "Mechanical",
    "소방": "Fire protection",
}
DRAWING = {
    "단위세대 평면도": "Dwelling unit floor plan",
    "동평면도": "Building floor plan",
    "단지배치도": "Site layout plan",
    "코아평면도": "Core floor plan",
    "실내재료마감표": "Interior finish schedule",
    "지하주차장 평면도": "Underground parking floor plan",
    "주단면도": "Main section",
    "창호상세도": "Window detail",
    "램프 평면도": "Ramp plan",
    "인테리어(주방가구)": "Interior (kitchen cabinets)",
    "단열 상세도": "Insulation detail",
    "부대복리시설": "Auxiliary welfare facilities",
    "방수 및 단열 상세도": "Waterproofing and insulation detail",
    "동입면도": "Building elevation",
    "주동평면도": "Residential tower plan",
    "부대복리시설 평면도": "Auxiliary welfare facility plan",
    "형별성능관계내역서": "Performance specification by unit type",
    "인테리어(신발장)": "Interior (shoe cabinet)",
    "램프 단면도": "Ramp section",
    "어린이집 평면도": "Daycare center plan",
    "부대복리시설 평면도 등": "Auxiliary welfare facility plan, etc.",
    "부대복리시설 창호도": "Auxiliary welfare facility window schedule",
    "인동거리배치도": "Inter-building distance layout plan",
    "건축개요": "Architectural overview",
    "DA상세도": "DA (supply/exhaust vent) detail",
    "외부계단 평·단면도": "Exterior stair plan and section",
    "복합설계도": "Composite design drawing",
    "부대시설평면도": "Auxiliary facility plan",
    "공통사항": "General notes",
    "방화구획도": "Fire compartment plan",
    "면적산출표": "Area calculation table",
    "주출입구 평면도": "Main entrance plan",
    "코어 평면도": "Core plan",
    "코어 단면도": "Core section",
    "계절창고 단면도": "Seasonal storage section",
    "단열 및 방수 상세도": "Insulation and waterproofing detail",
    "단위세대 창호도": "Dwelling unit window schedule",
    "인테리어(욕실)": "Interior (bathroom)",
    "인테리어(욕실, 거실 등)": "Interior (bathroom, living room, etc.)",
    "입면도": "Elevation",
    "필로티 평면도": "Piloti plan",
    "단위세대 단면도": "Dwelling unit section",
    "기계도서": "Mechanical drawings",
    "지하주차장": "Underground parking",
    "익스테리어": "Exterior",
    "걸레받이 및 반자돌림": "Baseboard and ceiling trim",
    "마감 시공한계도": "Finish construction limit plan",
    "단면도": "Section",
    "전기 발전기실 단면도": "Electrical generator room section",
    "램프 입면도": "Ramp elevation",
    "지하 교통체계도": "Underground traffic circulation plan",
    "램프 정면도": "Ramp front elevation",
    "전기 발전기실 평면도": "Electrical generator room plan",
    "지하주차장 단면도": "Underground parking section",
    "외부계단 평면도": "Exterior stair plan",
    "외부계단 단면도": "Exterior stair section",
    "휀룸 상세도": "Fan room detail",
    "지하시설물 복합평면도": "Underground utilities composite plan",
    "주동 평면도": "Residential tower plan",
    "주동 입면도": "Residential tower elevation",
    "근로자 휴게시설 평면도": "Worker rest facility plan",
    "경비실 평면도": "Security office plan",
    "다함께 돌봄센터 평면도": "Community care center plan",
    "평면도": "Floor plan",
    "부대복리시설 창호상세도": "Auxiliary welfare facility window detail",
    "실내재료마감상세도": "Interior finish detail",
    "부대복리시설 입면도": "Auxiliary welfare facility elevation",
    "익스테리어 보고서": "Exterior report",
}

DEDUCTION_TABLE = """## Appendix A. Deduction classification

Each checklist item carries a deduction applied to the verification score when
the item is not met. The table below is translated from the deduction classification sheet common to
both source workbooks (Existing = rate before the change; Proposed = rate after).

| Classification | Criterion | Existing | Proposed |
|---|---|---:|---:|
| Structural safety | Structurally unsafe due to an error in a major structural member (load-bearing wall, column, slab, beam, roof, foundation, main stair) | 0.50 | 0.50 |
| Structural safety | Major structural member error with no effect on structural safety | 0.20 | 0.20 |
| Structural safety | Other error in structural design (drawings, calculations) | 0.10 | 0.05 |
| Disaster safety | Fire doors, evacuation plan or temporary works insufficient, leaving the building vulnerable to fire or other disaster | 0.20 | 0.20 |
| Code/guideline | Violation of a design code, certification scheme or higher-level plan | 0.20 | 0.20 |
| Code/guideline | Non-compliance with a project approval condition or local-authority agreement | — | — |
| Major defect | Risk in one of the five major defect areas: leakage, condensation, insulation, noise, indoor air quality | — | — |
| Major defect | Performance cannot be secured, e.g. undersized windows or rooms | 0.20 | 0.20 |
| Major defect | Drawing not prepared or unclear, creating a defect risk | — | — |
| Major defect | Omission or estimate error likely to change the project cost (new category) | — | — |
| General defect | Violation of an internal guideline, or a defect, complaint, safety or constructability issue not covered above | 0.10 | 0.05 |
| Simple error | Drawing consistency or other simple error outside the categories above | 0.05 | 0.05 |
| Other recommendation | Not a drawing error, but a design improvement proposed by the reviewer | — | — |

Subcategory-to-category mapping and deduction per item:

| Subcategory | Category | Deduction |
|---|---|---:|
| Disaster safety | Disaster safety | 0.20 |
| Code violation | Code/guideline | 0.20 |
| Approval condition | Code/guideline | 0.20 |
| Five major defects | Major defect | 0.20 |
| Performance deficiency | Major defect | 0.20 |
| Drawing not prepared | Major defect | 0.20 |
| Project cost change | Major defect | 0.20 |
| General defect | General defect | 0.05 |
| Simple error | Simple error | 0.05 |
| Other recommendation | Other recommendation | 0.00 |
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.source_json.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in source}

    translated: dict[int, dict] = {}
    for path in sorted(args.translations.glob("part*.en.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload["items"]:
            translated[entry["id"]] = entry

    errors = []
    for item_id, item in by_id.items():
        if item_id not in translated:
            errors.append(f"missing translation for id {item_id}")
            continue
        if len(translated[item_id]["checkpoints"]) != len(item["checkpoints"]):
            errors.append(
                f"id {item_id}: {len(translated[item_id]['checkpoints'])} translated "
                f"checkpoints vs {len(item['checkpoints'])} source"
            )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    rows = []
    for item_id, item in by_id.items():
        tr = translated[item_id]
        area_ko = item["section"].split("\n")
        row = {
            "id": item_id,
            "grade": item["code"],
            "discipline": " / ".join(
                DISCIPLINE.get(part.strip()) or part.strip()
                for part in item["discipline"].split("\n")
            ),
            "area": " / ".join(AREA.get(part) or part for part in area_ko),
            "drawing": " / ".join(
                DRAWING.get(part.strip()) or part.strip()
                for part in item["drawing"].split("\n")
            ),
            "item": clean(tr["item"]),
            "checkpoints": [clean(point) for point in tr["checkpoints"]],
            "comments": clean(tr.get("comments", "")),
            "other": clean(tr.get("other", "")),
            "basis": clean(tr.get("basis", ""), sep=" · "),
            "stage": STAGE.get(item["stage"], item["stage"]),
            "subcategory": SUBCATEGORY.get(item["subcategory"], item["subcategory"]),
            "category": CATEGORY.get(item["category"], item["category"]),
            "deduction": item["deduction"],
        }
        rows.append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "architecture-design-verification-checklist.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    with (args.out / "architecture-design-verification-checklist.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "grade",
                "discipline",
                "area",
                "drawing",
                "checklist_item",
                "checkpoints",
                "additional_comment",
                "other",
                "basis",
                "verification_stage",
                "subcategory",
                "category",
                "deduction",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["id"],
                    row["grade"],
                    row["discipline"],
                    row["area"],
                    row["drawing"],
                    row["item"],
                    " || ".join(row["checkpoints"]),
                    row["comments"],
                    row["other"],
                    row["basis"],
                    row["stage"],
                    row["subcategory"],
                    row["category"],
                    row["deduction"],
                ]
            )

    (args.out / "architecture-design-verification-checklist.md").write_text(
        markdown(rows), encoding="utf-8"
    )
    print(f"wrote {len(rows)} items and {sum(len(r['checkpoints']) for r in rows)} checkpoints")
    return 0


def clean(value: str, sep: str = " ") -> str:
    """Trim, collapse line wraps, and remove Korean glosses that duplicate English."""
    if not value:
        return ""
    value = value.replace(" (주거약자법)", "").replace("(주거약자법)", "")
    value = value.replace(" (다함께 돌봄센터)", "").replace("(다함께 돌봄센터)", "")
    value = re.sub(r"\s*\n\s*", sep, value)
    value = re.sub(r"[ \t]+", " ", value)
    value = value.replace(" ,", ",")
    return value.strip()


def markdown(rows: list[dict]) -> str:
    total_points = sum(len(row["checkpoints"]) for row in rows)
    lines = [
        "# Architectural Design Verification Checklist (2025)",
        "",
        "English translation of the Korean 2025 design-verification checklist for",
        "architecture, consolidated from the 2025-07-01 policy draft and the",
        "2025-07-09 distribution release.",
        "",
        f"**{len(rows)} checklist items · {total_points} checkpoints.**",
        "",
        "The Korean source is authoritative. Items retain their original numbering.",
        "An English CSV and a machine-readable JSON file sit beside this document.",
        "",
        "The 2025-07-01 draft and the 2025-07-09 release contain the same 135 item texts.",
        "The draft's 490 checkpoint fragments all appear in the release's 453 consolidated",
        "checkpoints; the difference is line wrapping, not omitted content.",
        "",
        "## Contents",
        "",
    ]

    counts: dict[str, int] = {}
    for row in rows:
        primary = row["area"].split(" / ")[0]
        counts[primary] = counts.get(primary, 0) + 1

    lines += ["| Area | Items |", "|---|---:|"]
    lines += [f"| {area} | {count} |" for area, count in counts.items()]
    lines += ["", "## Checklist", ""]

    for row in rows:
        lines.append(f"### {row['id']}. {row['item']}")
        lines.append("")
        meta = [
            f"**Area:** {row['area']}",
            f"**Drawing:** {row['drawing']}" if row["drawing"] else "",
            f"**Grade:** {row['grade']}" if row["grade"] else "",
            f"**Verification stage:** {row['stage']}" if row["stage"] else "",
            f"**Classification:** {row['subcategory']} / {row['category']}"
            if row["subcategory"] or row["category"]
            else "",
            f"**Deduction:** {row['deduction']}" if row["deduction"] else "",
        ]
        lines.append(" · ".join(part for part in meta if part))
        lines.append("")
        if row["checkpoints"]:
            lines.append("**Checkpoints**")
            lines.append("")
            lines += [f"- [ ] {point}" for point in row["checkpoints"]]
            lines.append("")
        for label, key in (
            ("Additional comment", "comments"),
            ("Other", "other"),
            ("Basis", "basis"),
        ):
            if row[key]:
                lines.append(f"**{label}.** {row[key]}")
                lines.append("")

    lines += ["", DEDUCTION_TABLE]
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
