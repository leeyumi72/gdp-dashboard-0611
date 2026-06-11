import streamlit as st
import pandas as pd
import math
from pathlib import Path

st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:',
)

# Region → country code mapping (individual countries only)
REGION_MAP = {
    'All': [],
    'Asia': [
        'AFG', 'ARM', 'AZE', 'BGD', 'BHR', 'BRN', 'BTN', 'CHN', 'GEO',
        'HKG', 'IDN', 'IND', 'IRN', 'IRQ', 'ISR', 'JOR', 'JPN', 'KAZ',
        'KGZ', 'KHM', 'KOR', 'KWT', 'LAO', 'LBN', 'LKA', 'MAC', 'MDV',
        'MMR', 'MNG', 'MYS', 'NPL', 'OMN', 'PAK', 'PHL', 'PSE', 'QAT',
        'SAU', 'SGP', 'SYR', 'THA', 'TJK', 'TKM', 'TLS', 'TUR', 'UZB',
        'VNM', 'YEM',
    ],
    'Europe': [
        'ALB', 'AND', 'AUT', 'BEL', 'BGR', 'BIH', 'BLR', 'CHE', 'CYP',
        'CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 'GRC',
        'HRV', 'HUN', 'IRL', 'ISL', 'ITA', 'LIE', 'LTU', 'LUX', 'LVA',
        'MCO', 'MDA', 'MKD', 'MLT', 'MNE', 'NLD', 'NOR', 'POL', 'PRT',
        'ROU', 'RUS', 'SMR', 'SRB', 'SVK', 'SVN', 'SWE', 'UKR', 'XKX',
    ],
    'Americas': [
        'ARG', 'ATG', 'BHS', 'BLZ', 'BOL', 'BRA', 'BRB', 'CAN', 'CHL',
        'COL', 'CRI', 'CUB', 'DMA', 'DOM', 'ECU', 'GRD', 'GTM', 'GUY',
        'HND', 'HTI', 'JAM', 'KNA', 'LCA', 'MEX', 'NIC', 'PAN', 'PER',
        'PRY', 'SLV', 'SUR', 'TTO', 'URY', 'USA', 'VCT', 'VEN',
    ],
    'Africa': [
        'AGO', 'BDI', 'BEN', 'BFA', 'BWA', 'CAF', 'CIV', 'CMR', 'COD',
        'COG', 'COM', 'CPV', 'DJI', 'DZA', 'EGY', 'ERI', 'ETH', 'GAB',
        'GHA', 'GIN', 'GMB', 'GNB', 'GNQ', 'KEN', 'LBR', 'LBY', 'LSO',
        'MAR', 'MDG', 'MLI', 'MOZ', 'MRT', 'MUS', 'MWI', 'NAM', 'NER',
        'NGA', 'RWA', 'SDN', 'SEN', 'SLE', 'SOM', 'SSD', 'STP', 'SWZ',
        'SYC', 'TCD', 'TGO', 'TUN', 'TZA', 'UGA', 'ZAF', 'ZMB', 'ZWE',
    ],
    'Middle East': [
        'ARE', 'BHR', 'IRN', 'IRQ', 'ISR', 'JOR', 'KWT', 'LBN', 'OMN',
        'PSE', 'QAT', 'SAU', 'SYR', 'YEM',
    ],
    'Oceania': [
        'AUS', 'FJI', 'FSM', 'KIR', 'MHL', 'NRU', 'NZL', 'PLW', 'PNG',
        'SLB', 'TON', 'TUV', 'VUT', 'WSM',
    ],
}

UNIT_OPTIONS = {
    'Billion ($B)': 1_000_000_000,
    'Trillion ($T)': 1_000_000_000_000,
    'Million ($M)': 1_000_000,
}
UNIT_SUFFIX = {
    'Billion ($B)': 'B',
    'Trillion ($T)': 'T',
    'Million ($M)': 'M',
}


@st.cache_data
def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent / 'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    gdp_df = raw_gdp_df.melt(
        ['Country Name', 'Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce')

    return gdp_df


gdp_df = get_gdp_data()

# code → name lookup
code_to_name = (
    gdp_df[['Country Code', 'Country Name']]
    .drop_duplicates()
    .set_index('Country Code')['Country Name']
    .to_dict()
)

'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

''
''

# ── Filters ──────────────────────────────────────────────────────────────────

col_unit, col_region = st.columns([1, 2])

with col_unit:
    unit_label = st.radio('GDP unit', list(UNIT_OPTIONS.keys()), horizontal=True)

with col_region:
    region = st.selectbox('Filter by region', list(REGION_MAP.keys()))

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value],
)

# Apply region filter to available country options
all_codes = gdp_df['Country Code'].unique().tolist()
if region == 'All':
    available_codes = all_codes
else:
    available_codes = [c for c in REGION_MAP[region] if c in all_codes]

# Default selections (keep only those in the available pool)
default_defaults = ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN']
default_selection = [c for c in default_defaults if c in available_codes]

# Build display options as "Name (CODE)"
def label(code):
    name = code_to_name.get(code, code)
    return f'{name} ({code})'

available_labels = [label(c) for c in available_codes]
default_labels = [label(c) for c in default_selection]

selected_labels = st.multiselect(
    'Which countries would you like to view?',
    available_labels,
    default_labels,
)

# Reverse-map labels back to codes
label_to_code = {label(c): c for c in available_codes}
selected_countries = [label_to_code[l] for l in selected_labels]

if not selected_countries:
    st.warning('Select at least one country')
    st.stop()

''
''
''

# ── Chart ─────────────────────────────────────────────────────────────────────

divisor = UNIT_OPTIONS[unit_label]
suffix = UNIT_SUFFIX[unit_label]

filtered_gdp_df = gdp_df[
    gdp_df['Country Code'].isin(selected_countries)
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
].copy()

filtered_gdp_df['GDP_display'] = filtered_gdp_df['GDP'] / divisor

st.header('GDP over time', divider='gray')
''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP_display',
    color='Country Code',
)

''
''

# ── Metric cards ──────────────────────────────────────────────────────────────

first_year_df = gdp_df[gdp_df['Year'] == from_year]
last_year_df = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')
''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_rows = first_year_df[first_year_df['Country Code'] == country]['GDP']
        last_rows = last_year_df[last_year_df['Country Code'] == country]['GDP']

        first_val = first_rows.iloc[0] if len(first_rows) > 0 else float('nan')
        last_val = last_rows.iloc[0] if len(last_rows) > 0 else float('nan')

        first_gdp = first_val / divisor if not math.isnan(float(first_val or 'nan')) else float('nan')
        last_gdp = last_val / divisor if not math.isnan(float(last_val or 'nan')) else float('nan')

        country_name = code_to_name.get(country, country)

        if math.isnan(last_gdp):
            value_str = 'N/A'
        else:
            value_str = f'{last_gdp:,.2f}{suffix}'

        if math.isnan(first_gdp) or math.isnan(last_gdp) or first_gdp == 0:
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country_name}',
            value=value_str,
            delta=growth,
            delta_color=delta_color,
        )
