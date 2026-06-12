// TUMAINI CARE — CHW Alerts Component
import { useState, useEffect } from 'react'

const API = 'https://tumaini-care.onrender.com'

const RISK_STYLE = {
  HIGH:      { bg:'#FCEBEB', text:'#A32D2D', border:'#E24B4A' },
  EMERGENCY: { bg:'#A32D2D', text:'#fff',    border:'#791F1F' },
  MODERATE:  { bg:'#FAEEDA', text:'#854F0B', border:'#EF9F27' },
  LOW:       { bg:'#E1F5EE', text:'#0F6E56', border:'#1D9E75' },
}

// Static synthetic alerts for display
const STATIC_ALERTS = [
  { alert_id:'ALT0001', name:'Njeri A.',  county:'Siaya',  date:'2025-04-18', risk:'EMERGENCY', mins:219, visited:true,  referred:true,  facility:'Nyanza General Hospital',        outcome:'Stabilised at home' },
  { alert_id:'ALT0002', name:'Auma M.',   county:'Nakuru', date:'2025-01-05', risk:'HIGH',      mins:10,  visited:true,  referred:false, facility:'',                               outcome:'Ongoing monitoring' },
  { alert_id:'ALT0003', name:'Grace G.',  county:'Migori', date:'2025-01-12', risk:'HIGH',      mins:88,  visited:true,  referred:false, facility:'',                               outcome:'Stabilised at home' },
  { alert_id:'ALT0004', name:'Grace N.',  county:'Vihiga', date:'2025-02-03', risk:'EMERGENCY', mins:45,  visited:true,  referred:true,  facility:'Kisumu County Referral Hospital', outcome:'Treated and discharged' },
  { alert_id:'ALT0005', name:'Njeri M.',  county:'Kisumu', date:'2025-02-14', risk:'HIGH',      mins:67,  visited:true,  referred:false, facility:'',                               outcome:'Ongoing monitoring' },
  { alert_id:'ALT0006', name:'Lydia M.',  county:'Nakuru', date:'2025-03-01', risk:'EMERGENCY', mins:33,  visited:true,  referred:true,  facility:'Nakuru Level 5 Hospital',        outcome:'Admitted' },
  { alert_id:'ALT0007', name:'Esther K.', county:'Bungoma',date:'2025-03-18', risk:'HIGH',      mins:190, visited:false, referred:false, facility:'',                               outcome:'No visit' },
  { alert_id:'ALT0008', name:'Fatuma A.', county:'Vihiga', date:'2025-04-02', risk:'HIGH',      mins:55,  visited:true,  referred:false, facility:'',                               outcome:'Stabilised at home' },
]

function Badge({ text, bg, color, border }) {
  return (
    <span style={{
      fontSize:10, fontWeight:700, padding:'2px 8px',
      borderRadius:5, background:bg, color:color,
      border:`1px solid ${border}`, whiteSpace:'nowrap'
    }}>{text}</span>
  )
}

export function Alerts() {
  const [alerts, setAlerts]   = useState(STATIC_ALERTS)
  const [stats, setStats]     = useState(null)
  const [filter, setFilter]   = useState('ALL')

  useEffect(() => {
    fetch(`${API}/api/alerts/stats`).then(r=>r.json()).then(setStats).catch(()=>{})
    fetch(`${API}/api/alerts/list`).then(r=>r.json()).then(d=>{
      if (d.alerts?.length) setAlerts(d.alerts)
    }).catch(()=>{})
  }, [])

  const filtered = filter === 'ALL' ? alerts : alerts.filter(a => a.risk === filter)

  return (
    <div>
      {/* Stats row */}
      {stats && (
        <div style={{ display:'flex', gap:8, marginBottom:14, flexWrap:'wrap' }}>
          {[
            { label:'Total alerts',  value: stats.total_alerts },
            { label:'Emergency',     value: stats.emergency_alerts, color:'#A32D2D' },
            { label:'Home visits',   value: `${stats.visit_rate_pct}%`, color:'#0F6E56' },
            { label:'Referrals',     value: stats.referrals_generated, color:'#185FA5' },
            { label:'Avg response',  value: `${stats.avg_response_mins}m` },
          ].map(s => (
            <div key={s.label} style={{ background:'#fff', border:'.5px solid #E8E6DE',
              borderRadius:10, padding:'.65rem .9rem', flex:1, minWidth:90 }}>
              <div style={{ fontSize:10, color:'#9E9C94', textTransform:'uppercase',
                letterSpacing:'.05em', marginBottom:3 }}>{s.label}</div>
              <div style={{ fontSize:20, fontWeight:700, color:s.color||'#1a1a1a' }}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Filter buttons */}
      <div style={{ display:'flex', gap:6, marginBottom:12 }}>
        {['ALL','EMERGENCY','HIGH','MODERATE'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            fontSize:11, padding:'4px 12px', borderRadius:20,
            border: `.5px solid ${filter===f ? '#0F6E56' : '#D3D1C7'}`,
            background: filter===f ? '#0F6E56' : '#fff',
            color: filter===f ? '#fff' : '#5F5E5A', cursor:'pointer', fontWeight:500
          }}>{f}</button>
        ))}
        <span style={{ marginLeft:'auto', fontSize:12, color:'#9E9C94', alignSelf:'center' }}>
          {filtered.length} alerts
        </span>
      </div>

      {/* Alert list */}
      <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
        {filtered.map(a => {
          const rs = RISK_STYLE[a.risk] || RISK_STYLE.LOW
          return (
            <div key={a.alert_id} style={{
              background:'#fff', border:'.5px solid #E8E6DE',
              borderRadius:10, padding:'.85rem 1rem',
              borderLeft:`4px solid ${rs.border}`
            }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6, flexWrap:'wrap' }}>
                <span style={{ fontSize:13, fontWeight:700, color:'#1a1a1a' }}>
                  {a.name || a.patient_id}
                </span>
                <span style={{ fontSize:11, color:'#9E9C94' }}>{a.alert_id}</span>
                <Badge text={a.risk} bg={rs.bg} color={rs.text} border={rs.border}/>
                {a.referred && <Badge text="REFERRED" bg="#E6F1FB" color="#185FA5" border="#B5D4F4"/>}
                {!a.visited && <Badge text="NO VISIT" bg="#FCEBEB" color="#A32D2D" border="#E24B4A"/>}
              </div>
              <div style={{ display:'flex', gap:16, flexWrap:'wrap' }}>
                <span style={{ fontSize:12, color:'#5F5E5A' }}>📍 {a.county}</span>
                <span style={{ fontSize:12, color:'#5F5E5A' }}>📅 {a.date}</span>
                <span style={{ fontSize:12, color:'#5F5E5A' }}>
                  ⏱ CHW response: <strong style={{ color:'#1a1a1a' }}>{a.mins}m</strong>
                </span>
                <span style={{ fontSize:12, color: a.visited ? '#0F6E56' : '#A32D2D' }}>
                  {a.visited ? '✓ Visit completed' : '✗ No visit recorded'}
                </span>
              </div>
              {a.facility && (
                <div style={{ fontSize:12, color:'#5F5E5A', marginTop:4 }}>
                  🏥 {a.facility}
                </div>
              )}
              <div style={{ fontSize:12, color:'#9E9C94', marginTop:3 }}>
                Outcome: {a.outcome}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}