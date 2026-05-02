import streamlit as st
import pandas as pd

st.set_page_config(page_title="반려견 영양 연구소 계산기 v3.4", layout="wide")
st.title("🐶 반려견 영양 연구소 [AAFCO 생식 계산기 v3.4]")
st.info("💡 전문가용 맞춤형 영양 컨설팅 & 레시피 분석 시스템")

# --- [1. AAFCO 기준] ---
aafco_standards = {
    "단백질(g)": {"min": 45, "max": None},
    "지방(g)": {"min": 13.8, "max": None},
    "칼슘(mg)": {"min": 1250, "max": 6250},
    "인(mg)": {"min": 1000, "max": 4000},
    "철(mg)": {"min": 10, "max": None},
    "아연(mg)": {"min": 20, "max": None},
    "구리(mg)": {"min": 1.83, "max": None},
    "망간(mg)": {"min": 1.25, "max": None},
    "비타민A(IU)": {"min": 1250, "max": None},
    "비타민D(IU)": {"min": 125, "max": None},
    "비타민E(IU)": {"min": 12.5, "max": None},
    "나트륨(mg)": {"min": 200, "max": None},
}

# --- [2. 데이터베이스] ---
db_data = [
    # 뼈류
    {"재료명": "닭발 (뼈 60%)", "category": "bone", "bone_pct": 0.60, "칼로리": 215, "단백질": 19.0, "지방": 14.6, "칼슘": 2500, "인": 1500, "철": 2.0, "아연": 1.5, "구리": 0.1, "망간": 0.05, "비타민A": 30, "비타민D": 0, "비타민E": 0, "나트륨": 67},
    {"재료명": "닭목뼈 (뼈 36%)", "category": "bone", "bone_pct": 0.36, "칼로리": 154, "단백질": 17.6, "지방": 8.78, "칼슘": 1500, "인": 900, "철": 2.06, "아연": 2.68, "구리": 0.1, "망간": 0.03, "비타민A": 146, "비타민D": 0, "비타민E": 0, "나트륨": 81},
    {"재료명": "닭날개 (뼈 45%)", "category": "bone", "bone_pct": 0.45, "칼로리": 203, "단백질": 18.0, "지방": 14.0, "칼슘": 1875, "인": 1125, "철": 1.0, "아연": 1.0, "구리": 0.1, "망간": 0.02, "비타민A": 40, "비타민D": 0, "비타민E": 0.3, "나트륨": 70},
    {"재료명": "닭북채 (뼈 30%)", "category": "bone", "bone_pct": 0.30, "칼로리": 120, "단백질": 18.0, "지방": 4.0, "칼슘": 1250, "인": 750, "철": 0.8, "아연": 1.5, "구리": 0.1, "망간": 0.02, "비타민A": 20, "비타민D": 0, "비타민E": 0.2, "나트륨": 80},
    {"재료명": "전체 칠면조 (뼈 21%)", "category": "bone", "bone_pct": 0.21, "칼로리": 160, "단백질": 20.0, "지방": 8.0, "칼슘": 875, "인": 525, "철": 1.5, "아연": 2.0, "구리": 0.1, "망간": 0.02, "비타민A": 50, "비타민D": 0, "비타민E": 0, "나트륨": 60},
    {"재료명": "칠면조 목뼈 (뼈 42%)", "category": "bone", "bone_pct": 0.42, "칼로리": 225, "단백질": 30.0, "지방": 11.0, "칼슘": 1750, "인": 1050, "철": 2.0, "아연": 3.0, "구리": 0.2, "망간": 0.04, "비타민A": 40, "비타민D": 0, "비타민E": 0, "나트륨": 90},
    {"재료명": "칠면조 날개 (뼈 37%)", "category": "bone", "bone_pct": 0.37, "칼로리": 200, "단백질": 18.0, "지방": 13.0, "칼슘": 1540, "인": 925, "철": 1.5, "아연": 1.5, "구리": 0.1, "망간": 0.02, "비타민A": 30, "비타민D": 0, "비타민E": 0, "나트륨": 80},
    {"재료명": "전체 오리 (뼈 28%)", "category": "bone", "bone_pct": 0.28, "칼로리": 250, "단백질": 15.0, "지방": 20.0, "칼슘": 1166, "인": 700, "철": 2.5, "아연": 1.8, "구리": 0.2, "망간": 0.03, "비타민A": 60, "비타민D": 0, "비타민E": 0.5, "나트륨": 65},
    {"재료명": "오리 목뼈 (뼈 50%)", "category": "bone", "bone_pct": 0.50, "칼로리": 250, "단백질": 18.0, "지방": 18.0, "칼슘": 2083, "인": 1250, "철": 2.8, "아연": 2.0, "구리": 0.2, "망간": 0.04, "비타민A": 50, "비타민D": 0, "비타민E": 0, "나트륨": 85},
    {"재료명": "오리발 (뼈 60%)", "category": "bone", "bone_pct": 0.60, "칼로리": 253, "단백질": 20.0, "지방": 18.0, "칼슘": 2500, "인": 1500, "철": 2.0, "아연": 1.5, "구리": 0.1, "망간": 0.05, "비타민A": 40, "비타민D": 0, "비타민E": 0, "나트륨": 90},
    {"재료명": "소갈비뼈 (뼈 52%)", "category": "bone", "bone_pct": 0.52, "칼로리": 300, "단백질": 18.0, "지방": 25.0, "칼슘": 2166, "인": 1300, "철": 3.0, "아연": 4.5, "구리": 0.1, "망간": 0.02, "비타민A": 10, "비타민D": 2, "비타민E": 0, "나트륨": 70},
    {"재료명": "소꼬리 (뼈 55%)", "category": "bone", "bone_pct": 0.55, "칼로리": 262, "단백질": 21.0, "지방": 18.0, "칼슘": 2290, "인": 1375, "철": 4.9, "아연": 3.5, "구리": 0.1, "망간": 0.02, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 60},
    {"재료명": "양 갈비뼈 (뼈 27%)", "category": "bone", "bone_pct": 0.27, "칼로리": 355, "단백질": 22.0, "지방": 30.0, "칼슘": 1125, "인": 675, "철": 2.0, "아연": 4.0, "구리": 0.1, "망간": 0.02, "비타민A": 0, "비타민D": 1, "비타민E": 0.1, "나트륨": 76},
    {"재료명": "양 목뼈 (뼈 32%)", "category": "bone", "bone_pct": 0.32, "칼로리": 260, "단백질": 20.0, "지방": 20.0, "칼슘": 1333, "인": 800, "철": 4.0, "아연": 4.2, "구리": 0.2, "망간": 0.02, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 70},
    {"재료명": "전체 메츄리 (뼈 10%)", "category": "bone", "bone_pct": 0.10, "칼로리": 200, "단백질": 20.0, "지방": 12.0, "칼슘": 416, "인": 250, "철": 4.0, "아연": 2.5, "구리": 0.5, "망간": 0.02, "비타민A": 50, "비타민D": 10, "비타민E": 1.0, "나트륨": 50},
    # 내장
    {"재료명": "소간 (Beef Liver)", "category": "organ", "bone_pct": 0, "칼로리": 135, "단백질": 20.4, "지방": 3.63, "칼슘": 5, "인": 387, "철": 4.9, "아연": 4.0, "구리": 9.76, "망간": 0.31, "비타민A": 16900, "비타민D": 49, "비타민E": 0.38, "나트륨": 69},
    {"재료명": "소심장 (Beef Heart)", "category": "organ", "bone_pct": 0, "칼로리": 112, "단백질": 18.5, "지방": 3.4, "칼슘": 4, "인": 209, "철": 4.38, "아연": 1.51, "구리": 0.373, "망간": 0.034, "비타민A": 34, "비타민D": 6, "비타민E": 1.22, "나트륨": 86},
    {"재료명": "소폐 (Beef Lung)", "category": "organ", "bone_pct": 0, "칼로리": 92, "단백질": 16.2, "지방": 2.5, "칼슘": 10, "인": 224, "철": 7.95, "아연": 1.61, "구리": 0.26, "망간": 0.019, "비타민A": 46, "비타민D": 0, "비타민E": 0, "나트륨": 198},
    {"재료명": "그린트라이프 (Green Tripe)", "category": "organ", "bone_pct": 0, "칼로리": 85, "단백질": 14.9, "지방": 1.98, "칼슘": 112, "인": 159, "철": 4.44, "아연": 1.72, "구리": 0.094, "망간": 4.06, "비타민A": 20, "비타민D": 8, "비타민E": 0.45, "나트륨": 81},
    # 육류
    {"재료명": "닭가슴살 (Chicken Breast)", "category": "meat", "bone_pct": 0, "칼로리": 120, "단백질": 22.5, "지방": 2.62, "칼슘": 5, "인": 213, "철": 0.37, "아연": 0.68, "구리": 0.037, "망간": 0.011, "비타민A": 30, "비타민D": 0, "비타민E": 0.56, "나트륨": 45},
    {"재료명": "소고기 (Beef)", "category": "meat", "bone_pct": 0, "칼로리": 152, "단백질": 20.8, "지방": 7.0, "칼슘": 10, "인": 192, "철": 2.33, "아연": 4.97, "구리": 0.075, "망간": 0.01, "비타민A": 14, "비타민D": 3, "비타민E": 0.17, "나트륨": 66},
    {"재료명": "말고기 (Horse Meat)", "category": "meat", "bone_pct": 0, "칼로리": 133, "단백질": 21.4, "지방": 4.6, "칼슘": 6, "인": 221, "철": 3.82, "아연": 2.9, "구리": 0.144, "망간": 0.019, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 53},
    {"재료명": "사슴고기 (Venison)", "category": "meat", "bone_pct": 0, "칼로리": 116, "단백질": 21.5, "지방": 2.66, "칼슘": 7, "인": 201, "철": 2.92, "아연": 4.2, "구리": 0.14, "망간": 0.014, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 75},
    {"재료명": "정어리 (Sardine)", "category": "meat", "bone_pct": 0, "칼로리": 208, "단백질": 24.6, "지방": 11.4, "칼슘": 382, "인": 490, "철": 2.92, "아연": 1.4, "구리": 0.186, "망간": 0, "비타민A": 30, "비타민D": 4.8, "비타민E": 1.38, "나트륨": 307},
    {"재료명": "계란노른자 (Egg Yolk)", "category": "meat", "bone_pct": 0, "칼로리": 322, "단백질": 15.9, "지방": 26.5, "칼슘": 129, "인": 390, "철": 2.73, "아연": 2.3, "구리": 0.077, "망간": 0.31, "비타민A": 1440, "비타민D": 49, "비타민E": 0.38, "나트륨": 48},
    # veggie / 기타
    {"재료명": "해바라기씨 (Sunflower Seed)", "category": "veggie", "bone_pct": 0, "칼로리": 559, "단백질": 30.2, "지방": 49.0, "칼슘": 46, "인": 1230, "철": 8.82, "아연": 7.81, "구리": 1.34, "망간": 4.54, "비타민A": 3.3, "비타민D": 0, "비타민E": 2.18, "나트륨": 7},
    {"재료명": "굴 (Oyster)", "category": "veggie", "bone_pct": 0, "칼로리": 68, "단백질": 7.67, "지방": 2.68, "칼슘": 49, "인": 151, "철": 7.28, "아연": 98.9, "구리": 4.85, "망간": 0.45, "비타민A": 326, "비타민D": 1, "비타민E": 0.92, "나트륨": 122},
    {"재료명": "블루베리 (Blueberry)", "category": "veggie", "bone_pct": 0, "칼로리": 57, "단백질": 0.74, "지방": 0.33, "칼슘": 6, "인": 12, "철": 0.28, "아연": 0.06, "구리": 1.6, "망간": 0.262, "비타민A": 54, "비타민D": 0, "비타민E": 0.57, "나트륨": 1},
    # 야채 퓨레 9종 (USDA 기준, 100g당)
    {"재료명": "브로콜리 퓨레 (Broccoli)", "category": "veggie", "bone_pct": 0, "칼로리": 34, "단백질": 2.82, "지방": 0.37, "칼슘": 47, "인": 66, "철": 0.73, "아연": 0.41, "구리": 0.049, "망간": 0.21, "비타민A": 623, "비타민D": 0, "비타민E": 0.78, "나트륨": 33},
    {"재료명": "토마토 퓨레 (Tomato)", "category": "veggie", "bone_pct": 0, "칼로리": 18, "단백질": 0.88, "지방": 0.2, "칼슘": 10, "인": 24, "철": 0.27, "아연": 0.17, "구리": 0.059, "망간": 0.114, "비타민A": 833, "비타민D": 0, "비타민E": 0.54, "나트륨": 5},
    {"재료명": "우엉 퓨레 (Burdock Root)", "category": "veggie", "bone_pct": 0, "칼로리": 72, "단백질": 1.53, "지방": 0.15, "칼슘": 41, "인": 51, "철": 0.8, "아연": 0.33, "구리": 0.08, "망간": 0.23, "비타민A": 0, "비타민D": 0, "비타민E": 0.4, "나트륨": 5},
    {"재료명": "청경채 퓨레 (Bok Choy)", "category": "veggie", "bone_pct": 0, "칼로리": 13, "단백질": 1.5, "지방": 0.2, "칼슘": 105, "인": 37, "철": 0.8, "아연": 0.19, "구리": 0.021, "망간": 0.159, "비타민A": 4468, "비타민D": 0, "비타민E": 0.09, "나트륨": 65},
    {"재료명": "단호박 퓨레 (Kabocha)", "category": "veggie", "bone_pct": 0, "칼로리": 34, "단백질": 1.0, "지방": 0.1, "칼슘": 20, "인": 30, "철": 0.4, "아연": 0.15, "구리": 0.07, "망간": 0.15, "비타민A": 1370, "비타민D": 0, "비타민E": 0.3, "나트륨": 3},
    {"재료명": "본브로스 소뼈 (Bone Broth)", "category": "veggie", "bone_pct": 0, "칼로리": 18, "단백질": 4.0, "지방": 0.0, "칼슘": 5, "인": 10, "철": 0.2, "아연": 0.1, "구리": 0.02, "망간": 0, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 20},
    {"재료명": "파프리카 퓨레 (Paprika)", "category": "veggie", "bone_pct": 0, "칼로리": 31, "단백질": 1.0, "지방": 0.3, "칼슘": 7, "인": 26, "철": 0.43, "아연": 0.25, "구리": 0.017, "망간": 0.11, "비타민A": 3131, "비타민D": 0, "비타민E": 1.58, "나트륨": 4},
    {"재료명": "샐러리 퓨레 (Celery)", "category": "veggie", "bone_pct": 0, "칼로리": 16, "단백질": 0.69, "지방": 0.17, "칼슘": 40, "인": 24, "철": 0.2, "아연": 0.13, "구리": 0.04, "망간": 0.1, "비타민A": 449, "비타민D": 0, "비타민E": 0.27, "나트륨": 80},
    {"재료명": "당근 퓨레 (Carrot)", "category": "veggie", "bone_pct": 0, "칼로리": 41, "단백질": 0.93, "지방": 0.24, "칼슘": 33, "인": 35, "철": 0.3, "아연": 0.24, "구리": 0.045, "망간": 0.143, "비타민A": 16706, "비타민D": 0, "비타민E": 0.66, "나트륨": 69},
]
food_df = pd.DataFrame(db_data)

