#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_SCOPE="${INSTALL_SCOPE:-user}"

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PYTHON_BIN`
# 输出参数:
#   0 表示环境检查通过，非 0 表示失败
# 作用:
#   检查系统 `python3` 与 `pip` 是否可用，保证卸载过程使用系统 Python
# 出处:
#   - 卸载流程入口: `scripts/uninstall.sh`
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
#   标准输出打印 pip 卸载参数
# 作用:
#   根据安装范围生成 pip 卸载参数
# 出处:
#   - 卸载流程入口: `scripts/uninstall.sh`
# 注意:
#   pip uninstall 不支持 --user 选项，用户级和系统级卸载命令相同
build_uninstall_args() {
  printf '%s\n' "aupt"
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PYTHON_BIN`
# 输出参数:
#   0 表示卸载成功，非 0 表示失败
# 作用:
#   调用 `python3 -m pip uninstall` 卸载 AUPT
# 出处:
#   - 打包配置: `pyproject.toml`
uninstall_aupt() {
  local -a uninstall_args
  mapfile -t uninstall_args < <(build_uninstall_args)
  "${PYTHON_BIN}" -m pip uninstall -y "${uninstall_args[@]}"
}

# 函数说明:
# 输入参数:
#   无
# 输出参数:
#   0 表示脚本执行成功，非 0 表示失败
# 作用:
#   统一串联检查与卸载，是卸载脚本主入口
# 出处:
#   - 卸载流程入口: `scripts/uninstall.sh`
main() {
  ensure_python
  uninstall_aupt
  echo "AUPT 卸载完成。"
}

main "$@"
