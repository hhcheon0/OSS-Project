from pathlib import Path
from dotenv import load_dotenv


_LOADED = False


def load_project_env() -> None:
    """
    프로젝트 루트의 `.env` 파일만 명시적으로 로드합니다.
    여러 모듈에서 호출되어도 1회만 동작합니다.
    """
    global _LOADED
    if _LOADED:
        return

    project_root = Path(__file__).resolve().parents[2]
    dotenv_path = project_root / ".env"
    # `.env` 값을 항상 우선 적용 (Windows 환경변수에 남아있는 값으로 덮어씌워지는 문제 방지)
    load_dotenv(dotenv_path=dotenv_path, override=True)
    _LOADED = True
