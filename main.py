import socket
import json
import subprocess
import time
import platform
import threading
import ctypes

# 生成客户端ID
CLIENT_ID = 'pc_soul'

# 当前状态
current_status = {
    "online": True,
    "lock": "unlocked",
    "volume": 75,
    "mute": False
}


def is_locked():
    """准确检测Windows锁屏状态"""
    if platform.system() == 'Windows':
        try:
            # 使用Windows API检测锁屏状态
            h_desktop = ctypes.windll.user32.OpenInputDesktop(0, False, 0)
            if h_desktop:
                ctypes.windll.user32.CloseDesktop(h_desktop)
                return False  # 未锁定
            return True  # 锁定
        except:
            return False
    else:
        # 其他平台暂时返回未锁定
        return False


def get_system_status():
    """获取系统状态"""
    try:
        # 检测是否锁屏
        current_status["lock"] = "locked" if is_locked() else "unlocked"

        # 获取音量状态 (Windows特定实现)
        if platform.system() == 'Windows':
            # 确保 COM 已初始化
            import pythoncom
            pythoncom.CoInitialize()

            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_status["volume"] = round(volume.GetMasterVolumeLevelScalar() * 100)
            current_status["mute"] = bool(volume.GetMute())

        return current_status

    except Exception as e:
        print(f"获取系统状态失败: {e}")
        return current_status


def lock_screen():
    """锁屏命令"""
    try:
        if platform.system() == 'Windows':
            # 立即更新状态为锁定
            current_status["lock"] = "locked"

            # 执行锁屏命令
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            return {"status": "success", "message": "锁屏成功"}
        elif platform.system() == 'Darwin':
            subprocess.run(['osascript', '-e',
                            'tell application "System Events" to keystroke "q" using {control down, command down}'],
                           check=True)
            current_status["lock"] = "locked"
            return {"status": "success", "message": "锁屏成功"}
        else:
            try:
                subprocess.run(['gnome-screensaver-command', '--lock'], check=True)
            except:
                try:
                    subprocess.run(['xflock4'], check=True)
                except:
                    subprocess.run(['xdg-screensaver', 'lock'], check=True)
            current_status["lock"] = "locked"
            return {"status": "success", "message": "锁屏成功"}
    except Exception as e:
        return {"status": "error", "message": f"锁屏失败: {str(e)}"}


def shutdown_computer():
    """关机命令"""
    try:
        if platform.system() == 'Windows':
            subprocess.run(['shutdown', '/s', '/t', '0'], check=True)
            return {"status": "success", "message": "关机命令已执行"}
        elif platform.system() == 'Darwin':
            subprocess.run(['osascript', '-e', 'tell app "System Events" to shut down'], check=True)
            return {"status": "success", "message": "关机命令已执行"}
        else:
            subprocess.run(['shutdown', 'now'], check=True)
            return {"status": "success", "message": "关机命令已执行"}
    except Exception as e:
        return {"status": "error", "message": f"关机失败: {str(e)}"}


def set_volume(level):
    """设置音量"""
    try:
        level = int(level)
        current_status["volume"] = level
        if level > 0:
            current_status["mute"] = False

        if platform.system() == 'Windows':
            # 确保 COM 已初始化
            import pythoncom
            pythoncom.CoInitialize()

            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return {"status": "success", "message": f"音量设置为 {level}%", "volume": level}
        elif platform.system() == 'Darwin':
            subprocess.run(['osascript', '-e', f'set volume output volume {level}'], check=True)
            return {"status": "success", "message": f"音量设置为 {level}%", "volume": level}
        else:
            subprocess.run(['amixer', 'set', 'Master', f'{level}%'], check=True)
            return {"status": "success", "message": f"音量设置为 {level}%", "volume": level}
    except Exception as e:
        return {"status": "error", "message": f"设置音量失败: {str(e)}"}


def mute_volume():
    """静音"""
    try:
        current_status["mute"] = True
        if platform.system() == 'Windows':
            # 确保 COM 已初始化
            import pythoncom
            pythoncom.CoInitialize()

            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)
            return {"status": "success", "message": "已静音"}
        elif platform.system() == 'Darwin':
            subprocess.run(['osascript', '-e', 'set volume output muted true'], check=True)
            return {"status": "success", "message": "已静音"}
        else:
            subprocess.run(['amixer', 'set', 'Master', 'mute'], check=True)
            return {"status": "success", "message": "已静音"}
    except Exception as e:
        return {"status": "error", "message": f"静音失败: {str(e)}"}


