#!/usr/bin/env bash
set -euo pipefail

# AUPT 兼容性安装脚本
# 支持 Python 3.6+ (Ubuntu 18.04+, Debian 9+, CentOS 7+)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_SCOPE="${INSTALL_SCOPE:-user}"
MIN_PYTHON_VERSION="3.6"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# 比较版本号
# 返回: 0 表示 version1 >= version2, 1 表示 version1 < version2
version_ge() {
    local version1="$1"
    local version2="$2"
    
    # 使用 sort -V 进行版本比较
    if printf '%s\n%s\n' "$version2" "$version1" | sort -V -C 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 获取 Python 版本
get_python_version() {
    local python_bin="$1"
    "$python_bin" -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))" 2>/dev/null || echo "0.0"
}

# 检查 Python 是否可用
check_python() {
    local python_bin="$1"
    
    if ! command -v "$python_bin" >/dev/null 2>&1; then
        return 1
    fi
    
    local version
    version=$(get_python_version "$python_bin")
    
    if [[ "$version" == "0.0" ]]; then
        return 1
    fi
    
    if version_ge "$version" "$MIN_PYTHON_VERSION"; then
        echo "$version"
        return 0
    else
        return 1
    fi
}

# 查找可用的 Python
find_python() {
    local candidates=("python3" "python3.10" "python3.9" "python3.8" "python3.7" "python3.6" "python")
    
    print_info "正在查找可用的 Python 解释器..."
    
    for candidate in "${candidates[@]}"; do
        if version=$(check_python "$candidate"); then
            print_success "找到 Python $version: $candidate"
            echo "$candidate"
            return 0
        fi
    done
    
    return 1
}

