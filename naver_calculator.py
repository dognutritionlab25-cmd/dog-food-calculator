import streamlit as st
import pandas as pd

st.set_page_config(page_title="반려견 영양 연구소 계산기 v4.0", layout="wide")
st.title("🐶 반려견 영양 연구소 [AAFCO 계산기 v4.0]")
st.info("💡 v4.0: 신규 재료 추가 (고등어·케일·아스파라거스 등) + 화식 계산 기능 추가")

# --- [1. AAFCO 기준] ---
aafco_standards = {
    "단백질(g)": {"min": 45,   "max": None},
    "지방(g)":   {"min": 13.8, "max": None},
    "칼슘(mg)":  {"min": 1250, "max": 6250},
    "인(mg)":    {"min": 1000, "max": 4000},
    "철(mg)":    {"min": 10,   "max": None},
    "아연(mg)":  {"min": 20,   "max": None},
    "구리(mg)":  {"min": 1.83, "max": None},
    "망간(mg)":  {"min": 1.25, "max": None},
    "비타민A(IU)": {"min": 1250, "max": None},
    "비타민D(IU)": {"min": 125,  "max": None},
    "비타민E(IU)": {"min": 12.5, "max": None},
    "나트륨(mg)": {"min": 200,  "max": None},
    "요오드(mcg)": {"min": 220,  "max": 1400},  # NRC 2006 권장 220, 안전상한 1400 (1000kcal당)
}

# --- [2. 데이터베이스] ---
# category 분류:
#   bone   = 뼈고기 (칼슘 공급, 뼈 비율 계산)
#   meat   = 근육고기 (심장·폐·모래주머니·생식기 포함 - 근육성 기관)
#   organ  = 분비성 내장 (간·신장·비장·췌장 등 - 진짜 내장)
#   veggie = 채소·과일·기타