# --- [3. 메인 화면] ---
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("🐶 강아지 정보")
    weight = st.number_input("몸무게 (kg)", 0.1, 60.0, 3.0, step=0.1)

    der_options = {
        "1.0: 체중 감량이 필요한 성견 (다이어트)": 1.0,
        "1.2: 중성화 성견 · 매우 낮은 활동량": 1.2,
        "1.4: 중성화 성견 · 낮은 활동량 / 비만 경향": 1.4,
        "1.6: 중성화 성견 · 보통 활동량 (기본값)": 1.6,
        "1.8: 비중성화 성견 · 보통 활동량": 1.8,
        "2.0: 매우 활동적인 성견 / 야외 훈련량 많음": 2.0,
        "3.0: 성장기 강아지 (퍼피)": 3.0,
    }

    selected_label = st.selectbox(
        "강아지의 현재 상태를 선택해 주세요!",
        options=list(der_options.keys()),
        index=3,
    )

    activity = der_options[selected_label]
    rer = 70 * (weight ** 0.75)
    der = rer * activity
    st.metric(label="하루 목표 칼로리 (DER)", value=f"{der:.1f} kcal")

with col2:
    st.subheader("🥩 냉장고 털기 (재료 선택)")
    all_foods = food_df["재료명"].tolist()
    bone_options = [f for f in all_foods if "뼈" in f or "발" in f or "날개" in f or "전체" in f]
    default_selections = [bone_options[0]] if bone_options else []
    selected = st.multiselect("재료를 고르세요:", all_foods, default=default_selections)

