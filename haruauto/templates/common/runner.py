"""하루자동화 공통 실행 뼈대.

모든 납품물이 공유하는 최소 계약:
  - 설정은 코드가 아니라 config.yaml 한 곳에 있다 (고객이 직접 수정 가능)
  - 실행 기록이 파일로 남는다
  - --dry-run 으로 실제 반영 없이 결과를 미리 볼 수 있다
  - 실패하면 사람이 안다 (조용히 죽지 않는다)
  - 나쁜 입력 한 줄이 전체를 멈추지 않는다
"""

from __future__ import annotations

import argparse
import logging
import smtplib
import sys
import traceback
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Callable

import yaml

LOG = logging.getLogger("haruauto")


# --------------------------------------------------------------------------- #
# 설정
# --------------------------------------------------------------------------- #

def load_config(path: str | Path) -> dict[str, Any]:
    """config.yaml 을 읽는다. 없거나 비어 있으면 즉시 실패시킨다."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"설정 파일을 찾을 수 없습니다: {p}\n"
            f"config.example.yaml 을 config.yaml 로 복사한 뒤 값을 채워주세요."
        )
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"설정 파일 형식이 잘못되었습니다: {p}")
    return data


def require(cfg: dict[str, Any], *keys: str) -> None:
    """필수 설정 키가 비어 있으면 실행 전에 멈춘다.

    작업 중간에 KeyError 로 죽는 것보다, 시작하자마자 무엇이 비었는지
    알려주는 편이 담당자에게 훨씬 낫다.
    """
    missing = [k for k in keys if not _dig(cfg, k)]
    if missing:
        raise ValueError("config.yaml 에 다음 값이 비어 있습니다: " + ", ".join(missing))


def _dig(cfg: dict[str, Any], dotted: str) -> Any:
    cur: Any = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


# --------------------------------------------------------------------------- #
# 로그
# --------------------------------------------------------------------------- #

def setup_logging(log_dir: str | Path = "logs", verbose: bool = False) -> Path:
    """콘솔과 파일에 동시에 기록한다. 로그 파일 경로를 돌려준다."""
    d = Path(log_dir)
    d.mkdir(parents=True, exist_ok=True)
    log_file = d / "run.log"

    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers.clear()

    fmt = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", "%Y-%m-%d %H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    LOG.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    LOG.addHandler(sh)

    return log_file


# --------------------------------------------------------------------------- #
# 실행 결과 집계
# --------------------------------------------------------------------------- #

@dataclass
class Result:
    """한 번의 실행 결과. 인수인계 시 담당자에게 보여주는 요약이기도 하다."""

    processed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)

    def skip(self, reason: str) -> None:
        """나쁜 입력 한 줄 때문에 전체가 멈추면 안 된다. 건너뛰고 기록만 남긴다."""
        self.skipped += 1
        self.errors.append(reason)
        LOG.warning("건너뜀 — %s", reason)

    def summary(self) -> str:
        lines = [
            f"처리 {self.processed}건 · 건너뜀 {self.skipped}건",
        ]
        if self.outputs:
            lines.append("생성된 결과물:")
            lines += [f"  - {o}" for o in self.outputs]
        if self.errors:
            lines.append(f"건너뛴 항목 ({len(self.errors)}건):")
            lines += [f"  - {e}" for e in self.errors[:20]]
            if len(self.errors) > 20:
                lines.append(f"  ... 외 {len(self.errors) - 20}건 (자세한 내용은 logs/run.log)")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 실패 알림
# --------------------------------------------------------------------------- #

def notify(cfg: dict[str, Any], subject: str, body: str) -> None:
    """실패나 완료를 사람에게 알린다.

    조용히 멈추는 자동화는 수작업보다 위험하다. 알림 설정이 없으면
    로그에만 남기고 넘어가되, 알림 발송 자체가 실패해도 본 작업을
    되돌리지는 않는다.
    """
    mail = cfg.get("notify", {}).get("email") or {}
    if not mail.get("to"):
        LOG.info("알림 설정이 없어 메일을 보내지 않았습니다.")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = mail["from"]
        msg["To"] = mail["to"]
        msg.set_content(body)

        with smtplib.SMTP(mail.get("host", "smtp.gmail.com"), mail.get("port", 587)) as s:
            s.starttls()
            s.login(mail["from"], mail["password"])
            s.send_message(msg)
        LOG.info("알림 메일을 %s 로 보냈습니다.", mail["to"])
    except Exception as exc:  # 알림 실패가 본 작업을 무효화하지 않는다
        LOG.error("알림 메일 발송에 실패했습니다: %s", exc)


# --------------------------------------------------------------------------- #
# 진입점
# --------------------------------------------------------------------------- #

def main(job: Callable[[dict[str, Any], bool], Result], job_name: str) -> int:
    """모든 납품물이 공유하는 진입점.

    job(cfg, dry_run) -> Result 형태의 함수 하나만 넘기면
    설정 로드 / 로그 / dry-run / 예외 처리 / 알림이 전부 붙는다.
    """
    ap = argparse.ArgumentParser(description=f"하루자동화 — {job_name}")
    ap.add_argument("-c", "--config", default="config.yaml", help="설정 파일 경로")
    ap.add_argument("--dry-run", action="store_true",
                    help="실제 반영 없이 결과만 확인합니다")
    ap.add_argument("-v", "--verbose", action="store_true", help="자세한 로그")
    args = ap.parse_args()

    log_file = setup_logging(verbose=args.verbose)
    LOG.info("=" * 60)
    LOG.info("%s 시작%s", job_name, "  [연습 실행 — 실제 반영 안 함]" if args.dry_run else "")

    cfg: dict[str, Any] = {}
    try:
        cfg = load_config(args.config)
        result = job(cfg, args.dry_run)

        LOG.info("완료\n%s", result.summary())
        if not args.dry_run:
            notify(cfg, f"[하루자동화] {job_name} 완료", result.summary())
        return 0

    except Exception:
        detail = traceback.format_exc()
        LOG.error("실행이 중단되었습니다\n%s", detail)
        notify(
            cfg,
            f"[하루자동화] {job_name} 실패",
            f"자동화가 중단되었습니다.\n\n{detail}\n\n로그: {log_file.resolve()}",
        )
        return 1
