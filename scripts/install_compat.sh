#!/usr/bin/env bash
set -euo pipefail

# AUPT 兼容性安装脚本
# 支持 Python 3.6+ (Ubuntu 18.04+, Debian 9+, CentOS 7+)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_SCOPE="${INSTALL_SCOPE:-user}"
MIN_PYTHON_VERSION="3.6"
MIRROR_TIMEOUT="${MIRROR_TIMEOUT:-15}"

# pip 镜像源列表
PIP_MIRRORS=(
  "official|https://pypi.org/simple"
  "tuna|https://pypi.tuna.tsinghua.edu.cn/simple"
  "aliyun|https://mirrors.aliyun.com/pypi/simple"
  "ustc|https://pypi.mirrors.ustc.edu.cn/simple"
)

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

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PIP_MIRRORS`、`MIRROR_TIMEOUT`
# 输出参数:
#   标准输出仅打印选中的 pip 索引地址(纯URL)；提示信息走 stderr
# 作用:
#   显示 pip 镜像源交互菜单，超时自动选择 [1] 测速最优；返回选中的镜像 URL
# 出处:
#   - 安装流程入口: `scripts/install_compat.sh`
select_pip_mirror() {
  echo "" >&2
  echo "====================================================" >&2
  echo "  pip 镜像源选择" >&2
  echo "====================================================" >&2
  echo "  [1] 自动测速并选择最佳镜像源 (推荐，${MIRROR_TIMEOUT}s 后自动执行)" >&2
  local idx=2
  for entry in "${PIP_MIRRORS[@]}"; do
    local name="${entry%%|*}"
    local url="${entry##*|}"
    printf "  [%d] %-12s %s\n" "$idx" "$name" "$url" >&2
    ((idx++))
  done
  local cancel_idx=$idx
  echo "  [${cancel_idx}] 跳过，不修改 pip 源" >&2
  echo "====================================================" >&2

  local choice
  choice=$(read_pip_choice "$((idx - 1))")
  if [[ -z "$choice" || "$choice" == "0" ]]; then
    return 0
  fi
  if [[ "$choice" == "1" ]]; then
    echo "" >&2
    echo "正在测速 pip 镜像源..." >&2
    pip_mirror_auto
    return 0
  fi
  local mirror_idx=$((choice - 2))
  local selected_url="${PIP_MIRRORS[$mirror_idx]##*|}"
  echo "" >&2
  echo "已选择 pip 镜像: ${PIP_MIRRORS[$mirror_idx]%%|*}" >&2
  printf '%s' "$selected_url"
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PIP_MIRRORS`、`PYTHON_BIN`
# 输出参数:
#   标准输出仅打印最快镜像 URL；测速过程信息走 stderr
# 作用:
#   对 pip 镜像列表依次测速，选择最快的
# 出处:
#   - 由 `select_pip_mirror()` 调用
pip_mirror_auto() {
  local best_name="" best_url="" best_time=999999
  for entry in "${PIP_MIRRORS[@]}"; do
    local name="${entry%%|*}"
    local url="${entry##*|}"
    if command -v curl >/dev/null 2>&1; then
      local elapsed
      elapsed=$(curl -s -o /dev/null -w '%{time_total}' --connect-timeout 3 --max-time 5 "$url" 2>/dev/null || echo "999")
      echo "  ${name}: ${elapsed}s" >&2
      if LC_ALL=C awk -v e="$elapsed" -v b="$best_time" 'BEGIN {exit !(e < b)}' 2>/dev/null; then
        best_time=$elapsed
        best_name=$name
        best_url=$url
      fi
    fi
  done
  if [[ -n "$best_url" ]]; then
    echo "已选择最快镜像: ${best_name} (${best_time}s)" >&2
    printf '%s' "$best_url"
  fi
}

# 函数说明:
# 输入参数:
#   mirror_count: 镜像条目数
# 输出参数:
#   标准输出仅打印用户选项编号(纯数字)，提示信息走 stderr
# 作用:
#   读取用户按键，超时返回 1(自动测速)；提示信息不走 stdout 避免污染调用方变量
# 出处:
#   - 由 `select_pip_mirror()` 调用
read_pip_choice() {
  local mirror_count=$1
  local cancel_idx=$((mirror_count + 1))
  printf "请输入选项 [1-%d]，%ds 内无输入自动执行 [1]: " "$cancel_idx" "$MIRROR_TIMEOUT" >&2

  if [[ ! -t 0 ]]; then
    echo "" >&2
    echo "非交互终端，自动执行 [1] 自动测速并选择最佳镜像源" >&2
    echo "1"
    return
  fi

  read -r -t "$MIRROR_TIMEOUT" choice 2>/dev/null || true
  if [[ -z "$choice" ]]; then
    echo "" >&2
    echo "超时，自动执行 [1] 自动测速并选择最佳镜像源" >&2
    echo "1"
    return
  fi

  if [[ "$choice" == "$cancel_idx" ]]; then
    echo "已取消，跳过 pip 镜像源修改。" >&2
    echo "0"
    return
  fi

  if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= mirror_count )); then
    echo "$choice"
    return
  fi

  echo "无效选项 ${choice}，自动执行 [1]" >&2
  echo "1"
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

  # pip 镜像源选择交互
  local pip_index_url
  pip_index_url=$(select_pip_mirror)
  if [[ -n "$pip_index_url" ]]; then
    install_args+=("--index-url" "$pip_index_url")
  fi

  echo ""
  print_info "开始安装 AUPT ..."
    
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
