from flask import current_app
import pymysql
from dbutils.pooled_db import PooledDB
import time


class DatabasePool:
    _instance = None
    _pool = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
        self.create_pool()

    def create_pool(self):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self._pool = PooledDB(
                    creator=pymysql,
                    maxconnections=30,  # 增加最大连接数
                    mincached=5,  # 初始化时创建的连接数
                    maxcached=20,  # 连接池最大缓存数
                    maxshared=10,  # 最大共享连接数
                    blocking=True,  # 连接池中如果没有可用连接后是否阻塞等待
                    maxusage=None,  # 一个连接最多被重复使用的次数
                    setsession=['SET time_zone = "+08:00"'],  # 设置时区
                    ping=1,  # 检查连接是否有效
                    host="47.116.5.151",
                    port=13316,
                    user="root",
                    password="hasf12345",
                    database="jiance",
                    charset="utf8",
                    cursorclass=pymysql.cursors.DictCursor,
                )
                current_app.logger.info("数据库连接池创建成功")
                break
            except Exception as e:
                retry_count += 1
                current_app.logger.error(
                    f"创建连接池失败 (尝试 {retry_count}/{self.max_retries}): {str(e)}"
                )
                if retry_count < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def get_connection(self):
        """获取数据库连接"""
        try:
            if not self._pool:
                self.create_pool()
            return self._pool.connection()
        except Exception as e:
            current_app.logger.error(f"获取数据库连接失败: {str(e)}")
            raise

    def close_all(self):
        """关闭所有连接"""
        try:
            if self._pool:
                self._pool.close()
                current_app.logger.info("所有数据库连接已关闭")
        except Exception as e:
            current_app.logger.error(f"关闭数据库连接失败: {str(e)}")


def execute_query(sql, params=None):
    """执行SQL查询并返回结果"""
    db = DatabasePool.get_instance()
    conn = None
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
    except Exception as e:
        current_app.logger.error(f"数据库查询错误: {str(e)}")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                current_app.logger.error(f"关闭数据库连接失败: {str(e)}")
