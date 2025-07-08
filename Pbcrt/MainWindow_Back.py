import sys
import os

import numpy as np
import cv2

from PySide6.QtCore import (QObject, QThread, QTimer, QMutex, QMutexLocker, Qt,QFile,
                            QIODevice, QDateTime)
from PySide6.QtCore import Signal, Slot
from PySide6.QtNetwork import QUdpSocket, QHostAddress
from PySide6.QtWidgets import (QMainWindow, QApplication, QMessageBox, QTableWidgetItem,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
                               )
from PySide6.QtGui import QCloseEvent, QImage, QPixmap

from MainWindow_ui import Ui_MainWindow
from udp_server import UdpSender, UdpServerThread
from TcpClient import TcpClientWorker, TcpClientThread
from ive_image_converter import IVEImageTypeConvert, IVEImageType
from YoloSegmentInfer import YoloSegmentInfer

# 模型
YOLO_MODEL_PATH = "\model\qhmu-pv-seg-v1.pt"
YOLO_CLASS_PATH = "\model\qhmu-pv-seg.yaml"

# 定义常量
RES_DATA_FIEL_PATH_NAME = "\cache\\table_data.csv"
SRC_IMAGES_DIR_PATH = "\images\src\\"
RES_IMAGES_DIR_PATH = "\images\\res\\"

UDP_BTN_NET_CONN_TEXT = "设备连接"
UDP_BTN_NET_DISC_TEXT = "断开连接"
CONN_ACK_TIMEOUT_MS = 3000  # 超时时间 ms
AUDIO_ACK_TIMEOUT_MS = 4000  # 超时时间 ms

DEVC_CONN_ACK = 0x0001
DEVC_DISC_ACK = 0x0003

# 网络连接类型选择
NETWORK_MODE_UDP = "UDP"
NETWORK_MODE_TCP = "TCP"
USER_NETWORK_MODE = NETWORK_MODE_UDP

