// TUMAINI CARE — Dashboard Component
// Shows real-time stats pulled from backend API
import { useState, useEffect } from 'react'

const API = 'https://tumaini-care.onrender.com'

const COLORS = {
  LOW:       { bg: '#E1F5EE', text: '#0F6E56', bar: '#1D9E75' },
  MODERATE:  { bg: '#FAEEDA', text: '#854F0B', bar: '#EF9F27' },
  HIGH:      { bg: '#FCEBEB', text: '#A32D2D', bar: '#E24B4A' },
  EMERGENCY: { bg: '#A32D2D', text: '#fff',    bar: '#7B1818' },
}

function StatCard({ label, value, sub, color }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 12, padding: '1.1rem 1.25rem',
      border: '.5px solid #E8E6DE', flex: 1, minWidth: 130
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#9E9C94',
        textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: color || '#1a1a1a', lineHeight: 1 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: '#9E9C94', marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

function BarRow({ label, value, max, color }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
      <div style={{ fontSize: 12, color: '#5F5E5A', width: 110, flexShrink: 0,
        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {label}
      </div>
      <div style={{ flex: 1, height: 8, background: '#F1EFE8', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{
          width: `${Math.min(value / max * 100, 100)}%`, height: '100%',
          background: color || '#1D9E75', borderRadius: 4,
          transition: 'width 0.6s ease'
        }} />
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: '#1a1a1a', width: 24, textAlign: 'right' }}>
        {value}
      </div>
    </div>
  )
}

// Static synthetic data — swapped for API in production
const STATIC = {
  enrolled: 60, logs: 840, alerts: 229, referrals: 41,
  responseRate: 79.6, visitRate: 77.3, avgResponse: 114,
  riskDist: { LOW: 330, MODERATE: 110, HIGH: 164, EMERGENCY: 65 },
  counties: { Siaya:12,Vihiga:11,Nakuru:8,Migori:7,Bungoma:6,Mombasa:4,'Homa Bay':4,Kisumu:3,Kakamega:3,Kisii:2 },
  eplTypes: { 'Spontaneous m/c':35,'Missed m/c':17,'Ectopic':9,'Chemical':5,'Molar':2 },
  channels: { WhatsApp:36, SMS:15, USSD:9 },
}

export default function Dashboard({ hideStatusBanner = false }) {
  const [stats, setStats]     = useState(STATIC)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/patients/stats/summary`).then(r => r.json()).catch(() => null),
      fetch(`${API}/api/alerts/stats`).then(r => r.json()).catch(() => null),
    ]).then(([patStats, alertStats]) => {
      if (patStats || alertStats) {
        setStats(prev => ({
          ...prev,
          enrolled:     patStats?.total_enrolled   ?? prev.enrolled,
          counties:     patStats?.by_county         ?? prev.counties,
          alerts:       alertStats?.total_alerts    ?? prev.alerts,
          referrals:    alertStats?.referrals_generated ?? prev.referrals,
          visitRate:    alertStats?.visit_rate_pct  ?? prev.visitRate,
          avgResponse:  alertStats?.avg_response_mins ?? prev.avgResponse,
        }))
      }
      setLoading(false)
    })
  }, [])

  const total = Object.values(stats.riskDist).reduce((a,b)=>a+b,0)

  return (
    <div>


      {/* Stat cards row 1 */}
      <div style={{ display:'flex', gap:10, marginBottom:10, flexWrap:'wrap' }}>
        <StatCard label="Women enrolled"  value={stats.enrolled}                 sub="Pilot cohort" color="#0F6E56"/>
        <StatCard label="Check-ins logged" value={stats.logs}                    sub="14-day window"/>
        <StatCard label="CHW alerts"      value={stats.alerts}                   sub={`${stats.referrals} referrals`} color="#A32D2D"/>
        <StatCard label="Response rate"   value={`${stats.responseRate}%`}       sub="Daily completion"/>
      </div>

      {/* Stat cards row 2 */}
      <div style={{ display:'flex', gap:10, marginBottom:16, flexWrap:'wrap' }}>
        <StatCard label="CHW visit rate"  value={`${stats.visitRate}%`}          sub="Alerts → home visit" color="#185FA5"/>
        <StatCard label="Avg CHW response" value={`${stats.avgResponse}m`}       sub="Alert to action"/>
        <StatCard label="Counties covered" value={Object.keys(stats.counties).length} sub="Pilot area"/>
        <StatCard label="Referrals generated" value={stats.referrals}            sub="Auto-populated docs" color="#0F6E56"/>
      </div>

      {/* Risk distribution */}
      <div style={{ background:'#fff', border:'.5px solid #E8E6DE', borderRadius:12,
        padding:'1rem 1.25rem', marginBottom:12 }}>
        <div style={{ fontSize:11, fontWeight:600, color:'#9E9C94', textTransform:'uppercase',
          letterSpacing:'.06em', marginBottom:10 }}>
          Risk distribution — all {stats.logs} check-ins
        </div>
        <div style={{ display:'flex', height:12, borderRadius:6, overflow:'hidden', gap:2, marginBottom:10 }}>
          {Object.entries(stats.riskDist).map(([level, count]) => (
            <div key={level} style={{
              flex: count/total, background: COLORS[level]?.bar || '#ccc', minWidth:2
            }}/>
          ))}
        </div>
        <div style={{ display:'flex', gap:16, flexWrap:'wrap' }}>
          {Object.entries(stats.riskDist).map(([level, count]) => (
            <div key={level} style={{ display:'flex', alignItems:'center', gap:6 }}>
              <div style={{ width:10, height:10, borderRadius:'50%',
                background: COLORS[level]?.bar }}/>
              <span style={{ fontSize:12, color:'#5F5E5A' }}>{level}</span>
              <span style={{ fontSize:12, fontWeight:700, color:'#1a1a1a' }}>{count}</span>
              <span style={{ fontSize:11, color:'#9E9C94' }}>
                ({Math.round(count/total*100)}%)
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* County + EPL breakdown */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
        <div style={{ background:'#fff', border:'.5px solid #E8E6DE', borderRadius:12, padding:'1rem 1.25rem' }}>
          <div style={{ fontSize:11, fontWeight:600, color:'#9E9C94', textTransform:'uppercase',
            letterSpacing:'.06em', marginBottom:10 }}>By county</div>
          {Object.entries(stats.counties).map(([c,n]) =>
            <BarRow key={c} label={c} value={n} max={12} color="#1D9E75"/>
          )}
        </div>
        <div style={{ background:'#fff', border:'.5px solid #E8E6DE', borderRadius:12, padding:'1rem 1.25rem' }}>
          <div style={{ fontSize:11, fontWeight:600, color:'#9E9C94', textTransform:'uppercase',
            letterSpacing:'.06em', marginBottom:10 }}>EPL type</div>
          {Object.entries(stats.eplTypes).map(([t,n]) =>
            <BarRow key={t} label={t} value={n} max={35} color="#534AB7"/>
          )}
          <div style={{ marginTop:16 }}>
            <div style={{ fontSize:11, fontWeight:600, color:'#9E9C94', textTransform:'uppercase',
              letterSpacing:'.06em', marginBottom:8 }}>Channel</div>
            {Object.entries(stats.channels).map(([ch,n]) =>
              <BarRow key={ch} label={ch} value={n} max={36}
                color={ch==='WhatsApp'?'#25D366':ch==='SMS'?'#185FA5':'#854F0B'}/>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}