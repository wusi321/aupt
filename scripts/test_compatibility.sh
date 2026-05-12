#!/usr/bin/env bash
set -euo pipefail

# AUPT 兼容性测试脚本
# 测试不同 Python 版本的兼容性

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "=========================================="
    echo "  $*"
    echo "=========================================="
    echo ""
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

print_error() {
    echo -e "${RED}[✗]${NC} $*"
}

# 测试单个 Python 版本
test_python_version() {
    local python_bin="$1"
    local version
    
    if ! command -v "$python_bin" >/dev/null 2>&1; then
        print_error "$python_bin 未安装"
        return 1
    fi
    
    version=$("$python_bin" -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))" 2>/dev/null || echo "unknown")
    
    print_info "测试 $python_bin (版本 $version)"
    
    # 测试导入主要模块
    if ! "$python_bin" -c "
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from aupt.cli.commands import main
from aupt.core.dispatcher import Dispatcher
from aupt.core.distro_detector import DistroDetector
from aupt.backends.apt_backend import AptBackend
print('所有模块导入成功')
" 2>&1; then
        print_error "$python_bin: 模块导入失败"
        return 1
    fi
    
    print_success "$python_bin: 所有测试通过"
    return 0
}

# 主函数
main() {
    print_header "AUPT Python 兼容性测试"
    
    print_info "项目路径: $PROJECT_ROOT"
    echo ""
    
    local -a python_versions=(
        "python3.6"
        "python3.7"
        "python3.8"
        "python3.9"
        "python3.10"
        "python3.11"
        "python3.12"
        "python3"
    )
    
    local passed=0
    local failed=0
    local skipped=0
    
    for python_bin in "${python_versions[@]}"; do
        if test_python_version "$python_bin"; then
            ((passed++))
        else
            if command -v "$python_bin" >/dev/null 2>&1; then
                ((failed++))
            else
                ((skipped++))
            fi
        fi
        echo ""
    done
    
    print_header "测试结果"
    
    echo -e "${GREEN}通过: $passed${NC}"
    echo -e "${RED}失败: $failed${NC}"
    echo -e "${YELLOW}跳过: $skipped${NC}"
    echo ""
    
    if [[ $failed -gt 0 ]]; then
        print_error "部分测试失败"
        return 1
    fi
    
    if [[ $passed -eq 0 ]]; then
        print_error "没有可用的 Python 版本"
        return 1
    fi
    
    print_success "所有测试通过！"
    return 0
}

main "$@"