db_data = [
    # ── 뼈류 ──
    # ── 뼈고기 (bone) ─────────────────────────────────────────────────────────
    # 칼슘 출처: Segal=Monica Segal K9 Kitchen 실측값, est=bone_pct×4166 추정값
    # 인(P): Segal 실측값 없음 → 뼈 Ca:P≈2:1 기준으로 칼슘×0.5 추정
    # 요오드: 해조류 아니므로 0
    {"재료명":"닭발 (뼈 60%)",        "category":"bone","bone_pct":0.60,"칼슘":1839,"인":920,"칼슘출처":"est_poultry_avg30.6", "칼로리":215,"단백질":19.0,"지방":14.6,"철":2.0, "아연":1.5, "구리":0.1,  "망간":0.05,"비타민A":30,  "비타민D":0,  "비타민E":0,   "나트륨":67, "요오드(mcg)":0},
    {"재료명":"닭목뼈 (뼈 36%)",      "category":"bone","bone_pct":0.36,"칼슘":1150,"인":575, "칼슘출처":"Segal","칼로리":154,"단백질":17.6,"지방":8.78,"철":2.06,"아연":2.68,"구리":0.1,  "망간":0.03,"비타민A":146, "비타민D":0,  "비타민E":0,   "나트륨":81, "요오드(mcg)":0},
    {"재료명":"닭날개 (뼈 45%)",      "category":"bone","bone_pct":0.45,"칼슘":920, "인":460, "칼슘출처":"Segal","칼로리":203,"단백질":18.0,"지방":14.0,"철":1.0, "아연":1.0, "구리":0.1,  "망간":0.02,"비타민A":40,  "비타민D":0,  "비타민E":0.3, "나트륨":70, "요오드(mcg)":0},
    {"재료명":"닭북채 (뼈 30%)",      "category":"bone","bone_pct":0.30,"칼슘":880, "인":440, "칼슘출처":"Segal","칼로리":120,"단백질":18.0,"지방":4.0, "철":0.8, "아연":1.5, "구리":0.1,  "망간":0.02,"비타민A":20,  "비타민D":0,  "비타민E":0.2, "나트륨":80, "요오드(mcg)":0},
    {"재료명":"전체 칠면조 (뼈 21%)", "category":"bone","bone_pct":0.21,"칼슘":644, "인":322, "칼슘출처":"est_poultry_avg30.6", "칼로리":160,"단백질":20.0,"지방":8.0, "철":1.5, "아연":2.0, "구리":0.1,  "망간":0.02,"비타민A":50,  "비타민D":0,  "비타민E":0,   "나트륨":60, "요오드(mcg)":0},
    {"재료명":"칠면조 목뼈 (뼈 42%)", "category":"bone","bone_pct":0.42,"칼슘":1840,"인":920, "칼슘출처":"Segal","칼로리":225,"단백질":30.0,"지방":11.0,"철":2.0, "아연":3.0, "구리":0.2,  "망간":0.04,"비타민A":40,  "비타민D":0,  "비타민E":0,   "나트륨":90, "요오드(mcg)":0},
    {"재료명":"칠면조 날개 (뼈 37%)", "category":"bone","bone_pct":0.37,"칼슘":1134,"인":567,"칼슘출처":"est_poultry_avg30.6","칼로리":200,"단백질":18.0,"지방":13.0,"철":1.5, "아연":1.5, "구리":0.1,  "망간":0.02,"비타민A":30,  "비타민D":0,  "비타민E":0,   "나트륨":80, "요오드(mcg)":0},
    {"재료명":"전체 오리 (뼈 28%)",   "category":"bone","bone_pct":0.28,"칼슘":870, "인":435, "칼슘출처":"Segal","칼로리":250,"단백질":15.0,"지방":20.0,"철":2.5, "아연":1.8, "구리":0.2,  "망간":0.03,"비타민A":60,  "비타민D":0,  "비타민E":0.5, "나트륨":65, "요오드(mcg)":0},
    {"재료명":"오리 목뼈 (뼈 50%)",   "category":"bone","bone_pct":0.50,"칼슘":1532,"인":766,"칼슘출처":"est_poultry_avg30.6", "칼로리":250,"단백질":18.0,"지방":18.0,"철":2.8, "아연":2.0, "구리":0.2,  "망간":0.04,"비타민A":50,  "비타민D":0,  "비타민E":0,   "나트륨":85, "요오드(mcg)":0},
    {"재료명":"오리발 (뼈 60%)",      "category":"bone","bone_pct":0.60,"칼슘":1839,"인":920,"칼슘출처":"est_poultry_avg30.6", "칼로리":253,"단백질":20.0,"지방":18.0,"철":2.0, "아연":1.5, "구리":0.1,  "망간":0.05,"비타민A":40,  "비타민D":0,  "비타민E":0,   "나트륨":90, "요오드(mcg)":0},
    {"재료명":"소갈비뼈 (뼈 52%)",    "category":"bone","bone_pct":0.52,"칼슘":2621,"인":1310,"칼슘출처":"est_mammal_avg50.4", "칼로리":300,"단백질":18.0,"지방":25.0,"철":3.0, "아연":4.5, "구리":0.1,  "망간":0.02,"비타민A":10,  "비타민D":2,  "비타민E":0,   "나트륨":70, "요오드(mcg)":0},
    {"재료명":"소꼬리 (뼈 55%)",      "category":"bone","bone_pct":0.55,"칼슘":2772,"인":1386,"칼슘출처":"est_mammal_avg50.4", "칼로리":262,"단백질":21.0,"지방":18.0,"철":4.9, "아연":3.5, "구리":0.1,  "망간":0.02,"비타민A":0,   "비타민D":0,  "비타민E":0,   "나트륨":60, "요오드(mcg)":0},
    {"재료명":"양 갈비뼈 (뼈 27%)",   "category":"bone","bone_pct":0.27,"칼슘":1360,"인":680, "칼슘출처":"Segal","칼로리":355,"단백질":22.0,"지방":30.0,"철":2.0, "아연":4.0, "구리":0.1,  "망간":0.02,"비타민A":0,   "비타민D":1,  "비타민E":0.1, "나트륨":76, "요오드(mcg)":0},
    {"재료명":"양 목뼈 (뼈 32%)",     "category":"bone","bone_pct":0.32,"칼슘":1613,"인":806, "칼슘출처":"est_mammal_avg50.4", "칼로리":260,"단백질":20.0,"지방":20.0,"철":4.0, "아연":4.2, "구리":0.2,  "망간":0.02,"비타민A":0,   "비타민D":0,  "비타민E":0,   "나트륨":70, "요오드(mcg)":0},
    {"재료명":"전체 메츄리 (뼈 10%)", "category":"bone","bone_pct":0.10,"칼슘":306, "인":153, "칼슘출처":"est_poultry_avg30.6", "칼로리":200,"단백질":20.0,"지방":12.0,"철":4.0, "아연":2.5, "구리":0.5,  "망간":0.02,"비타민A":50,  "비타민D":10, "비타민E":1.0, "나트륨":50, "요오드(mcg)":0},

    # ── 분비성 내장 (organ) ──
    {"재료명":"소간 (Beef Liver)",          "category":"organ","bone_pct":0,"칼로리":135,"단백질":20.4,"지방":3.63,"칼슘":5,  "인":387,"철":4.9,  "아연":4.0, "구리":9.76, "망간":0.31, "비타민A":16900,"비타민D":49,"비타민E":0.38,"나트륨":69, "요오드(mcg)":0},
    {"재료명":"소신장 (Beef Kidney)",        "category":"organ","bone_pct":0,"칼로리":97, "단백질":17.4,"지방":2.82,"칼슘":13, "인":257,"철":4.37, "아연":1.93,"구리":0.436,"망간":0.138,"비타민A":1166, "비타민D":49,"비타민E":0.29,"나트륨":182, "요오드(mcg)":0},
    {"재료명":"소비장/지라 (Beef Spleen)",   "category":"organ","bone_pct":0,"칼로리":105,"단백질":18.3,"지방":3.04,"칼슘":8,  "인":249,"철":30.3, "아연":2.42,"구리":0.147,"망간":0.032,"비타민A":8,    "비타민D":0, "비타민E":0.26,"나트륨":84, "요오드(mcg)":0},
    {"재료명":"소췌장 (Beef Pancreas)",      "category":"organ","bone_pct":0,"칼로리":233,"단백질":14.7,"지방":19.1,"칼슘":10, "인":234,"철":2.26, "아연":2.0, "구리":0.097,"망간":0.046,"비타민A":0,    "비타민D":0, "비타민E":0.23,"나트륨":85, "요오드(mcg)":0},
    {"재료명":"닭간 (Chicken Liver)",        "category":"organ","bone_pct":0,"칼로리":119,"단백질":16.9,"지방":4.83,"칼슘":8,  "인":297,"철":9.0,  "아연":2.67,"구리":0.492,"망간":0.351,"비타민A":3296, "비타민D":55,"비타민E":1.1, "나트륨":71, "요오드(mcg)":0},
    {"재료명":"오리간 (Duck Liver)",         "category":"organ","bone_pct":0,"칼로리":136,"단백질":18.7,"지방":4.64,"칼슘":11, "인":263,"철":30.5, "아연":2.68,"구리":0.999,"망간":0.314,"비타민A":4970, "비타민D":80,"비타민E":1.51,"나트륨":144, "요오드(mcg)":0},
    {"재료명":"돼지간 (Pork Liver)",         "category":"organ","bone_pct":0,"칼로리":134,"단백질":20.9,"지방":3.65,"칼슘":8,  "인":387,"철":17.9, "아연":4.02,"구리":0.796,"망간":0.355,"비타민A":6502, "비타민D":53,"비타민E":0.39,"나트륨":49, "요오드(mcg)":0},
    {"재료명":"돼지신장 (Pork Kidney)",      "category":"organ","bone_pct":0,"칼로리":100,"단백질":16.7,"지방":3.09,"칼슘":10, "인":244,"철":4.52, "아연":2.07,"구리":0.344,"망간":0.078,"비타민A":36,   "비타민D":49,"비타민E":0.26,"나트륨":113, "요오드(mcg)":0},
    {"재료명":"그린트라이프 (Green Tripe)",  "category":"organ","bone_pct":0,"칼로리":85, "단백질":14.9,"지방":1.98,"칼슘":112,"인":159,"철":4.44, "아연":1.72,"구리":0.094,"망간":4.06, "비타민A":20,   "비타민D":8, "비타민E":0.45,"나트륨":81, "요오드(mcg)":0},

    # ── 근육고기 (meat) — 심장·폐·모래주머니·생식기 포함 ──
    {"재료명":"닭가슴살 (Chicken Breast)",   "category":"meat","bone_pct":0,"칼로리":120,"단백질":22.5,"지방":2.62,"칼슘":5,  "인":213,"철":0.37, "아연":0.68,"구리":0.037,"망간":0.011,"비타민A":30,   "비타민D":0, "비타민E":0.56,"나트륨":45, "요오드(mcg)":0},
    {"재료명":"소고기 (Beef)",               "category":"meat","bone_pct":0,"칼로리":152,"단백질":20.8,"지방":7.0, "칼슘":10, "인":192,"철":2.33, "아연":4.97,"구리":0.075,"망간":0.01, "비타민A":14,   "비타민D":3, "비타민E":0.17,"나트륨":66, "요오드(mcg)":0},
    {"재료명":"말고기 (Horse Meat)",         "category":"meat","bone_pct":0,"칼로리":133,"단백질":21.4,"지방":4.6, "칼슘":6,  "인":221,"철":3.82, "아연":2.9, "구리":0.144,"망간":0.019,"비타민A":0,    "비타민D":0, "비타민E":0,   "나트륨":53, "요오드(mcg)":0},
    {"재료명":"사슴고기 (Venison)",          "category":"meat","bone_pct":0,"칼로리":116,"단백질":21.5,"지방":2.66,"칼슘":7,  "인":201,"철":2.92, "아연":4.2, "구리":0.14, "망간":0.014,"비타민A":0,    "비타민D":0, "비타민E":0,   "나트륨":75, "요오드(mcg)":0},
    {"재료명":"정어리 (Sardine)",            "category":"meat","bone_pct":0,"칼로리":208,"단백질":24.6,"지방":11.4,"칼슘":382,"인":490,"철":2.92, "아연":1.4, "구리":0.186,"망간":0,    "비타민A":30,   "비타민D":4.8,"비타민E":1.38,"나트륨":307, "요오드(mcg)":0},
    {"재료명":"계란노른자 (Egg Yolk)",       "category":"meat","bone_pct":0,"칼로리":322,"단백질":15.9,"지방":26.5,"칼슘":129,"인":390,"철":2.73, "아연":2.3, "구리":0.077,"망간":0.31, "비타민A":1440, "비타민D":49,"비타민E":0.38,"나트륨":48, "요오드(mcg)":0},
    # 근육성 기관 (organ → meat 재분류)
    {"재료명":"소심장 (Beef Heart)",         "category":"meat","bone_pct":0,"칼로리":112,"단백질":18.5,"지방":3.4, "칼슘":4,  "인":209,"철":4.38, "아연":1.51,"구리":0.373,"망간":0.034,"비타민A":34,   "비타민D":6, "비타민E":1.22,"나트륨":86, "요오드(mcg)":0},
    {"재료명":"소폐 (Beef Lung)",            "category":"meat","bone_pct":0,"칼로리":92, "단백질":16.2,"지방":2.5, "칼슘":10, "인":224,"철":7.95, "아연":1.61,"구리":0.26, "망간":0.019,"비타민A":46,   "비타민D":0, "비타민E":0,   "나트륨":198, "요오드(mcg)":0},
    {"재료명":"소우신통 (Beef Penis)",       "category":"meat","bone_pct":0,"칼로리":120,"단백질":22.0,"지방":3.0, "칼슘":8,  "인":180,"철":2.0,  "아연":2.0, "구리":0.1,  "망간":0.02, "비타민A":0,    "비타민D":0, "비타민E":0.5, "나트륨":70, "요오드(mcg)":0},
    {"재료명":"닭심장 (Chicken Heart)",      "category":"meat","bone_pct":0,"칼로리":153,"단백질":15.6,"지방":9.33,"칼슘":11, "인":159,"철":5.95, "아연":6.49,"구리":0.301,"망간":0.073,"비타민A":34,   "비타민D":0, "비타민E":1.0, "나트륨":65, "요오드(mcg)":0},
    {"재료명":"닭근위 (Chicken Gizzard)",    "category":"meat","bone_pct":0,"칼로리":94, "단백질":17.7,"지방":2.06,"칼슘":9,  "인":148,"철":2.49, "아연":2.72,"구리":0.122,"망간":0.038,"비타민A":40,   "비타민D":0, "비타민E":0.22,"나트륨":69, "요오드(mcg)":0},
    {"재료명":"돼지심장 (Pork Heart)",       "category":"meat","bone_pct":0,"칼로리":118,"단백질":17.7,"지방":4.67,"칼슘":6,  "인":210,"철":3.37, "아연":2.63,"구리":0.382,"망간":0.031,"비타민A":0,    "비타민D":49,"비타민E":0.83,"나트륨":57, "요오드(mcg)":0},

    # ── 채소·과일·기타 (veggie) ──
    {"재료명":"블루베리 (Blueberry)",        "category":"veggie","bone_pct":0,"칼로리":57, "단백질":0.74,"지방":0.33,"칼슘":6,  "인":12, "철":0.28, "아연":0.06,"구리":1.6,  "망간":0.262,"비타민A":54,   "비타민D":0, "비타민E":0.57,"나트륨":1, "요오드(mcg)":0},
    {"재료명":"브로콜리 퓨레 (Broccoli)",   "category":"veggie","bone_pct":0,"칼로리":34, "단백질":2.82,"지방":0.37,"칼슘":47, "인":66, "철":0.73, "아연":0.41,"구리":0.049,"망간":0.21, "비타민A":623,  "비타민D":0, "비타민E":0.78,"나트륨":33, "요오드(mcg)":0},
    {"재료명":"토마토 퓨레 (Tomato)",       "category":"veggie","bone_pct":0,"칼로리":18, "단백질":0.88,"지방":0.2, "칼슘":10, "인":24, "철":0.27, "아연":0.17,"구리":0.059,"망간":0.114,"비타민A":833,  "비타민D":0, "비타민E":0.54,"나트륨":5, "요오드(mcg)":0},
    {"재료명":"우엉 퓨레 (Burdock Root)",   "category":"veggie","bone_pct":0,"칼로리":72, "단백질":1.53,"지방":0.15,"칼슘":41, "인":51, "철":0.8,  "아연":0.33,"구리":0.08, "망간":0.23, "비타민A":0,    "비타민D":0, "비타민E":0.4, "나트륨":5, "요오드(mcg)":0},
    {"재료명":"청경채 퓨레 (Bok Choy)",    "category":"veggie","bone_pct":0,"칼로리":13, "단백질":1.5, "지방":0.2, "칼슘":105,"인":37, "철":0.8,  "아연":0.19,"구리":0.021,"망간":0.159,"비타민A":4468, "비타민D":0, "비타민E":0.09,"나트륨":65, "요오드(mcg)":0},
    {"재료명":"단호박 퓨레 (Kabocha)",     "category":"veggie","bone_pct":0,"칼로리":34, "단백질":1.0, "지방":0.1, "칼슘":20, "인":30, "철":0.4,  "아연":0.15,"구리":0.07, "망간":0.15, "비타민A":1370, "비타민D":0, "비타민E":0.3, "나트륨":3, "요오드(mcg)":0},
    {"재료명":"본브로스 소뼈 (Bone Broth)","category":"veggie","bone_pct":0,"칼로리":18, "단백질":4.0, "지방":0.0, "칼슘":5,  "인":10, "철":0.2,  "아연":0.1, "구리":0.02, "망간":0,    "비타민A":0,    "비타민D":0, "비타민E":0,   "나트륨":20, "요오드(mcg)":0},
    {"재료명":"파프리카 퓨레 (Paprika)",   "category":"veggie","bone_pct":0,"칼로리":31, "단백질":1.0, "지방":0.3, "칼슘":7,  "인":26, "철":0.43, "아연":0.25,"구리":0.017,"망간":0.11, "비타민A":3131, "비타민D":0, "비타민E":1.58,"나트륨":4, "요오드(mcg)":0},
    {"재료명":"샐러리 퓨레 (Celery)",     "category":"veggie","bone_pct":0,"칼로리":16, "단백질":0.69,"지방":0.17,"칼슘":40, "인":24, "철":0.2,  "아연":0.13,"구리":0.04, "망간":0.1,  "비타민A":449,  "비타민D":0, "비타민E":0.27,"나트륨":80, "요오드(mcg)":0},
    {"재료명":"당근 퓨레 (Carrot)",       "category":"veggie","bone_pct":0,"칼로리":41, "단백질":0.93,"지방":0.24,"칼슘":33, "인":35, "철":0.3,  "아연":0.24,"구리":0.045,"망간":0.143,"비타민A":16706,"비타민D":0, "비타민E":0.66,"나트륨":69, "요오드(mcg)":0},

    # ── v5.3 신규 추가 ──────────────────────────────────────────────────────
    # 칠면조 가슴살 (USDA FDC 171093 Turkey breast raw)
    {"재료명":"칠면조 가슴살 (Turkey Breast)",  "category":"meat","bone_pct":0,"칼로리":111,"단백질":24.6,"지방":0.7, "칼슘":10, "인":206,"철":1.2,  "아연":1.2, "구리":0.06, "망간":0.02, "비타민A":0,    "비타민D":0,  "비타민E":0.1, "나트륨":49, "요오드(mcg)":0},
    # 오리 가슴살 야생 (USDA FDC 174469 Duck wild breast raw)
    {"재료명":"오리 가슴살 (Duck Breast)",      "category":"meat","bone_pct":0,"칼로리":123,"단백질":19.8,"지방":4.3, "칼슘":3,  "인":186,"철":4.5,  "아연":1.5, "구리":0.26, "망간":0.02, "비타민A":60,   "비타민D":0,  "비타민E":0.5, "나트륨":57, "요오드(mcg)":0},
    # 염소고기 (USDA FDC 175306 Goat raw)
    {"재료명":"염소고기 (Goat)",               "category":"meat","bone_pct":0,"칼로리":109,"단백질":20.6,"지방":2.31,"칼슘":13, "인":180,"철":2.83, "아연":4.5, "구리":0.11, "망간":0.019,"비타민A":0,    "비타민D":0,  "비타민E":0.27,"나트륨":82, "요오드(mcg)":0},
    # 양고기 다리살 (USDA FDC 174369 Lamb leg raw)
    {"재료명":"양고기 (Lamb)",                 "category":"meat","bone_pct":0,"칼로리":153,"단백질":20.3,"지방":7.64,"칼슘":16, "인":190,"철":1.88, "아연":3.95,"구리":0.117,"망간":0.023,"비타민A":0,    "비타민D":0,  "비타민E":0.14,"나트륨":72, "요오드(mcg)":0},
    # 열빙어/smelt (USDA FDC 175150 Smelt rainbow raw)
    {"재료명":"열빙어 (Smelt)",                "category":"meat","bone_pct":0,"칼로리":97, "단백질":17.6,"지방":2.42,"칼슘":60, "인":230,"철":0.9,  "아연":1.7, "구리":0.14, "망간":0.7,  "비타민A":15,   "비타민D":32, "비타민E":0.5, "나트륨":60, "요오드(mcg)":0},
    # 산양유 케피어/요거트 (USDA FDC 171264 Goat milk raw 기반, 발효로 단백질/칼슘 소폭 조정)
    {"재료명":"산양유 케피어 (Goat Kefir)",    "category":"meat","bone_pct":0,"칼로리":69, "단백질":3.5, "지방":4.0, "칼슘":134,"인":111,"철":0.05, "아연":0.3, "구리":0.05, "망간":0.02, "비타민A":185,  "비타민D":4,  "비타민E":0.1, "나트륨":50, "요오드(mcg)":0},


    # ── v5.4 신규 추가 ──────────────────────────────────────────────────────
    # 돼지 안심 (USDA FDC 168249 Pork tenderloin raw)
    {"재료명":"돼지 안심 (Pork Tenderloin)",    "category":"meat","bone_pct":0,"칼로리":109,"단백질":20.9,"지방":2.1, "칼슘":5,  "인":247,"철":0.97, "아연":1.88,"구리":0.094,"망간":0.012,"비타민A":0,    "비타민D":8,  "비타민E":0.22,"나트륨":53, "요오드(mcg)":0},
    # 양간 (USDA FDC 172531 Lamb liver raw) — 100g 환산
    {"재료명":"양간 (Lamb Liver)",              "category":"organ","bone_pct":0,"칼로리":139,"단백질":20.7,"지방":5.1, "칼슘":7,  "인":369,"철":7.5,  "아연":4.6, "구리":7.14, "망간":0.18, "비타민A":6990, "비타민D":0,  "비타민E":0,   "나트륨":71, "요오드(mcg)":0},
    # 꿩 살코기 생 (USDA FDC 169902 Pheasant raw meat only)
    {"재료명":"꿩 (Pheasant)",                  "category":"meat","bone_pct":0,"칼로리":133,"단백질":23.6,"지방":3.6, "칼슘":12, "인":214,"철":1.1,  "아연":1.0, "구리":0.07, "망간":0.01, "비타민A":177,  "비타민D":0,  "비타민E":0,   "나트륨":40, "요오드(mcg)":0},
    # 토끼고기 가정사육 생 (USDA FDC 172521 Rabbit domesticated raw)
    {"재료명":"토끼고기 (Rabbit)",              "category":"meat","bone_pct":0,"칼로리":136,"단백질":20.4,"지방":5.6, "칼슘":13, "인":216,"철":1.6,  "아연":1.6, "구리":0.14, "망간":0.04, "비타민A":0,    "비타민D":0,  "비타민E":0,   "나트륨":41, "요오드(mcg)":0},
    # 치아씨드 (USDA FDC 170554 Chia seeds raw)
    {"재료명":"치아씨드 (Chia Seeds)",          "category":"veggie","bone_pct":0,"칼로리":486,"단백질":16.5,"지방":30.7,"칼슘":631,"인":860,"철":7.7,  "아연":4.6, "구리":0.924,"망간":2.72, "비타민A":54,   "비타민D":0,  "비타민E":0.5, "나트륨":16, "요오드(mcg)":0},
    # 메추리알 생 (USDA FDC 172188 Quail egg raw)
    {"재료명":"메추리알 (Quail Egg)",           "category":"meat","bone_pct":0,"칼로리":158,"단백질":13.1,"지방":11.1,"칼슘":64, "인":226,"철":3.65, "아연":1.47,"구리":0.11, "망간":0.10, "비타민A":543,  "비타민D":132,"비타민E":1.08,"나트륨":141, "요오드(mcg)":0},
    # 연어 대서양 양식 생 (USDA FDC 175167 Salmon Atlantic farmed raw)
    {"재료명":"연어 (Salmon)",                  "category":"meat","bone_pct":0,"칼로리":208,"단백질":20.4,"지방":13.4,"칼슘":9,  "인":240,"철":0.34, "아연":0.36,"구리":0.05, "망간":0.01, "비타민A":50,   "비타민D":447,"비타민E":3.55,"나트륨":59,  "요오드(mcg)":0},
    # ── v5.5 신규 ──────────────────────────────────────────────────────────
    # 켈프 생 (USDA FDC 168457) — 요오드는 제품·종·산지마다 다름, 1500mcg/100g은 참고값
    # NRC 권장: 220mcg/1000kcal, 안전상한: 1400mcg/1000kcal
    {"재료명":"켈프 (Kelp/Seaweed)",            "category":"veggie","bone_pct":0,"칼로리":43, "단백질":1.68,"지방":0.56,"칼슘":168,"인":42, "철":2.85, "아연":1.23,"구리":0.13, "망간":0.2,  "비타민A":116, "비타민D":0,  "비타민E":0.87,"나트륨":233, "요오드(mcg)":1500},
    # 양배추 퓨레 생 (USDA FDC 169975 Cabbage raw)
    {"재료명":"양배추 퓨레 (Cabbage)",          "category":"veggie","bone_pct":0,"칼로리":25, "단백질":1.28,"지방":0.1, "칼슘":40, "인":26,  "철":0.47, "아연":0.18,"구리":0.019,"망간":0.16, "비타민A":98,  "비타민D":0,  "비타민E":0.15,"나트륨":18,  "요오드(mcg)":0},
    # 배추 퓨레 생 (USDA FDC 169979 Napa cabbage raw)
    {"재료명":"배추 퓨레 (Napa Cabbage)",       "category":"veggie","bone_pct":0,"칼로리":12, "단백질":0.9, "지방":0.1, "칼슘":105,"인":37,  "철":0.8,  "아연":0.19,"구리":0.021,"망간":0.16, "비타민A":4468,"비타민D":0,  "비타민E":0.09,"나트륨":65,  "요오드(mcg)":0},

    # ── v5.7 신규 ──────────────────────────────────────────────────────────
    # 소목뼈 (뼈 37% 추정) — USDA 실측값 없음, 포유류 평균 밀도 50.4mg/g 적용
    # Ca = 37g × 50.4 = 1865mg, P = Ca × 0.5 = 932mg
    {"재료명":"소목뼈 (Beef Neck Bone, 뼈 37%)", "category":"bone","bone_pct":0.37,"칼슘":1865,"인":932,"칼슘출처":"est_mammal_avg50.4","칼로리":215,"단백질":17.0,"지방":14.0,"철":3.0,"아연":4.0,"구리":0.1,"망간":0.02,"비타민A":0,"비타민D":0,"비타민E":0,"나트륨":65,"요오드(mcg)":0},

    # 캥거루 사태 raw (AFCD Release 3 FSANZ F009791 — 사태/스테이크 부위)
    {"재료명":"캥거루 사태 (Kangaroo Shank)",    "category":"meat","bone_pct":0,"칼로리":102,"단백질":22.5,"지방":1.0, "칼슘":4,  "인":190,"철":3.1,  "아연":2.6, "구리":0.16, "망간":0.02, "비타민A":0,   "비타민D":2,  "비타민E":0.3, "나트륨":40,  "요오드(mcg)":0},

    # 오리울대 (식도, 순수 근육) — 오리 가슴살 유사 추정값
    {"재료명":"오리 울대 (Duck Esophagus)",      "category":"meat","bone_pct":0,"칼로리":123,"단백질":19.8,"지방":4.3, "칼슘":3,  "인":186,"철":4.5,  "아연":1.5, "구리":0.26, "망간":0.02, "비타민A":60,  "비타민D":0,  "비타민E":0.5, "나트륨":57,  "요오드(mcg)":0},

    # 아몬드 가루 (USDA FDC 170567 Almonds raw — 비타민E 공급원, 소량 사용 권장)
    # ⚠️ 지방 함량 높음(50g/100g), 소량(5~10g/일) 이상 급여 시 췌장 부담 위험
    {"재료명":"아몬드 가루 ⚠️ (Almond Flour)",  "category":"veggie","bone_pct":0,"칼로리":579,"단백질":21.2,"지방":49.9,"칼슘":264,"인":484,"철":3.71, "아연":3.12,"구리":1.03, "망간":2.18, "비타민A":0,   "비타민D":0,  "비타민E":25.6,"나트륨":1,   "요오드(mcg)":0},

    # 햄프씨드 탈각 (USDA FDC 170148 Seeds hemp seed hulled)
    {"재료명":"햄프씨드 (Hemp Seeds)",           "category":"veggie","bone_pct":0,"칼로리":553,"단백질":31.6,"지방":48.8,"칼슘":70, "인":1650,"철":8.0,  "아연":9.9, "구리":1.6,  "망간":7.6,  "비타민A":11,  "비타민D":0,  "비타민E":0.8, "나트륨":5,   "요오드(mcg)":0},

    # 호박씨 가루 (USDA FDC 170556 Seeds pumpkin squash kernels dried)
    {"재료명":"호박씨 가루 (Pumpkin Seeds)",     "category":"veggie","bone_pct":0,"칼로리":559,"단백질":30.2,"지방":49.1,"칼슘":46, "인":1174,"철":8.82, "아연":7.81,"구리":1.34, "망간":4.54, "비타민A":0,   "비타민D":0,  "비타민E":2.18,"나트륨":7,   "요오드(mcg)":0},

    # 크랜베리 생 (USDA FDC 171722 Cranberries raw)
    {"재료명":"크랜베리 (Cranberry)",            "category":"veggie","bone_pct":0,"칼로리":46, "단백질":0.46,"지방":0.13,"칼슘":8,  "인":13,  "철":0.25, "아연":0.1, "구리":0.061,"망간":0.36, "비타민A":60,  "비타민D":0,  "비타민E":1.2, "나트륨":2,   "요오드(mcg)":0},

    # 케일 퓨레 생 (USDA FDC 168421 Kale raw)
    {"재료명":"케일 퓨레 (Kale)",               "category":"veggie","bone_pct":0,"칼로리":35, "단백질":2.92,"지방":1.49,"칼슘":150,"인":92,  "철":1.5,  "아연":0.56,"구리":1.5,  "망간":0.66, "비타민A":15376,"비타민D":0, "비타민E":1.54,"나트륨":38,  "요오드(mcg)":0},

    # 아스파라거스 퓨레 생 (USDA FDC 168389 Asparagus raw)
    {"재료명":"아스파라거스 퓨레 (Asparagus)",   "category":"veggie","bone_pct":0,"칼로리":20, "단백질":2.2, "지방":0.12,"칼슘":24, "인":52,  "철":2.14, "아연":0.54,"구리":0.19, "망간":0.16, "비타민A":756, "비타민D":0,  "비타민E":1.13,"나트륨":2,   "요오드(mcg)":0},

    # 고등어 대서양 생 (USDA FDC 175119 Fish mackerel Atlantic raw)
    {"재료명":"고등어 (Mackerel)",               "category":"meat","bone_pct":0,"칼로리":205,"단백질":18.6,"지방":13.9,"칼슘":12, "인":217,"철":1.63, "아연":0.63,"구리":0.072,"망간":0.018,"비타민A":187, "비타민D":720,"비타민E":1.52,"나트륨":90,  "요오드(mcg)":0},

    # 굴 익힘 (USDA FDC 171980 Oyster eastern wild cooked moist heat) — 100g 기준 환산
    {"재료명":"굴 (Oyster, 익힘)",         "category":"meat","bone_pct":0,"칼로리":102,"단백질":11.4,"지방":3.3, "칼슘":116,"인":194,"철":9.3,  "아연":78.6,"구리":5.71, "망간":0.6,  "비타민A":88,  "비타민D":2,  "비타민E":1.69,"나트륨":166, "요오드(mcg)":109},

    # 초록홍합 익힘 — 생 기준 대비 단백질↑ 수분↓ 미네랄 농축, NZ FSANZ 참고 추정
    {"재료명":"초록홍합 (Green-Lipped Mussel, 익힘)",      "category":"meat","bone_pct":0,"칼로리":97, "단백질":14.8,"지방":2.6, "칼슘":40, "인":303,"철":3.95, "아연":3.1, "구리":0.18, "망간":4.1,  "비타민A":50,  "비타민D":5,  "비타민E":1.1, "나트륨":220, "요오드(mcg)":0},
]
food_df = pd.DataFrame(db_data)