#YOLO模型类型选择
YOLO_DETECT_MODEL = "detect"
YOLO_SEGMENT_MODEL = "segment"
USER_YOLO_MODEl = YOLO_SEGMENT_MODEL

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("光伏板检测")
        # 获取当前这个目录
        self.application_path = os.getcwd()
        print(f"当前工作目录:{self.application_path}")

        # 加载YOLO模型
        self.yoloModel = YoloSegmentInfer(self.application_path+YOLO_MODEL_PATH,
                                          self.application_path+YOLO_CLASS_PATH)

        #初始化控件
        self.qButtonGetImage.setEnabled(False)
        self.YoloResTableWidgetInit()
        if USER_NETWORK_MODE == NETWORK_MODE_UDP:
            # UDP控制成员
            self.udp_thread = None
            self.udp_worker = None
            self.udp_sender = UdpSender()
        elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
            # TCP控制成员
            self.tcp_thread = None
            self.tcp_worker = None

        self.conn_timeout_timer = QTimer(self)
        self.conn_timeout_timer.setSingleShot(True)
        self.conn_timeout_timer.timeout.connect(self.on_conn_timeout)

        self.audio_timeout_timer = QTimer(self)
        self.audio_timeout_timer.setSingleShot(True)
        self.audio_timeout_timer.timeout.connect(self.on_audio_timeout)

        # 绑定按钮事件
        self.qButtonUdpNetConn.clicked.connect(self.on_udp_button_clicked)
        self.qButtonGetImage.clicked.connect(self.on_image_button_clicked)
        self.qButtonDeleteTableRow.clicked.connect(self.on_yolo_table_remove_row_button_clicked)

    @Slot()
    def on_image_button_clicked(self):
        remoteHost = self.qLineEditRemoteIpv4.text().strip()
        remotePort = int(self.qLineEditRemotePort.text().strip())
        if USER_NETWORK_MODE == NETWORK_MODE_UDP:
            # UDP获取图像
            self.udp_sender.send_get_image_request(remoteHost, remotePort)
        elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
            self.tcp_worker.send_get_image_request()

        self.qButtonGetImage.setEnabled(False)
        self.qButtonUdpNetConn.setEnabled(False)
        self.audio_timeout_timer.start(AUDIO_ACK_TIMEOUT_MS)

    @Slot()
    def on_audio_timeout(self):
        self.qButtonGetImage.setEnabled(True)
        self.qButtonUdpNetConn.setEnabled(True)

    @Slot()
    def on_udp_button_clicked(self):
        btn_text = self.qButtonUdpNetConn.text().strip()
        ip_str = self.qLineEditRemoteIpv4.text().strip()
        port_str = self.qLineEditRemotePort.text().strip()
        local_ip = self.qLineEditLocalIpv4.text().strip()
        local_port_str = self.qLineEditLocalPort.text().strip()

        if not ip_str or not port_str:
            QMessageBox.warning(self, "输入错误", "请输入远程IP地址和端口号")
            return

        try:
            port = int(port_str)
            local_port = int(local_port_str)
        except ValueError:
            QMessageBox.critical(self, "格式错误", f"端口号无效: {port_str,local_port_str}")
            return

        if btn_text == UDP_BTN_NET_CONN_TEXT:
            if USER_NETWORK_MODE == NETWORK_MODE_UDP:
                self.start_udp_receiver(local_ip, local_port, ip_str, port)
            elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
                self.start_tcp_receiver(local_ip, local_port, ip_str, port)
        elif btn_text == UDP_BTN_NET_DISC_TEXT:
            if USER_NETWORK_MODE == NETWORK_MODE_UDP:
                self.udp_sender.send_disc_request(ip_str, port)
            elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
                self.tcp_worker.send_disc_request()
        self.conn_timeout_timer.start(CONN_ACK_TIMEOUT_MS)

    def start_udp_receiver(self,localHost, localHostPort, remoteHost, remotePort):
        # 启动UDP接收线程（仅启动一次）
        if self.udp_thread is None:
            self.udp_thread = UdpServerThread(localHost, localHostPort)
            self.udp_thread.worker_ready.connect(self.on_udp_worker_ready)
            self.udp_thread.finished.connect(lambda: print("[UDP线程] 已结束"))
            self.udp_thread.start()
            # 延迟发送连接请求，确保worker已启动
            QTimer.singleShot(300, lambda: self.udp_sender.send_conn_request(remoteHost, remotePort))
            print("[UDP] 已启动连接过程")
        else:
            print("[UDP] 接收线程已存在")

    @Slot(object)
    def on_udp_worker_ready(self, worker):
        self.udp_worker = worker
        worker.frameReceived.connect(self.on_frame_received)
        worker.udpAckDataPackArrival.connect(self.on_ack_arrival)
        print("[UDP] worker 信号连接完成")

    def start_tcp_receiver(self, localHost, localHostPort, remoteHost, remotePort):
        if self.tcp_thread is None:
            self.tcp_thread = TcpClientThread(localHost, localHostPort, remoteHost, remotePort)
            self.tcp_thread.worker_ready.connect(self.on_tcp_worker_ready)
            self.tcp_thread.finished.connect(lambda: print("[TCP线程] 已结束"))
            self.tcp_thread.start()
            print("[TCP] 已启动连接过程")
        else:
            print("[TCP] 线程已存在")

    @Slot(object)
    def on_tcp_worker_ready(self, worker):
        self.tcp_worker = worker
        worker.frameReceived.connect(self.on_frame_received)
        worker.tcpAckDataPackArrival.connect(self.on_ack_arrival)
        # 延迟发送连接请求，确保worker已连接
        QTimer.singleShot(500, self.tcp_worker.send_conn_request)
        print("[TCP] worker 信号连接完成")

    @Slot(bytes, int, int, int)
    def on_frame_received(self, data: bytes, w: int, h: int, img_type: int):
        print(f"[UDP] 收到完整图像帧: 尺寸={w}x{h}, 类型={IVEImageTypeConvert.ive_type_to_string(img_type)}, 大小={len(data)}")
        # 处理图像数据并推理显示
        self.image_seg_pred(data, w, h, img_type)

    def image_seg_pred(self, data: bytes, w: int, h: int, img_type: int):
        try:
            # === 原始图像数据转 BGR ===
            bgr_src_img = IVEImageTypeConvert.convert(data, w, h, img_type)
            # === 显示图像（OpenCV BGR → RGB）
            rgb_src_img = cv2.cvtColor(bgr_src_img, cv2.COLOR_BGR2RGB)
            # === 使用模型进行推理 ===
            if USER_YOLO_MODEl == YOLO_SEGMENT_MODEL:
                rgb_res_img, class_score_map = self.yoloModel.predict(rgb_src_img)
            elif USER_YOLO_MODEl == YOLO_DETECT_MODEL:
                rgb_res_img, class_score_map, detections = self.yoloModel.detect(rgb_src_img)
            # === 生成时间戳文件名 ===
            timestamp = QDateTime.currentDateTime().toString("yyyy_MM_dd_HH_mm_ss_zzz")
            src_filename = f"img_src_{timestamp}.jpg"
            res_filename = f"img_res_{timestamp}.jpg"
            src_path = self.application_path + SRC_IMAGES_DIR_PATH + src_filename
            res_path = self.application_path + RES_IMAGES_DIR_PATH + res_filename
            # === 保存 RGB 图像（OpenCV） ===
            os.makedirs(SRC_IMAGES_DIR_PATH, exist_ok=True)
            os.makedirs(RES_IMAGES_DIR_PATH, exist_ok=True)
            cv2.imwrite(src_path, rgb_src_img)
            cv2.imwrite(res_path, rgb_res_img)
            print(f"[保存] 原图保存: {src_path}")
            print(f"[保存] 结果图保存: {res_path}")
            # === 识别信息插入TableWidget ===
            self.AppendResultToTableWidget(timestamp, class_score_map)
            # === 打印类别及置信度 ===
            print("[YOLO] 预测完成：")
            for cls_name, scores in class_score_map.items():
                print(f"类别: {cls_name}，置信度: {scores}")

        except Exception as e:
            print(f"[YOLO] 图像推理出错: {e}")

    @Slot(int)
    def on_ack_arrival(self, ack_type: int):
        print(f"[UDP] 收到ACK控制帧: 类型=0x{ack_type:04X}")
        self.conn_timeout_timer.stop()
        if ack_type == DEVC_CONN_ACK:  # DEVC_CONN_ACK
            print("设备UDP连接应答确认收到")
            self.qButtonUdpNetConn.setText(UDP_BTN_NET_DISC_TEXT)
            self.qLineEditLocalPort.setEnabled(False)
            self.qLineEditLocalIpv4.setEnabled(False)
            self.qLineEditRemotePort.setEnabled(False)
            self.qLineEditRemoteIpv4.setEnabled(False)
            self.qButtonGetImage.setEnabled(True)
        elif ack_type == DEVC_DISC_ACK:
            self.qButtonUdpNetConn.setText(UDP_BTN_NET_CONN_TEXT)
            self.qLineEditLocalPort.setEnabled(True)
            self.qLineEditLocalIpv4.setEnabled(True)
            self.qLineEditRemotePort.setEnabled(True)
            self.qLineEditRemoteIpv4.setEnabled(True)
            self.qButtonGetImage.setEnabled(False)
            # 停止并清理网络线程
            if USER_NETWORK_MODE == NETWORK_MODE_UDP:
                if self.udp_thread:
                    self.udp_thread.stop()
                    self.udp_thread = None
            elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
                if self.tcp_thread:
                    self.tcp_thread.stop()
                    self.tcp_thread = None

    @Slot()
    def on_conn_timeout(self):
        QMessageBox.warning(self, "连接超时", "设备未响应请求，请检查设备状态或网络连接")
        self.qButtonUdpNetConn.setText(UDP_BTN_NET_CONN_TEXT)
        self.qLineEditLocalPort.setEnabled(True)
        self.qLineEditLocalIpv4.setEnabled(True)
        self.qLineEditRemotePort.setEnabled(True)
        self.qLineEditRemoteIpv4.setEnabled(True)
        # 停止并清理网络线程
        if USER_NETWORK_MODE == NETWORK_MODE_UDP:
            if self.udp_thread:
                self.UserSendUdpDisconnRequest()
                self.udp_thread.stop()
                self.udp_thread = None
        elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
            if self.tcp_thread:
                self.UserSendTcpDisconnRequest()
                self.tcp_thread.stop()
                self.tcp_thread = None

    def UserSendUdpDisconnRequest(self):
        #清除UDP服务句柄
        ip_str = self.qLineEditRemoteIpv4.text().strip()
        port_str = self.qLineEditRemotePort.text().strip()
        try:
            port = int(port_str)
        except ValueError:
            return
        # 发送断开请求
        self.udp_sender.send_disc_request(ip_str, port)

    def UserSendTcpDisconnRequest(self):
        ip_str = self.qLineEditRemoteIpv4.text().strip()
        port_str = self.qLineEditRemotePort.text().strip()
        try:
            port = int(port_str)
        except ValueError:
            return
        # 发送断开请求
        self.tcp_worker.send_disc_request()

    def YoloResTableWidgetInit(self):
        header_list = ["时间", "结果类别", "类别信度"]
        self.qTableYoloRes.setColumnCount(len(header_list))
        self.qTableYoloRes.setHorizontalHeaderLabels(header_list)
        self.qTableYoloRes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.qTableYoloRes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.qTableYoloRes.verticalHeader().setVisible(False)
        self.qTableYoloRes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.qTableYoloRes.setStyleSheet("QTableWidget::item:selected { background-color: lightgray; }")

        self.qTableYoloRes.itemDoubleClicked.connect(self.DoubleClickTableWidgetItemEvent)

        self.ImportTableWidgetFromFile()

        if self.qTableYoloRes.rowCount() > 0:
            self.qTableYoloRes.setCurrentCell(0, 0)
            self.qTableYoloRes.selectRow(0)
            time_str = self.qTableYoloRes.item(0, 0).text()

            src_image_path = self.application_path + SRC_IMAGES_DIR_PATH + f"img_src_{self.TimestampToFileType(time_str)}.jpg"
            print(f"YoloResTable 初始化源图文件路径:{src_image_path}")
            res_image_path = self.application_path + RES_IMAGES_DIR_PATH + f"img_res_{self.TimestampToFileType(time_str)}.jpg"
            print(f"YoloResTable 初始化结果文件路径:{res_image_path}")

            src_image = QImage(src_image_path)
            if src_image.isNull():
                print("[WARN] 源图像加载失败")
                return
            self.qLabelSrcImage.setPixmap(QPixmap.fromImage(src_image))

            res_image = QImage(res_image_path)
            if res_image.isNull():
                print("[WARN] 结果图像加载失败")
                return
            self.qLabelResImage.setPixmap(QPixmap.fromImage(res_image))

    def ImportTableWidgetFromFile(self):
        file_path = self.application_path + RES_DATA_FIEL_PATH_NAME
        print(f"Yolo result data input file path: {file_path}")
        if not os.path.exists(file_path):
            print(f"[WARN] 无法打开文件读取：{file_path}")
            return
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if not lines:
            print("[WARN] 文件为空")
            return
        first_line = lines[0].strip()
        if not first_line.startswith("TableRowCount;"):
            print(f"[WARN] 首行格式异常，期望 TableRowCount; 实际为：{first_line}")
            return
        parts = first_line.split(';')
        if len(parts) < 2 or not parts[1].isdigit():
            print(f"[WARN] 无法解析表格行数：{parts[1] if len(parts) > 1 else ''}")
            return
        expected_row_count = int(parts[1])
        print(f"[DEBUG] 期望导入表格行数：{expected_row_count}")
        self.qTableYoloRes.clearContents()
        self.qTableYoloRes.setRowCount(0)
        row_index = 0
        for line in lines[1:]:  # 从第二行开始处理数据
            line = line.strip()
            if not line:
                continue
            columns = line.split(';')
            self.qTableYoloRes.insertRow(row_index)
            for col_index, text in enumerate(columns):
                item = QTableWidgetItem(text)
                self.qTableYoloRes.setItem(row_index, col_index, item)
            row_index += 1
        print(f"[DEBUG] 成功从文件导入表格数据：{file_path}")

    def AppendResultToTableWidget(self, timestamp: str, yolo_class_res_current: dict[str, list[float]]):
        """
        向表格添加一行推理结果：时间戳、类别、置信度。
        """
        # 类别拼接
        class_list = list(yolo_class_res_current.keys())
        # 构造置信度字符串
        accu_list = []
        for cls in class_list:
            scores = yolo_class_res_current[cls]
            score_strs = [f"{score:.2f}" for score in scores]
            accu_list.append(f"[{','.join(score_strs)}]")
        # 插入新行到顶部
        new_row = 0
        self.qTableYoloRes.insertRow(new_row)
        self.qTableYoloRes.setItem(new_row, 0, QTableWidgetItem(self.TimestampToTableType(timestamp)))
        self.qTableYoloRes.setItem(new_row, 1, QTableWidgetItem(",".join(class_list)))
        self.qTableYoloRes.setItem(new_row, 2, QTableWidgetItem(",".join(accu_list)))
        # 自动选中新行
        self.qTableYoloRes.selectRow(new_row)
        # 显示图像
        self.ShowImagesDataToLabel(timestamp)

    def ExportTableWidgetToFile(self, table: QTableWidget):
        # 构造导出文件路径
        file_path = self.application_path + RES_DATA_FIEL_PATH_NAME
        print(f"Yolo result data export file path: {file_path}")
        if table is None :
            print("[WARN] 表格无效，无法导出。")
            return


        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                # 表格为空也要写 TableRowCount;0
                if table.rowCount() == 0 or table.columnCount() == 0:
                    file.write("TableRowCount;0\n")
                    print(f"[导出] 表格为空，已清空文件并写入行数 0: {file_path}")
                    return
                # 写入表头信息
                file.write(f"TableRowCount;{table.rowCount()}\n")
                # 写入每一行
                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    file.write(";".join(row_data) + "\n")
            print(f"[DEBUG] 数据成功导出到: {file_path}")
        except Exception as e:
            print(f"[WARN] 无法写入文件: {file_path}，错误信息: {e}")

    def ShowImagesDataToLabel(self, timestamp: str):
        src_filename = f"img_src_{timestamp}.jpg"
        res_filename = f"img_res_{timestamp}.jpg"

        src_path = self.application_path + SRC_IMAGES_DIR_PATH + src_filename
        res_path = self.application_path + RES_IMAGES_DIR_PATH + res_filename

        # 加载并显示原图
        src_pixmap = QPixmap(src_path)
        if not src_pixmap.isNull():
            self.qLabelSrcImage.setPixmap(
                src_pixmap.scaledToWidth(self.qLabelSrcImage.width(), Qt.SmoothTransformation))
        else:
            print(f"[警告] 原图加载失败: {src_path}")

        # 加载并显示结果图
        res_pixmap = QPixmap(res_path)
        if not res_pixmap.isNull():
            self.qLabelResImage.setPixmap(
                res_pixmap.scaledToWidth(self.qLabelResImage.width(), Qt.SmoothTransformation))
        else:
            print(f"[警告] 结果图加载失败: {res_path}")

    def DoubleClickTableWidgetItemEvent(self, item: QTableWidgetItem):
        if item is None:
            return
        row = item.row()  # 获取被点击项所在的行
        # 获取时间戳（假设在第 0 列，即 TW_TIME_COL = 0）
        time_item = self.qTableYoloRes.item(row, 0)
        if time_item is None:
            print("[WARN] 时间项不存在")
            return
        timestamp_str = time_item.text()
        # 转换为文件命名格式
        formatted_timestamp = self.TimestampToFileType(timestamp_str)
        # 显示图像
        self.ShowImagesDataToLabel(formatted_timestamp)

    def TimestampToFileType(self, time_str: str) -> str:
        """
        将时间字符串（"yyyy-MM-dd hh:mm:ss.zzz"）转为文件名格式："yyyy_MM_dd_HH_mm_ss_zzz"
        """
        return time_str.replace('-', '_').replace(':', '_').replace(' ', '_').replace('.', '_')

    def TimestampToTableType(self, file_str: str) -> str:
        """
        将文件名格式时间字符串转换为可读时间格式："yyyy-MM-dd HH:mm:ss.zzz"
        """
        parts = file_str.split('_')
        if len(parts) != 7:
            raise ValueError("时间戳格式错误，应为7段")
        return f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}:{parts[5]}.{parts[6]}"

    def on_yolo_table_remove_row_button_clicked(self):
        current_row = self.qTableYoloRes.currentRow()
        if current_row < 0:
            print("当前没有选中任何行，无法删除。")
            return
        # 删除当前行（Qt 会自动将后续行前移）
        del_item = self.qTableYoloRes.item(current_row, 0)
        if del_item is None:
            print("时间项不存在")
            return
        timestamp_del = del_item.text()
        self.qTableYoloRes.removeRow(current_row)
        self.DeleteImagesByTimestamp(timestamp_del)
        print(f"已删除第 {current_row} 行。")
        # 重新选择删除后当前行
        total_rows = self.qTableYoloRes.rowCount()
        if total_rows > 0:
            new_row = min(current_row, total_rows - 1)
            self.qTableYoloRes.selectRow(new_row)
            time_item = self.qTableYoloRes.item(new_row, 0)
            if time_item is None:
                print("时间项不存在")
                return
            timestamp_str = time_item.text()
            # 转换为文件命名格式
            formatted_timestamp = self.TimestampToFileType(timestamp_str)
            # 显示图像
            self.ShowImagesDataToLabel(formatted_timestamp)
        elif total_rows == 0:
            self.qLabelSrcImage.setText("原始图像显示")
            self.qLabelResImage.setText("推理图像显示")

    def DeleteImagesByTimestamp(self, timestamp: str):
        """
        根据时间戳删除对应的原图和结果图像文件。

        :param timestamp: 格式为 "yyyy_MM_dd_HH_mm_ss_zzz"
        """
        timestamp_file = self.TimestampToFileType(timestamp)
        src_filename = f"img_src_{timestamp_file}.jpg"
        res_filename = f"img_res_{timestamp_file}.jpg"
        src_path = self.application_path + SRC_IMAGES_DIR_PATH + src_filename
        res_path = self.application_path + RES_IMAGES_DIR_PATH + res_filename
        # 删除源图像
        if os.path.exists(src_path):
            os.remove(src_path)
            print(f"[删除] 已删除原图像文件: {src_path}")
        else:
            print(f"[删除] 原图像文件不存在: {src_path}")
        # 删除结果图像
        if os.path.exists(res_path):
            os.remove(res_path)
            print(f"[删除] 已删除结果图像文件: {res_path}")
        else:
            print(f"[删除] 结果图像文件不存在: {res_path}")

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            "确认退出",
            "你确定要退出程序吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("正在退出程序...")
            # 在此释放资源或关闭线程等
            self.ExportTableWidgetToFile(self.qTableYoloRes)
            # 停止并清理网络线程
            if USER_NETWORK_MODE == NETWORK_MODE_UDP:
                if self.udp_thread:
                    self.UserSendUdpDisconnRequest()
                    self.udp_thread.stop()
                    self.udp_thread = None
            elif USER_NETWORK_MODE == NETWORK_MODE_TCP:
                if self.tcp_thread:
                    UserSendTcpDisconnRequest()
                    self.tcp_thread.stop()
                    self.tcp_thread = None
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()