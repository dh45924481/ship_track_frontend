import multiprocessing

# 绑定的IP和端口
bind = "0.0.0.0:5000"

# worker数量，建议设置为CPU核心数的2-4倍
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式为gevent
worker_class = "gevent"

# 每个worker的最大并发请求数
worker_connections = 1000

# 超时设置
timeout = 300  # 增加超时时间到300秒

# 最大请求数，超过这个数量后worker将重启
max_requests = 2000
max_requests_jitter = 200

# 日志配置
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"

# 进程名称
proc_name = "ship_track_app"

# 优雅的重启
graceful_timeout = 120
