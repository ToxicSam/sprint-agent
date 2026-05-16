#!/bin/bash
set -e

echo "🚀 Sprint Agent 一键部署脚本"
echo "=============================="

# 检查依赖
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 未检测到 $1，请先安装"
        return 1
    fi
    echo "✅ $1 已安装"
    return 0
}

echo ""
echo "🔍 检查依赖..."
check_dependency docker || exit 1
check_dependency docker-compose || exit 1

# 获取数据目录
DATA_DIR="${DATA_DIR:-./data}"

echo ""
echo "📁 数据目录: $DATA_DIR"
mkdir -p "$DATA_DIR"/{active,sprints,story_pool,retro,assessments}

# 检查是否需要初始化数据
if [ ! -f "$DATA_DIR/active/active_sprint.json" ]; then
    echo ""
    echo "📝 未检测到 Sprint 数据，需要初始化"
    echo ""
    echo "请选择操作:"
    echo "  1) 创建新 Sprint"
    echo "  2) 从现有 JSON 文件导入"
    echo "  3) 稍后手动配置"
    echo ""
    read -p "请选择 [1/2/3]: " choice

    case $choice in
        1)
            read -p "Sprint 名称 (如: 5.12-5.23): " sprint_name
            read -p "开始日期 (YYYY-MM-DD): " start_date
            read -p "结束日期 (YYYY-MM-DD): " end_date
            read -p "工作日数 [10]: " workdays
            workdays=${workdays:-10}

            cat > "$DATA_DIR/config.json" <<EOF
{
  "sm_id": "admin",
  "initialized": true
}
EOF
            echo "✅ 配置已创建，Sprint 将在启动后通过 API 创建"
            ;;
        2)
            read -p "JSON 文件路径: " json_path
            if [ -f "$json_path" ]; then
                cp "$json_path" "$DATA_DIR/active/active_sprint.json"
                echo "✅ 数据已导入"
            else
                echo "❌ 文件不存在: $json_path"
                exit 1
            fi
            ;;
        3)
            echo "⏭️ 跳过初始化，启动后通过 API 或 CLI 配置"
            ;;
    esac
fi

# 构建并启动
echo ""
echo "🏗️ 构建 Docker 镜像..."
docker-compose build

echo ""
echo "▶️ 启动服务..."
docker-compose up -d

# 等待服务就绪
echo ""
echo "⏳ 等待服务就绪..."
for i in {1..30}; do
    if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        echo ""
        echo "✅ Sprint Agent 已启动！"
        echo ""
        echo "📊 看板地址: http://localhost:8080"
        echo "📡 API 地址: http://localhost:8080/api"
        echo "❤️  健康检查: http://localhost:8080/api/health"
        echo ""
        echo "常用命令:"
        echo "  查看日志: docker-compose logs -f"
        echo "  停止服务: docker-compose down"
        echo "  重启服务: docker-compose restart"
        echo ""
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "⚠️ 服务启动可能遇到问题，请查看日志:"
echo "  docker-compose logs"
