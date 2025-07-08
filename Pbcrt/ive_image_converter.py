from typing import Any

from PySide6.QtGui import QImage
import cv2
import numpy as np
from numpy import ndarray, dtype


class IVEImageType:
    U8C1 = 0
    S8C1 = 1
    YUV420SP = 2
    YUV422SP = 3
    YUV420P = 4
    YUV422P = 5
    S8C2_PACKAGE = 6
    S8C2_PLANAR = 7
    S16C1 = 8
    U16C1 = 9
    U8C3_PACKAGE = 10
    U8C3_PLANAR = 11
    S32C1 = 12
    U32C1 = 13
    S64C1 = 14
    U64C1 = 15
    BUTT = 16

class IVEImageTypeConvert:

    @staticmethod
    def to_qimage(mat: np.ndarray) -> QImage:
        """OpenCV Mat 转换为 QImage"""
        if len(mat.shape) == 2:
            return QImage(mat.data, mat.shape[1], mat.shape[0], mat.strides[0], QImage.Format.Format_Grayscale8).copy()
        elif mat.shape[2] == 3:
            return QImage(mat.data, mat.shape[1], mat.shape[0], mat.strides[0], QImage.Format.Format_BGR888).copy()
        else:
            raise ValueError("不支持的图像格式")

    @staticmethod
    def convert(data: bytes, width: int, height: int, img_type: int) -> np.ndarray:
        """
        将原始图像数据根据图像类型转换为 OpenCV BGR 格式的 np.ndarray。
        支持灰度、打包 RGB/YUV、分离 YUV 等格式。
        """
        total_size = len(data)
        array = np.frombuffer(data, dtype=np.uint8)

        if img_type == IVEImageType.U8C1:
            expected = width * height
            if total_size < expected:
                raise ValueError("U8C1 数据不足")
            gray = array[:expected].reshape((height, width))
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        elif img_type == IVEImageType.S8C1:
            expected = width * height
            if total_size < expected:
                raise ValueError("S8C1 数据不足")
            gray = np.frombuffer(data, dtype=np.int8)[:expected].reshape((height, width)).astype(np.uint8)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        elif img_type == IVEImageType.U8C3_PACKAGE:
            expected = width * height * 3
            if total_size < expected:
                raise ValueError("U8C3_PACKAGE 数据不足")
            return array[:expected].reshape((height, width, 3))  # 默认 BGR

        elif img_type == IVEImageType.U8C3_PLANAR:
            expected = width * height * 3
            if total_size < expected:
                raise ValueError("U8C3_PLANAR 数据不足")
            y = array[0:width * height].reshape((height, width))
            u = array[width * height:2 * width * height].reshape((height, width))
            v = array[2 * width * height:expected].reshape((height, width))
            return cv2.merge([v, u, y])  # YUV 转 BGR 可加一步转 cv2.COLOR_YCrCb2BGR

        elif img_type == IVEImageType.YUV420SP:
            expected = width * height * 3 // 2
            if total_size < expected:
                raise ValueError("YUV420SP 数据不足")
            yuv = array[:expected].reshape((height * 3 // 2, width))
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)

        elif img_type == IVEImageType.YUV422SP:
            expected = width * height * 2
            if total_size < expected:
                raise ValueError("YUV422SP 数据不足")
            yuv = array[:expected].reshape((height, width * 2))
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_YUY2)

        elif img_type == IVEImageType.YUV420P:
            expected = width * height * 3 // 2
            if total_size < expected:
                raise ValueError("YUV420P 数据不足")
            y = array[0:width * height].reshape((height, width))
            u = array[width * height:width * height + (width // 2) * (height // 2)].reshape((height // 2, width // 2))
            v = array[width * height + (width // 2) * (height // 2):expected].reshape((height // 2, width // 2))
            u_up = cv2.resize(u, (width, height), interpolation=cv2.INTER_LINEAR)
            v_up = cv2.resize(v, (width, height), interpolation=cv2.INTER_LINEAR)
            yuv = cv2.merge([y, u_up, v_up])
            return cv2.cvtColor(yuv, cv2.COLOR_YCrCb2BGR)

        elif img_type == IVEImageType.YUV422P:
            expected = width * height * 2
            if total_size < expected:
                raise ValueError("YUV422P 数据不足")
            y = array[0:width * height].reshape((height, width))
            u = array[width * height:width * height + (width // 2) * height].reshape((height, width // 2))
            v = array[width * height + (width // 2) * height:expected].reshape((height, width // 2))
            u_up = cv2.resize(u, (width, height), interpolation=cv2.INTER_LINEAR)
            v_up = cv2.resize(v, (width, height), interpolation=cv2.INTER_LINEAR)
            yuv = cv2.merge([y, u_up, v_up])
            return cv2.cvtColor(yuv, cv2.COLOR_YCrCb2BGR)

        else:
            raise ValueError(f"不支持的图像类型: {img_type}")

    @staticmethod
    def ive_type_to_string(img_type: int) -> str:
        """将 IVE 图像类型整数转换为字符串表示"""
        mapping = {
            0: "U8C1",
            1: "S8C1",
            2: "YUV420SP",
            3: "YUV422SP",
            4: "YUV420P",
            5: "YUV422P",
            6: "S8C2_PACKAGE",
            7: "S8C2_PLANAR",
            8: "S16C1",
            9: "U16C1",
            10: "U8C3_PACKAGE",
            11: "U8C3_PLANAR",
            12: "S32C1",
            13: "U32C1",
            14: "S64C1",
            15: "U64C1",
            16: "BUTT"
        }
        return mapping.get(img_type, "UNKNOWN")

    @staticmethod
    def ive_string_to_type(value: int) -> int:
        """将整数安全转换为 IVEImageType 枚举值"""
        if not (0 <= value <= IVEImageType.BUTT):
            raise ValueError(f"Invalid IVEImageType value: {value}")
        return value

