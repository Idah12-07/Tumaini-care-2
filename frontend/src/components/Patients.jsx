// TUMAINI CARE — Patients Component
import { useState, useEffect } from 'react'

const API = 'https://tumaini-care.onrender.com'

const RISK_COLORS = {
  HIGH:      { bg:'#FCEBEB', text:'#A32D2D', border:'#E24B4A' },
  EMERGENCY: { bg:'#A32D2D', text:'#fff',    border:'#791F1F' },
  MODERATE:  { bg:'#FAEEDA', text:'#854F0B', border:'#EF9F27' },
  LOW:       { bg:'#E1F5EE', text:'#0F6E56', border:'#1D9E75' },
}

const STATIC_PATIENTS = [
  { patient_id:'TUM0001', first_name:'Auma M.',    age:39, county:'Nakuru',   epl_type:'Spontaneous m/c (incomplete)', channel:'SMS',      language_pref:'English', day_post_loss_today:14, risk:'HIGH' },
  { patient_id:'TUM0002', first_name:'Njeri A.',   age:16, county:'Siaya',    epl_type:'Missed miscarriage',           channel:'SMS',      language_pref:'English', day_post_loss_today:13, risk:'MODERATE' },
  { patient_id:'TUM0003', first_name:'Grace G.',   age:33, county:'Migori',   epl_type:'Spontaneous m/c (incomplete)', channel:'WhatsApp', language_pref:'English', day_post_loss_today:14, risk:'HIGH' },
  { patient_id:'TUM0004', first_name:'Zainab H.',  age:37, county:'Siaya',    epl_type:'Missed miscarriage',           channel:'WhatsApp', language_pref:'Swahili', day_post_loss_today:14, risk:'MODERATE' },
  { patient_id:'TUM0005', first_name:'Grace N.',   age:38, county:'Vihiga',   epl_type:'Spontaneous m/c (incomplete)', channel:'WhatsApp', language_pref:'Swahili', day_post_loss_today:14, risk:'HIGH' },
  { patient_id:'TUM0006', first_name:'Njeri M.',   age:19, county:'Kisumu',   epl_type:'Spontaneous m/c (incomplete)', channel:'SMS',      language_pref:'English', day_post_loss_today:13, risk:'HIGH' },
  { patient_id:'TUM0007', first_name:'Beatrice O.',age:30, county:'Migori',   epl_type:'Spontaneous m/c (incomplete)', channel:'SMS',      language_pref:'Swahili', day_post_loss_today:14, risk:'LOW' },
  { patient_id:'TUM0008', first_name:'Lydia M.',   age:27, county:'Nakuru',   epl_type:'Ectopic pregnancy',            channel:'SMS',      language_pref:'Swahili', day_post_loss_today:13, risk:'LOW' },
  { patient_id:'TUM0009', first_name:'Fatuma A.',  age:24, county:'Vihiga',   epl_type:'Chemical pregnancy',           channel:'WhatsApp', language_pref:'Swahili', day_post_loss_today:7,  risk:'LOW' },
  { patient_id:'TUM0010', first_name:'Esther K.',  age:31, county:'Bungoma',  epl_type:'Missed miscarriage',           channel:'USSD',     language_pref:'Swahili', day_post_loss_today:10, risk:'MODERATE' },
]

const channelColor = { WhatsApp:'#25D366', SMS:'#185FA5', USSD:'#854F0B' }

export function Patients() {
  const [patients, setPatients] = useState(STATIC_PATIENTS)
  const [search, setSearch]     = useState('')
  const [filter, setFilter]     = useState('ALL')

  useEffect(() => {
    fetch(`${API}/api/patients/list`).then(r=>r.json()).then(d=>{
      if (d.patients?.length) setPatients(d.patients)
    }).catch(()=>{})
  }, [])

  const visible = patients
    .filter(p => filter === 'ALL' || p.risk === filter)
    .filter(p =>
      p.first_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.county?.toLowerCase().includes(search.toLowerCase()) ||
      p.patient_id?.toLowerCase().includes(search.toLowerCase())
    )

  return (
    <div>
      {/* Controls */}
      <div style={{ display:'flex', gap:8, marginBottom:12, flexWrap:'wrap' }}>
        <input
          value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search by name, county or ID..."
          style={{ flex:1, minWidth:180, fontSize:13, padding:'.5rem .85rem',
            border:'.5px solid #D3D1C7', borderRadius:8, outline:'none' }}
        />
        {['ALL','HIGH','EMERGENCY','MODERATE','LOW'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            fontSize:11, padding:'4px 10px', borderRadius:20,
            border:`.5px solid ${filter===f?'#0F6E56':'#D3D1C7'}`,
            background: filter===f ? '#0F6E56' : '#fff',
            color: filter===f ? '#fff' : '#5F5E5A', cursor:'pointer'
          }}>{f}</button>
        ))}
      </div>

      <div style={{ fontSize:12, color:'#9E9C94', marginBottom:8 }}>
        Showing {visible.length} of {patients.length} enrolled women
      </div>

      {/* Table */}
      <div style={{ overflowX:'auto' }}>
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:12 }}>
          <thead>
            <tr style={{ borderBottom:'1px solid #E8E6DE' }}>
              {['ID','Name','Age','County','EPL Type','Channel','Language','Day','Last Risk'].map(h => (
                <th key={h} style={{ textAlign:'left', padding:'7px 8px', fontWeight:600,
                  fontSize:10, color:'#9E9C94', textTransform:'uppercase',
                  letterSpacing:'.04em', whiteSpace:'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((p, i) => {
              const rs = RISK_COLORS[p.risk] || RISK_COLORS.LOW
              return (
                <tr key={p.patient_id} style={{
                  borderBottom:'.5px solid #F1EFE8',
                  background: i%2===0 ? '#fff' : '#FAFAF8'
                }}>
                  <td style={{ padding:'8px 8px', fontFamily:'monospace',
                    fontSize:10, color:'#9E9C94' }}>{p.patient_id}</td>
                  <td style={{ padding:'8px 8px', fontWeight:600, color:'#1a1a1a',
                    whiteSpace:'nowrap' }}>{p.first_name}</td>
                  <td style={{ padding:'8px 8px', color:'#5F5E5A' }}>{p.age}</td>
                  <td style={{ padding:'8px 8px', color:'#5F5E5A' }}>{p.county}</td>
                  <td style={{ padding:'8px 8px', color:'#5F5E5A', fontSize:11 }}>
                    {p.epl_type?.replace('miscarriage','m/c').replace('pregnancy','preg')}
                  </td>
                  <td style={{ padding:'8px 8px' }}>
                    <span style={{ fontSize:10, fontWeight:600, padding:'2px 7px',
                      borderRadius:5, color:'#fff',
                      background: channelColor[p.channel] || '#9E9C94' }}>
                      {p.channel}
                    </span>
                  </td>
                  <td style={{ padding:'8px 8px', color:'#5F5E5A', fontSize:11 }}>
                    {p.language_pref}
                  </td>
                  <td style={{ padding:'8px 8px', color:'#5F5E5A', textAlign:'center' }}>
                    {p.day_post_loss_today}
                  </td>
                  <td style={{ padding:'8px 8px' }}>
                    <span style={{
                      fontSize:10, fontWeight:700, padding:'2px 8px', borderRadius:5,
                      background:rs.bg, color:rs.text, border:`1px solid ${rs.border}`
                    }}>{p.risk}</span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop:10, fontSize:11, color:'#9E9C94' }}>

      </div>
    </div>
  )
}
