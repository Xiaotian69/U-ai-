import argparse
import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


DEFAULT_URL = (
    "https://ucontent.unipus.cn/_explorationpc_default/pc.html?"
    "cid=1589613532819833081&theme=3264FA&aitutorialId=25705&"
    "cloudCurriculaId=266531&source=cloud&courseResourceId=20000948094#/"
    "course-v2:7f3402a1f00cf77+nhce_v4_rw_2+20230116/courseware/"
    "6275f64dc00123f/662b4f1c5000d39/662b4f6530010bf/662b47cde000d39"
)

DEFAULT_BUTTON_TEXT = "\u786e\u5b9a"


@dataclass(frozen=True)
class Settings:
    url: str = DEFAULT_URL
    button_text: str = DEFAULT_BUTTON_TEXT
    poll_seconds: float = 5.0
    profile_dir: Path = Path(".browser-profile")
    log_dir: Path = Path("logs")
    headless: bool = False

    def __post_init__(self) -> None:
        if self.poll_seconds < 1:
            raise ValueError("poll_seconds must be at least 1 second")
        object.__setattr__(self, "profile_dir", Path(self.profile_dir))
        object.__setattr__(self, "log_dir", Path(self.log_dir))


def build_button_patterns(button_text: str) -> list[str]:
    return [
        button_text,
        f"text={button_text}",
        f'button:has-text("{button_text}")',
        f'[role=button]:has-text("{button_text}")',
        f'.ant-btn:has-text("{button_text}")',
        f'a:has-text("{button_text}")',
    ]


def configure_logging(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("popup_clicker")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_dir / "popup_clicker.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


def _candidate_locators(frame, button_text: str):
    escaped_text = re.escape(button_text)
    yield frame.get_by_role("button", name=re.compile(rf"^\s*{escaped_text}\s*$"))

    for pattern in build_button_patterns(button_text):
        if pattern == button_text:
            yield frame.get_by_text(button_text, exact=True)
        else:
            yield frame.locator(pattern)


def click_known_popup(page, button_text: str) -> bool:
    for frame in page.frames:
        for locator in _candidate_locators(frame, button_text):
            try:
                if locator.count() == 0:
                    continue

                target = locator.first
                if target.is_visible(timeout=500):
                    target.click(timeout=1500)
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
    return False


def parse_args(argv: list[str] | None = None) -> Settings:
    parser = argparse.ArgumentParser(
        description="Open the Unipus page and click the normal notification popup.",
    )
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--button-text", default=DEFAULT_BUTTON_TEXT)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--profile-dir", type=Path, default=Path(".browser-profile"))
    parser.add_argument("--log-dir", type=Path, default=Path("logs"))
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args(argv)

    return Settings(
        url=args.url,
        button_text=args.button_text,
        poll_seconds=args.poll_seconds,
        profile_dir=args.profile_dir,
        log_dir=args.log_dir,
        headless=args.headless,
    )


def run(settings: Settings) -> None:
    logger = configure_logging(settings.log_dir)
    settings.profile_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting browser. Profile: %s", settings.profile_dir.resolve())
    logger.info("Target URL: %s", settings.url)
    logger.info(
        "If a login page appears, sign in manually in the visible browser. "
        "The script will keep watching."
    )

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(settings.profile_dir.resolve()),
            headless=settings.headless,
            viewport={"width": 1280, "height": 900},
            args=["--start-maximized"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(settings.url, wait_until="domcontentloaded", timeout=60_000)

        try:
            while True:
                clicked = False
                for current_page in list(context.pages):
                    if current_page.is_closed():
                        continue
                    try:
                        if click_known_popup(current_page, settings.button_text):
                            clicked = True
                            logger.info('Clicked popup button "%s"', settings.button_text)
                            break
                    except PlaywrightError as exc:
                        logger.warning("Popup check skipped on one page: %s", exc)

                if not clicked:
                    logger.debug('No "%s" popup visible yet', settings.button_text)

                time.sleep(settings.poll_seconds)
        except KeyboardInterrupt:
            logger.info("Stopping after Ctrl+C.")
        finally:
            context.close()


def main(argv: list[str] | None = None) -> int:
    settings = parse_args(argv)
    run(settings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
