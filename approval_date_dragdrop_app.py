import pandas as pd
import streamlit as st
import holidays

st.set_page_config(page_title="📅 지급일자 차이 계산기", layout="wide")
st.title("📅 회계처리 지연차이 5일 찾기")

st.markdown("""
### ℹ️ 분석 기준 안내

- **대상 컬럼:** `품의일자`, `원인행위일`, `지급일자`
- **계산 항목:**  
  - `날짜차이(일)`: 원인행위일과 지급일자의 단순 일수 차이  
  - `품의~지급 차이(일)`: 품의일자와 지급일자의 단순 일수 차이  
  - `영업일일수 차이 : 결제일 포함, 주말(토/일) 및 법정공휴일을 제외한 실제 영업일 수 (지방회계법 별표4)
  - 이호조 21126 , 경비구분 일상경비, 통계목 업추비 설정, 조회 파일저장
""")

uploaded_file = st.file_uploader("📤 엑셀 파일을 드래그 앤 드롭 또는 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, dtype=str)

    # 날짜 변환: 시분초 제거 (date만)
    for col in ["품의일자", "원인행위일", "지급일자"]:
        df[col] = pd.to_datetime(df[col], format="%Y%m%d", errors="coerce").dt.date

    # 날짜 차이 계산
    df["날짜차이(일)"] = (df["지급일자"] - df["원인행위일"]).dt.days
    df["품의일자_지급일자_차이(일)"] = (df["지급일자"] - df["품의일자"]).dt.days

    # 영업일 계산 (공휴일 + 주말 제외)
    kr_holidays = holidays.KR(years=[2024])
    def count_business_days(start, end):
        if pd.isna(start) or pd.isna(end): return None
        days = pd.date_range(start, end, freq='D')
        business_days = [d for d in days if d.weekday() < 5 and d not in kr_holidays]
        return len(business_days)

    df["영업일수(품의~지급)"] = df.apply(
        lambda row: count_business_days(row["품의일자"], row["지급일자"]), axis=1
    )

    # 결과 정리
    result = df[[
        "품의일자", "원인행위일", "지급일자", "결의금액", "품의담당자",
        "날짜차이(일)", "품의일자_지급일자_차이(일)", "영업일수(품의~지급)",
        "적요", "거래처명"
    ]].sort_values(by="지급일자")

    # 표출
    st.success("✅ 분석 완료! 아래에서 확인하세요.")
    st.dataframe(result, use_container_width=True)

    # 다운로드
    csv = result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 결과 다운로드 (CSV)", csv, "지급일자_차이_분석.csv", "text/csv")