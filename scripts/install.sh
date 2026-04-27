#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_SCOPE="${INSTALL_SCOPE:-user}"

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PROJECT_ROOT`、`PYTHON_BIN`、`INSTALL_SCOPE`
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
  user_base="$("${PYTHON_BIN}" -m site --user-base)"
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
  user_base="$("${PYTHON_BIN}" -m site --user-base)"
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
  "${PYTHON_BIN}" -m pip install "${install_args[@]}"
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