def unmute_volume():
    """取消静音"""
    try:
        current_status["mute"] = False
        if platform.system() == 'Windows':
            # 确保 COM 已初始化
            import pythoncom
            pythoncom.CoInitialize()

            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)
            return {"status": "success", "message": "已取消静音"}
        elif platform.system() == 'Darwin':
            subprocess.run(['osascript', '-e', 'set volume output muted false'], check=True)
            return {"status": "success", "message": "已取消静音"}
        else:
            subprocess.run(['amixer', 'set', 'Master', 'unmute'], check=True)
            return {"status": "success", "message": "已取消静音"}
    except Exception as e:
        return {"status": "error", "message": f"取消静音失败: {str(e)}"}


# 状态监控线程
def status_monitor(connection, interval=2):
    """持续监控系统状态变化并上报"""
    last_status = current_status.copy()

    while True:
        try:
            # 获取最新状态
            get_system_status()

            # 检查状态是否有变化
            if current_status != last_status:
                # 构造状态报告
                report = {
                    "type": "status_report",
                    "status": current_status
                }

                # 发送状态报告
                connection.sendall(json.dumps(report).encode('utf-8'))
                print(f"状态变化上报: {json.dumps(report, ensure_ascii=False)}")

                # 更新最后状态
                last_status = current_status.copy()

            # 等待下一次检查
            time.sleep(interval)

        except Exception as e:
            print(f"状态监控错误: {e}")
            # 发生错误时稍作等待后重试
            time.sleep(5)


def connect_to_server():
    """连接到云服务器"""
    server_ip = 'your.server.ip'  #更改为自己的服务器IP
    server_port = 8822

    while True:
        try:
            print(f"尝试连接到服务器 {server_ip}:{server_port}...")
            # 创建socket连接
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, server_port))

            # 启动状态监控线程
            monitor_thread = threading.Thread(target=status_monitor, args=(s,), daemon=True)
            monitor_thread.start()

            # 发送注册信息
            register_data = json.dumps({
                'type': 'register',
                'client': 'pc',
                'id': CLIENT_ID,
                'status': get_system_status()  # 发送当前状态
            })
            s.sendall(register_data.encode('utf-8'))

            # 接收注册响应
            response = s.recv(1024).decode('utf-8')
            data = json.loads(response)
            if data.get('status') == 'success' or data.get('message') == '注册成功':
                print(f"成功连接到云服务器 (ID: {CLIENT_ID})")

                # 处理指令
                while True:
                    try:
                        # 接收指令
                        command = s.recv(1024).decode('utf-8')
                        if not command:
                            break

                        data = json.loads(command)
                        print(f"收到指令: {json.dumps(data, ensure_ascii=False)}")

                        # 处理指令
                        command_type = data.get('command')
                        if command_type == "lock_screen":
                            result = lock_screen()
                        elif command_type == "shutdown":
                            result = shutdown_computer()
                        elif command_type == "set_volume":
                            # 修复音量参数获取方式
                            level = data.get('data', {}).get('volume', 75)
                            result = set_volume(level)
                        elif command_type == "mute":
                            result = mute_volume()
                        elif command_type == "unmute":
                            result = unmute_volume()
                        elif command_type == "get_status":
                            result = {"status": "success", "data": get_system_status()}
                        else:
                            result = {"status": "error", "message": f"未知指令: {command_type}"}

                        # 添加当前状态到响应
                        result["current_status"] = get_system_status()

                        # 发送响应
                        s.sendall(json.dumps(result).encode('utf-8'))
                    except Exception as e:
                        print(f"指令处理错误: {e}")
                        s.sendall(json.dumps({
                            "status": "error",
                            "message": f"指令处理错误: {str(e)}",
                            "current_status": get_system_status()
                        }).encode('utf-8'))
        except Exception as e:
            print(f"连接错误: {e}")
            print("10秒后尝试重新连接...")
            time.sleep(10)
        finally:
            try:
                s.close()
            except:
                pass


if __name__ == "__main__":
    print(f"启动远程控制客户端 (ID: {CLIENT_ID})")
    # 初始化状态
    get_system_status()
    connect_to_server()
