// TUMAINI CARE — Patient Enrolment Form v2
// - All 47 Kenya counties + subcounties
// - Self-enrolment supported (no hospital required)
// - EPL type optional (home loss supported)
import { useState } from 'react'
import { KENYA_COUNTIES, COUNTY_NAMES } from '../utils/KenyaCounties'

const API = 'https://tumaini-care.onrender.com'

const EPL_TYPES = [
  { value: 'Not sure — loss happened at home',       label: 'Not sure — loss happened at home', note: 'Common — woman can self-enrol' },
  { value: 'Spontaneous miscarriage (incomplete)',    label: 'Spontaneous miscarriage (incomplete)', note: 'Facility diagnosed' },
  { value: 'Spontaneous miscarriage (complete)',      label: 'Spontaneous miscarriage (complete)', note: 'Facility diagnosed' },
  { value: 'Missed miscarriage',                      label: 'Missed miscarriage', note: 'Facility diagnosed' },
  { value: 'Ectopic pregnancy',                       label: 'Ectopic pregnancy', note: 'Requires urgent care' },
  { value: 'Chemical pregnancy',                      label: 'Chemical pregnancy', note: 'Very early loss' },
  { value: 'Molar pregnancy',                         label: 'Molar pregnancy', note: 'Requires follow-up' },
]

const CHANNELS  = [
  { id:'WhatsApp', note:'Needs internet' },
  { id:'SMS',      note:'No data needed' },
  { id:'USSD',     note:'Zero cost' },
]
const LANGUAGES = ['Swahili','English','Swahili+English mix','Local dialect']
const CHW_IDS   = Array.from({length:20}, (_,i) => `CHW${String(i+1).padStart(3,'0')}`)

const ENROLLED_BY = [
  'Self (woman enrolled herself)',
  'Community Health Worker (CHW)',
  'Facility nurse / midwife',
  'Family member',
]

const FIELD = ({label, required, note, children}) => (
  <div style={{marginBottom:14}}>
    <label style={{display:'block',fontSize:12,fontWeight:500,
      color:'var(--color-text-secondary)',marginBottom:4}}>
      {label}
      {required && <span style={{color:'var(--color-text-danger)'}}> *</span>}
      {note && <span style={{fontSize:11,color:'var(--color-text-tertiary)',
        fontWeight:400,marginLeft:6}}>{note}</span>}
    </label>
    {children}
  </div>
)

const INPUT = (props) => (
  <input {...props} style={{width:'100%',fontSize:13,padding:'.55rem .85rem',
    border:'.5px solid var(--color-border-secondary)',borderRadius:8,
    background:'var(--color-background-primary)',
    color:'var(--color-text-primary)',outline:'none',...props.style}}/>
)

const SELECT = ({children,...props}) => (
  <select {...props} style={{width:'100%',fontSize:13,padding:'.55rem .85rem',
    border:'.5px solid var(--color-border-secondary)',borderRadius:8,
    background:'var(--color-background-primary)',
    color:'var(--color-text-primary)',outline:'none'}}>
    {children}
  </select>
)

const EMPTY = {
  phone_number:'',first_name:'',last_name_initial:'',age:'',
  county:'',sub_county:'',rural:true,
  epl_type:'Not sure — loss happened at home',
  gestational_age_weeks:'',date_of_loss:'',
  parity:'0',prior_losses:'0',facility_of_diagnosis:'',
  enrolled_by:'Self (woman enrolled herself)',
  channel:'SMS',language_pref:'Swahili',chw_id:'CHW001',
  consent_given:false,
}

