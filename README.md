# Financial Health Dashboard

**Helping investors identify financial risks and opportunities**

An interactive Streamlit app that analyzes a company's financial health using WRDS Compustat data.  
Supports Apple, Microsoft, Alphabet (Google) by default, and any other company via GVKEY.

---

## Problem & User

- **Problem**: Individual investors and finance students often struggle to interpret financial ratios and compare companies against industry peers.
- **User**: Retail investors, students, and analysts who need a quick, visual assessment of liquidity, leverage, and profitability.

---

## Data Source

- **WRDS Compustat** (North America – Fundamentals Annual)
- Data accessed: April 2026
- Key tables: `comp.funda`, `comp.namesd`, `comp.company`

---

## Methods

- Data acquisition via `wrds` library (SQL queries).
- Financial ratios calculated: Current ratio, Quick ratio, Debt ratio, ROE, Gross/Net margin, Inventory/Receivables turnover.
- Industry benchmark from 2020–2024 median values (generated separately).
- Visualization: Radar chart (company vs industry), historical trends (dual-axis), risk alerts.

---

## How to Run

1. **Clone this repository**
   ```bash
   git clone https://github.com/wendyhoo-creator/ACC102_Financial_Health.git
   cd ACC102_Financial_Health
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure you have a WRDS account** (XJTLU students and staff can apply via the library).
4. **Place industry_benchmarks.csv** in the root folder (already included).
5. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```
   
## Product Links

- **GitHub Repository**: [https://github.com/wendyhoo-creator/ACC102_Financial_Health](https://github.com/wendyhoo-creator/ACC102_Financial_Health)
- **Demo Video**: [Mediasite link to be added]
  
## Limitations

- Requires a WRDS account with Duo authentication.
- Data may be up to 6 months behind (reporting lag).
- Industry benchmarks are based on 2020–2024 data; not updated dynamically.
- Only companies with indfmt='INDL', consol='C', etc., are included.

## Future Improvements

- PDF report export
- Real-time industry benchmark calculation
- User-adjustable risk thresholds

## Author

- **Name**: Yawen Hu
- **Student ID**: 2469331
- **Course**: ACC102 Mini Assignment (Track 4)
- **Date**: April 20, 2026

## AI Disclosure

This project was developed with the assistance of AI tools:

- **Tool**: DeepSeek
- **Version**: V3.2
- **Access Date**: April 15–20, 2026
- **Use**: Assisted in writing Streamlit layout, debugging SQLAlchemy errors, generating analysis logic, and structuring documentation. All code was reviewed, tested, and understood by the author.