# ── 조리 보존율 (USDA Retention Factor 기반 추정 보정값) ────────────────────
COOK_RETENTION = {
    "저온찜":    {"단백질": 0.975, "미네랄": 0.975, "비타민지용성": 0.875, "비타민B": 0.80,  "오메가3": 0.875},
    "삶기":      {"단백질": 0.95,  "미네랄": 0.95,  "비타민지용성": 0.825, "비타민B": 0.65,  "오메가3": 0.825},
    "볶기/구이": {"단백질": 0.95,  "미네랄": 0.95,  "비타민지용성": 0.80,  "비타민B": 0.725, "오메가3": 0.725},
    "압력조리":  {"단백질": 0.95,  "미네랄": 0.95,  "비타민지용성": 0.875, "비타민B": 0.775, "오메가3": 0.825},
}
COOK_YIELD = {"저온찜": 0.85, "삶기": 0.80, "볶기/구이": 0.75, "압력조리": 0.82}

def get_rf(nutri, method):
    r = COOK_RETENTION.get(method, COOK_RETENTION["삶기"])
    if nutri in ["단백질(g)", "지방(g)"]: return r["단백질"]
    if nutri in ["칼슘(mg)", "인(mg)", "철(mg)", "아연(mg)", "구리(mg)", "망간(mg)", "나트륨(mg)", "요오드(mcg)"]: return r["미네랄"]
    if nutri in ["비타민A(IU)", "비타민D(IU)", "비타민E(IU)"]: return r["비타민지용성"]
    return r["미네랄"]

