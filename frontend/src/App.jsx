import { useState, useEffect } from 'react'
import Dashboard    from './components/Dashboard'
import Companion    from './components/Companion'
import { Triage }   from './components/Triage'
import { Alerts }   from './components/Alerts'
import { Patients } from './components/Patients'
import EnrolmentForm from './components/EnrolmentForm'

const API = 'https://tumaini-care.onrender.com'

const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    /* Primary palette — deep forest green, warm and clinical */
    --forest:      #0B5E42;
    --forest-mid:  #0D7A57;
    --forest-light:#E8F5F0;
    --forest-pale: #F2FAF6;

    /* Accent — warm gold for alerts/highlights */
    --gold:        #C07D2A;
    --gold-light:  #FDF3E3;

    /* Danger */
    --danger:      #B22222;
    --danger-light:#FDF0F0;

    /* Neutrals — warm grey, not cold blue-grey */
    --ink:         #1A1F1C;
    --ink-2:       #3D4840;
    --ink-3:       #6B756F;
    --ink-4:       #A8B5AD;
    --ink-5:       #D4DDD7;

    /* Surfaces */
    --bg:          #F5F7F5;
    --surface:     #FFFFFF;
    --surface-2:   #F0F4F1;

    /* Sidebar */
    --sidebar-bg:  #0A1F16;
    --sidebar-mid: #0D2B1E;
    --sidebar-accent: #1A5C40;

    --font-body:   'DM Sans', system-ui, sans-serif;
    --font-display:'DM Serif Display', Georgia, serif;

    --r-sm: 8px;
    --r-md: 12px;
    --r-lg: 16px;
    --r-xl: 20px;

    --shadow-sm: 0 1px 3px rgba(0,0,0,.06);
    --shadow-md: 0 4px 12px rgba(0,0,0,.08);
    --shadow-lg: 0 8px 24px rgba(0,0,0,.1);
  }

  html, body, #root {
    height: 100%;
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
  }

  /* ─── SHELL ──────────────────────────────── */
  .shell { display: flex; min-height: 100vh; }

  /* ─── SIDEBAR ────────────────────────────── */
  .sidebar {
    width: 252px;
    flex-shrink: 0;
    background: var(--sidebar-bg);
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0;
    height: 100vh;
    z-index: 50;
  }

  /* Brand */
  .brand {
    padding: 1.5rem 1.25rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 11px;
    border-bottom: 1px solid rgba(255,255,255,.07);
  }

  .logo-mark {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: var(--forest-mid);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 1px solid rgba(255,255,255,.12);
  }

  .brand-text-wrap { line-height: 1; }

  .brand-name {
    font-family: var(--font-display);
    font-size: 17px;
    color: #FFFFFF;
    letter-spacing: .01em;
  }

  .brand-tagline {
    font-size: 10px;
    color: rgba(255,255,255,.4);
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-top: 4px;
    font-weight: 300;
  }

  /* Nav */
  .nav {
    flex: 1;
    padding: 1rem .75rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .nav-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: rgba(255,255,255,.25);
    padding: .75rem .625rem .3rem;
    margin-top: .25rem;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 9px;
    width: 100%;
    padding: .575rem .75rem;
    border: none;
    border-radius: var(--r-sm);
    cursor: pointer;
    font-family: var(--font-body);
    font-size: 13.5px;
    font-weight: 400;
    color: rgba(255,255,255,.55);
    text-align: left;
    background: transparent;
    transition: background .15s, color .15s;
    position: relative;
  }

  .nav-btn:hover {
    background: rgba(255,255,255,.07);
    color: rgba(255,255,255,.85);
  }

  .nav-btn.active {
    background: var(--forest-mid);
    color: #FFFFFF;
    font-weight: 500;
  }

  .nav-btn.active::before {
    content: '';
    position: absolute;
    left: 0; top: 25%; bottom: 25%;
    width: 3px;
    border-radius: 0 2px 2px 0;
    background: #5DCAA5;
  }

  .nav-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: rgba(255,255,255,.2);
    flex-shrink: 0;
    margin-left: auto;
  }
  .nav-dot.red   { background: #F87171; }
  .nav-dot.amber { background: #FBBF24; }
  .nav-dot.green { background: #34D399; }

  /* Sidebar footer */
  .sidebar-foot {
    padding: 1rem 1.25rem;
    border-top: 1px solid rgba(255,255,255,.07);
  }

  .api-status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
  }

  .status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .status-dot.online   { background: #34D399; box-shadow: 0 0 0 3px rgba(52,211,153,.2); }
  .status-dot.offline  { background: #F87171; }
  .status-dot.checking { background: #FBBF24; }

  .api-status-text {
    font-size: 11.5px;
    color: rgba(255,255,255,.45);
  }

  .sidebar-user {
    font-size: 11px;
    color: rgba(255,255,255,.3);
    line-height: 1.6;
  }

  .sidebar-user strong {
    color: rgba(255,255,255,.5);
    font-weight: 500;
    display: block;
  }

  /* ─── MAIN ───────────────────────────────── */
  .main {
    margin-left: 252px;
    flex: 1;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Topbar */
  .topbar {
    background: var(--surface);
    border-bottom: 1px solid var(--ink-5);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 40;
    box-shadow: var(--shadow-sm);
  }

  .page-title {
    font-family: var(--font-display);
    font-size: 20px;
    color: var(--ink);
    font-style: normal;
    line-height: 1.1;
  }

  .page-sub {
    font-size: 12px;
    color: var(--ink-3);
    margin-top: 3px;
    font-weight: 300;
  }

  .topbar-chips { display: flex; align-items: center; gap: 7px; }

  .chip {
    font-size: 11px;
    font-weight: 500;
    padding: 4px 11px;
    border-radius: 20px;
    letter-spacing: .01em;
    border: 1px solid transparent;
  }

  .chip-green {
    background: #E8F5F0;
    color: var(--forest);
    border-color: #B8DDD0;
  }
  .chip-amber {
    background: var(--gold-light);
    color: var(--gold);
    border-color: #F0C87A;
  }
  .chip-grey {
    background: var(--surface-2);
    color: var(--ink-3);
    border-color: var(--ink-5);
  }

  /* Content */
  .content {
    flex: 1;
    padding: 1.75rem 2rem 3rem;
    max-width: 1440px;
    width: 100%;
    margin: 0 auto;
  }

  /* ─── ENROL HERO ─────────────────────────── */
  .enrol-hero {
    background: var(--sidebar-bg);
    border-radius: var(--r-lg);
    padding: 1.75rem 2rem;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    gap: 20px;
    position: relative;
    overflow: hidden;
  }

  .enrol-hero::after {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(13,122,87,.3);
    pointer-events: none;
  }

  .enrol-icon-wrap {
    width: 54px; height: 54px;
    border-radius: var(--r-md);
    background: var(--forest-mid);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 1px solid rgba(255,255,255,.15);
    z-index: 1;
  }

  .enrol-hero-body { z-index: 1; }

  .enrol-hero-title {
    font-family: var(--font-display);
    font-size: 18px;
    color: #FFFFFF;
    margin-bottom: 5px;
  }

  .enrol-hero-sub {
    font-size: 13px;
    color: rgba(255,255,255,.6);
    line-height: 1.55;
    font-weight: 300;
  }

  .enrol-pills {
    margin-left: auto;
    display: flex;
    flex-direction: column;
    gap: 6px;
    align-items: flex-end;
    flex-shrink: 0;
    z-index: 1;
  }

  .enrol-pill {
    font-size: 10.5px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 20px;
    background: rgba(13,122,87,.4);
    color: rgba(255,255,255,.85);
    border: 1px solid rgba(255,255,255,.12);
    white-space: nowrap;
    letter-spacing: .02em;
  }
`

const TABS = [
  { id: 'dashboard', label: 'Overview' },
  { id: 'companion', label: 'AI Companion' },
  { id: 'triage',    label: 'Symptom Triage' },
  { id: 'alerts',    label: 'CHW Alerts' },
  { id: 'patients',  label: 'Patient Registry' },
  { id: 'enrol',     label: 'Enrol Patient' },
]

const PAGE = {
  dashboard: { title: 'Overview',           sub: 'Patient monitoring, risk levels, and system activity across Kenya' },
  companion: { title: 'AI Grief Companion', sub: 'Confidential bilingual support in Swahili and English' },
  triage:    { title: 'Symptom Triage',     sub: 'WHO/FIGO clinical danger sign scoring — post-EPL assessment' },
  alerts:    { title: 'CHW Alerts',         sub: 'Community health worker notifications and home visit tracking' },
  patients:  { title: 'Patient Registry',   sub: 'All enrolled women in the 14-day post-EPL monitoring window' },
  enrol:     { title: 'Enrol a Patient',    sub: 'Register a woman into Tumaini monitoring — no hospital required' },
}

// Tumaini logo — heart with clinical cross, clean SVG
const Logo = () => (
  <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
    <path d="M11 19.5S2 14 2 7.5C2 5.015 4.015 3 6.5 3c1.74 0 3.26.96 4.5 2.4C12.24 3.96 13.76 3 15.5 3 17.985 3 20 5.015 20 7.5c0 6.5-9 12-9 12Z" fill="rgba(255,255,255,0.9)"/>
    <rect x="10" y="6.5" width="2" height="7" rx=".8" fill="#0B5E42"/>
    <rect x="7.5" y="9" width="7" height="2" rx=".8" fill="#0B5E42"/>
  </svg>
)

// Minimal nav icons using clean SVG paths
const NavIcon = ({ id }) => {
  const icons = {
    dashboard: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <rect x="1" y="1" width="6" height="6" rx="1.5"/>
        <rect x="9" y="1" width="6" height="6" rx="1.5"/>
        <rect x="1" y="9" width="6" height="6" rx="1.5"/>
        <rect x="9" y="9" width="6" height="6" rx="1.5"/>
      </svg>
    ),
    companion: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <path d="M14 5c0-2.2-1.8-4-4-4H6C3.8 1 2 2.8 2 5c0 1.8 1.2 3.4 3 3.8V11l2.5-2H10c2.2 0 4-1.8 4-4Z"/>
      </svg>
    ),
    triage: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <rect x="2" y="2" width="12" height="12" rx="2"/>
        <path d="M8 5v6M5 8h6"/>
      </svg>
    ),
    alerts: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <path d="M8 1.5C5.5 1.5 3.5 3.5 3.5 6v3l-1 2h11l-1-2V6C12.5 3.5 10.5 1.5 8 1.5Z"/>
        <path d="M6.5 13c0 .8.7 1.5 1.5 1.5s1.5-.7 1.5-1.5"/>
      </svg>
    ),
    patients: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <circle cx="8" cy="5" r="3"/>
        <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
      </svg>
    ),
    enrol: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <circle cx="7" cy="5" r="3"/>
        <path d="M1 14c0-3.3 2.7-6 6-6"/>
        <path d="M12 10v5M9.5 12.5h5"/>
      </svg>
    ),
  }
  return icons[id] || null
}

export default function App() {
  const [tab, setTab] = useState('dashboard')
  const [api, setApi] = useState('checking')
  const meta = PAGE[tab]

  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.ok ? setApi('online') : setApi('offline'))
      .catch(() => setApi('offline'))
  }, [])

  const statusLabel = { online: 'System live', offline: 'API offline', checking: 'Connecting...' }

  return (
    <>
      <style>{STYLES}</style>
      <div className="shell">

        {/* ── SIDEBAR ── */}
        <aside className="sidebar">
          <div className="brand">
            <div className="logo-mark"><Logo /></div>
            <div className="brand-text-wrap">
              <div className="brand-name">Tumaini Care</div>
              <div className="brand-tagline">Post-EPL Surveillance · Kenya</div>
            </div>
          </div>

          <nav className="nav">
            <div className="nav-label">Navigation</div>
            {TABS.map(t => (
              <button
                key={t.id}
                className={`nav-btn ${tab === t.id ? 'active' : ''}`}
                onClick={() => setTab(t.id)}
              >
                <NavIcon id={t.id} />
                {t.label}
                {t.id === 'alerts' && tab !== 'alerts' && (
                  <span className="nav-dot red" title="Active alerts" />
                )}
              </button>
            ))}
          </nav>

          <div className="sidebar-foot">
            <div className="api-status-row">
              <div className={`status-dot ${api}`} />
              <span className="api-status-text">{statusLabel[api]}</span>
            </div>
            <div className="sidebar-user">
              <strong>Idah Anyango</strong>
              University of Nairobi · UNITID
            </div>
          </div>
        </aside>

        {/* ── MAIN ── */}
        <div className="main">

          <header className="topbar">
            <div>
              <div className="page-title">{meta.title}</div>
              <div className="page-sub">{meta.sub}</div>
            </div>
            <div className="topbar-chips">
              {api === 'online'
                ? <span className="chip chip-green">Live</span>
                : api === 'offline'
                  ? <span className="chip chip-amber">Offline</span>
                  : <span className="chip chip-grey">Connecting</span>
              }
              <span className="chip chip-green">Kenya Pilot 2026</span>
            </div>
          </header>

          <div className="content">
            {tab === 'dashboard' && <Dashboard />}
            {tab === 'companion' && <Companion />}
            {tab === 'triage'    && <Triage />}
            {tab === 'alerts'    && <Alerts />}
            {tab === 'patients'  && <Patients />}
            {tab === 'enrol' && (
              <>
                <div className="enrol-hero">
                  <div className="enrol-icon-wrap">
                    <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                      <path d="M13 23S3 17 3 10c0-3.3 2.7-6 6-6 2.1 0 4 1.1 5 2.9C15 5.1 16.9 4 19 4c3.3 0 6 2.7 6 6 0 7-12 13-12 13Z" fill="rgba(255,255,255,0.9)"/>
                      <rect x="12" y="7" width="2.5" height="9" rx="1" fill="#0B5E42"/>
                      <rect x="8.5" y="10.5" width="9" height="2.5" rx="1" fill="#0B5E42"/>
                    </svg>
                  </div>
                  <div className="enrol-hero-body">
                    <div className="enrol-hero-title">Register a New Patient</div>
                    <div className="enrol-hero-sub">
                      No hospital visit required. Any woman who has experienced pregnancy loss<br/>
                      can be enrolled — by herself, a CHW, or a nurse at discharge.
                    </div>
                  </div>
                  <div className="enrol-pills">
                    <span className="enrol-pill">Self-enrolment supported</span>
                    <span className="enrol-pill">All 47 counties</span>
                    <span className="enrol-pill">Consent captured</span>
                  </div>
                </div>
                <EnrolmentForm onSuccess={() => setTab('patients')} />
              </>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
