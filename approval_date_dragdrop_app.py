import pandas as pd
import streamlit as st
import holidays

st.set_page_config(page_title="📅 지급일자 차이 계산기", layout="wide")
st.title("📅 회계처리 지연차이 계산기")

st.markdown("""
### ℹ️ 분석 기준 안내

- **대상 컬럼:** `품의일자`, `원인행위일`, `지급일자`
- **계산 항목:**  
  - `날짜차이(일)`: 원인행위일과 지급일자의 단순 일수 차이  
  - `품의일자_지급일자_차이(일)`: 품의일자와 지급일자의 단순 일수 차이  
  - `영업일수(품의~지급)`: 결제일 포함, 주말(토/일) 및 대한민국 법정공휴일을 제외한 실제 영업일 수
- **날짜 형식:** `YYYY-MM-DD` (시분초 제외)
- **금액 형식:** 천 단위 구분 쉼표 포함 (예: 240,000)
""")

uploaded_file = st.file_uploader("📤 엑셀 파일을 드래그 앤 드롭 또는 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, dtype=str)

    # 날짜 컬럼 처리
    for col in ["품의일자", "원인행위일", "지급일자"]:
        df[col] = pd.to_datetime(df[col], format="%Y%m%d", errors="coerce")

    # 날짜 차이 계산
    df["날짜차이(일)"] = (df["지급일자"] - df["원인행위일"]).dt.days
    df["품의일자_지급일자_차이(일)"] = (df["지급일자"] - df["품의일자"]).dt.days

    # 영업일수 계산
    kr_holidays = holidays.KR(years=[2024])
    def count_business_days(start, end):
        if pd.isna(start) or pd.isna(end): return None
        days = pd.date_range(start, end, freq='D')
        business_days = [d for d in days if d.weekday() < 5 and d not in kr_holidays]
        return len(business_days)

    df["영업일수(품의~지급)"] = df.apply(
        lambda row: count_business_days(row["품의일자"], row["지급일자"]), axis=1
    )

    # 날짜를 문자열로 변환 (시분초 제거)
    for col in ["품의일자", "원인행위일", "지급일자"]:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    # 결의금액 형식화 (콤마 삽입)
    df["결의금액"] = pd.to_numeric(df["결의금액"], errors="coerce").fillna(0).astype(int).apply(lambda x: f"{x:,}")

    # 결과 정리
    result = df[[
        "품의일자", "원인행위일", "지급일자", "결의금액", "품의담당자",
        "날짜차이(일)", "품의일자_지급일자_차이(일)", "영업일수(품의~지급)",
        "적요", "거래처명"
    ]].sort_values(by="지급일자")

    # 결과 출력
    st.success("✅ 분석 완료! 아래에서 확인하세요.")
    st.dataframe(result, use_container_width=True)

    # 다운로드
    csv = result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 결과 다운로드 (CSV)", csv, "지급일자_차이_분석.csv", "text/csv")