import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class EtlRuntime:
    trigger: threading.Event = field(default_factory=threading.Event)
    iteration: int = 0
    last_run_started_at: Optional[datetime] = None
    last_run_finished_at: Optional[datetime] = None
    last_tick_duration_ms: Optional[float] = None
