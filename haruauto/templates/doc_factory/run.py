"""doc_factory — 데이터 한 행당 문서 하나를 자동 생성한다.

LITE 등급의 나머지 절반이 이 모양이다:
  "거래처마다 정산서를 매달 손으로 만들어요"

템플릿 안의 {{항목명}} 자리에 각 행의 값을 채워 넣는다.
결과는 거래처별로 나뉜 파일이 되고, 원본 데이터는 건드리지 않는다.

사용:
    python run.py --dry-run      # 몇 건이 어떤 이름으로 만들어질지만 확인
    python run.py                # 실제 생성
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.runner import LOG, Result, main, require  # noqa: E402

PLACEHOLDER = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
UNSAFE = re.compile(r'[\\/:*?"<>|]')


def _format(value: Any, spec: str | None) -> str:
    """설정에 형식이 지정된 열은 사람이 읽는 모양으로 바꾼다."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if spec == "money":
        try:
            return f"{float(value):,.0f}"
        except (TypeError, ValueError):
            return str(value)
    if spec == "date":
        try:
            return pd.to_datetime(value).strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def _fill(template: str, row: dict[str, Any], formats: dict[str, str],
          result: Result, label: str) -> str:
    """{{항목명}} 을 실제 값으로 바꾼다. 데이터에 없는 항목은 비워두고 기록한다."""
    missing: set[str] = set()

    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in row:
            missing.add(key)
            return ""
        return _format(row[key], formats.get(key))

    out = PLACEHOLDER.sub(sub, template)
    if missing:
        result.skip(f"{label} — 템플릿의 항목이 데이터에 없습니다: {sorted(missing)}")
    return out


def _safe_name(name: str) -> str:
    """파일명에 쓸 수 없는 문자를 제거한다 (윈도우 기준)."""
    cleaned = UNSAFE.sub("_", str(name)).strip().rstrip(".")
    return cleaned[:120] or "무제"


def job(cfg: dict[str, Any], dry_run: bool) -> Result:
    require(cfg, "data.file", "template.file", "output.folder", "output.filename")
    result = Result()

    data_path = Path(cfg["data"]["file"]).expanduser()
    tpl_path = Path(cfg["template"]["file"]).expanduser()
    for p in (data_path, tpl_path):
        if not p.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {p}")

    if data_path.suffix.lower() in (".xlsx", ".xls", ".xlsm"):
        df = pd.read_excel(data_path, sheet_name=cfg["data"].get("sheet_name", 0))
    else:
        df = pd.read_csv(data_path, encoding=cfg["data"].get("encoding", "utf-8-sig"))
    LOG.info("데이터 %d행을 읽었습니다.", len(df))

    template = tpl_path.read_text(encoding="utf-8")
    formats: dict[str, str] = cfg["template"].get("formats") or {}

    declared = set(PLACEHOLDER.findall(template))
    unknown = declared - set(df.columns)
    if unknown:
        # 시작하자마자 알려준다. 100건 만든 뒤에 발견하면 늦다.
        LOG.warning("템플릿에는 있지만 데이터에 없는 항목: %s", sorted(unknown))

    out_dir = Path(cfg["output"]["folder"]).expanduser()
    name_tpl = cfg["output"]["filename"]
    ext = cfg["output"].get("extension", ".txt")
    overwrite = cfg["output"].get("overwrite", False)

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for idx, raw in df.iterrows():
        row = raw.to_dict()
        label = f"{idx + 2}행"  # 엑셀에서 보이는 행 번호 (제목 줄 포함)

        filename = _safe_name(_fill(name_tpl, row, formats, result, label)) + ext
        target = out_dir / filename

        if target.exists() and not overwrite:
            result.skip(f"{label} — 같은 이름의 파일이 이미 있습니다: {filename}")
            continue

        body = _fill(template, row, formats, result, label)

        if dry_run:
            LOG.info("[연습] 만들 파일: %s", filename)
        else:
            target.write_text(body, encoding="utf-8")
            LOG.info("생성: %s", filename)

        result.processed += 1
        if not dry_run:
            result.outputs.append(str(target.resolve()))

    if dry_run:
        LOG.info("연습 실행이므로 파일을 만들지 않았습니다. (%d건 생성 예정)", result.processed)

    return result


if __name__ == "__main__":
    raise SystemExit(main(job, "문서 자동 생성"))
