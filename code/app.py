import streamlit as st
from content_analyzer import analyze_serp_content
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Content Strategy Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .result-box {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .hebrew {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎯 מנתח אסטרטגיית תוכן")
st.markdown("""
<div class="hebrew">
כלי זה מנתח את תוצאות החיפוש בגוגל ומספק המלצות לאסטרטגיית תוכן מבוססת AI. הכלי:
- מנתח את 10 התוצאות הראשונות בגוגל
- בודק את סוג התוכן, המבנה והנושאים
- מספק המלצות מפורטות לתוכן אופטימלי
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("הגדרות")
    serpapi_key = st.text_input("SerpAPI Key", value=os.getenv('SERPAPI_KEY', ''), type="password")
    claude_key = st.text_input("Claude API Key", value=os.getenv('CLAUDE_KEY', ''), type="password")
    if not serpapi_key or not claude_key:
        st.warning("נא להזין את שני מפתחות ה-API")

# Main content
st.markdown('<div class="hebrew">', unsafe_allow_html=True)
search_query = st.text_input("הזן מילת חיפוש לניתוח")
st.markdown('</div>', unsafe_allow_html=True)

if st.button("נתח תוצאות") and search_query and serpapi_key and claude_key:
    try:
        with st.spinner('מנתח תוצאות... זה עשוי לקחת כמה דקות...'):
            results = analyze_serp_content(search_query, serpapi_key, claude_key)
            
            # Save results with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_results_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Display results
            st.success(f"הניתוח הושלם! התוצאות נשמרו ב-{filename}")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["ניתוח", "URLs שנותחו"])
            
            with tab1:
                if "error" in results:
                    st.error(f"שגיאה בניתוח: {results['error']}")
                else:
                    analysis = results.get('analysis', {})
                    
                    # Display analysis results in a more structured way
                    st.markdown('<div class="hebrew result-box">', unsafe_allow_html=True)
                    
                    # Content Type
                    st.subheader("סוג התוכן המומלץ")
                    st.info(analysis.get('content_type', ''))
                    
                    # Specificity
                    st.subheader("רמת הספציפיות")
                    st.info(analysis.get('specificity', ''))
                    
                    # Recommended Sections
                    st.subheader("נושאים מומלצים")
                    sections = analysis.get('recommended_sections', [])
                    if sections:
                        for section in sections:
                            st.markdown(f"- {section}")
                    else:
                        st.info("לא נמצאו נושאים מומלצים")
                    
                    # Content Focus
                    st.subheader("מיקוד התוכן")
                    st.info(analysis.get('content_focus', ''))
                    
                    # Structure Recommendation
                    st.subheader("המלצה למבנה התוכן")
                    st.info(analysis.get('structure_recommendation', ''))
                    
                    # Reasoning
                    st.subheader("הסבר להמלצות")
                    st.info(analysis.get('reasoning', ''))
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                st.subheader("URLs שנותחו")
                urls = results.get('analyzed_urls', [])
                if urls:
                    for url in urls:
                        st.markdown(f"- [{url}]({url})")
                else:
                    st.info("לא נמצאו URLs לניתוח")
                
    except Exception as e:
        st.error(f"אירעה שגיאה: {str(e)}")
else:
    if not serpapi_key or not claude_key:
        st.info("נא להזין את מפתחות ה-API בסרגל הצד כדי להתחיל.")
    elif not search_query:
        st.info("הזן מילת חיפוש ולחץ על 'נתח תוצאות' כדי להתחיל.") 