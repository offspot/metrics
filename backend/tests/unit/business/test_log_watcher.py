import json
import shutil
import time
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from typing import Any

import pytest
from watchdog.events import FileDeletedEvent, FileMovedEvent

from offspot_metrics_backend.business.log_watcher import (
    LogWatcher,
    LogWatcherHandler,
    NewLineEvent,
)

# Pause to perform in the middle of the tests to let watchdog process previous events
PAUSE_IN_MS = 0.1


class LogWatcherTester:
    """Helper tester class for tests"""

    def __init__(self, tmp_path: Path) -> None:
        self.new_lines: list[str] = []
        self.watched_path = tmp_path.joinpath("watched")
        self.watched_path.mkdir()
        self.data_path = tmp_path.joinpath("data")
        self.data_path.mkdir()
        self.fail_on_demand = False
        self.watcher = None

    def new_line_handler(self, event: NewLineEvent):
        if self.fail_on_demand and "fail" in event.line_content.lower():
            raise ValueError("Something bad happens")
        self.new_lines.append(event.line_content)

    async def run_watcher(self, watcher: LogWatcher):
        await watcher.run_async()

    def run(self, func: Callable[[Path], None], *, recursive: bool = True):
        self.new_lines = []

        self.watcher = LogWatcher(
            watched_folder=str(self.watched_path),
            data_folder=str(self.data_path),
            handler=self.new_line_handler,
            recursive=recursive,
        )

        thread = Thread(target=self.watcher.run_sync)
        thread.start()

        time.sleep(PAUSE_IN_MS)  # Provide some slack time to let inotify setup complete
        func(self.watched_path)  # Perform test modifications
        time.sleep(PAUSE_IN_MS)  # Provide some slack time for watcher to complete
        self.watcher.stop()


@pytest.fixture
def log_watcher_tester(tmp_path: Path) -> LogWatcherTester:
    """A help class to create log files and watch them"""
    return LogWatcherTester(tmp_path=tmp_path)


@pytest.fixture
def noop() -> Callable[[NewLineEvent], None]:
    """A noop log event handler"""

    def _noop(_: NewLineEvent):
        pass

    return _noop


@pytest.fixture
def persisted_data() -> dict[str, Any]:
    """A sample dataset that could have been persisted to disk"""
    return {
        "file_pointers": {
            "file1.log": 123,
            "file2.log": 456,
        }
    }


def test_log_watcher_noop(log_watcher_tester: LogWatcherTester):
    def noop(_: Path):
        pass

    log_watcher_tester.run(noop)
    assert len(log_watcher_tester.new_lines) == 0


