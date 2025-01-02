from contextlib import contextmanager
from flask import current_app
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
import time


class DatabasePool:
    _pool = None
    _max_retries = 3  # 减少重试次数
    _retry_delay = 5  # 增加每次重试的间隔时间

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            cls._pool = PooledDB(
                creator=pymysql,
                maxconnections=10,  # 减少最大连接数
                mincached=2,  # 减少初始连接数
                maxcached=8,  # 减少最大空闲连接数
                maxshared=0,  # 禁用共享连接
                blocking=True,  # 连接数达到最大时阻塞等待
                maxusage=None,  # 不限制连接复用次数
                setsession=[],  # 开始会话前执行的命令
                ping=1,  # 使用ping检测连接是否有效
                host="47.116.5.151",
                port=13316,
                user="root",
                password="hasf12345",
                database="jiance",
                charset="utf8",
                cursorclass=DictCursor,
                connect_timeout=60,  # 增加连接超时时间
                read_timeout=60,  # 读取超时时间
                write_timeout=60,  # 写入超时时间
            )
        return cls._pool

    @classmethod
    def reset_pool(cls):
        """重置连接池"""
        if cls._pool is not None:
            try:
                cls._pool.close()
            except:
                pass
            finally:
                cls._pool = None

    @classmethod
    def _get_connection_with_retry(cls):
        """带重试机制的获取连接"""
        for attempt in range(cls._max_retries):
            try:
                if attempt > 0:  # 如果不是第一次尝试，重置连接池
                    cls.reset_pool()
                    time.sleep(cls._retry_delay)  # 重试前等待
                return cls.get_pool().connection()
            except Exception as e:
                current_app.logger.warning(
                    f"获取数据库连接失败，正在重试 ({attempt + 1}/{cls._max_retries}): {str(e)}"
                )
                if attempt == cls._max_retries - 1:  # 最后一次尝试
                    current_app.logger.error(f"获取数据库连接失败 (最终尝试): {str(e)}")
                    raise

    @classmethod
    @contextmanager
    def get_connection(cls):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = cls._get_connection_with_retry()
            yield conn
        except Exception as e:
            current_app.logger.error(f"数据库连接错误: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    current_app.logger.error(f"关闭数据库连接错误: {str(e)}")

    @classmethod
    @contextmanager
    def get_cursor(cls):
        """获取数据库游标的上下文管理器"""
        with cls.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                yield cursor
                conn.commit()  # 自动提交事务
            except Exception as e:
                if conn:
                    conn.rollback()  # 发生错误时回滚
                current_app.logger.error(f"数据库操作错误: {str(e)}")
                raise
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except Exception as e:
                        current_app.logger.error(f"关闭游标错误: {str(e)}")


def execute_query(sql, params=None):
    """执行查询并返回结果"""
    for attempt in range(DatabasePool._max_retries):
        try:
            with DatabasePool.get_cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
        except Exception as e:
            if attempt == DatabasePool._max_retries - 1:  # 最后一次尝试
                current_app.logger.error(f"查询失败 (最终尝试): {str(e)}")
                raise
            current_app.logger.warning(
                f"查询失败，正在重试 ({attempt + 1}/{DatabasePool._max_retries}): {str(e)}"
            )
            time.sleep(DatabasePool._retry_delay)


def execute_update(sql, params=None):
    """执行更新操作"""
    for attempt in range(DatabasePool._max_retries):
        try:
            with DatabasePool.get_cursor() as cursor:
                return cursor.execute(sql, params or ())
        except Exception as e:
            if attempt == DatabasePool._max_retries - 1:  # 最后一次尝试
                current_app.logger.error(f"更新失败 (最终尝试): {str(e)}")
                raise
            current_app.logger.warning(
                f"更新失败，正在重试 ({attempt + 1}/{DatabasePool._max_retries}): {str(e)}"
            )
            time.sleep(DatabasePool._retry_delay)
