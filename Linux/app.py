from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import time

app = Flask(__name__)
CORS(app)

@app.route('/system-info', methods=['GET'])
def system_info():
    # CPU信息
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=True)

    # 内存信息
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_total = round(memory.total / (1024 ** 3), 2)
    memory_used = round(memory.used / (1024 ** 3), 2)

    # 硬盘信息
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_total = round(disk.total / (1024 ** 3), 2)
    disk_used = round(disk.used / (1024 ** 3), 2)

    # 运行天数
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_days = round(uptime_seconds / (60 * 60 * 24), 2)

    # 温度信息
    temps = {}
    if hasattr(psutil, "sensors_temperatures"):
        for name, entries in psutil.sensors_temperatures().items():
            temps[name] = [
                {
                    "label": entry.label or name,
                    "current": entry.current,
                    "high": entry.high,
                    "critical": entry.critical,
                }
                for entry in entries
            ]

    # 网络流量信息
    net_io = psutil.net_io_counters()
    net_sent = round(net_io.bytes_sent / (1024 ** 2), 2)
    net_recv = round(net_io.bytes_recv / (1024 ** 2), 2)

    # 前10个进程
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:10]:
        processes.append({
            "pid": proc.info['pid'],
            "name": proc.info['name'],
            "cpu_percent": proc.info['cpu_percent']
        })

    return jsonify({
        "cpu": {
            "usage": cpu_usage,
            "count": cpu_count
        },
        "memory": {
            "usage": memory_usage,
            "total": memory_total,
            "used": memory_used
        },
        "disk": {
            "usage": disk_usage,
            "total": disk_total,
            "used": disk_used
        },
        "uptime_days": uptime_days,
        "temps": temps,
        "network": {
            "sent": net_sent,
            "recv": net_recv
        },
        "processes": processes
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9706)