# --- [3. 메인 화면] ---
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("🐶 강아지 정보")
    weight = st.number_input("몸무게 (kg)", 0.1, 60.0, 3.0, step=0.1)

    der_options = {
        "3.0: 성장기 강아지 (퍼피)": 3.0,
        "2.0: 체중 증가 필요": 2.0,
        "2.0: 매우 활동적인 성견 / 야외 훈련량 많음": 2.0,
        "1.8: 비중성화 성견 · 보통 활동량": 1.8,
        "1.6: 중성화 성견 · 보통 활동량 (기본값)": 1.6,
        "1.4: 중성화 성견 · 낮은 활동량 / 비만 경향": 1.4,
        "1.4: 노견 · 활동적": 1.4,
        "1.2: 중성화 성견 · 매우 낮은 활동량": 1.2,
        "1.2: 노견 · 보통": 1.2,
        "1.0: 노견 · 거의 안 움직임": 1.0,
        "1.0: 체중 감량이 필요한 성견 (다이어트)": 1.0,
    }

    selected_label = st.selectbox(
        "강아지의 현재 상태를 선택해 주세요!",
        options=list(der_options.keys()),
        index=4,
    )

    activity = der_options[selected_label]
    rer = 70 * (weight ** 0.75)
    der = rer * activity
    st.metric(label="하루 목표 칼로리 (DER)", value=f"{der:.1f} kcal")

