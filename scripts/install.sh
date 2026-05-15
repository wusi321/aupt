#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_SCOPE="${INSTALL_SCOPE:-user}"
MIRROR_TIMEOUT="${MIRROR_TIMEOUT:-15}"

# pip 镜像源列表
PIP_MIRRORS=(
  "official|https://pypi.org/simple"
  "tuna|https://pypi.tuna.tsinghua.edu.cn/simple"
  "aliyun|https://mirrors.aliyun.com/pypi/simple"
  "ustc|https://pypi.mirrors.ustc.edu.cn/simple"
)

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PIP_MIRRORS`、`MIRROR_TIMEOUT`
# 输出参数:
#   标准输出仅打印选中的 pip 索引地址(纯URL)；提示信息走 stderr
# 作用:
#   显示 pip 镜像源交互菜单，超时自动选择 [1] 测速最优；返回选中的镜像 URL
# 出处:
#   - 安装流程入口: `scripts/install.sh`
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

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PYTHON_BIN`
# 输出参数:
#   0 表示环境检查通过，非 0 表示失败
# 作用:
#   检查系统 `python3` 与 `pip` 是否可用，保证安装过程使用系统 Python
# 出处:
#   - 安装流程入口: `scripts/install.sh`
ensure_python() {
  if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "错误: 未找到 ${PYTHON_BIN}，请先安装系统 python3。" >&2
    exit 1
  fi

  # 检查 Python 版本
  local python_version
  python_version=$("${PYTHON_BIN}" -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))" 2>/dev/null || echo "0.0")
  
  if [[ "$python_version" == "0.0" ]]; then
    echo "错误: 无法获取 Python 版本信息。" >&2
    exit 1
  fi
  
  echo "检测到 Python 版本: $python_version"
  
  # 检查是否满足最低版本要求 (3.6+)
  local major minor
  major=$(echo "$python_version" | cut -d. -f1)
  minor=$(echo "$python_version" | cut -d. -f2)
  
  if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 6 ]]; }; then
    echo "错误: AUPT 需要 Python 3.6 或更高版本，当前版本: $python_version" >&2
    echo "建议使用兼容性安装脚本: ./scripts/install_compat.sh" >&2
    exit 1
  fi

  if ! "${PYTHON_BIN}" -m pip --version >/dev/null 2>&1; then
    echo "错误: ${PYTHON_BIN} 缺少 pip，请先安装 python3-pip。" >&2
    exit 1
  fi
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `INSTALL_SCOPE`
# 输出参数:
#   标准输出打印 pip 安装参数
# 作用:
#   根据安装范围生成 pip 参数，支持用户级安装和系统级安装
# 出处:
#   - 安装流程入口: `scripts/install.sh`
build_install_args() {
  if [[ "${INSTALL_SCOPE}" == "system" ]]; then
    printf '%s\n' "."
  else
    printf '%s\n' "--user" "."
  fi
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PYTHON_BIN`
# 输出参数:
#   0 表示 PATH 已包含用户脚本目录，1 表示未包含
# 作用:
#   检查 `python3 -m site --user-base` 对应的 bin 目录是否已进入 PATH
# 出处:
#   - 安装流程入口: `scripts/install.sh`
check_user_bin_in_path() {
  local user_base user_bin
  user_base="$("${PYTHON_BIN}" -m site --user-base 2>/dev/null || echo "$HOME/.local")"
  user_bin="${user_base}/bin"
  [[ ":${PATH}:" == *":${user_bin}:"* ]]
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PYTHON_BIN`
# 输出参数:
#   标准输出打印安装后的补充说明
# 作用:
#   在用户级安装完成后提示 PATH 配置，确保 `aupt` 可直接全局执行
# 出处:
#   - 安装流程入口: `scripts/install.sh`
print_path_hint() {
  local user_base user_bin
  user_base="$("${PYTHON_BIN}" -m site --user-base 2>/dev/null || echo "$HOME/.local")"
  user_bin="${user_base}/bin"

  if check_user_bin_in_path; then
    echo "用户级命令目录已在 PATH 中，可直接执行: aupt"
    return 0
  fi

  echo "检测到 ${user_bin} 尚未加入 PATH。"
  echo "请将下面一行加入 ~/.bashrc 或 ~/.zshrc 后重新打开终端:"
  echo "export PATH=\"${user_bin}:\$PATH\""
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PROJECT_ROOT`、`PYTHON_BIN`
# 输出参数:
#   0 表示安装成功，非 0 表示失败
# 作用:
#   进入项目根目录并调用 `python3 -m pip install` 完成本地包安装
# 出处:
#   - 打包配置: `pyproject.toml`
install_aupt() {
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
  echo "正在安装 AUPT ..."
  
  # 尝试正常安装
  if "${PYTHON_BIN}" -m pip install "${install_args[@]}" 2>&1 | tee /tmp/aupt_install.log; then
    return 0
  fi
  
  # 检查是否需要 --break-system-packages (Python 3.11+ on Debian/Ubuntu)
  if grep -q "externally-managed-environment" /tmp/aupt_install.log 2>/dev/null; then
    echo "检测到外部管理的环境，添加 --break-system-packages 选项..."
    "${PYTHON_BIN}" -m pip install "${install_args[@]}" --break-system-packages
    return $?
  fi
  
  return 1
}

# 函数说明:
# 输入参数:
#   无
# 输出参数:
#   0 表示脚本执行成功，非 0 表示失败
# 作用:
#   统一串联检查、安装与安装后提示，是安装脚本主入口
# 出处:
#   - 安装流程入口: `scripts/install.sh`
main() {
  ensure_python
  install_aupt

  echo "AUPT 安装完成。"
  echo "可执行检查命令: aupt doctor"

  if [[ "${INSTALL_SCOPE}" != "system" ]]; then
    print_path_hint
  fi
}

main "$@"
