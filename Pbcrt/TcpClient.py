from PySide6.QtCore import QObject, QThread, QDateTime, Signal, QMutex, QMutexLocker
import socket
import struct
import threading

# === 协议常量 ===
PACK_DATA_SIZE = 1024
UDP_PACKET_SIZE = 1052

PACK_HEAD = 0x5AA5
PACK_TAIL = 0x6BB6

ACK_PACK_HEAD = 0x6AA6
ACK_PACK_TAIL = 0x7BB7

HOST_CONN_ACK = 0x0000
HOST_DISC_ACK = 0x0002
GAIN_IMAG_ACK = 0x0004

class ImageBuffer:
    def __init__(self):
        self.data = bytearray()
        self.width = 0
        self.height = 0
        self.type = 0
        self.packet_count = 0
        self.received_count = 0
        self.received_flags = set()
        self.last_update = QDateTime.currentDateTime()


class TcpClientWorker(QObject):
    frameReceived = Signal(bytes, int, int, int)
    tcpAckDataPackArrival = Signal(int)
    socketError = Signal(str)

    def __init__(self, local_ip: str, local_port: int, remote_ip: str, remote_port: int):
        super().__init__()
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.client_socket = None
        self.running = False
        self.buffer_map = {}
        self.buf_lock = QMutex()
        self.recv_buf = bytearray()

    def start_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client_socket.bind((self.local_ip, self.local_port))
            self.client_socket.connect((self.remote_ip, self.remote_port))
            self.running = True
            threading.Thread(target=self.receive_loop, daemon=True).start()
            print(f"[TCP] 成功连接至 {self.remote_ip}:{self.remote_port}")
        except Exception as e:
            self.socketError.emit(f"[TCP错误] 连接失败: {e}")

    def receive_loop(self):
        try:
            while self.running:
                data = self.client_socket.recv(2048)
                if not data:
                    break
                self.recv_buf.extend(data)
                self.process_buffer()
        except Exception as e:
            self.socketError.emit(f"[TCP错误] 接收失败: {e}")
        finally:
            self.stop_connection()

    def process_buffer(self):
        print(f"[TCP] Recv data length: {len(self.recv_buf)}")
        while len(self.recv_buf) >= 6:
            if self.recv_buf[:2] == struct.pack('<H', ACK_PACK_HEAD) and self.recv_buf[4:6] == struct.pack('<H', ACK_PACK_TAIL):
                # 处理 ACK 包
                if len(self.recv_buf) >= 6:
                    _, ack_type, _ = struct.unpack('<HHH', self.recv_buf[:6])
                    self.tcpAckDataPackArrival.emit(ack_type)
                    self.recv_buf = self.recv_buf[6:]
                else:
                    break
            elif len(self.recv_buf) >= UDP_PACKET_SIZE:
                pkt = self.recv_buf[:UDP_PACKET_SIZE]
                self.recv_buf = self.recv_buf[UDP_PACKET_SIZE:]
                self.process_packet(pkt)
            else:
                break

    def process_packet(self, data: bytes):
        try:
            unpacked = struct.unpack('<HHIIIIHH{}sH2x'.format(PACK_DATA_SIZE), data)
            head, frame_len, index, count, w, h, img_type, valid_len, payload, tail = unpacked
            if head != PACK_HEAD or tail != PACK_TAIL:
                print(f"[TCP] 图像包头尾校验失败,head: {head:04X}, end: {tail:04X}")
                return
            print(f"[TCP] Recv image data index:{index} count:{count}");
            image_id = (w << 32) | count
            with QMutexLocker(self.buf_lock):
                if image_id not in self.buffer_map:
                    buf = ImageBuffer()
                    buf.data = bytearray(w * h * 3 // 2)
                    buf.width = w
                    buf.height = h
                    buf.type = img_type
                    buf.packet_count = count
                    self.buffer_map[image_id] = buf
                buf = self.buffer_map[image_id]
                offset = index * PACK_DATA_SIZE
                if index < count and offset + valid_len <= len(buf.data) and index not in buf.received_flags:
                    buf.data[offset:offset + valid_len] = payload[:valid_len]
                    buf.received_flags.add(index)
                    buf.received_count += 1
                    if buf.received_count == buf.packet_count:
                        print("[TCP] 图像接收完成")
                        self.frameReceived.emit(bytes(buf.data), buf.width, buf.height, buf.type)
                        del self.buffer_map[image_id]
        except Exception as e:
            self.socketError.emit(f"[TCP] 图像包处理失败: {e}")

    def send(self, data: bytes):
        try:
            if self.client_socket:
                self.client_socket.sendall(data)
        except Exception as e:
            self.socketError.emit(f"[TCP错误] 发送失败: {e}")

    def _make_ack_packet(self, ack_type: int) -> bytes:
        """构造一个ACK应答数据包"""
        return struct.pack('<HHH', ACK_PACK_HEAD, ack_type, ACK_PACK_TAIL)

    def send_conn_request(self):
        """发送连接请求ACK"""
        print("[TCP] 发送连接请求 ACK")
        self.send(self._make_ack_packet(HOST_CONN_ACK))

    def send_disc_request(self):
        """发送断开请求ACK"""
        print("[TCP] 发送断开请求 ACK")
        self.send(self._make_ack_packet(HOST_DISC_ACK))

    def send_get_image_request(self):
        """发送获取图像请求ACK"""
        print("[TCP] 发送获取图像请求 ACK")
        self.send(self._make_ack_packet(GAIN_IMAG_ACK))

    def stop_connection(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        self.buffer_map.clear()
        print("[TCP] 连接已断开")


class TcpClientThread(QThread):
    worker_ready = Signal(QObject)

    def __init__(self, local_ip: str, local_port: int, remote_ip: str, remote_port: int):
        super().__init__()
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.worker = None

    def run(self):
        self.worker = TcpClientWorker(self.local_ip, self.local_port, self.remote_ip, self.remote_port)
        self.worker.moveToThread(self)
        self.worker_ready.emit(self.worker)
        self.worker.start_connection()
        self.exec()

    def stop(self):
        if self.worker:
            self.worker.stop_connection()
        self.quit()
        self.wait()
        print("[TCP] 客户端线程停止")