def test_log_watcher_simple(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1.1\n")
            fh.write("L1.2\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L1.2"]


def test_log_watcher_simple_with_pending_line(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1.1\n")
            fh.write("L1.2\n")
            fh.write("L1.3")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L1.2"]


def test_log_watcher_simple_with_flush(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        fh = open(watched_path.joinpath("file1.txt"), mode="w")
        fh.write("L1.1\n")
        fh.write("L1.2\n")
        fh.flush()
        fh.write("L1.3")
        fh.close()

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L1.2"]


def test_log_watcher_simple_with_pause(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1.1\n")
            fh.write("L1.2\n")
            fh.write("L1")
            fh.flush()
            time.sleep(PAUSE_IN_MS)
            fh.write(".3\n")
            fh.write("L1.4")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L1.2", "L1.3"]


def test_log_watcher_simple_with_failures(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1.1\n")
            fh.write("L1.2\n")
            fh.write("Lfails\n")
            fh.write("L1.3\n")

    log_watcher_tester.fail_on_demand = True
    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L1.2", "L1.3"]


def test_log_watcher_many_append(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1.1\n")
            fh.flush()
            fh.write("L1.2\n")
            fh.flush()
            fh.write("L1.3")
        with open(watched_path.joinpath("file2.txt"), mode="w") as fh:
            fh.write("L2.1\n")
            fh.write("L2.2\n")
            fh.write("L2.")
            fh.write("3\n")
            fh.write("L2.4\n")
        with open(watched_path.joinpath("file3.txt"), mode="w") as fh:
            fh.write("L3.1\n")
            fh.write("L3.2\n")
            fh.write("L3.3\n")
            fh.write("L3.")
            fh.write("4\n")

        fh4 = open(watched_path.joinpath("file4.txt"), mode="w")
        fh4.write("L4.1\n")
        fh4.write("L4.2\n")
        fh4.flush()

        fh5 = open(watched_path.joinpath("file5.txt"), mode="w")
        fh5.write("L5.1\n")
        fh5.write("L5.2\n")
        fh5.write("L5.3\n")
        fh5.close()

        time.sleep(PAUSE_IN_MS)

        fh4.write("L4.3\n")
        fh4.write("L4.")
        fh4.write("4\n")
        fh4.close()

        fh5 = open(watched_path.joinpath("file5.txt"), mode="a")
        fh5.write("L5")
        fh5.write(".4\n")
        fh5.write("L5.")
        fh5.write("5\n")
        fh5.close()

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == (
        [
            "L1.1",
            "L1.2",
            "L2.1",
            "L2.2",
            "L2.3",
            "L2.4",
            "L3.1",
            "L3.2",
            "L3.3",
            "L3.4",
            "L4.1",
            "L4.2",
            "L4.3",
            "L4.4",
            "L5.1",
            "L5.2",
            "L5.3",
            "L5.4",
            "L5.5",
        ]
    )


def test_log_watcher_file_moved(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1\nL2\nL3")
            fh.flush()
            time.sleep(PAUSE_IN_MS)
            fh.write("\nL4")
        shutil.move(
            watched_path.joinpath("file1.txt"), watched_path.joinpath("file2.txt")
        )
        time.sleep(PAUSE_IN_MS)
        with open(watched_path.joinpath("file2.txt"), mode="a") as fh:
            fh.write("\nL5\nL6")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1", "L2", "L3", "L4", "L5"]


def test_log_watcher_file_deleted(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1\nL2\nL3")
        time.sleep(PAUSE_IN_MS)
        watched_path.joinpath("file1.txt").unlink()
        time.sleep(PAUSE_IN_MS)
        with open(watched_path.joinpath("file1.txt"), mode="a") as fh:
            fh.write("L4\nL5\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1", "L2", "L4", "L5"]


def test_log_watcher_file_existing_files_untouched(
    log_watcher_tester: LogWatcherTester,
):
    with open(log_watcher_tester.watched_path.joinpath("file1.txt"), mode="w") as fh:
        fh.write("L1\nL2\nL3")
    with open(log_watcher_tester.watched_path.joinpath("file3.txt"), mode="w") as fh:
        fh.write("M1\nM2\n")
    log_watcher_tester.watched_path.joinpath("subdir").mkdir()

    def noop(_: Path):
        pass

    log_watcher_tester.run(noop)

    assert sorted(log_watcher_tester.new_lines) == ["L1", "L2", "M1", "M2"]


def test_log_watcher_file_existing_files_with_failures(
    log_watcher_tester: LogWatcherTester,
):
    with open(log_watcher_tester.watched_path.joinpath("file1.txt"), mode="w") as fh:
        fh.write("L1\nLfails\nL3")
    with open(log_watcher_tester.watched_path.joinpath("file3.txt"), mode="w") as fh:
        fh.write("M1\nM2\n")
    log_watcher_tester.watched_path.joinpath("subdir").mkdir()

    def noop(_: Path):
        pass

    log_watcher_tester.fail_on_demand = True
    log_watcher_tester.run(noop)

    assert sorted(log_watcher_tester.new_lines) == ["L1", "M1", "M2"]


def test_log_watcher_file_existing_files_modified(
    log_watcher_tester: LogWatcherTester,
):
    with open(log_watcher_tester.watched_path.joinpath("file1.txt"), mode="w") as fh:
        fh.write("L1\nL2\nL3")
    with open(log_watcher_tester.watched_path.joinpath("file3.txt"), mode="w") as fh:
        fh.write("M1\nM2\n")

    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="a") as fh:
            fh.write("\nL4\n")
        with open(watched_path.joinpath("file3.txt"), mode="a") as fh:
            fh.write("M3\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == (
        ["L1", "L2", "L3", "L4", "M1", "M2", "M3"]
    )


def test_log_watcher_file_truncated_file(
    log_watcher_tester: LogWatcherTester,
):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1\nL2\nL3\n")
        time.sleep(PAUSE_IN_MS)
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("M1\nM2\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1", "L2", "L3", "M1", "M2"]


def test_log_watcher_file_nested_file_and_recursive(
    log_watcher_tester: LogWatcherTester,
):
    def modify_files(watched_path: Path):
        watched_path.joinpath("subdir").mkdir()
        with open(watched_path.joinpath("subdir/file1.txt"), mode="w") as fh:
            fh.write("L1\nL2\nL3\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1", "L2", "L3"]


def test_log_watcher_file_nested_file_and_norecursive(
    log_watcher_tester: LogWatcherTester,
):
    def modify_files(watched_path: Path):
        watched_path.joinpath("subdir").mkdir()
        with open(watched_path.joinpath("subdir/file1.txt"), mode="w") as fh:
            fh.write("L1\nL2\nL3\n")

    log_watcher_tester.run(modify_files, recursive=False)

    assert sorted(log_watcher_tester.new_lines) == []


def test_log_watcher_no_exit(noop: Callable[[NewLineEvent], None]):
    # These are "dummy" tests just to ensure 100% coverage of the base class:
    # - we should handle delete events even if the path has never been seen in the past
    # - we should handle move events even if the path has never been seen in the past
    # This is not supposed to happen and hence impossible to produce with the current
    # system but important to cover should something weird happen in the wild, e.g. the
    # system missing some 'created' or 'modified' events

    tempdir = TemporaryDirectory()
    lwh = LogWatcherHandler(data_folder=tempdir.name, handler=noop)
    lwh.on_any_event(FileDeletedEvent("some_path"))
    lwh.on_any_event(FileMovedEvent("some_path", "other_path"))
    tempdir.cleanup()


def test_log_watcher_big_special_chars(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1😁1\n")
        time.sleep(PAUSE_IN_MS)
        with open(watched_path.joinpath("file1.txt"), mode="a") as fh:
            fh.write("L1😤2\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1😁1", "L1😤2"]


def test_log_watcher_missing_data_dir(
    tmp_path: Path, noop: Callable[[NewLineEvent], None]
):
    with pytest.raises(ValueError):
        LogWatcherHandler(
            data_folder=str(tmp_path.joinpath("idontexist")), handler=noop
        )


def test_log_watcher_existing_data_file(
    tmp_path: Path, noop: Callable[[NewLineEvent], None], persisted_data: dict[str, Any]
):
    with open(tmp_path.joinpath("log_watcher_state.json"), "w") as fh:
        json.dump(persisted_data, fh)
    lwh = LogWatcherHandler(data_folder=str(tmp_path), handler=noop)
    assert lwh.file_positions_map == persisted_data["file_pointers"]


def test_log_watcher_deleted_file(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        created_file = watched_path.joinpath("file1.txt")
        with open(created_file, mode="w") as fh:
            fh.write("L1.1\n")

        time.sleep(PAUSE_IN_MS)

        created_file.unlink()

        time.sleep(PAUSE_IN_MS)

        with open(created_file, mode="w") as fh:
            fh.write("L2.1\n")

        time.sleep(PAUSE_IN_MS)

        created_file.unlink()

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L2.1"]


def test_log_watcher_file_disappeared(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        created_file = watched_path.joinpath("file1.txt")

        with open(created_file, mode="w") as fh:
            fh.write("L1.1\n")

        time.sleep(PAUSE_IN_MS)

        # we will try to create and move the file so fast that it won't be possible
        # for the watcher to read it (but it will still be notified by watchdog)
        # we will do it 5 times to increase chances that file disappear before read
        moved_file = watched_path.joinpath("file2.txt")
        for _ in range(5):
            open(created_file, mode="w").close()
            created_file.rename(moved_file)
            moved_file.unlink()

        time.sleep(PAUSE_IN_MS)

        with open(created_file, mode="w") as fh:
            fh.write("L2.1\n")

    log_watcher_tester.run(modify_files)

    assert sorted(log_watcher_tester.new_lines) == ["L1.1", "L2.1"]


def test_log_watcher_stop_twice(log_watcher_tester: LogWatcherTester):
    def modify_files(watched_path: Path):
        with open(watched_path.joinpath("file1.txt"), mode="w") as fh:
            fh.write("L1.1\n")

    log_watcher_tester.run(modify_files)

    time.sleep(PAUSE_IN_MS)

    assert log_watcher_tester.watcher
    log_watcher_tester.watcher.stop()

    assert sorted(log_watcher_tester.new_lines) == ["L1.1"]