amounts = {}
if selected:
    cols = st.columns(3)
    for i, f in enumerate(selected):
        with cols[i % 3]:
            amounts[f] = st.number_input(f"{f} (g)", 0, 1000, 50, step=5)

# --- [4. 계산 및 판정] ---
if selected:
    st.divider()

    total_grams = sum(amounts.values())
    mass_breakdown = {"actual_bone": 0, "muscle_meat": 0, "organ": 0, "veggie": 0}
    total_stats = {k: 0 for k in aafco_standards.keys()}
    total_kcal = 0
    recipe_save_list = []

    for f in selected:
        grams = amounts[f]
        if grams > 0:
            recipe_save_list.append({"재료명": f, "급여량(g)": grams})
            row = food_df[food_df["재료명"] == f].iloc[0]
            ratio = grams / 100
            total_kcal += row["칼로리"] * ratio
            for nutri in aafco_standards.keys():
                col_name = nutri.split("(")[0]
                if col_name in row:
                    total_stats[nutri] += row[col_name] * ratio

            cat, b_pct = row["category"], row["bone_pct"]
            if cat == "bone":
                mass_breakdown["actual_bone"] += grams * b_pct
                mass_breakdown["muscle_meat"] += grams * (1 - b_pct)
            elif cat == "meat":
                mass_breakdown["muscle_meat"] += grams
            elif cat == "organ":
                mass_breakdown["organ"] += grams
            else:
                mass_breakdown["veggie"] += grams

    # --- 레시피 저장 ---
    st.subheader("💾 레시피 저장 및 고객 발송")
    c_btn1, c_btn2 = st.columns(2)

    with c_btn1:
        if recipe_save_list:
            df_recipe = pd.DataFrame(recipe_save_list)
            csv = df_recipe.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 엑셀(CSV) 파일로 저장하기",
                data=csv,
                file_name=f"영양레시피_{weight}kg.csv",
                mime="text/csv",
            )
    with c_btn2:
        with st.expander("🖨️ PDF로 저장해서 고객에게 보내려면?"):
            st.write("1. Ctrl + P (맥북은 Command + P) 를 누르세요.")
            st.write("2. 인쇄 설정 창에서 대상(프린터)를 PDF로 저장 으로 바꾸세요.")
            st.write("3. 저장 버튼을 누르면 리포트가 만들어집니다.")

    st.divider()

    # --- 분석 결과 ---
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("⚖️ 식단 비율")
        st.metric("총 급여량", f"{total_grams:.1f} g")

        if total_grams > 0:
            pct_bone   = (mass_breakdown["actual_bone"]  / total_grams) * 100
            pct_meat   = (mass_breakdown["muscle_meat"]  / total_grams) * 100
            pct_organ  = (mass_breakdown["organ"]        / total_grams) * 100
            pct_veggie = (mass_breakdown["veggie"]       / total_grams) * 100

            st.write(f"뼈 ({pct_bone:.1f}%) | 목표 12%")
            st.progress(min(pct_bone / 20, 1.0))
            st.write(f"살코기 ({pct_meat:.1f}%) | 목표 60~70%")
            st.progress(min(pct_meat / 100, 1.0))
            st.write(f"내장 ({pct_organ:.1f}%) | 목표 10~25%")
            st.progress(min(pct_organ / 40, 1.0))
            st.write(f"야채 ({pct_veggie:.1f}%) | 목표 5~10%")
            st.progress(min(pct_veggie / 20, 1.0))

    with c2:
        st.subheader("📊 AAFCO 영양 분석")
        if total_kcal > 0:
            kcal_ratio = (total_kcal / der) * 100
            st.progress(min(kcal_ratio / 100, 1.0), text=f"칼로리 충족률: {kcal_ratio:.1f}%")

            res_data = []
            for nutri, std in aafco_standards.items():
                val_1000 = (total_stats[nutri] / total_kcal) * 1000
                min_v, max_v = std["min"], std["max"]
                status = "적합"
                if val_1000 < min_v:
                    status = f"부족 (최소 {min_v})"
                elif max_v and val_1000 > max_v:
                    status = f"과잉 (최대 {max_v})"
                res_data.append({
                    "영양소": nutri,
                    "현재(1000kcal당)": f"{val_1000:.2f}",
                    "AAFCO 기준": f"{min_v}~{max_v if max_v else ''}",
                    "판정": status,
                })

            res_df = pd.DataFrame(res_data)

            def color_status(val):
                if "적합" in str(val):
                    return "color: green; font-weight: bold"
                elif "부족" in str(val):
                    return "color: red; font-weight: bold"
                else:
                    return "color: orange; font-weight: bold"

            st.dataframe(res_df.style.map(color_status, subset=["판정"]), use_container_width=True)

            ca = total_stats["칼슘(mg)"]
            p  = total_stats["인(mg)"]
            if p > 0:
                st.info(f"Ca:P 비율 = {ca/p:.2f} : 1  (권장 1.1~2 : 1)")

else:
    st.info("재료를 선택하면 분석 결과가 나타납니다.")