# 检查 pip 是否可用
check_pip() {
    local python_bin="$1"
    
    if "$python_bin" -m pip --version >/dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# 尝试安装 pip
install_pip() {
    local python_bin="$1"
    
    print_warning "pip 未安装，尝试自动安装..."
    
    # 尝试使用 ensurepip
    if "$python_bin" -m ensurepip --version >/dev/null 2>&1; then
        print_info "使用 ensurepip 安装 pip..."
        "$python_bin" -m ensurepip --default-pip --user
        return $?
    fi
    
    # 尝试使用 get-pip.py
    print_info "下载 get-pip.py..."
    local temp_dir
    temp_dir=$(mktemp -d)
    
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL https://bootstrap.pypa.io/pip/get-pip.py -o "$temp_dir/get-pip.py"
    elif command -v wget >/dev/null 2>&1; then
        wget -q https://bootstrap.pypa.io/pip/get-pip.py -O "$temp_dir/get-pip.py"
    else
        print_error "需要 curl 或 wget 来下载 get-pip.py"
        rm -rf "$temp_dir"
        return 1
    fi
    
    print_info "安装 pip..."
    "$python_bin" "$temp_dir/get-pip.py" --user
    local result=$?
    rm -rf "$temp_dir"
    return $result
}

# 检查并安装依赖
ensure_dependencies() {
    local python_bin="$1"
    
    print_info "检查 Python 环境..."
    
    # 检查 pip
    if ! check_pip "$python_bin"; then
        if ! install_pip "$python_bin"; then
            print_error "无法安装 pip"
            print_info "请手动安装 pip:"
            print_info "  Ubuntu/Debian: sudo apt install python3-pip"
            print_info "  CentOS/RHEL:   sudo yum install python3-pip"
            print_info "  Fedora:        sudo dnf install python3-pip"
            return 1
        fi
    fi
    
    print_success "pip 已就绪"
    
    # 检查 setuptools
    if ! "$python_bin" -c "import setuptools" 2>/dev/null; then
        print_warning "setuptools 未安装，尝试安装..."
        "$python_bin" -m pip install --user setuptools || true
    fi
    
    # 检查 wheel
    if ! "$python_bin" -c "import wheel" 2>/dev/null; then
        print_info "安装 wheel 以加速构建..."
        "$python_bin" -m pip install --user wheel || true
    fi
    
    return 0
}

# 构建安装参数
build_install_args() {
    if [[ "${INSTALL_SCOPE}" == "system" ]]; then
        printf '%s\n' "."
    else
        printf '%s\n' "--user" "."
    fi
}

# 检查是否需要 --break-system-packages
needs_break_system_packages() {
    local python_bin="$1"
    
    # Python 3.11+ 在某些发行版上需要此选项
    local version
    version=$(get_python_version "$python_bin")
    
    if version_ge "$version" "3.11"; then
        # 检查是否是 Debian/Ubuntu 系统
        if [[ -f /etc/os-release ]]; then
            if grep -qiE "debian|ubuntu" /etc/os-release; then
                return 0
            fi
        fi
    fi
    
    return 1
}

# 安装 AUPT
install_aupt() {
    local python_bin="$1"
    local -a install_args
    mapfile -t install_args < <(build_install_args)
    
    cd "${PROJECT_ROOT}"
    
    print_info "开始安装 AUPT..."
    
    # 尝试正常安装
    if "$python_bin" -m pip install "${install_args[@]}" 2>&1 | tee /tmp/aupt_install.log; then
        print_success "安装成功"
        return 0
    fi
    
    # 检查是否需要 --break-system-packages
    if grep -q "externally-managed-environment" /tmp/aupt_install.log; then
        print_warning "检测到外部管理的环境，添加 --break-system-packages 选项"
        if "$python_bin" -m pip install "${install_args[@]}" --break-system-packages; then
            print_success "安装成功"
            return 0
        fi
    fi
    
    # 尝试使用 --user 强制用户级安装
    if [[ "${INSTALL_SCOPE}" != "user" ]]; then
        print_warning "系统级安装失败，尝试用户级安装..."
        if "$python_bin" -m pip install --user .; then
            print_success "用户级安装成功"
            return 0
        fi
    fi
    
    print_error "安装失败"
    return 1
}

# 检查 PATH
check_user_bin_in_path() {
    local python_bin="$1"
    local user_base user_bin
    
    user_base=$("$python_bin" -m site --user-base 2>/dev/null || echo "$HOME/.local")
    user_bin="${user_base}/bin"
    
    [[ ":${PATH}:" == *":${user_bin}:"* ]]
}

# 打印 PATH 提示
print_path_hint() {
    local python_bin="$1"
    local user_base user_bin
    
    user_base=$("$python_bin" -m site --user-base 2>/dev/null || echo "$HOME/.local")
    user_bin="${user_base}/bin"
    
    if check_user_bin_in_path "$python_bin"; then
        print_success "用户级命令目录已在 PATH 中，可直接执行: aupt"
        return 0
    fi
    
    print_warning "检测到 ${user_bin} 尚未加入 PATH"
    echo ""
    echo "请将下面一行加入 ~/.bashrc 或 ~/.zshrc 后重新打开终端:"
    echo ""
    echo "    export PATH=\"${user_bin}:\$PATH\""
    echo ""
    echo "或者立即生效:"
    echo ""
    echo "    export PATH=\"${user_bin}:\$PATH\""
    echo "    source ~/.bashrc"
    echo ""
}

# 显示系统信息
show_system_info() {
    print_info "系统信息:"
    
    if [[ -f /etc/os-release ]]; then
        local distro_name distro_version
        distro_name=$(grep "^PRETTY_NAME=" /etc/os-release | cut -d'"' -f2)
        echo "  发行版: ${distro_name}"
    fi
    
    echo "  内核: $(uname -r)"
    echo "  架构: $(uname -m)"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  AUPT 兼容性安装脚本"
    echo "  支持 Python ${MIN_PYTHON_VERSION}+"
    echo "=========================================="
    echo ""
    
    show_system_info
    
    # 查找 Python
    local python_bin
    if ! python_bin=$(find_python); then
        print_error "未找到可用的 Python ${MIN_PYTHON_VERSION}+ 解释器"
        echo ""
        print_info "请安装 Python 3.6 或更高版本:"
        print_info "  Ubuntu 18.04+: sudo apt install python3 python3-pip"
        print_info "  Ubuntu 16.04:  sudo apt install python3.6 python3.6-pip"
        print_info "  Debian 9+:     sudo apt install python3 python3-pip"
        print_info "  CentOS 7:      sudo yum install python3 python3-pip"
        print_info "  CentOS 8+:     sudo dnf install python3 python3-pip"
        exit 1
    fi
    
    local python_version
    python_version=$(get_python_version "$python_bin")
    
    echo ""
    print_info "使用 Python: $python_bin (版本 $python_version)"
    echo ""
    
    # 检查依赖
    if ! ensure_dependencies "$python_bin"; then
        exit 1
    fi
    
    echo ""
    
    # 安装 AUPT
    if ! install_aupt "$python_bin"; then
        exit 1
    fi
    
    echo ""
    print_success "=========================================="
    print_success "  AUPT 安装完成！"
    print_success "=========================================="
    echo ""
    
    print_info "可执行以下命令进行测试:"
    echo "  aupt doctor"
    echo "  aupt mirror list"
    echo ""
    
    if [[ "${INSTALL_SCOPE}" != "system" ]]; then
        print_path_hint "$python_bin"
    fi
    
    print_info "更多帮助请查看: README.md"
    echo ""
}

main "$@"
