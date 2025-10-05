from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, Iterable, List, Tuple

from openai import OpenAI

from ..core.config import settings


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _hash_key(model: str, text: str) -> str:
    h = hashlib.sha256()
    h.update(model.encode("utf-8"))
    h.update(b"|")
    h.update(text.encode("utf-8"))
    return h.hexdigest()


class EmbeddingCache:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or settings.embedding_cache_path
        _ensure_dir(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as con:
            con.execute(
                """
                create table if not exists embeddings (
                  key text primary key,
                  model text not null,
                  text_hash text not null,
                  vector_json text not null,
                  created_at timestamp default current_timestamp
                )
                """
            )

    @contextmanager
    def _conn(self):
        con = sqlite3.connect(self.db_path)
        try:
            yield con
        finally:
            con.close()

    def get_many(self, keys: List[str]) -> Dict[str, List[float]]:
        if not keys:
            return {}
        placeholders = ",".join(["?"] * len(keys))
        with self._conn() as con:
            cur = con.execute(
                f"select key, vector_json from embeddings where key in ({placeholders})",
                keys,
            )
            rows = cur.fetchall()
        out: Dict[str, List[float]] = {}
        for key, vector_json in rows:
            out[key] = json.loads(vector_json)
        return out

    def set_many(self, items: Dict[str, List[float]]) -> None:
        if not items:
            return
        with self._conn() as con:
            con.executemany(
                "insert or replace into embeddings (key, model, text_hash, vector_json) values (?,?,?,?)",
                [
                    (
                        key,
                        key.split(":", 1)[0],
                        key.split(":", 1)[1],
                        json.dumps(vec),
                    )
                    for key, vec in items.items()
                ],
            )
            con.commit()


def embed_with_cache(
    texts: List[str],
    *,
    client: OpenAI,
    model: str,
    batch_size: int = 100,
    cache: EmbeddingCache | None = None,
) -> List[List[float]]:
    if not texts:
        return []

    cache = cache or EmbeddingCache()

    # Build cache keys
    pairs: List[Tuple[str, str]] = []  # (key, text)
    for text in texts:
        text_hash = _hash_key(model, text)
        key = f"{model}:{text_hash}"
        pairs.append((key, text))

    keys = [k for k, _ in pairs]
    key_to_text = {k: t for k, t in pairs}

    cached = cache.get_many(keys)

    missing_keys = [k for k in keys if k not in cached]
    missing_texts = [key_to_text[k] for k in missing_keys]

    new_vectors: Dict[str, List[float]] = {}
    for start in range(0, len(missing_texts), batch_size):
        batch = missing_texts[start : start + batch_size]
        if not batch:
            continue
        resp = client.embeddings.create(model=model, input=batch)
        vecs = [item.embedding for item in resp.data]
        for key, vec in zip(missing_keys[start : start + batch_size], vecs):
            new_vectors[key] = vec

    if new_vectors:
        cache.set_many(new_vectors)

    # Assemble in the original order
    final_vectors: List[List[float]] = []
    for key, _ in pairs:
        vec = cached.get(key) or new_vectors.get(key)
        assert vec is not None
        final_vectors.append(vec)
    return final_vectors
