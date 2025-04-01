from flask import Flask, jsonify
from flask_cors import CORS
import threading
import pythoncom
import psutil
import wmi
import os
import time

app = Flask(__name__)
CORS(app)  # 全局启用 CORS

def get_hardware_data():
    """从 Open Hardware Monitor 获取硬件数据"""
    pythoncom.CoInitialize()
    try:
        hardware_data = {
            "temperatures": {},
            "fan_speeds": {},
            "voltages": {}
        }
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        sensors = w.Sensor()

        for sensor in sensors:
            hardware_name = sensor.Parent
            sensor_name = sensor.Name
            sensor_value = sensor.Value

            # 温度数据
            if sensor.SensorType == "Temperature":
                if hardware_name not in hardware_data["temperatures"]:
                    hardware_data["temperatures"][hardware_name] = []
                hardware_data["temperatures"][hardware_name].append({
                    "label": sensor_name,
                    "current": sensor_value,
                    "high": None,
                    "critical": None
                })

            # 风扇转速数据
            elif sensor.SensorType == "Fan":
                if hardware_name not in hardware_data["fan_speeds"]:
                    hardware_data["fan_speeds"][hardware_name] = []
                hardware_data["fan_speeds"][hardware_name].append({
                    "label": sensor_name,
                    "speed": sensor_value
                })

            # 电压数据
            elif sensor.SensorType == "Voltage":
                if hardware_name not in hardware_data["voltages"]:
                    hardware_data["voltages"][hardware_name] = []
                hardware_data["voltages"][hardware_name].append({
                    "label": sensor_name,
                    "voltage": sensor_value
                })

        return hardware_data
    finally:
        pythoncom.CoUninitialize()


def get_top_processes():
    """获取占用 CPU 前十的进程"""
    processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']):
        try:
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": proc.info['cpu_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:10]


def get_disk_info():
    """获取磁盘使用情况"""
    disk = psutil.disk_usage('/')
    return {
        "usage": disk.percent,
        "total": round(disk.total / (1024 ** 3), 2),
        "used": round(disk.used / (1024 ** 3), 2)
    }


def get_uptime_days():
    """获取系统运行天数"""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    return round(uptime_seconds / (60 * 60 * 24), 2)


def get_load_average():
    """获取系统负载百分比"""
    if hasattr(os, 'getloadavg'):
        load_avg = os.getloadavg()
        num_cpus = psutil.cpu_count()
        return round(load_avg[0] / num_cpus * 100, 2)
    else:  # Windows
        return psutil.cpu_percent(interval=0.1)


def get_network_traffic():
    """获取网络上下行实时流量和总流量"""
    net_io = psutil.net_io_counters()
    return {
        "sent": round(net_io.bytes_sent / (1024 ** 2), 2),
        "recv": round(net_io.bytes_recv / (1024 ** 2), 2),
        "realtime_sent": round(psutil.net_io_counters().bytes_sent / (1024 ** 2), 2),
        "realtime_recv": round(psutil.net_io_counters().bytes_recv / (1024 ** 2), 2)
    }


@app.route('/system-info', methods=['GET'])
def get_system_info():
    hardware_data = get_hardware_data()

    system_info = {
        "cpu": {"usage": psutil.cpu_percent(interval=0.1), "count": psutil.cpu_count()},
        "memory": {
            "usage": psutil.virtual_memory().percent,
            "total": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "used": round(psutil.virtual_memory().used / (1024 ** 3), 2)
        },
        "disk": get_disk_info(),
        "uptime_days": get_uptime_days(),
        "load_avg_percent": get_load_average(),
        "temps": hardware_data["temperatures"],
        "fan_speeds": hardware_data["fan_speeds"],
        "voltages": hardware_data["voltages"],
        "network": get_network_traffic(),
        "processes": get_top_processes()
    }

    return jsonify(system_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9706)
