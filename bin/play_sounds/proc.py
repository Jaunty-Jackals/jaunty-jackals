from __future__ import annotations

import atexit
import signal
from functools import partial
from multiprocessing import Process
from pathlib import Path
from platform import platform
from sys import exit
from typing import Any, Callable, Optional, Set, Union
from weakref import finalize as finalizer

PLATFORM: str = platform().lower()
_PROCS: Procs = set()

_SIGINT: Callable = signal.getsignal(signal.SIGINT)


Procs = Set[Process]


def play_process(
    file: Union[Path, str],
    target: Callable,
    *args,
    finalize: bool = True,
    running_procs: Optional[Procs] = _PROCS,
    **kwargs,
) -> Process:
    """Play process"""
    proc = Process(target=target, args=(file, *args), kwargs=kwargs, daemon=True)

    if finalize:
        finalizer(proc, kill_process, proc=proc, running_procs=running_procs)

    if running_procs is not None:
        running_procs.add(proc)

    proc.start()

    return proc


def kill_process(proc: Process, running_procs: Optional[Procs] = _PROCS):
    """Kill process"""
    proc.kill()
    proc.join()

    if running_procs and proc in running_procs:
        running_procs.remove(proc)


def kill_child_procs(
    signum: Optional[int] = None, frame: Optional[Any] = None, perform_exit: bool = True
):
    """Kill child processes"""
    if _PROCS:
        for proc in _PROCS.copy():
            try:
                kill_process(proc)

            except Exception as excp:
                print(f"{excp}")
                pass
            else:
                pass

    if perform_exit:
        exit()


kill_procs_no_exit: Callable = partial(kill_child_procs, perform_exit=False)


def handle_sigint(
    signum: Optional[int] = None,
    frame: Optional[Any] = None,
):
    """Handle SIGINTs"""
    kill_procs_no_exit()
    _SIGINT(signum, frame)


def register_handlers():
    """Handle registers"""
    # handle graceful shutdown
    atexit.register(kill_procs_no_exit)

    # allow users to catch KeyboardInterrupt without exiting
    signal.signal(signal.SIGINT, handle_sigint)

    # handle ungraceful shutdown
    signal.signal(signal.SIGTERM, kill_child_procs)
    signal.signal(signal.SIGSEGV, kill_child_procs)
    signal.signal(signal.SIGABRT, kill_child_procs)
    signal.signal(signal.SIGILL, kill_child_procs)

    if "windows" not in PLATFORM:
        signal.signal(signal.SIGPIPE, kill_child_procs)
        signal.signal(signal.SIGQUIT, kill_child_procs)
        signal.signal(signal.SIGBUS, kill_child_procs)
        signal.signal(signal.SIGHUP, kill_child_procs)


register_handlers()