with col2:
    st.subheader("🥩 재료 선택")
    all_foods = food_df["재료명"].tolist()
    cooked_foods = food_df[food_df["category"] != "bone"]["재료명"].tolist()

    diet_mode = st.radio("식단 종류", ["🥩 생식", "🍲 화식"], horizontal=True, key="diet_mode")
    is_cooked = diet_mode == "🍲 화식"

    if not is_cooked:
        bone_options = [f for f in all_foods if food_df[food_df["재료명"] == f]["category"].values[0] == "bone"]
        default_selections = [bone_options[0]] if bone_options else []
        selected = st.multiselect("재료를 고르세요:", all_foods, default=default_selections, key="raw_sel")
        cooking_method = "생식"
        cooked_sel = []
        cooked_amounts_dict = {}
        ca_sup_total = 0.0
    else:
        st.caption("⚠️ 화식 계산은 조리 과정의 영양소 손실을 반영한 **추정치**입니다. 실제 보존율은 재료·조리시간·온도·물 사용 여부에 따라 달라질 수 있습니다.")
        cooking_method = st.radio("조리 방법", ["저온찜", "삶기", "볶기/구이", "압력조리"], horizontal=True, key="cook_method")
        ret = COOK_RETENTION[cooking_method]
        st.caption(f"추정 보존율 — 단백질/미네랄: ~{int(ret['단백질']*100)}% | 지용성 비타민: ~{int(ret['비타민지용성']*100)}% | 비타민B: ~{int(ret['비타민B']*100)}% | 오메가3: ~{int(ret['오메가3']*100)}%")
        st.info("🦴 화식에서는 뼈고기를 익히면 안 됩니다. 칼슘은 아래 보충제로 공급해주세요.")
        cooked_sel = st.multiselect("재료를 고르세요 (뼈고기 제외):", cooked_foods, key="cooked_sel")
        selected = []

        # 칼슘 보충
        csup1, csup2 = st.columns(2)
        with csup1:
            use_egg = st.checkbox("난각가루", key="n_use_egg")
            egg_g, egg_ca = 0.0, 380
            if use_egg:
                egg_g = st.number_input("난각가루 (g)", 0.0, 10.0, 0.5, step=0.1, key="n_egg_g")
                egg_ca = st.number_input("Ca 함량 (mg/g)", 100, 600, 380, step=10, key="n_egg_ca")
        with csup2:
            use_sup = st.checkbox("칼슘 보충제", key="n_use_sup")
            sup_g, sup_ca = 0.0, 400
            if use_sup:
                sup_g = st.number_input("보충제 (g)", 0.0, 10.0, 0.5, step=0.1, key="n_sup_g")
                sup_ca = st.number_input("Ca 함량 (mg/g) — 제품 라벨 확인", 50, 600, 400, step=10, key="n_sup_ca")
        ca_sup_total = (egg_g * egg_ca if use_egg else 0) + (sup_g * sup_ca if use_sup else 0)
        if ca_sup_total > 0:
            st.caption(f"칼슘 보충 합계: {ca_sup_total:.0f}mg")
        cooked_amounts_dict = {}

