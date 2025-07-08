from PySide6.QtCore import QObject, QThread, QDateTime, Signal, QMutex, QMutexLocker, QTimer
from PySide6.QtNetwork import QUdpSocket, QHostAddress
import struct

# === 协议参数 ===
UDP_PACKET_SIZE = 1050
PACK_DATA_SIZE = 1024
PACK_HEAD = 0x5AA5
PACK_TAIL = 0x6BB6

ACK_PACK_HEAD = 0x6AA6
ACK_PACK_TAIL = 0x7BB7

HOST_CONN_ACK = 0x0000
HOST_DISC_ACK = 0x0002
GAIN_IMAG_ACK = 0x0004

class ImageBuffer:
    def __init__(self, w=0, h=0, img_type=0, packet_count=0):
        self.data = bytearray(w * h * 3 // 2)
        self.width = w
        self.height = h
        self.type = img_type
        self.packet_count = packet_count
        self.received_flags = set()
        self.received_count = 0
        self.last_update = QDateTime.currentDateTime()

class UdpServerWorker(QObject):
    frameReceived = Signal(bytes, int, int, int)
    udpAckDataPackArrival = Signal(int)
    socketError = Signal(str)

    def __init__(self, host: str, port: int):
        super().__init__()
        self.udp_socket = QUdpSocket()
        self.buffer_map = {}
        self.buf_lock = QMutex()

        # socket绑定
        hostAddress = QHostAddress(host)
        if not self.udp_socket.bind(hostAddress, port):
            err = self.udp_socket.errorString()
            print(f"[UDP错误] 绑定端口失败: {err}")
            self.socketError.emit(f"UDP绑定失败: {err}")
        else:
            print(f"[UDP] 成功绑定端口 {port}，等待接收数据")
            self.udp_socket.readyRead.connect(self.on_ready_read)

        # 启动定时清理
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup_stale_buffers)
        self.cleanup_timer.start(1000)

    def on_ready_read(self):
        now = QDateTime.currentDateTime()
        while self.udp_socket.hasPendingDatagrams():
            datagram, _, _ = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())
            if len(datagram) == UDP_PACKET_SIZE:
                pkt = struct.unpack('<HHIIIIHH{}sH'.format(PACK_DATA_SIZE), datagram)
                head, frame_len, index, count, w, h, img_type, valid_len, payload, tail = pkt
                if head != PACK_HEAD or tail != PACK_TAIL:
                    print(f"[UDP] 图像帧头/尾校验失败")
                    continue

                image_id = (w << 32) | count
                with QMutexLocker(self.buf_lock):
                    # 收到第一包，清除旧缓存
                    if image_id not in self.buffer_map and index == 0:
                        self.buffer_map.clear()

                    if image_id not in self.buffer_map:
                        self.buffer_map[image_id] = ImageBuffer(w, h, img_type, count)

                    buf = self.buffer_map[image_id]
                    offset = index * PACK_DATA_SIZE
                    if index < count and offset + valid_len <= len(buf.data):
                        if index not in buf.received_flags:
                            buf.data[offset:offset + valid_len] = payload[:valid_len]
                            buf.received_flags.add(index)
                            buf.received_count += 1
                            buf.last_update = now

                    if buf.received_count == buf.packet_count:
                        print("[UDP] 图像接收完成")
                        self.frameReceived.emit(bytes(buf.data), buf.width, buf.height, buf.type)
                        del self.buffer_map[image_id]

            elif len(datagram) == 6:
                head, ack_type, tail = struct.unpack('<HHH', datagram)
                if head == ACK_PACK_HEAD and tail == ACK_PACK_TAIL:
                    print("[UDP] ACK应答触发")
                    self.udpAckDataPackArrival.emit(ack_type)
            else:
                print(f"[UDP] 未知包类型: {len(datagram)} 字节")

    def cleanup_stale_buffers(self):
        now = QDateTime.currentDateTime()
        timeout_ms = 3000
        with QMutexLocker(self.buf_lock):
            for image_id in list(self.buffer_map.keys()):
                buf = self.buffer_map[image_id]
                if buf.last_update.msecsTo(now) > timeout_ms:
                    print(f"[UDP清理] 图像超时: image_id={image_id}, 已接收 {buf.received_count}/{buf.packet_count}")
                    expected_indexes = set(range(buf.packet_count))
                    missing = sorted(expected_indexes - buf.received_flags)
                    if missing:
                        print(f"[UDP清理] 丢包 index 列表: {missing}")
                    del self.buffer_map[image_id]

    def close(self):
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket.deleteLater()
        if self.cleanup_timer:
            self.cleanup_timer.stop()
        self.buffer_map.clear()


class UdpSender:
    def __init__(self):
        self.socket = QUdpSocket()

    def send_to_target(self, target_ip: str, target_port: int, data: bytes) -> bool:
        address = QHostAddress(target_ip)
        bytes_sent = self.socket.writeDatagram(data, address, target_port)
        if bytes_sent == -1:
            print(f"[UDP发送失败] {self.socket.errorString()}")
            return False
        print(f"[UDP发送成功] 字节数={bytes_sent}, IP={target_ip}, 端口={target_port}")
        return True

    def _make_ack_packet(self, ack_type: int) -> bytes:
        return struct.pack('<HHH', ACK_PACK_HEAD, ack_type, ACK_PACK_TAIL)

    def send_conn_request(self, ip: str, port: int) -> bool:
        print("发送 UDP 连接请求")
        return self.send_to_target(ip, port, self._make_ack_packet(HOST_CONN_ACK))

    def send_disc_request(self, ip: str, port: int) -> bool:
        print("发送 UDP 断开请求")
        return self.send_to_target(ip, port, self._make_ack_packet(HOST_DISC_ACK))

    def send_get_image_request(self, ip: str, port: int) -> bool:
        print("发送 UDP 获取图像请求")
        return self.send_to_target(ip, port, self._make_ack_packet(GAIN_IMAG_ACK))


class UdpServerThread(QThread):
    worker_ready = Signal(QObject)

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.worker = None

    def run(self):
        self.worker = UdpServerWorker(self.host, self.port)
        self.worker.moveToThread(self)
        self.worker_ready.emit(self.worker)
        self.exec()

    def stop(self):
        if self.worker:
            self.worker.close()
            self.worker.deleteLater()
        self.quit()
        self.wait()
        print("[UDP] worker 停止成功")
