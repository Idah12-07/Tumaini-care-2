// TUMAINI CARE — Symptom Triage Component
// Deterministic WHO/FIGO-based risk scoring
import { useState } from 'react'

const API = 'https://tumaini-care.onrender.com'

const SYMPTOMS = [
  { key:'heavy_bleeding',   label:'Heavy bleeding',          sw:'Damu nyingi',              score:3, desc:'Soaking more than 1 pad per hour' },
  { key:'foul_odour',       label:'Foul-smelling discharge', sw:'Harufu mbaya',             score:3, desc:'Unusual smell from vaginal area' },
  { key:'right_sided_pain', label:'Right-sided pain',        sw:'Maumivu upande wa kulia',  score:3, desc:'One-sided — possible ectopic sign' },
  { key:'fever',            label:'Fever / very hot',        sw:'Homa kali',                score:2, desc:'Temperature above 38.5°C' },
  { key:'severe_pain',      label:'Severe abdominal pain',   sw:'Maumivu makali tumboni',   score:2, desc:'Constant, does not go away' },
  { key:'dizziness',        label:'Dizziness / fainting',    sw:'Kizunguzungu',             score:2, desc:'Feeling faint or very weak' },
  { key:'vomiting',         label:'Vomiting / nausea',       sw:'Kutapika',                 score:1, desc:'Repeated vomiting since the loss' },
  { key:'no_bleeding',      label:'Bleeding has stopped',    sw:'Damu imesimama',           score:-1,desc:'May indicate complete passage' },
]

const RISK = {
  LOW:       { bg:'#E1F5EE', text:'#0F6E56', border:'#1D9E75', msg:'No danger signs. Continue daily check-ins and grief support.' },
  MODERATE:  { bg:'#FAEEDA', text:'#854F0B', border:'#EF9F27', msg:'Some concern. CHW should follow up within 24 hours.' },
  HIGH:      { bg:'#FCEBEB', text:'#A32D2D', border:'#E24B4A', msg:'Significant danger signs. CHW alert triggered. Consider facility referral.' },
  EMERGENCY: { bg:'#A32D2D', text:'#fff',    border:'#791F1F', msg:'EMERGENCY — Go to hospital NOW. CHW notified. Referral generated.' },
}

export function Triage() {
  const [checked, setChecked]   = useState({})
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)

  const toggle = (k) => setChecked(p => ({ ...p, [k]: !p[k] }))

  const score = Math.max(0, SYMPTOMS.reduce((s, sym) =>
    s + (checked[sym.key] ? sym.score : 0), 0))

  const localLevel = score >= 5 ? 'EMERGENCY' : score >= 3 ? 'HIGH' : score >= 1 ? 'MODERATE' : 'LOW'

  const runTriage = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/triage/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: 'TUM0001', day_post_loss: 2,
          ...Object.fromEntries(SYMPTOMS.map(s => [s.key, !!checked[s.key]])),
          raw_message: ''
        })
      })
      setResult(await res.json())
    } catch {
      setResult({ risk_level: localLevel, risk_score: score,
        trigger_chw_alert: localLevel !== 'LOW',
        trigger_referral: localLevel === 'EMERGENCY', note: 'Offline — local scoring' })
    }
    setLoading(false)
  }

  const level = result?.risk_level || localLevel
  const c = RISK[level]

  return (
    <div>
      <p style={{ fontSize:13, color:'#5F5E5A', marginBottom:14, lineHeight:1.6 }}>
        Select all symptoms the woman is currently reporting. The triage engine computes a
        clinical risk score based on WHO and FIGO EPL danger sign guidelines.
      </p>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:14 }}>
        {SYMPTOMS.map(s => (
          <div key={s.key} onClick={() => toggle(s.key)} style={{
            border: `1.5px solid ${checked[s.key] ? '#0F6E56' : '#E8E6DE'}`,
            borderRadius:10, padding:'.75rem', cursor:'pointer',
            background: checked[s.key] ? '#E1F5EE' : '#fff', transition:'all .15s'
          }}>
            <div style={{ display:'flex', gap:8, alignItems:'flex-start' }}>
              <div style={{
                width:18, height:18, borderRadius:5, flexShrink:0, marginTop:1,
                border: `1.5px solid ${checked[s.key] ? '#0F6E56' : '#D3D1C7'}`,
                background: checked[s.key] ? '#0F6E56' : '#fff',
                display:'flex', alignItems:'center', justifyContent:'center'
              }}>
                {checked[s.key] && <span style={{ color:'#fff', fontSize:11 }}>✓</span>}
              </div>
              <div>
                <div style={{ fontSize:13, fontWeight:600,
                  color: checked[s.key] ? '#0F6E56' : '#1a1a1a' }}>{s.label}</div>
                <div style={{ fontSize:11, color:'#9E9C94' }}>Sw: {s.sw}</div>
                <div style={{ fontSize:11, color:'#9E9C94', marginTop:2 }}>{s.desc}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button onClick={runTriage} disabled={loading} style={{
        width:'100%', padding:'.75rem', marginBottom:14,
        background: loading ? '#9E9C94' : '#0F6E56', color:'#fff',
        border:'none', borderRadius:10, fontSize:14, fontWeight:600, cursor:'pointer'
      }}>
        {loading ? 'Scoring...' : 'Run Triage Score →'}
      </button>

      {/* Risk result */}
      <div style={{
        border: `2px solid ${c.border}`, borderRadius:12,
        padding:'1rem 1.25rem', background: c.bg
      }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8 }}>
          <span style={{ fontSize:11, fontWeight:700, textTransform:'uppercase',
            letterSpacing:'.06em', color:c.text }}>Clinical risk level</span>
          <span style={{ fontSize:22, fontWeight:800, color:c.text }}>{level}</span>
        </div>
        <p style={{ fontSize:13, color:c.text, marginBottom:10 }}>{c.msg}</p>
        <div style={{ background:'rgba(0,0,0,.1)', height:8, borderRadius:4, overflow:'hidden' }}>
          <div style={{
            width:`${Math.min(score/8*100,100)}%`, height:'100%',
            background:c.text==='#fff'?'rgba(255,255,255,.5)':c.text,
            borderRadius:4, transition:'width .4s ease'
          }}/>
        </div>
        <div style={{ fontSize:11, color:c.text, marginTop:4 }}>
          Risk score: {score} / 8+ &nbsp;|&nbsp;
          {result?.trigger_chw_alert ? '🚨 CHW alert active' : '✓ No alert needed'} &nbsp;|&nbsp;
          {result?.trigger_referral  ? '🏥 Referral generated' : 'No referral'}
        </div>
      </div>
    </div>
  )
}