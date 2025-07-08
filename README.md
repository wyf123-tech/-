# 作品简介
- 该作品以HiSilicon海思 Hi3516DV300处理器为核心平台，集成改进版目标检测算法 RED-YOLO，面向自动驾驶复杂交通场景，实现对车辆、行人、交通标志等多类目标的高效识别。采用 RED-YOLO 改进模型，引入 RFAConv 注意力模块与 C2f-DCN 可变形卷积结构，自研模块DAP及PBR，显著提升复杂场景下的检测鲁棒性，对小目标、遮挡目标识别效果优于传统 YOLO 模型。能同时检测并区分多类交通目标（如车辆、行人、交通标志、障碍物等），输出目标位置与类别标签，服务于自动驾驶系统的环境感知层。
该系统融合了改进型检测算法、高效模型压缩策略和嵌入式部署优化技术，兼具准确性、实时性与低资源占用，适合应用于智能驾驶车辆的前装视觉模块、城市智能交通终端及无人系统的视觉感知组件。

# 代码介绍
- Pbcrt目录下是本作品基于PySide6的上位机程序，实现了图像信息获取、分析和展示。
  ![image](https://github.com/user-attachments/assets/e3d3d4ba-0508-4066-88d0-241897c4aeb8)
- __pycache__目录下是本作品相关模块的配置文件，包括自研模块的具体代码算法内容。
  ![image](https://github.com/user-attachments/assets/63b4c1e1-af73-4f22-9b01-02ce86341ec1)
- project目录下是本作品的模型文件，包括wk模型文件，以及在PC端训练的模型文件
  ![image](https://github.com/user-attachments/assets/77c00bb1-3ecd-4a5b-a63e-23ddcc7198a4)

