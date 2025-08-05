# -*- coding: utf-8 -*-
import socket
import threading
import asyncio
import websockets
import json
import queue

# 全局变量存储连接信息和状态
pc_clients = {}  # PC客户端连接 {client_id: socket}
mobile_clients = {}  # 手机客户端连接 {client_id: websocket}
pc_status = {}  # PC状态存储 {client_id: status}
pc_response_queues = {}  # PC响应队列 {client_id: queue.Queue}
main_event_loop = None  # 存储主事件循环


async def broadcast_status_update(pc_client_id, status):
    """广播状态更新给所有手机客户端"""
    to_remove = []  # 存储需要移除的断开连接客户端

    for mid, mobile_ws in mobile_clients.items():
        try:
            # 检查连接是否仍然打开
            if mobile_ws.open:
                await mobile_ws.send(json.dumps({
                    'type': 'status_update',
                    'pc_id': pc_client_id,
                    'status': status
                }))
            else:
                # 连接已关闭，标记为需要移除
                to_remove.append(mid)
        except Exception as e:
            print(f"无法发送状态更新到手机 {mid}: {str(e)}")
            to_remove.append(mid)

    # 移除断开的客户端
    for mid in to_remove:
        if mid in mobile_clients:
            del mobile_clients[mid]
            print(f"已移除断开的手机客户端: {mid}")


# WebSocket服务器处理手机客户端
async def handle_mobile_client(websocket, path):
    client_id = None
    try:
        # 接收注册信息
        register_data = await websocket.recv()
        data = json.loads(register_data)

        if data.get('type') == 'register' and data.get('client') == 'mobile':
            client_id = data.get('id')
            mobile_clients[client_id] = websocket
            print(f"手机客户端已连接: {client_id}")

            # 确认注册
            await websocket.send(json.dumps({
                'type': 'status',
                'message': '注册成功'
            }))

            # 发送当前PC状态（如果有）
            if pc_status:
                for pc_id, status in pc_status.items():
                    await websocket.send(json.dumps({
                        'type': 'status_update',
                        'pc_id': pc_id,
                        'status': status
                    }))
            else:
                # 如果没有PC在线，发送离线状态
                offline_status = {
                    "online": False,
                    "lock": "unknown",
                    "volume": 0,
                    "mute": False
                }
                await websocket.send(json.dumps({
                    'type': 'status_update',
                    'pc_id': 'no_pc',
                    'status': offline_status
                }))

            # 保持连接
            while True:
                try:
                    message = await websocket.recv()
                    if not message:
                        break

                    data = json.loads(message)
                    # 使用 json.dumps 确保中文正确显示
                    data_str = json.dumps(data, ensure_ascii=False)
                    print(f"收到手机指令: {data_str}")

                    # 转发指令给PC客户端
                    if data.get('type') == 'command':
                        # 如果没有PC客户端在线
                        if not pc_clients:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '没有在线的PC客户端'
                            }))
                            continue

                        # 获取第一个PC客户端
                        pc_client_id = next(iter(pc_clients.keys()))
                        pc_socket = pc_clients[pc_client_id]

                        try:
                            # 发送指令给PC
                            command_data = {
                                'command': data['command'],
                                'data': data.get('data', {})
                            }
                            pc_socket.sendall(json.dumps(command_data).encode('utf-8'))

                            # 获取响应队列
                            if pc_client_id not in pc_response_queues:
                                pc_response_queues[pc_client_id] = queue.Queue()
                            response_queue = pc_response_queues[pc_client_id]

                            # 等待响应（带超时）
                            loop = asyncio.get_event_loop()
                            try:
                                # 使用异步方式等待队列响应
                                response_str = await asyncio.wait_for(
                                    loop.run_in_executor(
                                        None,
                                        lambda: response_queue.get(timeout=5.0)
                                    ),
                                    timeout=5.0
                                )

                                # 解析响应
                                response_data = json.loads(response_str)
                                # 使用 json.dumps 确保中文正确显示
                                response_str_disp = json.dumps(response_data, ensure_ascii=False)
                                print(f"PC响应: {response_str_disp}")

                                # 更新状态
                                if 'current_status' in response_data:
                                    pc_status[pc_client_id] = response_data['current_status']

                                    # 广播状态更新
                                    await broadcast_status_update(pc_client_id, pc_status[pc_client_id])

                                # 发送响应给手机
                                await websocket.send(json.dumps({
                                    'type': 'status',
                                    'status': data['command'],
                                    'message': response_data.get('message', ''),
                                    'volume': response_data.get('volume', 0)
                                }))
                            except (queue.Empty, asyncio.TimeoutError):
                                print(f"等待PC响应超时: {data['command']}")
                                await websocket.send(json.dumps({
                                    'type': 'error',
                                    'message': '等待PC响应超时'
                                }))
                        except Exception as e:
                            print(f"指令传输错误: {e}")
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': str(e)
                            }))
                except websockets.exceptions.ConnectionClosed:
                    print(f"手机客户端 {client_id} 连接已关闭")
                    break
    except Exception as e:
        print(f"手机客户端处理错误: {e}")
    finally:
        if client_id and client_id in mobile_clients:
            del mobile_clients[client_id]
            print(f"手机客户端断开: {client_id}")