export default function EnrolmentForm({onSuccess}) {
  const [form, setForm]     = useState(EMPTY)
  const [submitting, setSub] = useState(false)
  const [result, setResult] = useState(null)
  const [step, setStep]     = useState(1)

  const set = (k,v) => setForm(f=>({...f,[k]:v}))

  const subcounties = form.county ? (KENYA_COUNTIES[form.county] || []) : []

  const validate = () => {
    if (!form.phone_number)    return 'Phone number is required'
    if (!form.first_name)      return 'First name is required'
    if (!form.last_name_initial) return 'Last name initial is required'
    if (!form.age || form.age < 10 || form.age > 60) return 'Valid age (10–60) required'
    if (!form.county)          return 'County is required'
    if (!form.date_of_loss)    return 'Date of loss is required (approximate is fine)'
    if (!form.consent_given)   return 'Informed consent must be confirmed'
    return null
  }

  const submit = async () => {
    const err = validate()
    if (err) { setResult({success:false,error:err}); return }
    setSub(true); setResult(null)
    try {
      const res = await fetch(`${API}/api/patients/enrol`,{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          ...form,
          age: parseInt(form.age),
          gestational_age_weeks: form.gestational_age_weeks ? parseInt(form.gestational_age_weeks) : null,
          parity: parseInt(form.parity)||0,
          prior_losses: parseInt(form.prior_losses)||0,
        })
      })
      const data = await res.json()
      if (res.ok) {
        setResult({success:true,patient_id:data.patient_id})
        setForm(EMPTY); setStep(1)
        if (onSuccess) onSuccess(data)
      } else {
        setResult({success:false,error:data.detail||'Enrolment failed — check all required fields'})
      }
    } catch(e) {
      setResult({success:false,error:'Cannot reach backend server. Is uvicorn running? Check your terminal.'})
    }
    setSub(false)
  }

  const steps = ['Identity','Clinical','Contact','Confirm']

  return (
    <div style={{maxWidth:620}}>

      {/* Self-enrolment notice */}
      <div style={{background:'var(--color-background-info)',border:'.5px solid var(--color-border-info)',
        borderRadius:10,padding:'.75rem 1rem',marginBottom:16,fontSize:12,
        color:'var(--color-text-info)'}}>
        <strong>Who can enrol?</strong> Any woman who has experienced pregnancy loss —
        whether at a facility or at home. Hospital visit not required.
        A CHW, nurse, or the woman herself can fill in this form.
      </div>

      {/* Step indicator */}
      <div style={{display:'flex',marginBottom:20}}>
        {steps.map((s,i) => (
          <div key={s} style={{flex:1,textAlign:'center'}}>
            <div style={{
              width:28,height:28,borderRadius:'50%',margin:'0 auto 4px',
              display:'flex',alignItems:'center',justifyContent:'center',
              fontSize:12,fontWeight:600,cursor: i<step?'pointer':'default',
              background: step===i+1?'#0F6E56':step>i+1?'#1D9E75':'var(--color-background-secondary)',
              color: step>=i+1?'#fff':'var(--color-text-tertiary)',
              border: step===i+1?'none':'.5px solid var(--color-border-tertiary)'
            }} onClick={()=>i<step&&setStep(i+1)}>
              {step>i+1?'✓':i+1}
            </div>
            <div style={{fontSize:10,
              color:step===i+1?'#0F6E56':'var(--color-text-tertiary)',
              fontWeight:step===i+1?600:400}}>{s}</div>
          </div>
        ))}
      </div>

      {/* Result */}
      {result && (
        <div style={{padding:'.75rem 1rem',borderRadius:8,marginBottom:14,fontSize:13,
          background:result.success?'var(--color-background-success)':'var(--color-background-danger)',
          border:`.5px solid ${result.success?'var(--color-border-success)':'var(--color-border-danger)'}`,
          color:result.success?'var(--color-text-success)':'var(--color-text-danger)'}}>
          {result.success
            ? `✅ Enrolled! Patient ID: ${result.patient_id} — Monitoring begins today.`
            : `⚠️ ${result.error}`}
        </div>
      )}

      {/* STEP 1 — Identity */}
      {step===1 && (
        <div>
          <FIELD label="Enrolled by">
            <SELECT value={form.enrolled_by} onChange={e=>set('enrolled_by',e.target.value)}>
              {ENROLLED_BY.map(e=><option key={e}>{e}</option>)}
            </SELECT>
          </FIELD>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
            <FIELD label="Phone number" required note="Will be hashed for privacy">
              <INPUT type="tel" placeholder="0712345678"
                value={form.phone_number} onChange={e=>set('phone_number',e.target.value)}/>
            </FIELD>
            <FIELD label="Age" required>
              <INPUT type="number" placeholder="e.g. 24" min="10" max="60"
                value={form.age} onChange={e=>set('age',e.target.value)}/>
            </FIELD>
            <FIELD label="First name" required>
              <INPUT placeholder="e.g. Auma"
                value={form.first_name} onChange={e=>set('first_name',e.target.value)}/>
            </FIELD>
            <FIELD label="Last name initial" required>
              <INPUT placeholder="e.g. O" maxLength={1}
                value={form.last_name_initial} onChange={e=>set('last_name_initial',e.target.value)}/>
            </FIELD>
            <FIELD label="County" required>
              <SELECT value={form.county} onChange={e=>{set('county',e.target.value);set('sub_county','')}}>
                <option value="">Select county...</option>
                {COUNTY_NAMES.map(c=><option key={c}>{c}</option>)}
              </SELECT>
            </FIELD>
            <FIELD label="Sub-county" note={!form.county?'Select county first':''}>
              <SELECT value={form.sub_county} onChange={e=>set('sub_county',e.target.value)}
                disabled={!form.county}>
                <option value="">Select sub-county...</option>
                {subcounties.map(s=><option key={s}>{s}</option>)}
              </SELECT>
            </FIELD>
          </div>
          <FIELD label="Location">
            <div style={{display:'flex',gap:16,marginTop:4}}>
              {['Rural','Urban'].map(l=>(
                <label key={l} style={{display:'flex',alignItems:'center',gap:6,
                  fontSize:13,cursor:'pointer'}}>
                  <input type="radio" name="rural"
                    checked={form.rural===(l==='Rural')}
                    onChange={()=>set('rural',l==='Rural')}/>
                  {l}
                </label>
              ))}
            </div>
          </FIELD>
        </div>
      )}

      {/* STEP 2 — Clinical */}
      {step===2 && (
        <div>
          <div style={{background:'var(--color-background-warning)',border:'.5px solid var(--color-border-warning)',
            borderRadius:8,padding:'.65rem 1rem',marginBottom:14,fontSize:12,color:'var(--color-text-warning)'}}>
            If the woman is unsure of her EPL type — perhaps the loss happened at home —
            select "Not sure". She can still be enrolled and monitored.
          </div>
          <FIELD label="Type of pregnancy loss" note="Optional if not diagnosed at facility">
            <SELECT value={form.epl_type} onChange={e=>set('epl_type',e.target.value)}>
              {EPL_TYPES.map(t=>(
                <option key={t.value} value={t.value}>{t.label} — {t.note}</option>
              ))}
            </SELECT>
          </FIELD>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
            <FIELD label="Date of loss" required note="Approximate date is fine">
              <INPUT type="date" value={form.date_of_loss}
                onChange={e=>set('date_of_loss',e.target.value)}/>
            </FIELD>
            <FIELD label="Weeks pregnant (if known)" note="Optional">
              <INPUT type="number" placeholder="e.g. 8" min="4" max="20"
                value={form.gestational_age_weeks}
                onChange={e=>set('gestational_age_weeks',e.target.value)}/>
            </FIELD>
            <FIELD label="Previous births (parity)">
              <INPUT type="number" placeholder="0" min="0" max="15"
                value={form.parity} onChange={e=>set('parity',e.target.value)}/>
            </FIELD>
            <FIELD label="Previous pregnancy losses">
              <INPUT type="number" placeholder="0" min="0" max="10"
                value={form.prior_losses} onChange={e=>set('prior_losses',e.target.value)}/>
            </FIELD>
          </div>
          <FIELD label="Facility of diagnosis" note="Leave blank if loss was at home">
            <INPUT placeholder="e.g. Kisumu County Referral Hospital"
              value={form.facility_of_diagnosis}
              onChange={e=>set('facility_of_diagnosis',e.target.value)}/>
          </FIELD>
        </div>
      )}

      {/* STEP 3 — Contact + System */}
      {step===3 && (
        <div>
          <FIELD label="How should Tumaini contact her?" required>
            <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:8}}>
              {CHANNELS.map(ch=>(
                <div key={ch.id} onClick={()=>set('channel',ch.id)} style={{
                  padding:'.75rem',borderRadius:8,textAlign:'center',cursor:'pointer',
                  border:`1.5px solid ${form.channel===ch.id?'#0F6E56':'var(--color-border-tertiary)'}`,
                  background:form.channel===ch.id?'#E1F5EE':'var(--color-background-primary)'}}>
                  <div style={{fontSize:13,fontWeight:600,
                    color:form.channel===ch.id?'#0F6E56':'var(--color-text-primary)'}}>{ch.id}</div>
                  <div style={{fontSize:10,color:'var(--color-text-tertiary)',marginTop:2}}>{ch.note}</div>
                </div>
              ))}
            </div>
          </FIELD>
          <FIELD label="Language preference">
            <SELECT value={form.language_pref} onChange={e=>set('language_pref',e.target.value)}>
              {LANGUAGES.map(l=><option key={l}>{l}</option>)}
            </SELECT>
          </FIELD>
          <FIELD label="Assigned CHW" required note="The CHW who will receive alerts for this woman">
            <SELECT value={form.chw_id} onChange={e=>set('chw_id',e.target.value)}>
              {CHW_IDS.map(c=><option key={c}>{c}</option>)}
            </SELECT>
          </FIELD>
        </div>
      )}

      {/* STEP 4 — Consent + confirm */}
      {step===4 && (
        <div>
          <div style={{background:'var(--color-background-secondary)',borderRadius:10,
            padding:'1rem',marginBottom:14,fontSize:12,
            color:'var(--color-text-secondary)',lineHeight:1.7}}>
            <strong style={{color:'var(--color-text-primary)',display:'block',marginBottom:6}}>
              Enrolment summary
            </strong>
            <strong>{form.first_name} {form.last_name_initial}.</strong> · Age {form.age} · {form.county}{form.sub_county?`, ${form.sub_county}`:''} · {form.rural?'Rural':'Urban'}<br/>
            EPL: {form.epl_type}<br/>
            Date of loss: {form.date_of_loss || 'Not specified'}<br/>
            Contact: {form.channel} · {form.language_pref} · CHW: {form.chw_id}<br/>
            Enrolled by: {form.enrolled_by}
          </div>

          <div style={{background:'#FAEEDA',border:'.5px solid #EF9F27',
            borderRadius:8,padding:'1rem',marginBottom:14}}>
            <div style={{fontSize:12,fontWeight:600,color:'#854F0B',marginBottom:6}}>
              Read this consent statement to the woman before enrolling:
            </div>
            <div style={{fontSize:12,color:'#854F0B',lineHeight:1.8}}>
              <strong>Swahili:</strong> "Tumaini ni mfumo wa kufuatilia afya yako baada ya kupoteza mimba.
              Tutakutumia ujumbe kila siku kwa siku 14 kuuliza kuhusu hali yako ya kimwili na kihisia.
              Taarifa yako italindwa na haitashirikiwa bila idhini yako.
              Unaweza kuacha wakati wowote kwa kutuma neno STOP."<br/><br/>
              <strong>English:</strong> "Tumaini is a system to support your health after pregnancy loss.
              We will message you daily for 14 days about how you are feeling physically and emotionally.
              Your information is protected and will not be shared without your consent.
              You may withdraw at any time by sending the word STOP."
            </div>
          </div>

          <label style={{display:'flex',alignItems:'flex-start',gap:10,cursor:'pointer',fontSize:13}}>
            <input type="checkbox" checked={form.consent_given}
              onChange={e=>set('consent_given',e.target.checked)}
              style={{marginTop:3,flexShrink:0}}/>
            <span style={{color:'var(--color-text-primary)',lineHeight:1.6}}>
              I confirm that the consent statement was read to the woman in her preferred language
              and she has agreed to participate in Tumaini monitoring.
            </span>
          </label>
        </div>
      )}

      {/* Navigation */}
      <div style={{display:'flex',justifyContent:'space-between',marginTop:20,gap:8}}>
        <button onClick={()=>setStep(s=>Math.max(1,s-1))} disabled={step===1} style={{
          padding:'.6rem 1.25rem',border:'.5px solid var(--color-border-secondary)',
          borderRadius:8,background:'none',fontSize:13,
          color:'var(--color-text-secondary)',cursor:step===1?'not-allowed':'pointer',
          opacity:step===1?0.4:1}}>← Back</button>

        {step<4
          ? <button onClick={()=>setStep(s=>s+1)} style={{
              padding:'.6rem 1.5rem',background:'#0F6E56',color:'#fff',
              border:'none',borderRadius:8,fontSize:13,fontWeight:600,cursor:'pointer'}}>
              Next →
            </button>
          : <button onClick={submit} disabled={submitting||!form.consent_given} style={{
              padding:'.6rem 1.5rem',
              background:submitting||!form.consent_given?'#9E9C94':'#0F6E56',
              color:'#fff',border:'none',borderRadius:8,fontSize:13,fontWeight:600,
              cursor:submitting||!form.consent_given?'not-allowed':'pointer'}}>
              {submitting?'Enrolling...':'✓ Enrol Patient'}
            </button>
        }
      </div>
    </div>
  )
}