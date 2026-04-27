#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_NAME="origin"
REMOTE_URL="git@github.com:wusi321/aupt.git"
DEFAULT_BRANCH="main"
FORCE_PUSH="false"
COMMIT_MESSAGE="${1:-update: sync project}"

if [[ "${1:-}" == "--force" ]]; then
  FORCE_PUSH="true"
  COMMIT_MESSAGE="${2:-update: sync project}"
fi

# 函数说明:
# 输入参数:
#   无，使用全局变量 `PROJECT_ROOT`
# 输出参数:
#   0 表示目录切换成功，非 0 表示失败
# 作用:
#   进入脚本所在的项目根目录，确保后续 Git 操作始终针对当前工程
# 出处:
#   - 脚本根目录变量: `git.sh` 中的 `PROJECT_ROOT`
enter_project_root() {
  cd "${PROJECT_ROOT}"
}

# 函数说明:
# 输入参数:
#   无
# 输出参数:
#   0 表示当前目录已是 Git 仓库或初始化成功，非 0 表示失败
# 作用:
#   检查当前工程是否为 Git 仓库；若不是则自动执行 `git init`
# 出处:
#   - Git 仓库检测命令: `git rev-parse --is-inside-work-tree`
ensure_git_repo() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 0
  fi

  echo "检测到当前目录尚未初始化 Git 仓库，正在执行 git init ..."
  git init
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `REMOTE_NAME`、`REMOTE_URL`
# 输出参数:
#   0 表示远程仓库配置完成，非 0 表示失败
# 作用:
#   自动创建或更新 `origin` 远程地址，避免因远程已存在导致脚本中断
# 出处:
#   - 远程仓库名称: `git.sh` 中的 `REMOTE_NAME`
#   - 远程仓库地址: `git.sh` 中的 `REMOTE_URL`
ensure_remote() {
  local current_url=""

  if git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
    current_url="$(git remote get-url "${REMOTE_NAME}")"
    if [[ "${current_url}" != "${REMOTE_URL}" ]]; then
      echo "检测到 ${REMOTE_NAME} 已存在，正在更新远程地址 ..."
      git remote set-url "${REMOTE_NAME}" "${REMOTE_URL}"
    fi
    return 0
  fi

  echo "正在添加远程仓库 ${REMOTE_NAME} -> ${REMOTE_URL}"
  git remote add "${REMOTE_NAME}" "${REMOTE_URL}"
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `COMMIT_MESSAGE`
# 输出参数:
#   0 表示已提交或无改动可提交，非 0 表示失败
# 作用:
#   自动暂存全部变更，并在存在文件改动时创建一次提交
# 出处:
#   - 提交信息变量: `git.sh` 中的 `COMMIT_MESSAGE`
commit_changes() {
  git add .

  if git diff --cached --quiet; then
    echo "没有新的变更可提交，跳过 commit。"
    return 0
  fi

  git commit -m "${COMMIT_MESSAGE}"
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `DEFAULT_BRANCH`
# 输出参数:
#   0 表示分支切换成功，非 0 表示失败
# 作用:
#   将当前分支统一重命名为 `main`
# 出处:
#   - 默认分支变量: `git.sh` 中的 `DEFAULT_BRANCH`
ensure_main_branch() {
  git branch -M "${DEFAULT_BRANCH}"
}

# 函数说明:
# 输入参数:
#   无，使用全局变量 `REMOTE_NAME`、`DEFAULT_BRANCH`、`FORCE_PUSH`
# 输出参数:
#   0 表示推送成功，非 0 表示失败
# 作用:
#   推送当前分支到远程仓库；默认普通推送，设置 `--force` 时执行强制推送
# 出处:
#   - 远程名称变量: `git.sh` 中的 `REMOTE_NAME`
#   - 默认分支变量: `git.sh` 中的 `DEFAULT_BRANCH`
#   - 强推开关变量: `git.sh` 中的 `FORCE_PUSH`
push_branch() {
  if [[ "${FORCE_PUSH}" == "true" ]]; then
    echo "正在执行强制推送到 ${REMOTE_NAME}/${DEFAULT_BRANCH} ..."
    git push -u "${REMOTE_NAME}" "${DEFAULT_BRANCH}" --force
    return 0
  fi

  echo "正在推送到 ${REMOTE_NAME}/${DEFAULT_BRANCH} ..."
  git push -u "${REMOTE_NAME}" "${DEFAULT_BRANCH}"
}

# 函数说明:
# 输入参数:
#   无
# 输出参数:
#   0 表示脚本执行成功，非 0 表示失败
# 作用:
#   串联仓库初始化、远程配置、提交与推送流程，是一键提交流程总入口
# 出处:
#   - 流程函数: `enter_project_root()`、`ensure_git_repo()`、`ensure_remote()`、`commit_changes()`、`ensure_main_branch()`、`push_branch()`，均位于 `git.sh`
main() {
  enter_project_root
  ensure_git_repo
  ensure_remote
  commit_changes
  ensure_main_branch
  push_branch

  echo "Git 提交流程完成。"
}

main "$@"
