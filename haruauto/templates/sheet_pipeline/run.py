"""sheet_pipeline — 여러 엑셀/CSV 파일을 취합하고 정제해 하나의 결과 파일로 만든다.

LITE 등급 요청의 대부분이 이 모양이다:
  "매일 채널별로 내려받은 주문서 파일들을 하나로 합쳐서 정리해요"

원본은 절대 건드리지 않고 결과를 새 파일로 만든다 (되돌릴 수 있어야 하므로).

사용:
    python run.py --dry-run      # 결과 미리보기 (파일 생성 안 함)
    python run.py                # 실제 실행
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.runner import LOG, Result, main, require  # noqa: E402


def _read_one(path: Path, cfg: dict[str, Any]) -> pd.DataFrame:
    """파일 하나를 읽는다. 확장자에 따라 알아서 처리한다."""
    src = cfg["source"]
    if path.suffix.lower() in (".xlsx", ".xls", ".xlsm"):
        return pd.read_excel(
            path,
            sheet_name=src.get("sheet_name", 0),
            header=src.get("header_row", 1) - 1,  # 사람은 1부터 센다
            dtype=str,
        )
    return pd.read_csv(path, header=src.get("header_row", 1) - 1, dtype=str,
                       encoding=src.get("encoding", "utf-8-sig"))


def _clean(df: pd.DataFrame, cfg: dict[str, Any], result: Result) -> pd.DataFrame:
    """설정에 적힌 정제 규칙을 순서대로 적용한다."""
    rules = cfg.get("clean", {})

    if rules.get("strip_whitespace", True):
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip().replace({"nan": None})

    rename = rules.get("rename_columns") or {}
    if rename:
        unknown = set(rename) - set(df.columns)
        if unknown:
            result.skip(f"설정의 rename_columns 에 없는 열이 있습니다: {sorted(unknown)}")
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    for col in rules.get("required_columns") or []:
        if col not in df.columns:
            raise ValueError(
                f"필수 열 '{col}' 이(가) 원본에 없습니다. "
                f"원본에 있는 열: {list(df.columns)}"
            )

    before = len(df)
    for col in rules.get("drop_if_empty") or []:
        if col in df.columns:
            df = df[df[col].notna() & (df[col].astype(str).str.strip() != "")]
    if before != len(df):
        LOG.info("빈 값 행 %d개를 제외했습니다.", before - len(df))

    for col in rules.get("numeric_columns") or []:
        if col in df.columns:
            cleaned = df[col].astype(str).str.replace(r"[,\s₩원]", "", regex=True)
            df[col] = pd.to_numeric(cleaned, errors="coerce")
            bad = int(df[col].isna().sum())
            if bad:
                result.skip(f"'{col}' 열에서 숫자로 읽을 수 없는 값 {bad}건")

    for col in rules.get("date_columns") or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    dedup = rules.get("dedupe_by") or []
    if dedup:
        keys = [c for c in dedup if c in df.columns]
        if keys:
            before = len(df)
            df = df.drop_duplicates(subset=keys, keep="last")
            if before != len(df):
                LOG.info("중복 %d행을 제거했습니다 (기준: %s).", before - len(df), ", ".join(keys))

    sort_by = [c for c in (rules.get("sort_by") or []) if c in df.columns]
    if sort_by:
        df = df.sort_values(sort_by)

    return df.reset_index(drop=True)


def _summarize(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame | None:
    """설정에 집계가 있으면 요약 시트를 만든다."""
    agg = cfg.get("summary") or {}
    group, value = agg.get("group_by"), agg.get("sum_column")
    if not (group and value):
        return None
    if group not in df.columns or value not in df.columns:
        LOG.warning("집계 설정의 열을 찾을 수 없어 요약을 건너뜁니다.")
        return None
    out = df.groupby(group, dropna=False)[value].agg(["count", "sum"]).reset_index()
    return out.rename(columns={"count": "건수", "sum": f"{value} 합계"})


def job(cfg: dict[str, Any], dry_run: bool) -> Result:
    require(cfg, "source.folder", "output.folder")
    result = Result()

    folder = Path(cfg["source"]["folder"]).expanduser()
    pattern = cfg["source"].get("pattern", "*.xlsx")
    files = sorted(p for p in folder.glob(pattern) if not p.name.startswith("~$"))

    if not files:
        raise FileNotFoundError(f"{folder} 안에 '{pattern}' 에 맞는 파일이 없습니다.")
    LOG.info("파일 %d개를 찾았습니다.", len(files))

    frames: list[pd.DataFrame] = []
    for path in files:
        try:
            df = _read_one(path, cfg)
            if cfg["source"].get("add_source_column", True):
                df["출처파일"] = path.name
            frames.append(df)
            result.processed += 1
            LOG.info("읽음: %s (%d행)", path.name, len(df))
        except Exception as exc:
            # 파일 하나가 깨져도 나머지는 처리한다
            result.skip(f"{path.name} — 읽기 실패: {exc}")

    if not frames:
        raise RuntimeError("읽을 수 있는 파일이 하나도 없었습니다.")

    merged = pd.concat(frames, ignore_index=True)
    LOG.info("합계 %d행을 합쳤습니다.", len(merged))

    cleaned = _clean(merged, cfg, result)
    LOG.info("정제 후 %d행이 남았습니다.", len(cleaned))

    summary = _summarize(cleaned, cfg)

    if dry_run:
        LOG.info("연습 실행이므로 파일을 만들지 않았습니다. 결과 미리보기:\n%s",
                 cleaned.head(10).to_string())
        return result

    out_dir = Path(cfg["output"]["folder"]).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime(cfg["output"].get("timestamp_format", "%Y%m%d_%H%M"))
    out_path = out_dir / f"{cfg['output'].get('filename_prefix', '취합결과')}_{stamp}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        cleaned.to_excel(writer, sheet_name="취합", index=False)
        if summary is not None:
            summary.to_excel(writer, sheet_name="요약", index=False)

    result.outputs.append(str(out_path.resolve()))
    LOG.info("결과 파일을 만들었습니다: %s", out_path)
    return result


if __name__ == "__main__":
    raise SystemExit(main(job, "파일 취합·정제"))
