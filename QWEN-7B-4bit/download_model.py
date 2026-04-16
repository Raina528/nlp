"""
下载 Qwen2-7B-Instruct 4bit 模型
"""
from huggingface_hub import snapshot_download
import os

def download_qwen():
    model_id = "Qwen/Qwen2-7B-Instruct"
    local_dir = os.path.join(os.path.dirname(__file__), "models", "qwen2-7b")
    
    print(f"正在下载 Qwen2-7B-Instruct 模型...")
    print(f"保存路径：{local_dir}")
    print("注意：首次下载会自动安装 bitsandbytes 用于 4bit 量化\n")
    
    try:
        snapshot_download(
            repo_id=model_id,
            local_dir=local_dir
        )
        print("\n✓ 模型下载完成！")
        print(f"下一步：python inference.py")
    except Exception as e:
        print(f"\n下载失败：{e}")
        print("请检查网络连接")

if __name__ == "__main__":
    download_qwen()
