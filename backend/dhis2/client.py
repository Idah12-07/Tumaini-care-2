# ============================================================
# TUMAINI CARE — DHIS2 / KHIS Kenya API Client
# Pulls aggregate maternal health indicators for context
# Push: de-identified EPL surveillance data
# ============================================================
import requests, os

DHIS2_BASE = os.getenv('DHIS2_BASE_URL', 'https://hiskenya.org/api')
AUTH = (os.getenv('DHIS2_USERNAME'), os.getenv('DHIS2_PASSWORD'))

# KEY INDICATORS for Tumaini context calibration
# These are AGGREGATE counts — not patient-level data
INDICATORS = {
    'anc_first_visit':      'h9IlBX9Lkmt',  # ANC 1st visit count
    'miscarriage_facility': 'YOUR_CODE_HERE', # Facility miscarriage reports
    'maternal_deaths':      'YOUR_CODE_HERE', # Maternal deaths by cause
    'chw_household_visits': 'YOUR_CODE_HERE', # CHW visit counts
}

def get_indicator(indicator_id: str, period: str = '2024', org_unit: str = 'Kenya'):
    '''Pull a single aggregate indicator from KHIS/DHIS2.'''
    url = f'{DHIS2_BASE}/analytics'
    params = {
        'dimension': f'dx:{indicator_id},pe:{period},ou:{org_unit}',
        'displayProperty': 'NAME',
        'outputIdScheme': 'CODE',
    }
    r = requests.get(url, params=params, auth=AUTH)
    r.raise_for_status()
    return r.json()

def get_maternal_indicators_by_county(period: str = '2024'):
    '''Pull all Tumaini-relevant indicators across 47 counties.'''
    results = {}
    for name, uid in INDICATORS.items():
        if uid != 'YOUR_CODE_HERE':
            results[name] = get_indicator(uid, period, 'LEVEL-2')  # County level
    return results