# TCP服务器处理PC客户端
def handle_pc_client(client_socket, address):
    client_id = None
    try:
        # 接收注册信息
        register_data = client_socket.recv(1024).decode('utf-8')
        data = json.loads(register_data)

        if data.get('type') == 'register' and data.get('client') == 'pc':
            client_id = data.get('id')
            pc_clients[client_id] = client_socket

            # 创建响应队列
            pc_response_queues[client_id] = queue.Queue()

            # 保存初始状态
            if 'status' in data:
                pc_status[client_id] = data['status']

            # 使用 json.dumps 确保中文正确显示
            status_str = json.dumps(pc_status.get(client_id, {}), ensure_ascii=False)
            print(f"PC客户端已连接: {client_id} (状态: {status_str})")

            # 确认注册
            client_socket.sendall(json.dumps({
                'type': 'status',
                'message': '注册成功'
            }).encode('utf-8'))

            # 广播状态更新（使用异步方式）
            if client_id in pc_status and main_event_loop is not None:
                coro = broadcast_status_update(client_id, pc_status[client_id])
                asyncio.run_coroutine_threadsafe(coro, main_event_loop)

            # 保持连接，接收数据
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    # 尝试解析消息
                    try:
                        # 尝试直接解码为 JSON 对象
                        response_data = json.loads(data.decode('utf-8'))
                        # 使用 json.dumps 确保中文正确显示
                        response_str = json.dumps(response_data, ensure_ascii=False)
                        print(f"收到PC消息: {response_str}")

                        # 处理状态报告
                        if response_data.get('type') == 'status_report':
                            new_status = response_data.get('status', {})
                            if new_status:
                                pc_status[client_id] = new_status
                                # 广播状态更新
                                if main_event_loop is not None:
                                    coro = broadcast_status_update(client_id, new_status)
                                    asyncio.run_coroutine_threadsafe(coro, main_event_loop)
                            continue

                        # 普通响应放入队列
                        if client_id in pc_response_queues:
                            pc_response_queues[client_id].put(data.decode('utf-8'))

                    except json.JSONDecodeError:
                        # 如果无法解析为 JSON，则直接放入队列
                        response_str = data.decode('utf-8')
                        print(f"收到PC消息: {response_str}")
                        if client_id in pc_response_queues:
                            pc_response_queues[client_id].put(response_str)

                except (ConnectionResetError, BrokenPipeError):
                    print(f"PC客户端 {client_id} 连接已断开")
                    break
                except Exception as e:
                    print(f"处理PC数据错误: {e}")
                    break
    except Exception as e:
        print(f"PC客户端处理错误: {e}")
    finally:
        if client_id:
            if client_id in pc_clients:
                del pc_clients[client_id]
                print(f"PC客户端断开: {client_id}")
            if client_id in pc_status:
                # 广播离线状态
                offline_status = {
                    "online": False,
                    "lock": "unknown",
                    "volume": 0,
                    "mute": False
                }
                if main_event_loop is not None:
                    coro = broadcast_status_update(client_id, offline_status)
                    asyncio.run_coroutine_threadsafe(coro, main_event_loop)
                del pc_status[client_id]
            if client_id in pc_response_queues:
                del pc_response_queues[client_id]
            try:
                client_socket.close()
            except:
                pass


# 启动TCP服务器
def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8822))
    server.listen(5)
    print("TCP服务器在端口8822启动...")

    while True:
        try:
            client_socket, addr = server.accept()
            print(f"新的PC连接: {addr}")
            client_thread = threading.Thread(target=handle_pc_client, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
        except Exception as e:
            print(f"接受连接错误: {e}")


# 启动WebSocket服务器
async def start_websocket_server():
    server = await websockets.serve(handle_mobile_client, "0.0.0.0", 8823)
    print("WebSocket服务器在端口8823启动...")
    await server.wait_closed()


# 主函数
def main():
    global main_event_loop

    # 创建事件循环
    main_event_loop = asyncio.get_event_loop()

    # 启动TCP服务器线程
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()

    # 启动WebSocket服务器
    try:
        main_event_loop.run_until_complete(start_websocket_server())
        main_event_loop.run_forever()
    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        main_event_loop.close()


if __name__ == "__main__":
    main()