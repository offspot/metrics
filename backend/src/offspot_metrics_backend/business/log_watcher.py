import json
import logging
from asyncio import sleep
from collections.abc import Callable
from pathlib import Path
from typing import TypeGuard

from pydantic.dataclasses import dataclass
from watchdog.events import (
    EVENT_TYPE_CREATED,
    EVENT_TYPE_DELETED,
    EVENT_TYPE_MODIFIED,
    EVENT_TYPE_MOVED,
    FileSystemEvent,
    FileSystemEventHandler,
    FileSystemMovedEvent,
)
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


@dataclass
class NewLineEvent:
    file_path: Path
    line_content: str


ENCODING = "utf-8"


class LogWatcherHandler(FileSystemEventHandler):
    """Handler of watchdog events"""

    def __init__(self, data_folder: str, handler: Callable[[NewLineEvent], None]):
        self.file_positions_map: dict[str, int] = {}
        self.line_process_func = handler
        if not Path(data_folder).exists():
            raise ValueError(f"Logwatcher data folder is missing: {data_folder}")
        self.state_file_path = Path(data_folder).joinpath("log_watcher_state.json")
        if not self.state_file_path.exists():
            return  # This is ok on first startup
        with open(self.state_file_path) as fh:
            state = json.load(fh)
            self.file_positions_map = state["file_pointers"]

    def _is_moved_event(
        self, event: FileSystemEvent
    ) -> TypeGuard[FileSystemMovedEvent]:
        """TypeGuard to help type checker detect moved event class"""
        return event.event_type == EVENT_TYPE_MOVED

    def process_new_lines(self, file_path: Path):
        """Process file to detect new lines appended"""

        # Reset position if it looks like file has been truncated
        if file_path.stat().st_size < self.file_positions_map[str(file_path)]:
            self.file_positions_map[str(file_path)] = 0

        with open(file_path, encoding=ENCODING) as file:
            file.seek(self.file_positions_map[str(file_path)])
            new_data = file.read()
            if not new_data:
                return

            # Process all lines but the last one
            for line in new_data.splitlines(keepends=True):
                if not line.endswith("\n"):
                    continue
                self.line_process_func(
                    NewLineEvent(file_path=file_path, line_content=line.strip())
                )
                self.file_positions_map[str(file_path)] += len(
                    line.encode(encoding=ENCODING)
                )

    def on_any_event(self, event: FileSystemEvent):
        """Function called by watch dog when event occurs"""
        if event.is_directory or event.event_type not in [
            EVENT_TYPE_CREATED,
            EVENT_TYPE_MODIFIED,
            EVENT_TYPE_MOVED,
            EVENT_TYPE_DELETED,
        ]:
            return

        if event.event_type in [
            EVENT_TYPE_CREATED,
            EVENT_TYPE_MODIFIED,
        ]:
            if event.src_path not in self.file_positions_map:
                self.file_positions_map[event.src_path] = 0
            try:
                self.process_new_lines(Path(event.src_path))
            except FileNotFoundError:  # pragma: no cover
                pass

        elif self._is_moved_event(event):
            if event.src_path in self.file_positions_map:
                self.file_positions_map[event.dest_path] = self.file_positions_map[
                    event.src_path
                ]
                del self.file_positions_map[event.src_path]
            try:
                self.process_new_lines(Path(event.dest_path))
            except FileNotFoundError:  # pragma: no cover
                pass

        elif event.event_type == EVENT_TYPE_DELETED:
            # Cleanup to limit memory footprint + allow file name to be reused
            if event.src_path in self.file_positions_map:
                del self.file_positions_map[event.src_path]

        with open(self.state_file_path, "w") as fh:
            json.dump({"file_pointers": self.file_positions_map}, fh)


class LogWatcher:
    """Watch log files and call the handler function for every new line appended

    The handler function is called only once the line is completed (i.e. ending with a
    carriage return character).

    Moved, deleted and truncated files are supported.

    Nested files are watched as well if `recursive` is True.

    Some limitations:
    - files must not be truncated and recreated bigger than before within few
    milliseconds
    - watchdog issues applies (e.g. special combinations of host an container OSes or
    special mount types might provide issues)
    """

    def __init__(
        self,
        watched_folder: str,
        data_folder: str,
        handler: Callable[[NewLineEvent], None],
        *,
        recursive: bool = True,
    ) -> None:
        self.watched_folder = Path(watched_folder)
        self.event_handler = LogWatcherHandler(data_folder=data_folder, handler=handler)
        self.recursive = recursive
        self.observer = Observer()

    async def run_async(self):
        """Watch directory"""
        self.process_existing_files()

        self.observer.schedule(  # pyright: ignore[reportUnknownMemberType]
            self.event_handler, self.watched_folder, recursive=self.recursive
        )

        self.observer.start()

        while self.observer.is_alive():
            self.observer.join(1)
            # perform a very small sleep, just to let the coroutine pause
            await sleep(0.001)

        self.observer.join()

    def run_sync(self):
        """Watch directory"""
        self.process_existing_files()

        self.observer.schedule(  # pyright: ignore[reportUnknownMemberType]
            self.event_handler, self.watched_folder, recursive=self.recursive
        )

        self.observer.start()

        while self.observer.is_alive():
            self.observer.join(1)

        self.observer.join()

    def stop(self):
        """Stop watcher"""
        if self.observer.is_alive():
            self.observer.stop()

    def process_existing_files(self):
        """Process files that are already there at watcher startup"""
        for file in self.watched_folder.rglob("*"):
            if not file.is_file():
                continue
            # Let's consider that all existing files have been modified, so that we
            # process any line that might have appeared since our last execution
            event = FileSystemEvent(str(file))
            event.is_directory = False
            event.event_type = EVENT_TYPE_MODIFIED
            self.event_handler.on_any_event(event)
