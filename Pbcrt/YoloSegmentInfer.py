import numpy as np
import torch
import cv2
import yaml
import random
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont


class YoloSegmentInfer:
    def __init__(self, model_path: str, yaml_path: str = None):

        print(f"Pytorch model path: {model_path}")
        print(f"Pytorch yaml path: {yaml_path}")

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"yolo run location: {self.device}")
        self.model = YOLO(model_path)  # 使用ultralytics自动加载
        self.model.to(self.device)
        self.class_names = []
        self.class_colors = []
        self.font = ImageFont.truetype("simhei.ttf", 20)

        if yaml_path:
            self.load_classes(yaml_path)

    def load_classes(self, yaml_path: str):
        """加载 YOLO 类别标签并分配颜色（中文）"""
        english_to_chinese = {
            "damaged": "破损",
            "birddrop": "鸟粪",
            "leaf": "树叶",
            "sandy": "风沙",
            "snow": "积雪",
            "hotspot": "热斑",
            "other": "其他"
        }

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
        except Exception as e:
            print(f"[YOLO] Failed to open YAML file: {e}")
            return

        if "names" not in content:
            print("[YOLO] No 'names' field found in YAML.")
            return

        # 替换为中文类名
        self.class_names = [
            english_to_chinese.get(name, name)
            for name in content["names"].values()
        ]

        if not self.class_names:
            print("[YOLO] Class name list is empty.")
            return

        self.class_colors.clear()
        if len(self.class_names) > 7:
            for i in range(len(self.class_names)):
                h = (i * 37) % 180
                s = random.randint(200, 255)
                v = random.randint(200, 255)

                hsv = np.uint8([[[h, s, v]]])
                bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
                self.class_colors.append(tuple(int(c) for c in bgr))
        else:
            self.class_colors = [
                (0, 0, 255),  # 组件破损
                (255, 0, 0),  # 鸟粪遮挡
                (0, 165, 255),  # 树叶遮挡
                (255, 0, 255),  # 风沙覆盖
                (81, 255, 106),  # 积雪覆盖
                (0, 255, 0),  # 热斑缺陷
                (240, 130, 20)  # 其他异常
            ]

        print(f"[YOLO] 加载类别成功: {self.class_names}")

    def draw_chinese(self, image_np, text, position, color):
        """使用 PIL 在 OpenCV 图像上绘制中文"""
        image_pil = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        draw.text(position, text, font=self.font, fill=color[::-1])  # BGR → RGB
        return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    def predict(self, image_np: np.ndarray):
        results = self.model(image_np,
                             conf=0.25,
                             iou=0.45,
                             verbose=False)[0]

        boxes = results.boxes.data.cpu().numpy()
        masks = results.masks.data.cpu().numpy() if results.masks is not None else None

        annotated = image_np.copy()
        class_score_map = {}

        if masks is not None:
            for i, box in enumerate(boxes):
                x1, y1, x2, y2, conf, cls_id = box
                cls_id = int(cls_id)
                conf = float(conf)
                if cls_id >= len(self.class_names):
                    continue

                name = self.class_names[cls_id]
                class_score_map.setdefault(name, []).append(conf)

                mask = masks[i].astype(bool)
                color = self.class_colors[cls_id % len(self.class_colors)]
                color_img = np.zeros_like(annotated, dtype=np.uint8)
                color_img[:, :] = color
                blended = cv2.addWeighted(annotated, 1.0, color_img, 0.5, 0)
                annotated[mask] = blended[mask]

                cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                label = f"{name} {conf:.2f}"
                annotated = self.draw_chinese(annotated, label, (int(x1), int(y1) - 25), color)

        if not class_score_map:
            class_score_map["未检测到目标"] = [0.0]

        return annotated, class_score_map

    def detect(self, image_np: np.ndarray):
        """
        输入为 BGR 图像，返回：
            - 绘制边框和中文标签后的图像 annotated
            - 每个类别对应的所有置信度列表组成的字典，如：{'破损': [0.91, 0.85], '鸟粪': [0.78]}
            - 检测框信息列表，每项格式为 (cls_name, conf, (x1, y1, x2, y2))
        """
        results = self.model(image_np,
                             conf=0.25,
                             iou=0.45,
                             verbose=False)[0]

        boxes = results.boxes.data.cpu().numpy()
        annotated = image_np.copy()
        class_score_map = {}
        detections = []

        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                x1, y1, x2, y2, conf, cls_id = box
                cls_id = int(cls_id)
                conf = float(conf)
                if cls_id >= len(self.class_names):
                    continue

                name = self.class_names[cls_id]
                class_score_map.setdefault(name, []).append(conf)
                detections.append((name, conf, (int(x1), int(y1), int(x2), int(y2))))

                # 画框
                color = self.class_colors[cls_id % len(self.class_colors)]
                cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

                # 使用 PIL 绘制中文标签
                label = f"{name} {conf:.2f}"
                annotated = self.draw_chinese(annotated, label, (int(x1), int(y1) - 25), color)
        else:
            class_score_map["未检测到目标"] = [0.0]

        return annotated, class_score_map, detections

