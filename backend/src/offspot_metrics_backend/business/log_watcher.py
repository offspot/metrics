import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeGuard

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


@dataclass
class NewLineEvent:
    file_path: str
    line_content: str


class LogWatcherHandler(FileSystemEventHandler):
    """Handler of watchdog events"""

    def __init__(self, handler: Callable[[NewLineEvent], None]):
        self.file_pointers: dict[str, int] = {}
        self.line_process_func = handler

    def _is_moved_event(
        self, event: FileSystemEvent
    ) -> TypeGuard[FileSystemMovedEvent]:
        """TypeGuard to help type checker detect moved event class"""
        return event.event_type == EVENT_TYPE_MOVED

    def process_new_lines(self, file_path: str):
        """Process file to detect new lines appended"""

        # Reset position if it looks like file has been truncated
        if os.path.getsize(file_path) < self.file_pointers[file_path]:
            self.file_pointers[file_path] = 0

        with open(file_path) as file:
            file.seek(self.file_pointers[file_path])
            new_data = file.read()
            if not new_data:
                return

            # Process all lines but the last one
            for line in new_data.splitlines(keepends=True):
                if not line.endswith("\n"):
                    continue
                self.line_process_func(
                    NewLineEvent(file_path=file_path, line_content=line[:-1])
                )
                self.file_pointers[file_path] += len(line.encode())

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
            if event.src_path not in self.file_pointers:
                self.file_pointers[event.src_path] = 0
            try:
                self.process_new_lines(event.src_path)
            except FileNotFoundError:  # pragma: no cover
                pass

        elif self._is_moved_event(event):
            if event.src_path in self.file_pointers:
                self.file_pointers[event.dest_path] = self.file_pointers[event.src_path]
                del self.file_pointers[event.src_path]
            try:
                self.process_new_lines(event.dest_path)
            except FileNotFoundError:  # pragma: no cover
                pass

        elif event.event_type == EVENT_TYPE_DELETED:
            # Cleanup to limit memory footprint + allow file name to be reused
            if event.src_path in self.file_pointers:
                del self.file_pointers[event.src_path]

        else:
            # we should never get there except if something bad happens when modiying
            # code above
            raise AttributeError  # pragma: no cover


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
        path: str,
        handler: Callable[[NewLineEvent], None],
        *,
        recursive: bool = True,
    ) -> None:
        self.path = Path(path)
        self.event_handler = LogWatcherHandler(handler=handler)
        self.recursive = recursive

    def start(self):
        """Start watching directory"""
        self.process_existing_files()

        self.observer = Observer()
        self.observer.schedule(  # pyright: ignore[reportUnknownMemberType]
            self.event_handler, self.path, recursive=self.recursive
        )

        self.observer.start()

        while self.observer.is_alive():
            self.observer.join(1)

        self.observer.join()

    def stop(self):
        """Stop watcher"""
        self.observer.stop()

    def process_existing_files(self):
        """Process files that are already there at watcher startup"""
        for root, _, files in os.walk(self.path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # Let consider that all existing files have been modified, so that we
                # process any line that might have apparead since our last execution
                event = FileSystemEvent(file_path)
                event.is_directory = False
                event.event_type = EVENT_TYPE_MODIFIED
                self.event_handler.on_any_event(event)
