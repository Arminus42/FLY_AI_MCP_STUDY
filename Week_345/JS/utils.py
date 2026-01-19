import os

def in_target(target_root, full_path):
    return os.path.commonpath([target_root, full_path]) == target_root
