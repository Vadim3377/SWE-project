from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv
import json


@dataclass
class Report:
    """
    Data container for a snapshot of simulation statistics.

    Holds calculated averages, maximums, and total counts for queues,
    delays, and exceptions at a specific point in time or at the end
    of a simulation run.
    """
    # Holding / Landing Stats
    max_holding_size: int = 0
    avg_holding_size: float = 0.0
    max_holding_time: float = 0.0
    avg_holding_time: float = 0.0

    # Takeoff Stats
    max_takeoff_queue_size: int = 0
    max_takeoff_wait: float = 0.0
    avg_takeoff_wait: float = 0.0

    # Exceptions
    diversions: int = 0
    cancellations: int = 0

    # Simulation Info
    total_time: int = 0


# CSV persistence for simulation statistics
# Stored alongside backend code by default (so both frontend and backend can agree on location).
DEFAULT_STATS_CSV_PATH = str((Path(__file__).resolve().parent / "simulation_statistics.csv").resolve())

# Stable column order for the CSV file. Unknown keys go into `extra_json`.
CSV_COLUMNS: List[str] = [
    "saved_at_utc",
    "sim_time_min",
    "maxHoldingQueue",
    "avgHoldingQueue",
    "maxArrivalDelay",
    "avgHoldingTime",
    "maxTakeoffQueue",
    "avgTakeoffQueue",
    "maxTakeoffWait",
    "avgTakeoffWait",
    "avgArrivalDelay",
    "diversions",
    "cancellations",
    "extra_json",
]


def _ensure_parent_dir(csv_path: str) -> None:
    """
    Ensure that the parent directory for the given file path exists.

    Parameters
    ----------
    csv_path : str
        The full file path where the directory structure needs to be verified or created.
    """
    Path(csv_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def append_report_csv(report: Dict[str, Any], sim_time_min: int, csv_path: str = DEFAULT_STATS_CSV_PATH) -> str:
    """
    Append a single simulation report snapshot to a persistent CSV file.

    This function ensures the report data is saved using a stable column schema.
    Any unknown or extra fields present in the report dictionary are serialized
    and stored in an `extra_json` column to prevent data loss without breaking
    the CSV structure.

    Parameters
    ----------
    report : Dict[str, Any]
        The dictionary containing the statistical metrics to save.
    sim_time_min : int
        The simulation time (in minutes) at which this report was generated.
    csv_path : str, optional
        The file path to the destination CSV. Defaults to DEFAULT_STATS_CSV_PATH.

    Returns
    -------
    str
        The resolved absolute path to the written CSV file.
    """
    _ensure_parent_dir(csv_path)
    p = Path(csv_path).expanduser().resolve()
    file_exists = p.exists()

    # Fill known columns
    row: Dict[str, Any] = {c: "" for c in CSV_COLUMNS}
    row["saved_at_utc"] = datetime.now(timezone.utc).isoformat()
    row["sim_time_min"] = int(sim_time_min)

    extras: Dict[str, Any] = {}
    for k, v in (report or {}).items():
        if k in row:
            row[k] = v
        else:
            extras[k] = v

    row["extra_json"] = json.dumps(extras, ensure_ascii=False) if extras else ""

    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            w.writeheader()
        w.writerow(row)

    return str(p)


def read_reports_csv(csv_path: str = DEFAULT_STATS_CSV_PATH) -> List[Dict[str, Any]]:
    """
    Read and parse all saved simulation reports from a CSV file.

    Reads the historical data, attempting to coerce known numeric fields back
    into their correct types (ints or floats). Data stored in the `extra_json`
    column is unpacked and merged back into the main dictionary.

    Parameters
    ----------
    csv_path : str, optional
        The file path to the CSV to read. Defaults to DEFAULT_STATS_CSV_PATH.

    Returns
    -------
    List[Dict[str, Any]]
        A list of parsed report dictionaries, ordered from oldest to newest.
    """
    p = Path(csv_path).expanduser().resolve()
    if not p.exists():
        return []

    with p.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = []
        for raw in r:
            row: Dict[str, Any] = dict(raw)
            # Coerce some known fields
            try:
                row["sim_time_min"] = int(float(row.get("sim_time_min") or 0))
            except Exception:
                row["sim_time_min"] = 0

            for k in ["maxHoldingQueue", "avgHoldingQueue", "maxArrivalDelay", "avgHoldingTime",
                      "maxTakeoffQueue", "avgTakeoffQueue", "maxTakeoffWait", "avgTakeoffWait",
                      "avgArrivalDelay", "diversions", "cancellations"]:
                if k in row and row[k] != "":
                    try:
                        row[k] = float(row[k])
                    except Exception:
                        pass

            # Merge extras (non-destructively)
            extra = row.get("extra_json") or ""
            if extra:
                try:
                    extra_obj = json.loads(extra)
                    if isinstance(extra_obj, dict):
                        for ek, ev in extra_obj.items():
                            row.setdefault(ek, ev)
                except Exception:
                    pass
            rows.append(row)

    return rows


def read_last_report(csv_path: str = DEFAULT_STATS_CSV_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieve only the most recent report snapshot from the CSV log.

    Parameters
    ----------
    csv_path : str, optional
        The file path to the CSV to read. Defaults to DEFAULT_STATS_CSV_PATH.

    Returns
    -------
    Optional[Dict[str, Any]]
        The most recent report dictionary, or None if the file is empty or does not exist.
    """
    rows = read_reports_csv(csv_path)
    return rows[-1] if rows else None