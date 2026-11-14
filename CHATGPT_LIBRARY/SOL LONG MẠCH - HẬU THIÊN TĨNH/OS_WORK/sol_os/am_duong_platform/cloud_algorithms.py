"""ÂM–DƯƠNG Cloud Computing 9-minute LAB: local, offline, bounded.

Educational simulation on three SQLite files, NOT real cloud nodes/consensus,
network replication, an SLA, or Coursera course completion.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sqlite3


class QuorumUnavailable(RuntimeError):
    pass


def map_reduce_count(items: list[str], workers: int = 3) -> dict[str, int]:
    """Partition/map/reduce word counts: O(N) items, O(U) output memory."""
    if not isinstance(items, list) or len(items) > 10000:
        raise ValueError("ITEMS_BOUND")
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError("WORKERS_BOUND")
    if any(not isinstance(s, str) or len(s) > 256 for s in items):
        raise ValueError("ITEM_INVALID")
    shards = [items[i::workers] for i in range(workers)]
    mapped = [Counter(part) for part in shards]
    result = Counter()
    for local in mapped:
        result.update(local)
    return dict(sorted(result.items()))


def rendezvous(key: str, nodes: tuple[str, ...]) -> list[str]:
    """Deterministic highest-random-weight hashing for shard placement."""
    if not isinstance(key, str) or not 1 <= len(key) <= 256:
        raise ValueError("KEY_BOUND")
    if not nodes or len(set(nodes)) != len(nodes):
        raise ValueError("INVALID_NODE_SET")
    return sorted(nodes, key=lambda n: (
        -int.from_bytes(sha256((key + "\0" + n).encode()).digest(), "big"), n
    ))


class ReplicaLab:
    """Three local SQLite files, quorum 2/3, offline failure, read repair.

    Sequential single-writer *simulation*: no concurrent-writer safety,
    leases, network partitions, Raft/Paxos, or distributed consensus.
    """
    NODES = ("node_a", "node_b", "node_c")

    def __init__(self, scratch_directory: Path):
        self.root = Path(scratch_directory).resolve()
        if not self.root.is_dir():
            raise ValueError("EXISTING_SCRATCH_DIR_REQUIRED")
        self.live = set(self.NODES)
        self.revision = 0
        for node in self.NODES:
            with self._connect(node) as db:
                db.execute("""CREATE TABLE IF NOT EXISTS kv(
                    key TEXT PRIMARY KEY, revision INTEGER NOT NULL,
                    content TEXT NOT NULL, digest TEXT NOT NULL)""")
                row = db.execute("SELECT COALESCE(MAX(revision),0) FROM kv").fetchone()
                self.revision = max(self.revision, row[0])

    def _connect(self, node):
        if node not in self.NODES:
            raise ValueError("UNKNOWN_NODE")
        return sqlite3.connect(self.root / (node + ".sqlite3"), timeout=5)

    def set_online(self, node: str, online: bool) -> None:
        if node not in self.NODES or type(online) is not bool:
            raise ValueError("NODE_STATUS_INVALID")
        (self.live.add if online else self.live.discard)(node)

    def _quorum(self):
        selected = [node for node in self.NODES if node in self.live]
        if len(selected) < 2:
            raise QuorumUnavailable("2_OF_3_REQUIRED")
        return selected

    def _valid_rows(self, key: str, nodes: list[str]):
        good = []
        for node in nodes:
            with self._connect(node) as db:
                row = db.execute("SELECT revision,content,digest FROM kv WHERE key=?", (key,)).fetchone()
            if row:
                rev, content, digest = row
                if sha256(content.encode()).hexdigest() == digest:
                    good.append((rev, content, node))
        return good

    @staticmethod
    def _key(key):
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ValueError("KEY_INVALID")
        return key

    def put(self, key: str, content: str) -> dict:
        key = self._key(key)
        if not isinstance(content, str) or len(content) > 10000:
            raise ValueError("CONTENT_INVALID")
        nodes = self._quorum()
        # Single-writer expected. The revision is local coordinator metadata.
        rev = max([self.revision] + [r[0] for r in self._valid_rows(key, nodes)]) + 1
        digest = sha256(content.encode()).hexdigest()
        acknowledged = []
        for node in nodes:
            with self._connect(node) as db:
                db.execute("""INSERT INTO kv VALUES(?,?,?,?) ON CONFLICT(key)
                    DO UPDATE SET revision=excluded.revision,content=excluded.content,
                    digest=excluded.digest WHERE excluded.revision >= kv.revision""",
                    (key, rev, content, digest))
            acknowledged.append(node)
        self.revision = rev
        return {"status": "QUORUM_ACK", "acks": len(acknowledged), "revision": rev,
                "digest": digest, "simulation": True}

    def get(self, key: str) -> dict:
        key = self._key(key)
        nodes = self._quorum()
        rows = self._valid_rows(key, nodes)
        if not rows:
            return {"found": False, "quorum": len(nodes), "simulation": True}
        # Latest valid row; may be insufficient for consensus under split-brain.
        rev, content, holder = max(rows, key=lambda r: (r[0], r[2]))
        return {"found": True, "content": content, "revision": rev,
                "digest": sha256(content.encode()).hexdigest(),
                "quorum": len(nodes), "simulation": True}

    def repair(self, key: str) -> dict:
        """Read repair to currently available nodes only, never offline nodes."""
        state = self.get(key)
        if not state["found"]:
            return {"repaired": 0, "reason": "NO_VALID_RECORD"}
        count = 0
        for node in self._quorum():
            rows = self._valid_rows(key, [node])
            if not rows or rows[0][0] < state["revision"]:
                with self._connect(node) as db:
                    db.execute("""INSERT INTO kv VALUES(?,?,?,?)
                        ON CONFLICT(key) DO UPDATE SET revision=excluded.revision,
                        content=excluded.content,digest=excluded.digest
                        WHERE excluded.revision >= kv.revision""",
                        (key, state["revision"], state["content"], state["digest"]))
                count += 1
        return {"repaired": count, "revision": state["revision"], "simulation": True}
