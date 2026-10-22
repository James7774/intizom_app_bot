"""Asynchronous database module using asyncpg for Neon PostgreSQL."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncpg
from config import DATABASE_URL, get_current_timestamp


class Database:
    def __init__(self, dsn: str = DATABASE_URL):
        # Clean URL if query parameter like channel_binding is attached
        self.dsn = dsn.split("&channel_binding=")[0]
        self.pool: Optional[asyncpg.Pool] = None

    async def init_db(self) -> None:
        """Initializes connection pool and creates tables/indexes in Neon Postgres."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=1,
                max_size=10,
                max_inactive_connection_lifetime=60.0,
                ssl="require",
            )

        async with self.pool.acquire() as conn:
            # 1. users table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 2. tasks table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    task_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);"
            )

            # 3. daily_logs table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_logs (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    task_id INTEGER NOT NULL,
                    date VARCHAR(10) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    UNIQUE(user_id, task_id, date)
                );
                """
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_daily_logs_lookup ON daily_logs(user_id, date);"
            )

    async def close(self) -> None:
        """Closes connection pool cleanly."""
        if self.pool:
            await self.pool.close()

    async def upsert_user(self, user_id: int, full_name: str) -> None:
        """Insert or update user information in Postgres."""
        now = get_current_timestamp()
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, full_name, created_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET full_name = EXCLUDED.full_name;
                """,
                user_id,
                full_name,
                now,
            )

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user record by ID."""
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, full_name, created_at FROM users WHERE user_id = $1;",
                user_id,
            )
            return dict(row) if row else None

    async def set_user_tasks(self, user_id: int, task_names: List[str]) -> int:
        """
        Overwrite existing tasks for a user with a new list of tasks in a single transaction.
        """
        now = get_current_timestamp()
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            # Delete previous tasks
            await conn.execute("DELETE FROM tasks WHERE user_id = $1;", user_id)

            # Insert new tasks
            task_records = [(user_id, name, now) for name in task_names]
            await conn.executemany(
                "INSERT INTO tasks (user_id, task_name, created_at) VALUES ($1, $2, $3);",
                task_records,
            )
            return len(task_records)

    async def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieve all active tasks for a user ordered by ID."""
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, task_name, created_at FROM tasks WHERE user_id = $1 ORDER BY id ASC;",
                user_id,
            )
            return [dict(row) for row in rows]

    async def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single task by ID."""
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, user_id, task_name FROM tasks WHERE id = $1;",
                task_id,
            )
            return dict(row) if row else None

    async def get_daily_logs_map(self, user_id: int, date_str: str) -> Dict[int, str]:
        """
        Get all logs for a user on a specific date.
        Returns a dict mapping task_id -> status ('done' | 'missed').
        """
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT task_id, status FROM daily_logs WHERE user_id = $1 AND date = $2;",
                user_id,
                date_str,
            )
            return {row["task_id"]: row["status"] for row in rows}

    async def set_task_status(
        self, user_id: int, task_id: int, date_str: str, status: str
    ) -> None:
        """
        Upsert a task status ('done' or 'missed') for a specific date.
        """
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO daily_logs (user_id, task_id, date, status)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, task_id, date) DO UPDATE SET status = EXCLUDED.status;
                """,
                user_id,
                task_id,
                date_str,
                status,
            )

    async def remove_task_log(self, user_id: int, task_id: int, date_str: str) -> None:
        """Remove a task status log, returning it to unmarked state."""
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM daily_logs WHERE user_id = $1 AND task_id = $2 AND date = $3;",
                user_id,
                task_id,
                date_str,
            )

    async def toggle_task_status(
        self, user_id: int, task_id: int, date_str: str
    ) -> str:
        """
        Cycles through task states:
        Unmarked (None) -> 'done' -> 'missed' -> Unmarked (None).
        """
        if not self.pool:
            await self.init_db()

        current_status: Optional[str] = None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT status FROM daily_logs WHERE user_id = $1 AND task_id = $2 AND date = $3;",
                user_id,
                task_id,
                date_str,
            )
            if row:
                current_status = row["status"]

        if current_status is None:
            new_status = "done"
            await self.set_task_status(user_id, task_id, date_str, "done")
        elif current_status == "done":
            new_status = "missed"
            await self.set_task_status(user_id, task_id, date_str, "missed")
        else:
            new_status = "none"
            await self.remove_task_log(user_id, task_id, date_str)

        return new_status

    async def get_user_stats(self, user_id: int, today_str: str) -> Dict[str, Any]:
        """
        Calculate user statistics from Neon Postgres.
        """
        if not self.pool:
            await self.init_db()

        tasks = await self.get_user_tasks(user_id)
        active_task_ids = {t["id"] for t in tasks}
        total_active = len(active_task_ids)

        today_logs = await self.get_daily_logs_map(user_id, today_str)

        today_done = sum(
            1 for tid, st in today_logs.items() if tid in active_task_ids and st == "done"
        )
        today_missed = sum(
            1 for tid, st in today_logs.items() if tid in active_task_ids and st == "missed"
        )
        today_unmarked = max(0, total_active - (today_done + today_missed))

        today_percentage = (
            round((today_done / total_active) * 100, 1) if total_active > 0 else 0.0
        )

        async with self.pool.acquire() as conn:
            all_time_done = (
                await conn.fetchval(
                    "SELECT COUNT(*) FROM daily_logs WHERE user_id = $1 AND status = 'done';",
                    user_id,
                )
                or 0
            )

            all_time_missed = (
                await conn.fetchval(
                    "SELECT COUNT(*) FROM daily_logs WHERE user_id = $1 AND status = 'missed';",
                    user_id,
                )
                or 0
            )

            rows = await conn.fetch(
                """
                SELECT DISTINCT date FROM daily_logs 
                WHERE user_id = $1 AND status = 'done' 
                ORDER BY date DESC;
                """,
                user_id,
            )
            distinct_dates = [r["date"] for r in rows]

        # Streak calculation
        streak = 0
        if distinct_dates:
            date_set = set(distinct_dates)
            check_date = datetime.strptime(today_str, "%Y-%m-%d").date()

            if today_str not in date_set:
                check_date = check_date - timedelta(days=1)

            while check_date.strftime("%Y-%m-%d") in date_set:
                streak += 1
                check_date -= timedelta(days=1)

        return {
            "total_active": total_active,
            "today_done": today_done,
            "today_missed": today_missed,
            "today_unmarked": today_unmarked,
            "today_percentage": today_percentage,
            "all_time_done": all_time_done,
            "all_time_missed": all_time_missed,
            "streak": streak,
        }


# Singleton database instance
db = Database()