active_sel = cooked_sel if is_cooked else selected

amounts = {}
cooked_amounts_dict = {} if not is_cooked else cooked_amounts_dict
if active_sel:
    cols = st.columns(3)
    for i, f in enumerate(active_sel):
        with cols[i % 3]:
            val = st.number_input(f"{f} {'생고기 기준 ' if is_cooked else ''}(g)", 0, 1000, 50, step=5, key=f"namt_{f}")
            if is_cooked:
                cooked_amounts_dict[f] = val
            else:
                amounts[f] = val

# --- [4. 계산 및 판정] ---
if active_sel:
    st.divider()

    active_amounts = cooked_amounts_dict if is_cooked else amounts
    total_grams = sum(active_amounts.values())
    mass_breakdown = {"actual_bone": 0, "muscle_meat": 0, "organ": 0, "veggie": 0}
    total_stats = {k: 0 for k in aafco_standards.keys()}
    total_kcal = 0
    recipe_save_list = []

    for f in active_sel:
        grams = active_amounts.get(f, 0)
        if grams > 0:
            recipe_save_list.append({"재료명": f, "급여량(g)": grams})
            row = food_df[food_df["재료명"] == f].iloc[0]
            ratio = grams / 100
            total_kcal += row["칼로리"] * ratio
            for nutri in aafco_standards.keys():
                col_name = nutri if nutri in row.index else nutri.split("(")[0]
                if col_name in row:
                    raw_val = row[col_name] * ratio
                    if is_cooked and row["category"] != "veggie":
                        raw_val *= get_rf(nutri, cooking_method)
                    total_stats[nutri] += raw_val

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

    # 화식 칼슘 보충제 추가
    if is_cooked:
        total_stats["칼슘(mg)"] += ca_sup_total

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
            kcal_pct = (total_kcal / der) * 100

            kcal_col1, kcal_col2, kcal_col3 = st.columns(3)
            with kcal_col1:
                st.metric("🔥 섭취 칼로리", f"{total_kcal:.0f} kcal")
            with kcal_col2:
                st.metric("🎯 목표 칼로리", f"{der:.0f} kcal")
            with kcal_col3:
                delta_kcal = total_kcal - der
                st.metric(
                    "📈 차이",
                    f"{delta_kcal:+.0f} kcal",
                    delta=f"{kcal_pct:.1f}% 충족",
                    delta_color="normal" if abs(delta_kcal) < 50 else ("inverse" if delta_kcal > 0 else "off")
                )

            st.progress(min(kcal_pct / 100, 1.0), text=f"칼로리 충족률: {kcal_pct:.1f}%")

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
                cap_r = ca / p
                if 1.1 <= cap_r <= 2.0:
                    st.info(f"🦴 Ca:P 비율 = {cap_r:.2f} : 1 ✅ (권장 1.1~2 : 1)")
                else:
                    st.warning(f"🦴 Ca:P 비율 = {cap_r:.2f} : 1 ⚠️ 권장 범위(1.1~2:1) 벗어남")
            if is_cooked:
                st.caption(f"📌 조리법: {cooking_method} | 보존율 추정 적용 (야채 제외) | 칼슘 보충 {ca_sup_total:.0f}mg 포함")

else:
    st.info("재료를 선택하면 분석 결과가 나타납니다.")
