#!/usr/bin/env bash
set -euo pipefail

# 手动镜像切换辅助脚本
# 用于在无法使用 sudo 的环境中手动切换镜像源

MIRROR_NAME="${1:-}"

if [[ -z "${MIRROR_NAME}" ]]; then
    echo "用法: $0 <镜像名称>"
    echo ""
    echo "可用镜像:"
    echo "  official - Ubuntu 官方源"
    echo "  tuna     - 清华大学镜像"
    echo "  ustc     - 中国科学技术大学镜像"
    echo "  aliyun   - 阿里云镜像"
    echo ""
    echo "示例: $0 tuna"
    exit 1
fi

# 镜像 URL 映射
declare -A MIRRORS=(
    ["official"]="http://archive.ubuntu.com/ubuntu"
    ["tuna"]="https://mirrors.tuna.tsinghua.edu.cn/ubuntu"
    ["ustc"]="https://mirrors.ustc.edu.cn/ubuntu"
    ["aliyun"]="https://mirrors.aliyun.com/ubuntu"
)

TARGET_URL="${MIRRORS[$MIRROR_NAME]:-}"
if [[ -z "${TARGET_URL}" ]]; then
    echo "错误: 未知的镜像名称: ${MIRROR_NAME}"
    exit 1
fi

SOURCES_FILE="/etc/apt/sources.list"
BACKUP_FILE="${SOURCES_FILE}.aupt.bak"

echo "准备切换到镜像: ${MIRROR_NAME}"
echo "目标 URL: ${TARGET_URL}"
echo ""

# 检查是否有权限
if [[ ! -w "${SOURCES_FILE}" ]]; then
    echo "错误: 没有写入权限: ${SOURCES_FILE}"
    echo ""
    echo "请使用以下命令之一:"
    echo "1. 切换到 root 用户:"
    echo "   sudo -i"
    echo "   bash $0 ${MIRROR_NAME}"
    echo ""
    echo "2. 或者手动编辑:"
    echo "   sudo nano ${SOURCES_FILE}"
    echo "   将所有镜像 URL 替换为: ${TARGET_URL}"
    exit 1
fi

# 备份原文件
if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "备份原配置文件..."
    cp "${SOURCES_FILE}" "${BACKUP_FILE}"
    echo "已备份到: ${BACKUP_FILE}"
fi

# 替换镜像 URL
echo "正在替换镜像源..."
TEMP_FILE=$(mktemp)

# 替换所有已知的镜像 URL
sed -e "s|http://archive.ubuntu.com/ubuntu|${TARGET_URL}|g" \
    -e "s|https://mirrors.tuna.tsinghua.edu.cn/ubuntu|${TARGET_URL}|g" \
    -e "s|https://mirrors.ustc.edu.cn/ubuntu|${TARGET_URL}|g" \
    -e "s|https://mirrors.aliyun.com/ubuntu|${TARGET_URL}|g" \
    "${SOURCES_FILE}" > "${TEMP_FILE}"

# 写入新配置
mv "${TEMP_FILE}" "${SOURCES_FILE}"

echo "✓ 镜像源已切换到: ${MIRROR_NAME}"
echo ""
echo "建议执行以下命令更新索引:"
echo "  apt update"
echo ""
echo "如需恢复原配置:"
echo "  cp ${BACKUP_FILE} ${SOURCES_FILE}"
