import pandas as pd
import streamlit as st
import holidays

st.set_page_config(page_title="📅 지급일자 차이 계산기", layout="wide")
st.title("📅 품의일자 ~ 지급일자 차이 계산기")

uploaded_file = st.file_uploader("📤 엑셀 파일을 드래그 앤 드롭 또는 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, dtype=str)

    for col in ["품의일자", "원인행위일", "지급일자"]:
        df[col] = pd.to_datetime(df[col], format="%Y%m%d", errors="coerce")

    df["날짜차이(일)"] = (df["지급일자"] - df["원인행위일"]).dt.days
    df["품의일자_지급일자_차이(일)"] = (df["지급일자"] - df["품의일자"]).dt.days

    kr_holidays = holidays.KR(years=[2024])
    def count_business_days(start, end):
        if pd.isna(start) or pd.isna(end): return None
        days = pd.date_range(start, end, freq='D')
        business_days = [d for d in days if d.weekday() < 5 and d not in kr_holidays]
        return len(business_days)

    df["영업일수(품의~지급)"] = df.apply(
        lambda row: count_business_days(row["품의일자"], row["지급일자"]), axis=1
    )

    result = df[[
        "품의일자", "원인행위일", "지급일자",
        "날짜차이(일)", "품의일자_지급일자_차이(일)", "영업일수(품의~지급)",
        "적요", "거래처명"
    ]].sort_values(by="지급일자")

    st.success("✅ 분석 완료! 아래에서 확인하세요.")
    st.dataframe(result, use_container_width=True)

    csv = result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 결과 다운로드 (CSV)", csv, "지급일자_차이_분석.csv", "text/csv")
