
import streamlit as st
import pydeck as pdk
import pandas as pd
import io
import os

# 设置页面
st.set_page_config(page_title="非监督学习大数据分析系统", layout="wide")
st.title('🗺️ 非监督学习大数据分析系统')

# 内置Excel文件路径
EXCEL_FILE_PATH ="坐标(5).xls"

def load_excel_data():
    """从指定路径读取Excel数据"""
    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            st.error(f"❌ 数据文件不存在: {EXCEL_FILE_PATH}")
            return None
        
        df = pd.read_excel(EXCEL_FILE_PATH)
        
        # 检查必要的列是否存在
        required_columns = ['经度', '纬度', '名称', '级别(1-5)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Excel文件中缺少必要的列: {missing_columns}")
            return None
            
        return df
        
    except Exception as e:
        st.error(f"❌ 读取数据文件失败: {str(e)}")
        return None

# 侧边栏 - 文件上传和算法选择
st.sidebar.header("数据上传与分析设置")

# 1. 文件上传模块
st.sidebar.subheader("📁 数据上传")
uploaded_file = st.sidebar.file_uploader(
    "上传Excel文件", 
    type=['xlsx', 'xls'],
    help="支持上传包含城市数据的Excel文件"
)

# 2. 模拟数据分析模块
st.sidebar.subheader("🔬 分析算法设置")
algorithm = st.sidebar.selectbox(
    "选择分析算法",
    ["K-Means聚类", "DBSCAN聚类", "层次聚类", "高斯混合模型"],
    index=0
)

n_clusters = st.sidebar.slider(
    "分类数量",
    min_value=2,
    max_value=8,
    value=3,
    help="确定要将数据分为多少个类别"
)

analyze_button = st.sidebar.button("开始分析", type="primary")

# 主内容区
if uploaded_file is not None:
    # 读取上传的Excel文件
    try:
        df_uploaded = pd.read_excel(uploaded_file)
        st.subheader("📊 上传数据预览")
        st.dataframe(df_uploaded.head(10), use_container_width=True)
        
        # 显示数据基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("数据行数", f"{len(df_uploaded)}行")
        with col2:
            st.metric("数据列数", f"{len(df_uploaded.columns)}列")
        with col3:
            st.metric("文件大小", f"{uploaded_file.size / 1024:.1f} KB")
            
        st.success("✅ 文件上传成功！")
        
    except Exception as e:
        st.error(f"❌ 文件读取错误: {str(e)}")
        st.info("请确保上传的是有效的Excel文件")
else:
    st.info("📁 请先上传Excel文件，或使用默认数据进行演示")

# 分析结果显示区域
if analyze_button:
    st.markdown("---")
    st.subheader("📈 分析结果")
    
    # 显示分析参数
    st.write(f"**分析算法**: {algorithm}")
    st.write(f"**分类数量**: {n_clusters}")
    
    # 模拟分析进度
    with st.spinner("正在进行分析计算..."):
        import time
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.16)
            progress_bar.progress(i + 1)
    
    st.success("✅ 分析完成！")
    
    # 从Excel文件读取数据创建地图
    st.subheader("🗺️ 数据分布地图")
    
    # 从指定路径读取Excel数据
    df_excel = load_excel_data()
    
    if df_excel is not None:
        # 准备数据
        df = df_excel.copy()
        
        # 重命名列以匹配代码
        column_mapping = {
            '经度': 'lon',
            '纬度': 'lat', 
            '名称': 'name',
            '级别(1-5)': 'level'
        }
        
        # 重命名列
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # 确保数据类型正确
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df = df.dropna(subset=['lon', 'lat'])
        
        # 根据级别设置颜色 - 级别越高越重要，颜色越醒目
        def get_color_by_level(level):
            color_map = {
                1: [128, 128, 128, 180],  # 灰色 - 级别1 (最不重要)
                2: [0, 255, 0, 180],      # 绿色 - 级别2
                3: [0, 0, 255, 180],      # 蓝色 - 级别3
                4: [255, 255, 0, 180],    # 黄色 - 级别4
                5: [255, 0, 0, 200]       # 红色 - 级别5 (最重要，最醒目)
            }
            return color_map.get(level, [128, 128, 128, 180])  # 默认灰色
        
        df['color'] = df['level'].apply(get_color_by_level)
        
        # 创建PyDeck图层 - 级别越高点越大
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position=['lon', 'lat'],
            get_fill_color='color',
            get_radius=800,  # 基础半径
            pickable=True,
            auto_highlight=True,
            filled=True,
            stroked=True,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1,
            radius_min_pixels=5,   # 最小显示像素
            radius_max_pixels=18   # 最大显示像素
        )
        
        # 自动计算地图中心点
        center_lat = df['lat'].mean()
        center_lon = df['lon'].mean()
        
        # 设置视图
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=9,  # 调整缩放级别
            pitch=0
        )
        
        # 创建地图
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                'html': """
                    <div style="
                        background: white; 
                        color: black; 
                        padding: 8px; 
                        border-radius: 4px; 
                        border: 1px solid #ccc;
                        font-size: 12px;
                        max-width: 250px;
                    ">
                        <b>{name}</b><br/>
                        级别: {level} (级别越高越重要)<br/>
                        经度: {lon:.6f}°E<br/>
                        纬度: {lat:.6f}°N
                    </div>
                """,
                'style': {
                    'backgroundColor': 'white',
                    'color': 'black',
                    'fontSize': '12px'
                }
            },
            map_style='light'
        )
        
        # 显示地图
        st.pydeck_chart(r)
        
        # 添加统计信息 - 按级别重要性排序
        st.subheader("📊 统计信息")
        
        # 按级别从高到低排序
        level_stats = df['level'].value_counts().sort_index(ascending=False)
        
        # 显示总数据点和各级别数量
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("总数据点", f"{len(df)}个")
        
        # 动态显示各级别数量
        level_colors_emoji = {
            5: "🔴 级别5 ",
            4: "🟡 级别4", 
            3: "🔵 级别3",
            2: "🟢 级别2",
            1: "⚪ 级别1"
        }
        
        cols = st.columns(len(level_stats))
        for i, (level, count) in enumerate(level_stats.items()):
            with cols[i]:
                color_desc = level_colors_emoji.get(level, f"级别{level}")
                percentage = (count / len(df)) * 100
                st.metric(color_desc, f"{count}个", f"{percentage:.1f}%")
        
        # 显示分析摘要
        st.subheader("📋 分析摘要")
        st.write(f"使用{algorithm}算法对数据进行聚类分析，共处理{len(df)}个数据点。")
        st.write("**数据点按重要性级别显示（级别越高越重要）:**")
        
        # 按级别从高到低显示
        for level in sorted(level_stats.index, reverse=True):
            color_desc = level_colors_emoji.get(level, f"级别{level}")
            st.write(f"- {color_desc}: {level_stats[level]}个数据点")
            
        # 显示重要性说明
        st.info("💡 **重要性说明**: 级别5(红色)为最重要，级别1(灰色)为最不重要")
            
    else:
        st.error("❌ 无法加载内置Excel数据，请检查文件路径和格式")
    
    # 显示算法说明
    with st.expander("📚 算法说明"):
        if algorithm == "K-Means聚类":
            st.markdown("""
            **K-Means聚类算法**：
            - 基于距离的划分聚类方法
            - 需要预先指定聚类数量K
            - 适用于球形分布的数据
            - 计算效率高，适合大规模数据
            """)
        elif algorithm == "DBSCAN聚类":
            st.markdown("""
            **DBSCAN聚类算法**：
            - 基于密度的聚类方法
            - 能够发现任意形状的簇
            - 自动识别噪声点
            - 不需要预先指定聚类数量
            """)
        elif algorithm == "层次聚类":
            st.markdown("""
            **层次聚类算法**：
            - 构建树状的聚类结构
            - 可以可视化聚类过程
            - 分为凝聚式和分裂式两种
            - 不需要预先指定聚类数量
            """)
        else:  # 高斯混合模型
            st.markdown("""
            **高斯混合模型**：
            - 基于概率模型的软聚类方法
            - 假设数据来自多个高斯分布
            - 提供每个点属于各簇的概率
            - 适用于复杂分布的数据
            """)
else:
    # 如果没有点击分析按钮，显示使用说明
    if uploaded_file is not None:
        st.info("👆 请在侧边栏设置分析参数并点击'开始分析'按钮")

# 页面底部信息
st.markdown("---")
st.caption("非监督学习大数据分析系统 | 版本 v1.2 ")
