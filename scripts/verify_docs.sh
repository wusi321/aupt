#!/usr/bin/env bash
set -euo pipefail

# 文档链接验证脚本

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

print_warning() {
    echo -e "${YELLOW}[!]${NC} $*"
}

# 检查文件是否存在
check_file() {
    local file="$1"
    if [[ -f "$file" ]]; then
        print_success "文件存在: $file"
        return 0
    else
        print_error "文件不存在: $file"
        return 1
    fi
}

# 检查目录是否存在
check_dir() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        print_success "目录存在: $dir"
        return 0
    else
        print_error "目录不存在: $dir"
        return 1
    fi
}

# 主函数
main() {
    print_header "AUPT 文档结构验证"
    
    local errors=0
    
    # 检查主 README
    print_info "检查主 README.md..."
    if ! check_file "README.md"; then
        ((errors++))
    fi
    echo ""
    
    # 检查 markdown 目录
    print_info "检查 markdown 目录..."
    if ! check_dir "markdown"; then
        ((errors++))
        print_error "markdown 目录不存在，无法继续验证"
        exit 1
    fi
    echo ""
    
    # 检查 markdown 目录中的文件
    print_info "检查 markdown 目录中的文档..."
    local docs=(
        "markdown/README.md"
        "markdown/QUICK_START.md"
        "markdown/QUICK_REFERENCE.md"
        "markdown/COMPATIBILITY.md"
        "markdown/COMPATIBILITY_SUMMARY.md"
        "markdown/PYTHON_COMPAT_REPORT.md"
        "markdown/RESTRICTED_ENV.md"
        "markdown/BUGFIX.md"
        "markdown/SOLUTION_SUMMARY.md"
        "markdown/CHANGELOG.md"
        "markdown/aupt.md"
    )
    
    for doc in "${docs[@]}"; do
        if ! check_file "$doc"; then
            ((errors++))
        fi
    done
    echo ""
    
    # 检查脚本目录
    print_info "检查 scripts 目录..."
    if ! check_dir "scripts"; then
        ((errors++))
    fi
    echo ""
    
    # 检查脚本文件
    print_info "检查脚本文件..."
    local scripts=(
        "scripts/install.sh"
        "scripts/install_compat.sh"
        "scripts/test_compatibility.sh"
        "scripts/uninstall.sh"
        "scripts/manual_mirror_switch.sh"
    )
    
    for script in "${scripts[@]}"; do
        if ! check_file "$script"; then
            ((errors++))
        fi
    done
    echo ""
    
    # 检查链接
    print_info "检查 README.md 中的链接..."
    local readme_links=(
        "markdown/QUICK_START.md"
        "markdown/QUICK_REFERENCE.md"
        "markdown/COMPATIBILITY.md"
        "markdown/RESTRICTED_ENV.md"
        "markdown/CHANGELOG.md"
    )
    
    for link in "${readme_links[@]}"; do
        if grep -q "$link" README.md; then
            print_success "链接存在: $link"
        else
            print_warning "链接可能缺失: $link"
        fi
    done
    echo ""
    
    # 统计结果
    print_header "验证结果"
    
    if [[ $errors -eq 0 ]]; then
        print_success "所有检查通过！文档结构正确。"
        return 0
    else
        print_error "发现 $errors 个错误"
        return 1
    fi
}

main "$@"
