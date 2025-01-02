import multiprocessing

# 绑定的IP和端口
bind = "0.0.0.0:5000"

# worker数量，减少worker数量以减少数据库连接
workers = 2

# 使用gevent作为worker类
worker_class = "gevent"

# 减少每个worker的最大并发请求数
worker_connections = 500

# 超时设置
timeout = 30  # 减少超时时间
keepalive = 2  # 减少保持连接时间

# 最大请求数，超过这个数量后worker将重启
max_requests = 1000
max_requests_jitter = 200

# 日志配置
accesslog = "access.log"
errorlog = "error.log"
loglevel = "warning"
access_log_format = (
    '%({x-real-ip}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)

# 进程名称
proc_name = "ship_track_app"

# 优雅的重启
graceful_timeout = 30

# 预加载应用
preload_app = True

# 工作模式
worker_class = "gevent"
worker_connections = 500

# 限制请求大小
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 设置进程文件
pidfile = "gunicorn.pid"

# 后台运行
daemon = True

# 错误通知配置
capture_output = True
enable_stdio_inheritance = True
