// TODO: Companion component
// TUMAINI CARE — AI Grief Companion Component
// Live Claude-powered bilingual (Swahili/English) grief companion
import { useState, useRef, useEffect } from 'react'

const API = 'https://tumaini-care.onrender.com'

const QUICK_MSGS = [
  'Sijui kwa nini hii ilitokea kwangu',
  'I feel so alone, nobody understands',
  'Damu nyingi sana leo, ninaogopa',
  'My family says it was my fault',
  'Ninahisi maumivu upande wa kulia',
  'I cannot stop thinking about my baby',
]

const DANGER_WORDS = [
  'damu nyingi','heavy bleeding','harufu mbaya','foul',
  'maumivu makali','severe pain','upande wa kulia','right side',
  'homa','fever','kizunguzungu','fainting'
]

const isDanger = (text) =>
  DANGER_WORDS.some(w => text.toLowerCase().includes(w))

export default function Companion() {
  const [msgs, setMsgs]     = useState([{
    role: 'assistant',
    content: 'Habari. Mimi ni Tumaini — companion wako katika wakati huu mgumu.\n\nHello. I am Tumaini — your companion during this difficult time. I am here with you. How are you feeling today?'
  }])
  const [input, setInput]   = useState('')
  const [loading, setLoading] = useState(false)
  const [alert, setAlert]   = useState(null)
  const [apiOk, setApiOk]   = useState(null)
  const bottomRef = useRef(null)

  // Check if backend is reachable
  useEffect(() => {
    fetch(`${API}/health`).then(() => setApiOk(true)).catch(() => setApiOk(false))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs])

  const send = async (text) => {
    if (!text.trim() || loading) return
    const userMsg = { role: 'user', content: text }
    const newMsgs = [...msgs, userMsg]
    setMsgs(newMsgs)
    setInput('')
    setLoading(true)
    setAlert(null)

    if (isDanger(text)) {
      setAlert({ type: 'emergency',
        text: '⚠️ Danger signs detected — CHW alert triggered. Please go to your nearest health facility immediately.' })
    }

    try {
      const res = await fetch(`${API}/api/companion/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: 'TUM0001',
          message: text,
          language: 'auto',
          conversation_history: newMsgs.slice(-6).map(m => ({
            role: m.role, content: m.content
          }))
        })
      })
      const data = await res.json()
      setMsgs(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setMsgs(prev => [...prev, {
        role: 'assistant',
        content: 'Samahani, kuna tatizo la mtandao. / Sorry, connection error. Please try again.'
      }])
    }
    setLoading(false)
  }

  return (
    <div style={{ display:'flex', flexDirection:'column', height: 560 }}>

      {/* Status bar */}
      <div style={{
        borderRadius: 10, padding: '.55rem 1rem', marginBottom: 8,
        fontSize: 12, display:'flex', justifyContent:'space-between', alignItems:'center',
        background: apiOk === false ? '#FCEBEB' : '#E1F5EE',
        border: `.5px solid ${apiOk === false ? '#E24B4A' : '#1D9E75'}`,
        color: apiOk === false ? '#A32D2D' : '#0F6E56'
      }}>
        <span>
          {apiOk === null && '⟳ Connecting to Tumaini AI...'}
          {apiOk === true && '🟢 Live — Claude AI active · Swahili & English'}
          {apiOk === false && '🔴 Backend offline — start uvicorn to enable live AI'}
        </span>
        <span style={{ fontSize:11, opacity:.7 }}>Patient: TUM0001</span>
      </div>

      {/* Danger alert */}
      {alert && (
        <div style={{
          background: '#FCEBEB', border: '.5px solid #E24B4A', borderRadius: 8,
          padding: '.6rem 1rem', marginBottom: 8, fontSize: 12,
          color: '#A32D2D', fontWeight: 600
        }}>
          {alert.text}
        </div>
      )}

      {/* Chat messages */}
      <div style={{ flex:1, overflowY:'auto', display:'flex',
        flexDirection:'column', gap:10, paddingRight:4 }}>
        {msgs.map((m, i) => (
          <div key={i} style={{
            display:'flex', justifyContent: m.role==='user' ? 'flex-end' : 'flex-start',
            alignItems:'flex-end', gap:8
          }}>
            {m.role === 'assistant' && (
              <div style={{
                width:30, height:30, borderRadius:'50%', background:'#0F6E56',
                display:'flex', alignItems:'center', justifyContent:'center',
                fontSize:14, color:'#fff', flexShrink:0
              }}>🌱</div>
            )}
            <div style={{
              maxWidth:'74%', fontSize:13, lineHeight:1.65,
              padding:'.65rem .95rem', borderRadius:14, whiteSpace:'pre-wrap',
              background: m.role==='user' ? '#0F6E56' : '#fff',
              color: m.role==='user' ? '#fff' : '#1a1a1a',
              border: m.role==='assistant' ? '.5px solid #E8E6DE' : 'none',
              borderBottomRightRadius: m.role==='user' ? 2 : 14,
              borderBottomLeftRadius:  m.role==='assistant' ? 2 : 14,
              boxShadow: '0 1px 4px rgba(0,0,0,.05)'
            }}>
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <div style={{ width:30, height:30, borderRadius:'50%', background:'#0F6E56',
              display:'flex', alignItems:'center', justifyContent:'center', fontSize:14 }}>🌱</div>
            <div style={{ background:'#fff', border:'.5px solid #E8E6DE',
              borderRadius:14, borderBottomLeftRadius:2,
              padding:'.65rem .95rem', fontSize:13, color:'#9E9C94' }}>
              Tumaini inaandika... / Tumaini is typing...
            </div>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      {/* Quick messages */}
      <div style={{ display:'flex', flexWrap:'wrap', gap:6, margin:'10px 0 8px' }}>
        {QUICK_MSGS.map(q => (
          <button key={q} onClick={() => send(q)} disabled={loading} style={{
            fontSize:11, padding:'4px 10px', border:'.5px solid #D3D1C7',
            borderRadius:20, background:'#fff', color:'#5F5E5A',
            cursor:'pointer', transition:'all .15s'
          }}>
            {q.length > 32 ? q.slice(0,32)+'…' : q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div style={{ display:'flex', gap:8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key==='Enter' && send(input)}
          placeholder="Type in English or Swahili…"
          disabled={loading}
          style={{
            flex:1, fontSize:13, padding:'.65rem 1rem',
            border:'.5px solid #D3D1C7', borderRadius:10,
            background:'#fff', color:'#1a1a1a', outline:'none'
          }}
        />
        <button onClick={() => send(input)} disabled={loading} style={{
          padding:'.65rem 1.25rem', background: loading ? '#9E9C94' : '#0F6E56',
          color:'#fff', border:'none', borderRadius:10,
          fontSize:13, fontWeight:600, cursor: loading ? 'not-allowed' : 'pointer'
        }}>
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}