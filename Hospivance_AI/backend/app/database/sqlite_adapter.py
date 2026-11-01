"""Pure-Python SQLite adapter for zero-dependency execution when SQLAlchemy is absent."""

import sqlite3
import os
from typing import List, Any, Optional

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "hospivance.db"))


class RowObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name)

    def __repr__(self):
        return f"<RowObject {self.__dict__}>"


class QueryBuilder:
    def __init__(self, conn: sqlite3.Connection, table_name: str, model_cls=None, select_expr="*"):
        self.conn = conn
        self.table_name = table_name
        self.model_cls = model_cls or RowObject
        self.select_expr = select_expr
        self.filters = []
        self.params = []
        self.order_by_clause = None
        self.limit_val = None

    def filter(self, *conditions):
        for cond in conditions:
            if isinstance(cond, tuple):
                self.filters.append(cond[0])
                if len(cond) > 1 and cond[1] is not None:
                    if isinstance(cond[1], (list, tuple)):
                        self.params.extend(cond[1])
                    else:
                        self.params.append(cond[1])
            elif isinstance(cond, str):
                self.filters.append(cond)
        return self

    def distinct(self):
        if not self.select_expr.startswith("DISTINCT"):
            self.select_expr = f"DISTINCT {self.select_expr}"
        return self

    def order_by(self, clause):
        self.order_by_clause = str(clause)
        return self

    def limit(self, val: int):
        self.limit_val = val
        return self

    def _build_sql(self) -> str:
        sql = f"SELECT {self.select_expr} FROM {self.table_name}"
        if self.filters:
            sql += " WHERE " + " AND ".join(self.filters)
        if self.order_by_clause:
            sql += f" ORDER BY {self.order_by_clause}"
        if self.limit_val is not None:
            sql += f" LIMIT {self.limit_val}"
        return sql

    def all(self) -> List[Any]:
        cur = self.conn.cursor()
        cur.execute(self._build_sql(), self.params)
        cols = [c[0] for c in cur.description] if cur.description else []
        rows = cur.fetchall()
        if self.select_expr != "*" and "," not in self.select_expr and "(" not in self.select_expr:
            # Single column distinct query, return tuples for compatibility like (row[0],)
            return [(r[0],) for r in rows]
        res = []
        for r in rows:
            obj = RowObject(**dict(zip(cols, r)))
            res.append(obj)
        return res

    def first(self) -> Optional[Any]:
        items = self.limit(1).all()
        return items[0] if items else None

    def count(self) -> int:
        sql = f"SELECT COUNT(*) FROM {self.table_name}"
        if self.filters:
            sql += " WHERE " + " AND ".join(self.filters)
        cur = self.conn.cursor()
        cur.execute(sql, self.params)
        return cur.fetchone()[0]

    def scalar(self) -> Any:
        cur = self.conn.cursor()
        cur.execute(self._build_sql(), self.params)
        r = cur.fetchone()
        return r[0] if r else None


class SQLiteSession:
    def __init__(self, db_path: str = DB_FILE):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def query(self, *entities):
        if len(entities) > 1:
            select_expr = ", ".join([getattr(e, "col_name", str(e)) for e in entities])
            table = getattr(entities[0], "table_name", "admissions_daily")
            return QueryBuilder(self.conn, table, select_expr=select_expr)

        entity = entities[0]
        if hasattr(entity, "__tablename__"):
            return QueryBuilder(self.conn, entity.__tablename__, entity)
        elif isinstance(entity, str):
            return QueryBuilder(self.conn, entity)
        elif hasattr(entity, "table_name"):
            select_expr = getattr(entity, "expr", getattr(entity, "col_name", "*"))
            table = entity.table_name
            return QueryBuilder(self.conn, table, select_expr=select_expr)
        else:
            return QueryBuilder(self.conn, str(entity))

    def add(self, obj):
        table = getattr(obj, "__tablename__", type(obj).__name__.lower())
        attrs = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        cols = list(attrs.keys())
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join(cols)
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        cur = self.conn.cursor()
        cur.execute(sql, [attrs[c] for c in cols])
        obj.id = cur.lastrowid

    def add_all(self, objects):
        for obj in objects:
            self.add(obj)

    def bulk_save_objects(self, objects):
        if not objects:
            return
        table = getattr(objects[0], "__tablename__", type(objects[0]).__name__.lower())
        attrs_list = [{k: v for k, v in o.__dict__.items() if not k.startswith("_")} for o in objects]
        cols = list(attrs_list[0].keys())
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join(cols)
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        cur = self.conn.cursor()
        cur.executemany(sql, [[a[c] for c in cols] for a in attrs_list])

    def commit(self):
        self.conn.commit()

    def refresh(self, obj):
        pass

    def close(self):
        self.conn.close()
