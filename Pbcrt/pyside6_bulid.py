# build_exe.py
import PyInstaller.__main__
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="PySide6 项目打包脚本")
    parser.add_argument(
        '--distpath', type=str, default='output',
        help='指定可执行文件输出目录 (默认: output)'
    )
    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.distpath, exist_ok=True)

    PyInstaller.__main__.run([
        'MainWindow_Back.py',
        '--noconfirm',
        '--clean',
        '--name=PvSegApp',
        '--windowed',
        '--noconfirm',
        '--onefile',
        '--icon=cache/pv_icon.png',
        '--add-data=images;images',
        '--add-data=model;model',
        '--add-data=cache;cache',
        f'--distpath={args.distpath}',
    ])

if __name__ == '__main__':
    main()
