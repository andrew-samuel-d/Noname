import React, { useState, useEffect, useRef, useMemo } from 'react';

    /* ── Business Presets (Real-world Credit-Invisible MSMEs: Kirana, Tailor, Repair) ── */
    const PRESETS = [
      { id: 'prime', label: 'Sharma Kirana Store', sub: 'Credit-Invisible • High UPI • 6 yrs', tier: 'low', data: { business_age_years:6, monthly_upi_volume:420000, monthly_bank_volume:1800000, monthly_cash_volume:110000, gst_filing_regularity:96, gst_turnover:18000000, bounce_frequency:0, avg_monthly_balance:650000, income_stability:92, seasonality_score:80, loan_default_history:'unknown' }},
      { id: 'women', label: 'Meera Tailoring & Boutique', sub: 'Women-Owned MSME • 4 yrs (SIDBI 35% Gap)', tier: 'mod', data: { business_age_years:4, monthly_upi_volume:210000, monthly_bank_volume:850000, monthly_cash_volume:50000, gst_filing_regularity:88, gst_turnover:7200000, bounce_frequency:0, avg_monthly_balance:240000, income_stability:78, seasonality_score:65, loan_default_history:'unknown' }},
      { id: 'repair', label: 'Apex Auto Repair Unit', sub: 'Small Repair Shop • 2 yrs • Zero Collateral', tier: 'mod', data: { business_age_years:2, monthly_upi_volume:150000, monthly_bank_volume:550000, monthly_cash_volume:45000, gst_filing_regularity:78, gst_turnover:4200000, bounce_frequency:1, avg_monthly_balance:130000, income_stability:64, seasonality_score:58, loan_default_history:'unknown' }},
      { id: 'stressed', label: 'Gupta General Trading', sub: 'High Risk • 1 yr • Frequent Bounces', tier: 'high', data: { business_age_years:1, monthly_upi_volume:35000, monthly_bank_volume:140000, monthly_cash_volume:40000, gst_filing_regularity:50, gst_turnover:1100000, bounce_frequency:6, avg_monthly_balance:20000, income_stability:38, seasonality_score:30, loan_default_history:1 }},
    ];

    /* ── Icons ── */
    const Icons = {
      chart: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m7 14 4-4 4 4 5-5" strokeLinecap="round" strokeLinejoin="round"/></svg>,
      user: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
      file: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8"/></svg>,
      layers: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>,
      shield: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
      check: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>,
      x: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
      upload: <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
      download: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
      zap: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
      wifi: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>,
      wifiOff: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/><path d="M10.71 5.05A16 16 0 0 1 22.56 9"/><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>,
      activity: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>,
      arrowRight: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>,
      printer: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>,
      sliders: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>
    };

    /* ── Helpers ── */
    const fmt = (n) => Number(n||0).toLocaleString('en-IN');

    /* ── Score Gauge ── */
    function ScoreGauge({ score, size=180 }) {
      const r = (size - 22) / 2;
      const circ = 2 * Math.PI * r;
      const pct = Math.max(0, Math.min(100, score)) / 100;
      const offset = circ * (1 - pct);
      const color = score >= 75 ? '#16a34a' : score >= 50 ? '#d97706' : '#dc2626';
      return (
        <div className="relative inline-flex items-center justify-center shrink-0" style={{width:size,height:size}}>
          <svg width={size} height={size} className="transform -rotate-90">
            <circle cx={size/2} cy={size/2} r={r} stroke="#f1f5f9" strokeWidth="11" fill="transparent" />
            <circle cx={size/2} cy={size/2} r={r} stroke={color} strokeWidth="11" strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" fill="transparent" className="gauge-ring" />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-5xl font-black font-mono leading-none tracking-tight" style={{color}}>{score}</span>
            <span className="text-[11px] text-surface-400 font-semibold mt-1 tracking-wider uppercase">Score / 100</span>
          </div>
        </div>
      );
    }

    function Stat({ label, value, sub, accent }) {
      return (
        <div className="flex flex-col">
          <span className="text-[10px] font-semibold text-surface-400 uppercase tracking-wider">{label}</span>
          <span className={`text-base font-bold font-mono ${accent || 'text-surface-900'}`}>{value}</span>
          {sub && <span className="text-[10px] text-surface-400 mt-0.5">{sub}</span>}
        </div>
      );
    }

    function Field({ label, value, onChange, prefix, suffix, type='number', options, action }) {
      if (options) {
        return (
          <div className="field-group">
            <div className="flex justify-between items-center mb-1">
              <label className="block text-[11px] font-semibold text-surface-600">{label}</label>
              {action}
            </div>
            <select value={value} onChange={e => onChange(e.target.value === 'unknown' ? 'unknown' : (parseFloat(e.target.value)||0))} className="w-full bg-white border border-surface-200 rounded-lg px-3 py-2 text-xs font-mono text-surface-800 focus:outline-none transition">
              {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        );
      }
      return (
        <div className="field-group">
          <div className="flex justify-between items-center mb-1">
            <label className="block text-[11px] font-semibold text-surface-600">{label}</label>
            {action}
          </div>
          <div className="relative">
            {prefix && <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-surface-400 font-medium">{prefix}</span>}
            <input type={type} value={value} onChange={e => onChange(parseFloat(e.target.value)||0)} className={`w-full bg-white border border-surface-200 rounded-lg ${prefix ? 'pl-6' : 'px-2.5'} ${suffix ? 'pr-9' : 'px-2.5'} py-2 text-xs font-mono text-surface-800 focus:outline-none transition`} />
            {suffix && <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-surface-400 font-medium">{suffix}</span>}
          </div>
        </div>
      );
    }

    /* ═══════════════════════════════════════════════════
       OFFICIAL SANCTION LETTER MODAL COMPONENT
       ═══════════════════════════════════════════════════ */
    function SanctionLetterModal({ isOpen, onClose, result, borrowerName, requestedAmount, formData }) {
      if (!isOpen || !result || !result.credit_terms || !result.credit_terms.eligible) return null;

      const ct = result.credit_terms;
      const loanAmount = requestedAmount || ct.max_credit_limit_inr;
      const rate = ct.interest_rate_pct;
      const tenure = ct.tenure_months;
      const mRate = (rate / 100) / 12;
      const emi = Math.round(loanAmount * (mRate * Math.pow(1 + mRate, tenure)) / (Math.pow(1 + mRate, tenure) - 1));
      const edi = Math.round(emi / 25);
      const dateStr = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
      const sanctionRef = `CFS/BL/2026/${Math.floor(Math.random() * 89999 + 10000)}`;

      return (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-surface-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl max-w-3xl w-full p-8 shadow-2xl border border-surface-200 my-8">
            {/* Header / Actions */}
            <div className="flex items-center justify-between pb-4 border-b border-surface-100 no-print">
              <span className="text-xs font-bold uppercase tracking-wider text-accent-700 bg-accent-50 px-2.5 py-1 rounded-md border border-accent-200">
                Prototype Loan Scenario — Not an Offer
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.print()}
                  className="px-3.5 py-1.5 rounded-lg bg-surface-900 text-white hover:bg-surface-800 text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  {Icons.printer} Print / Save PDF
                </button>
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg text-surface-400 hover:text-surface-700 hover:bg-surface-100 transition"
                >
                  {Icons.x}
                </button>
              </div>
            </div>

            {/* Printable Sanction Letter Body */}
            <div id="sanction-letter-print" className="mt-4 space-y-5 text-surface-800">
              {/* Institution Header */}
              <div className="flex justify-between items-start border-b border-surface-200 pb-4">
                <div>
                  <h1 className="text-lg font-black tracking-tight text-surface-900">CASHFLOWSCORE PROTOTYPE</h1>
                  <p className="text-[11px] text-surface-500 uppercase tracking-widest font-semibold mt-0.5">Illustrative MSME loan scenario</p>
                  <p className="text-[10px] text-surface-400">Synthetic-data demonstration only</p>
                </div>
                <div className="text-right text-[11px] font-mono">
                  <div className="font-bold text-surface-900">Scenario {sanctionRef}</div>
                  <div className="text-surface-500">{dateStr}</div>
                </div>
              </div>

              {/* Subject */}
              <div className="bg-surface-50 p-3.5 rounded-xl border border-surface-200">
                <div className="text-xs font-bold text-surface-900">
                  SUBJECT: Indicative terms from a synthetic-data prototype
                </div>
                <div className="text-[11px] text-surface-600 mt-1">
                  <span className="font-bold text-surface-900">{borrowerName}</span>: this estimate uses entered features. No bank or GST data was retrieved, and no loan has been approved or sanctioned.
                </div>
              </div>

              {/* Sanction Details Grid */}
              <table className="w-full text-xs border border-surface-200 rounded-lg overflow-hidden">
                <tbody className="divide-y divide-surface-200">
                  <tr className="bg-surface-50/50">
                    <td className="py-2 px-3 font-semibold text-surface-500 w-1/3">Borrower Entity</td>
                    <td className="py-2 px-3 font-bold text-surface-900">{borrowerName} (Vintage: {formData.business_age_years} Years)</td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 font-semibold text-surface-500">Illustrative Loan Amount</td>
                    <td className="py-2 px-3 font-mono font-bold text-accent-700 text-sm">₹{fmt(loanAmount)}</td>
                  </tr>
                  <tr className="bg-surface-50/50">
                    <td className="py-2 px-3 font-semibold text-surface-500">CashFlowScore & Risk Tier</td>
                    <td className="py-2 px-3 font-bold">{result.score}/100 — <span className="text-accent-600">{result.risk_tier}</span></td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 font-semibold text-surface-500">Rate of Interest</td>
                    <td className="py-2 px-3 font-mono font-semibold">{rate}% p.a. (Reducing Balance Basis)</td>
                  </tr>
                  <tr className="bg-surface-50/50">
                    <td className="py-2 px-3 font-semibold text-surface-500">Tenure</td>
                    <td className="py-2 px-3 font-mono">{tenure} Months</td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 font-semibold text-surface-500">Repayment Structure</td>
                    <td className="py-2 px-3 font-mono font-semibold">₹{fmt(emi)} estimated monthly installment</td>
                  </tr>
                  <tr className="bg-surface-50/50">
                    <td className="py-2 px-3 font-semibold text-surface-500">Collection setup</td>
                    <td className="py-2 px-3">{ct.repayment_mode}</td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 font-semibold text-surface-500">Collateral / Security</td>
                    <td className="py-2 px-3 font-medium text-surface-800">{ct.security_type}</td>
                  </tr>
                </tbody>
              </table>

              {/* Special Covenants */}
              <div className="text-[11px] text-surface-600 space-y-1 bg-surface-50 p-3 rounded-lg border border-surface-100">
                <div className="font-bold text-surface-800">Prototype notice:</div>
                <div>These terms are illustrative only. Affordability, collateral, guarantee eligibility, and repayment setup have not been verified.</div>
              </div>

              {/* Signatures */}
              <div className="flex justify-between items-end pt-6 border-t border-surface-200 text-xs">
                <div>
                  <div className="text-[10px] text-amber-700 font-mono">SYNTHETIC PROTOTYPE OUTPUT</div>
                  <div className="font-bold text-surface-700 mt-1">CashFlowScore Demo</div>
                  <div className="text-[10px] text-surface-400">Timestamp: {new Date().toISOString()}</div>
                </div>
                <div className="text-right">
                  <div className="w-36 border-b border-surface-400 mb-1"></div>
                  <div className="font-bold text-surface-800">No lender authorization</div>
                  <div className="text-[10px] text-surface-500">For prototype demonstration only</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    /* ═══════════════════════════════════════════════════
       MAIN APPLICATION
       ═══════════════════════════════════════════════════ */
    function App() {
      const [view, setView] = useState('score');
      const [offline, setOffline] = useState(false);
      const [form, setForm] = useState({...PRESETS[0].data});
      const [activePreset, setActivePreset] = useState('prime');
      const [scoring, setScoring] = useState(false);
      const [result, setResult] = useState(null);
      const [latency, setLatency] = useState(0);

      /* Interactive Loan Sizing Slider State */
      const [adjustedLoanAmount, setAdjustedLoanAmount] = useState(null);

      /* Kafka Real-Time Streaming State */
      const [kafkaStatus, setKafkaStatus] = useState({ cluster_state: 'ACTIVE', active_topics: ['msme.events.upi', 'msme.events.banking', 'msme.events.gst', 'msme.scores.realtime'], throughput_msg_per_sec: 24.5, total_partitions: 16 });
      const [kafkaEvents, setKafkaEvents] = useState([]);

      /* Poll Kafka Stream */
      useEffect(() => {
        let mounted = true;
        const fetchKafka = async () => {
          try {
            const [stRes, evRes] = await Promise.all([
              fetch('/api/kafka/status'),
              fetch('/api/kafka/events?limit=8')
            ]);
            if (stRes.ok && mounted) {
              const st = await stRes.json();
              setKafkaStatus(st);
            }
            if (evRes.ok && mounted) {
              const ev = await evRes.json();
              setKafkaEvents(ev);
            }
          } catch(e) {}
        };
        fetchKafka();
        const interval = setInterval(fetchKafka, 3000);
        return () => { mounted = false; clearInterval(interval); };
      }, []);

      /* Sanction Letter Modal State */
      const [sanctionModalOpen, setSanctionModalOpen] = useState(false);
      const [repaymentScenario, setRepaymentScenario] = useState(null);
      const [consentScopes, setConsentScopes] = useState(() => {
        try { return JSON.parse(localStorage.getItem('cashflowscore_demo_consent') || '[]'); } catch { return []; }
      });

      /* Batch State */
      const [batchWorking, setBatchWorking] = useState(false);
      const [batchDone, setBatchDone] = useState({ name: '', url:'', records:0, approved:0, rejected:0, avg:0, error:'' });

      /* Initial score on load */
      useEffect(() => { doScore(form); }, []);
      useEffect(() => { localStorage.setItem('cashflowscore_demo_consent', JSON.stringify(consentScopes)); }, [consentScopes]);

      const set = (k, v) => setForm(p => ({...p, [k]: v}));

      const doScore = async (data = form) => {
        setScoring(true);
        const t0 = performance.now();
        try {
          if (!offline) {
            const r = await fetch('/score', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
            if (r.ok) {
              const d = await r.json();
              setResult(d);
              setAdjustedLoanAmount(d.credit_terms?.max_credit_limit_inr || 0);
              setLatency(Math.round(performance.now()-t0));
              setScoring(false);
              return;
            }
          }
        } catch(e) {}

        /* Edge offline inference fallback */
        setTimeout(() => {
          const gst=Number(data.gst_filing_regularity||0), inc=Number(data.income_stability||0), age=Number(data.business_age_years||0);
          const bal=Number(data.avg_monthly_balance||0), bnc=Number(data.bounce_frequency||0);
          const historyUnknown=data.loan_default_history==null || String(data.loan_default_history).toLowerCase()==='unknown';
          const def=historyUnknown?0.5:Number(data.loan_default_history||0);
          let raw=(gst*0.25)+(inc*0.25)+(age*2)+(bal/50000)-(bnc*4)-(def*25);
          let prob=1/(1+Math.exp(-(raw-50)/10));
          let score=Math.max(0, Math.min(100, Math.round(prob*100)));
          let reasons = [];
          if (historyUnknown) reasons.push('No formal repayment history; estimate averages both history scenarios');
          if (def===1) reasons.push('Previous loan default recorded');
          if (bnc>3) reasons.push(`High cheque/mandate bounce frequency (${bnc} times)`);
          if (gst<80) reasons.push(`Low GST filing regularity (${gst}%)`);
          if (bal<100000) reasons.push(`Low average monthly balance (₹${fmt(bal)})`);
          if (age<3) reasons.push(`Young business vintage (${age} years)`);
          if (inc<50) reasons.push(`Income stability index is low (${inc})`);
          if (reasons.length===0) {
            if (!historyUnknown) reasons.push('Clean repayment track record with zero defaults');
            reasons.push(`Strong liquidity with ₹${fmt(bal)} avg balance`);
            if (gst>=90) reasons.push('Exceptional tax compliance (95%+ on-time GST)');
            if (age>=5) reasons.push(`Established market vintage (${age} years)`);
          }
          let ct = { eligible:false, max_credit_limit_inr:0, interest_rate_pct:null, tenure_months:0, monthly_emi_inr:0, daily_repayment_inr:0, repayment_mode:'N/A', security_type:'N/A', dscr_estimate:0 };
          if (score >= 50) {
            const upi=Number(data.monthly_upi_volume||0), bnk=Number(data.monthly_bank_volume||0);
            const mult=score>=85?2.5:(score>=70?1.8:1.2), cap=score>=85?2500000:(score>=70?1500000:500000);
            const rawL=Math.max(bal*mult,(upi+bnk)*0.3), cL=Math.round(Math.min(cap,Math.max(50000,rawL))/10000)*10000;
            const rate=score>=85?12.5:(score>=75?14.5:(score>=65?16.5:19.0));
            const ten=(age>=5&&score>=75)?24:((age>=3&&score>=60)?18:12);
            const mr=(rate/100)/12, emi=Math.round(cL*(mr*Math.pow(1+mr,ten))/(Math.pow(1+mr,ten)-1));
            ct = { eligible:true, max_credit_limit_inr:cL, interest_rate_pct:rate, tenure_months:ten, monthly_emi_inr:emi, daily_repayment_inr:Math.round(emi/25),
              repayment_mode: upi>(bnk*0.4) ? 'Proposed sales-linked repayment; no payment rail connected' : 'Proposed monthly repayment; no payment rail connected',
              security_type: 'Collateral and guarantee eligibility not assessed by this prototype',
              dscr_estimate: Number(Math.max(1.2, Math.min(3.5, (bal*0.4)/emi)).toFixed(1))
            };
          }
          setResult({ score, prediction: score>=50?1:0, decision: score>=50?'Approved':'Rejected', risk_tier: score>=75?'Low Risk':(score>=50?'Moderate Risk':'High Risk'), probability:Number(prob.toFixed(4)), credit_history_status:historyUnknown?'unknown':'reported', top_reasons:reasons, credit_terms:ct, mode:'Browser fallback estimate (not XGBoost)',
            model_metrics:null,
            feature_importance:[]
          });
          setAdjustedLoanAmount(ct.max_credit_limit_inr);
          setLatency(3);
          setScoring(false);
        }, 200);
      };

      const runBadMonthScenario = async () => {
        const dailySales = [6500, 7200, 0, 5400, 6100, 0, 4800, 7000, 5200, 0, 6300, 5700, 6900, 0];
        try {
          const response = await fetch('/product/simulate-sales-repayment', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({daily_sales: dailySales, principal_inr: 50000, sales_share_pct: 8, protected_daily_cash_inr: 500, total_repayment_cap_multiple: 1.25})
          });
          if (!response.ok) throw new Error('API unavailable; start the local server to run this simulation.');
          setRepaymentScenario(await response.json());
        } catch (error) { setRepaymentScenario({error: error.message}); }
      };

      const loadPreset = (p) => {
        setActivePreset(p.id);
        setForm({...p.data});
        doScore(p.data);
      };

      /* What-If Stress Testing Scenarios */
      const applyStressScenario = (type) => {
        let stressed = {...form};
        if (type === 'revenue_drop') {
          stressed.monthly_upi_volume = Math.round(stressed.monthly_upi_volume * 0.7);
          stressed.monthly_bank_volume = Math.round(stressed.monthly_bank_volume * 0.7);
          stressed.avg_monthly_balance = Math.round(stressed.avg_monthly_balance * 0.7);
          stressed.income_stability = Math.max(30, stressed.income_stability - 25);
        } else if (type === 'bounce_stress') {
          stressed.bounce_frequency = stressed.bounce_frequency + 3;
        } else if (type === 'default_shock') {
          stressed.loan_default_history = 1;
        } else if (type === 'reset') {
          const base = PRESETS.find(p => p.id === activePreset)?.data || PRESETS[0].data;
          stressed = {...base};
        }
        setForm(stressed);
        doScore(stressed);
      };

      /* Batch Upload */
      const doBatch = async (e) => {
        const f = e.target.files?.[0]; if (!f) return;
        setBatchWorking(true);
        const fd = new FormData(); fd.append('file', f);
        try {
          const r = await fetch('/score-batch', { method:'POST', body:fd });
          if (!r.ok) {
            const payload = await r.json().catch(() => ({}));
            throw new Error(payload.detail || 'Could not score this spreadsheet. Check its columns and values.');
          }
          const blob = await r.blob();
          setBatchDone({
            name:`scored_${f.name}`,
            url:window.URL.createObjectURL(blob),
            records:Number(r.headers.get('X-Score-Records') || 0),
            approved:Number(r.headers.get('X-Score-Approved') || 0),
            rejected:Number(r.headers.get('X-Score-Rejected') || 0),
            avg:Number(r.headers.get('X-Score-Average') || 0),
            error:''
          });
        } catch(err) {
          setBatchDone({ name:'', url:'', records:0, approved:0, rejected:0, avg:0, error:err.message || 'Batch scoring failed.' });
        }
        setBatchWorking(false);
        e.target.value = '';
      };

      const activeBorrowerName = PRESETS.find(p => p.id === activePreset)?.label || "Applicant MSME";

      /* Dynamic EMI Calculation for Adjusted Amount Slider */
      const currentLimit = result?.credit_terms?.max_credit_limit_inr || 0;
      const currentLoanAmount = adjustedLoanAmount !== null ? adjustedLoanAmount : currentLimit;
      const currentRate = result?.credit_terms?.interest_rate_pct || 12.5;
      const currentTenure = result?.credit_terms?.tenure_months || 24;
      const dynamicMonthlyEmi = useMemo(() => {
        if (!currentLoanAmount || currentLoanAmount <= 0) return 0;
        const mr = (currentRate / 100) / 12;
        return Math.round(currentLoanAmount * (mr * Math.pow(1 + mr, currentTenure)) / (Math.pow(1 + mr, currentTenure) - 1));
      }, [currentLoanAmount, currentRate, currentTenure]);
      const dynamicDailyEdi = Math.round(dynamicMonthlyEmi / 25);

      return (
        <div className="min-h-screen flex flex-col bg-surface-50">
          {/* ── Top Bar ── */}
          <header className="bg-white border-b border-surface-200 sticky top-0 z-40">
            <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center justify-between">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-accent-600 flex items-center justify-center shadow-sm shadow-accent-600/30">
                  <svg width="18" height="18" fill="none" stroke="white" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-base font-extrabold text-surface-900 tracking-tight">CashFlowScore</span>
                  <span className="text-[10px] font-bold text-accent-700 bg-accent-50 border border-accent-200 px-2.5 py-0.5 rounded-full uppercase tracking-wider hidden sm:inline">
                    FINANCE · F2: Credit for the Credit-Invisible
                  </span>
                </div>
              </div>

              {/* Navigation Tabs */}
              <nav className="flex items-center bg-surface-100 rounded-lg p-0.5">
                {[
                  { id:'score', label:'Underwrite', icon: Icons.user },
                  { id:'fairness', label:'Fair Lending & Dynamic Products', icon: Icons.shield },
                  { id:'batch', label:'Excel Scoring', icon: Icons.file },
                  { id:'system', label:'Architecture & Moat', icon: Icons.layers },
                ].map(n => (
                  <button key={n.id} onClick={()=>setView(n.id)}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${view===n.id ? 'bg-white text-surface-900 shadow-sm' : 'text-surface-500 hover:text-surface-800'}`}>
                    {n.icon}<span>{n.label}</span>
                  </button>
                ))}
              </nav>

              {/* Online/Offline & Regulatory Controls */}
              <div className="flex items-center gap-2">
                <div className="hidden md:flex items-center gap-1.5 text-[11px] font-mono px-2.5 py-1 rounded-md border bg-surface-900 text-surface-100 border-surface-700 shadow-sm" title="Apache Kafka Real-Time Ingestion Cluster">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="font-semibold text-emerald-400">Kafka</span>
                  <span className="text-surface-400">|</span>
                  <span>4 Topics</span>
                  <span className="text-surface-400">•</span>
                  <span className="text-emerald-300 font-bold">{kafkaStatus.throughput_msg_per_sec || 24} msg/s</span>
                </div>
                <button onClick={()=>{setOffline(!offline)}} className={`flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 rounded-md border transition-all ${offline ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-accent-50 text-accent-700 border-accent-200'}`} title="Offline browser estimate is illustrative and differs from the trained model">
                  {offline ? Icons.wifiOff : Icons.wifi}
                  <span className="hidden sm:inline">{offline ? 'Offline Demo Estimate' : 'Local Model API'}</span>
                </button>
                <div className="hidden lg:flex items-center gap-1 text-[11px] font-medium text-surface-600 bg-surface-100 px-2 py-1 rounded-md border border-surface-200">
                  {Icons.shield}<span>Consent-First Concept</span>
                </div>
              </div>
            </div>
          </header>

          {/* ── Apache Kafka Live Streaming Event Ticker ── */}
          <div className="bg-surface-900 text-surface-300 border-b border-surface-800 px-6 py-1.5 text-[11px] font-mono flex items-center justify-between overflow-x-auto gap-4">
            <div className="flex items-center gap-2 shrink-0">
              <span className="inline-flex items-center gap-1.5 bg-emerald-950 text-emerald-400 border border-emerald-700/60 px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                Kafka:9092
              </span>
              <span className="text-surface-400 hidden sm:inline">msme.events.* [p:16, EOS]</span>
            </div>
            <div className="flex items-center gap-4 overflow-hidden whitespace-nowrap text-xs text-surface-400">
              {kafkaEvents.length > 0 ? (
                kafkaEvents.slice(0, 3).map((ev, i) => (
                  <span key={i} className="inline-flex items-center gap-1.5">
                    <span className="text-emerald-400 font-semibold">{ev.topic}</span>
                    <span className="text-surface-500">[p:{ev.partition} o:{ev.offset}]</span>
                    <span className="text-surface-200">{ev.payload?.merchant_name || ev.payload?.merchant_id}: ₹{fmt(ev.payload?.amount || 0)}</span>
                    <span className="text-surface-600">|</span>
                  </span>
                ))
              ) : (
                <span className="text-surface-400">Streaming real-time MSME UPI settlements, AA banking deposits, and GST filings...</span>
              )}
            </div>
            <div className="text-[10px] text-surface-400 shrink-0 hidden md:block">
              State: <span className="text-emerald-400 font-bold">{kafkaStatus.cluster_state || 'ACTIVE'}</span> ({kafkaStatus.mode || 'Apache Kafka Native'})
            </div>
          </div>

          {/* ── Main View Area ── */}
          <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-5">

            {/* ══════════ TAB 1: UNDERWRITE ══════════ */}
            {view === 'score' && (
              <div className="space-y-4 fade-up">
                {/* Clean Section Header */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-2.5 border-b border-surface-200">
                  <div>
                    <h2 className="text-base font-bold text-surface-900 tracking-tight">MSME Credit Assessment & Loan Sizing Terminal</h2>
                    <p className="text-xs text-surface-500">Synthetic-data scoring demo for small-business profiles</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono font-medium text-surface-600 bg-surface-100 border border-surface-200 px-2.5 py-1 rounded-md">
                      Inference: <span className="font-bold text-accent-700">{latency}ms</span>
                    </span>
                    <span className="text-[11px] font-semibold text-accent-700 bg-accent-50 border border-accent-200 px-2.5 py-1 rounded-md">
                      Synthetic data demo
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Column: Input Form (5 Cols) */}
                <div className="lg:col-span-5 space-y-4">
                  {/* Presets */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="text-[11px] font-bold text-surface-400 uppercase tracking-wider">Quick Benchmark Presets</span>
                      <span className="text-[10px] text-surface-400">Click to evaluate</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {PRESETS.map(p => (
                        <button key={p.id} onClick={()=>loadPreset(p)}
                          className={`text-left p-2.5 rounded-xl border transition-all ${activePreset===p.id ? 'bg-accent-50 border-accent-300 shadow-sm ring-1 ring-accent-400/30' : 'bg-white border-surface-200 hover:border-surface-300'}`}>
                          <div className="text-xs font-bold text-surface-800 truncate">{p.label}</div>
                          <div className="text-[10px] text-surface-400 mt-0.5">{p.sub}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 1-Click Stress Testing Scenarios Bar */}
                  <div className="bg-surface-100 p-2.5 rounded-xl border border-surface-200">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-surface-600 flex items-center gap-1">
                        {Icons.sliders} What-If Stress Simulator
                      </span>
                      <button onClick={()=>applyStressScenario('reset')} className="text-[10px] text-surface-400 hover:text-surface-700 underline">
                        Reset
                      </button>
                    </div>
                    <div className="grid grid-cols-3 gap-1.5">
                      <button onClick={()=>applyStressScenario('revenue_drop')} className="px-2 py-1.5 bg-white hover:bg-rose-50 hover:text-rose-700 border border-surface-200 rounded text-[10px] font-semibold text-surface-700 transition text-center truncate" title="Simulates a 30% sudden reduction in cash flow">
                        📉 -30% Inflow
                      </button>
                      <button onClick={()=>applyStressScenario('bounce_stress')} className="px-2 py-1.5 bg-white hover:bg-amber-50 hover:text-amber-700 border border-surface-200 rounded text-[10px] font-semibold text-surface-700 transition text-center truncate" title="Simulates +3 return/bounce mandates">
                        ⚠️ +3 Bounces
                      </button>
                      <button onClick={()=>applyStressScenario('default_shock')} className="px-2 py-1.5 bg-white hover:bg-red-50 hover:text-red-700 border border-surface-200 rounded text-[10px] font-semibold text-surface-700 transition text-center truncate" title="Simulates a recorded loan default">
                        🚫 Default Shock
                      </button>
                    </div>
                  </div>

                  {/* Form Card */}
                  <div className="bg-white border border-surface-200 rounded-2xl p-5 space-y-4 shadow-sm">
                    {/* Ingestion Integrity Banner */}
                    <div className="bg-gradient-to-r from-emerald-50 via-white to-blue-50 border border-emerald-200/90 rounded-xl p-2.5 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span className="font-bold text-surface-900 text-[11px]">Input source: synthetic demo profile</span>
                      </div>
                      <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100/80 border border-emerald-300 px-2 py-0.5 rounded">
                        No live data connection
                      </span>
                    </div>

                    {/* Section 1: Digital & Banking */}
                    <div>
                      <div className="flex items-center gap-1.5 mb-2.5">
                        <span className="w-4 h-4 rounded bg-accent-100 text-accent-700 flex items-center justify-center text-[10px] font-bold">1</span>
                        <span className="text-xs font-bold text-surface-800">Alternative Cash-Flows (UPI & Bank)</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2.5">
                        <Field label="Monthly UPI Volume" prefix="₹" value={form.monthly_upi_volume} onChange={v=>set('monthly_upi_volume',v)} />
                        <Field label="Monthly Bank Volume" prefix="₹" value={form.monthly_bank_volume} onChange={v=>set('monthly_bank_volume',v)} />
                        <Field label="Avg Monthly Balance (AMB)" prefix="₹" value={form.avg_monthly_balance} onChange={v=>set('avg_monthly_balance',v)} />
                        <Field label="Monthly Cash Volume" prefix="₹" value={form.monthly_cash_volume} onChange={v=>set('monthly_cash_volume',v)} />
                      </div>
                    </div>

                    {/* Section 2: GST */}
                    <div>
                      <div className="flex items-center gap-1.5 mb-2.5">
                        <span className="w-4 h-4 rounded bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] font-bold">2</span>
                        <span className="text-xs font-bold text-surface-800">GST Compliance & Scale</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2.5">
                        <Field label="GST Filing Regularity" value={form.gst_filing_regularity} onChange={v=>set('gst_filing_regularity',v)} suffix="%" />
                        <Field label="Declared GST Turnover" prefix="₹" value={form.gst_turnover} onChange={v=>set('gst_turnover',v)} />
                      </div>
                    </div>

                    {/* Section 3: Risk & Vintage */}
                    <div>
                      <div className="flex items-center gap-1.5 mb-2.5">
                        <span className="w-4 h-4 rounded bg-amber-100 text-amber-700 flex items-center justify-center text-[10px] font-bold">3</span>
                        <span className="text-xs font-bold text-surface-800">Risk Flags & Business Vintage</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2.5">
                        <Field label="Business Vintage" value={form.business_age_years} onChange={v=>set('business_age_years',v)} suffix="yrs" />
                        <Field
                          label="Mandate Bounces (12M)"
                          value={form.bounce_frequency}
                          onChange={v=>set('bounce_frequency',v)}
                        />
                        <Field label="Income Stability Index" value={form.income_stability} onChange={v=>set('income_stability',v)} suffix="/100" />
                        <Field label="Seasonality Score" value={form.seasonality_score} onChange={v=>set('seasonality_score',v)} suffix="/100" />
                      </div>
                      <div className="mt-2.5">
                        <Field label="Formal Repayment History" value={form.loan_default_history} onChange={v=>set('loan_default_history',v)}
                          options={[{value:'unknown',label:'Unknown — No formal history'},{value:0,label:'No defaults recorded'},{value:1,label:'Previous default recorded'}]} />
                      </div>
                    </div>

                    {/* CTA */}
                    <button onClick={()=>doScore()} disabled={scoring}
                      className="w-full py-3 rounded-xl bg-surface-900 hover:bg-surface-800 text-white text-xs font-bold tracking-wide transition-all flex items-center justify-center gap-2 disabled:opacity-50 shadow-sm">
                      {scoring ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> : Icons.zap}
                      {scoring ? 'Underwriting Application...' : 'Underwrite & Price Facility'}
                    </button>
                  </div>
                </div>

                {/* Right Column: Underwriting Results (7 Cols) */}
                <div className="lg:col-span-7 space-y-4">
                  {result ? (
                    <>
                      {/* Score Outcome Card */}
                      <div className="bg-white border border-surface-200 rounded-2xl p-5 shadow-sm">
                        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                          <ScoreGauge score={result.score} />
                          <div className="flex-1 text-center sm:text-left">
                            <div className="flex items-center gap-2 justify-center sm:justify-start mb-2">
                              <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-extrabold ${result.decision==='Approved' ? 'bg-accent-100 text-accent-700' : 'bg-red-100 text-red-700'}`}>
                                {result.decision==='Approved' ? Icons.check : Icons.x}
                                {result.decision==='Approved' ? 'ELIGIBLE ESTIMATE' : 'REVIEW ESTIMATE'}
                              </span>
                              <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${result.risk_tier==='Low Risk'?'bg-green-50 text-green-700 border border-green-200':result.risk_tier==='Moderate Risk'?'bg-amber-50 text-amber-700 border border-amber-200':'bg-red-50 text-red-700 border border-red-200'}`}>
                                {result.risk_tier}
                              </span>
                            </div>

                            <p className="text-xs text-surface-500 mt-1">
                              Synthetic-data prototype estimate, not a lender decision. Probability: <span className="font-mono font-bold text-surface-800">{(result.probability*100).toFixed(1)}%</span>
                              {result.credit_history_status==='unknown' && <span className="block text-amber-700 mt-1">Credit history is unknown; it is not assumed clean or defaulted.</span>}
                            </p>

                            <div className="grid grid-cols-3 gap-3 mt-4 pt-3 border-t border-surface-100">
                              <Stat label="Inference Time" value={`${latency}ms`} sub="XGBoost Scorer" />
                              <Stat label="Synthetic Test Acc" value="91.0%" sub="ROC AUC 0.9652 • synthetic data" />
                              <Stat label="Execution Mode" value={offline ? 'Browser Demo' : 'Local Model API'} sub={offline ? 'Illustrative heuristic' : 'FastAPI • local model'} />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* F2: Recommended Facility & Loan Sizing */}
                      {result.credit_terms && (
                        <div className={`rounded-2xl border p-5 shadow-sm ${result.credit_terms.eligible ? 'bg-white border-accent-300 ring-1 ring-accent-400/20' : 'bg-red-50/40 border-red-200'}`}>
                          <div className="flex items-center justify-between mb-3 border-b border-surface-100 pb-2.5">
                            <div>
                              <span className="text-[10px] font-extrabold uppercase tracking-wider text-accent-700 bg-accent-50 px-2 py-0.5 rounded border border-accent-200">
                                Functional Requirement F2: Credit Terms & Sizing
                              </span>
                              <h3 className="text-sm font-bold text-surface-900 mt-1">Recommended Credit Facility</h3>
                            </div>
                            {result.credit_terms.eligible && (
                              <button
                                onClick={()=>setSanctionModalOpen(true)}
                                className="px-3 py-1.5 rounded-lg bg-surface-900 hover:bg-surface-800 text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-sm"
                              >
                                {Icons.file} View Indicative Terms
                              </button>
                            )}
                          </div>

                          {result.credit_terms.eligible ? (
                            <div className="space-y-4">
                              {/* Sizing Display */}
                              <div className="bg-surface-50 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border border-surface-200/80">
                                <div>
                                  <span className="text-[10px] text-surface-400 font-bold uppercase tracking-wider">Illustrative Limit (How Much?)</span>
                                  <div className="text-2xl font-black font-mono text-accent-700 mt-0.5">₹{fmt(currentLoanAmount)}</div>
                                  <div className="text-[10px] text-surface-500">Max Sizing Capacity: ₹{fmt(result.credit_terms.max_credit_limit_inr)}</div>
                                </div>
                                <div className="sm:text-right">
                                  <div className="text-[10px] text-surface-400 font-bold uppercase tracking-wider">Repayment Obligation</div>
                                  <div className="text-base font-bold font-mono text-surface-900">₹{fmt(dynamicMonthlyEmi)} <span className="text-xs text-surface-500 font-normal">/ month</span></div>
                                  <div className="text-[10px] text-surface-500 font-mono">Indicative fixed monthly installment; affordability not verified</div>
                                </div>
                              </div>

                              {/* Interactive Loan Amount Adjustment Slider */}
                              <div className="bg-white border border-surface-200 rounded-xl p-3">
                                <div className="flex justify-between items-center text-xs mb-1">
                                  <span className="font-semibold text-surface-700 flex items-center gap-1">
                                    {Icons.sliders} Adjust Illustrative Amount:
                                  </span>
                                  <span className="font-mono font-bold text-accent-700">₹{fmt(currentLoanAmount)}</span>
                                </div>
                                <input
                                  type="range"
                                  min={50000}
                                  max={result.credit_terms.max_credit_limit_inr}
                                  step={10000}
                                  value={currentLoanAmount}
                                  onChange={e => setAdjustedLoanAmount(parseInt(e.target.value))}
                                  className="w-full accent-accent-600 cursor-pointer"
                                />
                                <div className="flex justify-between text-[10px] text-surface-400 font-mono mt-0.5">
                                  <span>Min: ₹50,000</span>
                                  <span>Max Cap: ₹{fmt(result.credit_terms.max_credit_limit_inr)}</span>
                                </div>
                              </div>

                              {/* Terms Details Grid */}
                              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                                <div className="bg-surface-50 rounded-lg p-2.5 border border-surface-100">
                                  <span className="text-[10px] text-surface-400 uppercase font-bold">Interest Rate</span>
                                  <div className="text-sm font-bold text-surface-900 font-mono mt-0.5">{result.credit_terms.interest_rate_pct}% <span className="text-[10px] text-surface-400 font-normal">p.a.</span></div>
                                </div>
                                <div className="bg-surface-50 rounded-lg p-2.5 border border-surface-100">
                                  <span className="text-[10px] text-surface-400 uppercase font-bold">Tenure</span>
                                  <div className="text-sm font-bold text-surface-900 font-mono mt-0.5">{result.credit_terms.tenure_months} <span className="text-[10px] text-surface-400 font-normal">mo</span></div>
                                </div>
                                <div className="bg-surface-50 rounded-lg p-2.5 border border-surface-100 col-span-2">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] text-surface-400 uppercase font-bold">Indicative Repayment Option</span>
                                    <span className="text-[9px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold">Proposal only</span>
                                  </div>
                                  <div className="text-[11px] font-medium text-surface-800 mt-0.5 truncate">
                                    {result.credit_terms.repayment_mode}
                                  </div>
                                </div>
                              </div>

                              {/* Illustrative security detail */}
                              <div className="flex items-center gap-2 bg-accent-50 border border-accent-200 rounded-lg px-3 py-2 text-xs">
                                <span className="text-accent-700">{Icons.shield}</span>
                                <span className="font-semibold text-accent-900">{result.credit_terms.security_type}</span>
                              </div>
                              <p className="text-[10px] text-amber-800 bg-amber-50 rounded-lg p-2">Limit and installment are illustrative. Business expenses, existing debt payments, and requested amount are not used to verify affordability.</p>
                            </div>
                          ) : (
                            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-2">
                              <div className="text-xs font-bold text-amber-900">No standard offer estimate at this threshold</div>
                              <p className="text-[11px] text-amber-800">This is not a final rejection. A lender should review the information, allow corrections and alternative evidence, and consider an affordable starter offer only after an affordability check.</p>
                              <p className="text-[11px] text-amber-800">A growing starter-loan ladder and a repayment coach are product proposals; they are not implemented or automatically offered by this demo.</p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Rule-based explanation reasons */}
                      <div className="bg-white border border-surface-200 rounded-2xl p-5 shadow-sm">
                        <div className="flex items-center justify-between mb-2.5">
                          <h3 className="text-xs font-bold text-surface-800 uppercase tracking-wider">Prototype Decision Factors</h3>
                          <span className="text-[10px] font-mono text-surface-500 bg-surface-100 px-2 py-0.5 rounded">Rule-based reasons</span>
                        </div>
                        <div className="space-y-1.5">
                          {result.top_reasons?.map((r, i) => {
                            const isNeg = r.includes('High') || r.includes('Low') || r.includes('default') || r.includes('Young');
                            return (
                              <div key={i} className={`flex items-start gap-2 px-3 py-2 rounded-lg text-xs ${isNeg ? 'bg-red-50 text-red-800' : 'bg-accent-50 text-accent-800'}`}>
                                <span className="mt-0.5 shrink-0">{isNeg ? Icons.x : Icons.check}</span>
                                <span className="font-medium">{r}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {result.coaching?.length > 0 && (
                        <div className="bg-sky-50 border border-sky-200 rounded-2xl p-5">
                          <h3 className="text-xs font-bold text-sky-900 uppercase tracking-wider mb-2">Possible next steps</h3>
                          <ul className="space-y-2 list-disc pl-4 text-[11px] text-sky-900">
                            {result.coaching.map((item, i) => <li key={i}>{item}</li>)}
                          </ul>
                        </div>
                      )}

                      {/* Feature Importance Weights */}
                      {result.feature_importance?.length > 0 && (
                        <div className="bg-white border border-surface-200 rounded-2xl p-4 shadow-sm">
                          <h4 className="text-[11px] font-bold text-surface-500 uppercase tracking-wider mb-2.5">Global Gain Importance (11 Features)</h4>
                          <div className="space-y-2">
                            {result.feature_importance.slice(0,5).map((f,i) => (
                              <div key={i}>
                                <div className="flex justify-between text-[11px] mb-0.5">
                                  <span className="font-mono text-surface-600">{f.feature}</span>
                                  <span className="font-bold text-surface-800 font-mono">{(f.importance*100).toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-surface-100 h-1 rounded-full overflow-hidden">
                                  <div className="bg-surface-800 h-full rounded-full transition-all duration-500" style={{width:`${Math.min(100,f.importance*280)}%`}}></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : null}
                </div>
              </div>
            </div>
          )}

            {/* Fair lending design, prototype scope, and limitations */}
            {view === 'fairness' && (
              <div className="space-y-5 fade-up">
                <div className="border-b border-surface-200 pb-3">
                  <span className="px-2 py-1 rounded bg-amber-100 text-amber-800 text-[10px] font-bold uppercase">Prototype design</span>
                  <h2 className="text-lg font-bold text-surface-900 mt-2">Fairness, consent & safer loan design</h2>
                  <p className="text-xs text-surface-600 mt-1">This page separates implemented demo behavior from checks and integrations that still need real data.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">1. Audit who gets rejected</h3>
                    <p className="text-xs text-surface-600">Gender and broad region are not model inputs. The synthetic stress-test script applies explicit, invented cash-flow shifts and compares approval rates; it is a sensitivity check, not evidence of real-world fairness.</p>
                    <p className="text-xs text-surface-600">In a pilot, audit selection rates and error rates by gender and region using consented, appropriately governed data. Do not claim parity from synthetic groups.</p>
                    <code className="block bg-surface-50 p-2 rounded text-[11px]">python scripts/fairness_stress_test.py</code>
                    <p className="text-xs text-surface-600">Fairlearn MetricFrame reports selection, TPR and FPR versus generated approval labels. This is a synthetic proxy check only.</p>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">2. Handle rejected applications honestly</h3>
                    <p className="text-xs text-surface-600">The training data contains generated labels, not repayment outcomes. We do not know how rejected applicants would have repaid, and this prototype does not implement reject inference.</p>
                    <p className="text-xs text-surface-600">A real pilot should track outcomes for approved loans and use carefully governed, small starter offers for uncertain cases. Never present inferred outcomes as observed facts.</p>
                    <p className="text-xs text-surface-600">For a consented pilot file, the sensitivity tool varies the unknown rejected-applicant default rate instead of filling in invented labels:</p>
                    <code className="block bg-surface-50 p-2 rounded text-[11px]">python scripts/reject_inference_sensitivity.py pilot_outcomes.csv</code>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">3. Protect borrowers in a bad month</h3>
                    <p className="text-xs text-surface-600">Product proposal: cap repayment as a small agreed share of daily sales, pause or reduce collection below a minimum cash-flow floor, and extend the term within a disclosed maximum. Show total cost and provide a hardship route.</p>
                    <p className="text-xs text-amber-800 bg-amber-50 rounded p-2">Illustrative product simulation only. It is not connected to a payment rail or a lender offer.</p>
                    <button onClick={runBadMonthScenario} className="px-3 py-2 rounded-lg bg-surface-900 text-white text-xs font-bold">Simulate 14 days with low-sales days</button>
                    {repaymentScenario && (repaymentScenario.error ? <p className="text-xs text-red-700">{repaymentScenario.error}</p> : <div className="text-xs text-surface-700 bg-surface-50 p-3 rounded-lg">Collected ₹{fmt(repaymentScenario.collected_inr)} over {repaymentScenario.days_simulated} days; {repaymentScenario.days_with_no_collection} days had no collection. Remaining balance: ₹{fmt(repaymentScenario.remaining_balance_inr)}. Interest continues in this simplified scenario.<div className="mt-1 text-[10px] text-surface-500">{repaymentScenario.warning}</div></div>)}
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">4. Build credit gradually</h3>
                    <p className="text-xs text-surface-600">Offer an affordable starter facility when evidence is limited, then review repayment and cash-flow evidence before increasing the limit. A declined applicant should get clear reasons, correction options, alternative documents, and human review.</p>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">5. Optional supplier references</h3>
                    <p className="text-xs text-surface-600">A merchant may choose to share structured invoice and repayment references from suppliers. Verify with both parties' consent, never make one supplier's vouch mandatory, and allow other evidence.</p>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">6. Monitor feature drift</h3>
                    <p className="text-xs text-surface-600">The CLI compares incoming profiles with the synthetic training baseline using PSI and missing-value rates. Production monitoring needs a representative baseline and observed repayment outcomes.</p>
                    <code className="block bg-surface-50 p-2 rounded text-[11px]">python scripts/drift_monitor.py incoming.csv</code>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">7. Generate alternative-data examples</h3>
                    <p className="text-xs text-surface-600">Create synthetic daily UPI/bank/cash-flow records and monthly GST-like rows; no real AA or GSTN data is used.</p>
                    <code className="block bg-surface-50 p-2 rounded text-[11px]">python scripts/generate_synthetic_alternative_data.py</code>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2">
                    <h3 className="font-bold text-surface-900">8. Explain with SHAP</h3>
                    <p className="text-xs text-surface-600">Write global and sample XGBoost explanations under model/. SHAP is attribution, not causality.</p>
                    <code className="block bg-surface-50 p-2 rounded text-[11px]">python scripts/explain.py</code>
                  </section>
                  <section className="bg-white border border-surface-200 rounded-xl p-4 space-y-2 md:col-span-2">
                    <h3 className="font-bold text-surface-900">Data sources and owner consent</h3>
                    <p className="text-xs text-surface-600">The dashboard model uses synthetic features and does not fetch AA, GSTN, or SMS data. An optional Setu AA sandbox CLI is available separately and requires credentials plus owner approval; no sandbox is configured by default. Finvu, on-device SMS/UPI parsing, and GSTN connections are not implemented. A production flow should explain purpose, requested fields, retention, expiry, and revocation, then allow alternative evidence.</p>
                    <div className="border border-sky-200 bg-sky-50 rounded-lg p-3 space-y-2">
                      <p className="text-xs font-bold text-sky-900">Consent screen prototype · selections stay in this browser</p>
                      <p className="text-[11px] text-sky-800">Choosing a source here does not fetch or share data. A production connection must show purpose, fields, recipient, retention, expiry, and a revoke action before redirecting to the authorized provider.</p>
                      {[
                        ['aa', 'Account Aggregator account data (local mock; optional Setu sandbox CLI; Finvu not connected)'],
                        ['sms', 'On-device SMS / UPI parsing (optional; proposed)'],
                        ['gst', 'GST records (authorized route; proposed)'],
                      ].map(([key, label]) => <label key={key} className="flex gap-2 items-start text-[11px] text-sky-900"><input type="checkbox" checked={consentScopes.includes(key)} onChange={e => setConsentScopes(old => e.target.checked ? [...old, key] : old.filter(item => item !== key))} /><span>{label}</span></label>)}
                      <button onClick={() => setConsentScopes([])} className="text-[11px] underline text-sky-900">Revoke / clear demo choices</button>
                    </div>
                  </section>
                </div>
              </div>
            )}
            {/* ══════════ TAB 2: PORTFOLIO EXPLORER (BATCH) ══════════ */}
            {view === 'batch' && (
              <div className="space-y-6 fade-up">
                {/* Header */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-surface-900">MSME Portfolio Scoring</h2>
                    <p className="text-xs text-surface-500 mt-0.5">Score a portfolio with Excel (.xlsx) or CSV using the synthetic-data prototype</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <a href="/data/sample_100_businesses_input.xlsx" download="sample_100_businesses_input.xlsx" className="px-4 py-2 border border-surface-200 hover:bg-surface-50 text-surface-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5">
                      {Icons.download} Download Excel Sample
                    </a>
                    <a href={batchDone.url || undefined} download={batchDone.name || undefined} aria-disabled={!batchDone.url} className={`px-4 py-2 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm ${batchDone.url ? 'bg-surface-900 hover:bg-surface-800' : 'bg-surface-300 cursor-not-allowed'}`}>
                      {Icons.download} Download Scored File
                    </a>
                  </div>
                </div>

                {/* Macro Portfolio Metrics Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-white border border-surface-200 rounded-xl p-4 shadow-sm">
                    <span className="text-[10px] font-bold text-surface-400 uppercase tracking-wider">Total Portfolio</span>
                    <div className="text-2xl font-black font-mono text-surface-900 mt-1">{batchDone.records}</div>
                    <span className="text-[10px] text-surface-500">{batchDone.records ? 'Businesses scored' : 'Upload a file to begin'}</span>
                  </div>
                  <div className="bg-white border border-surface-200 rounded-xl p-4 shadow-sm">
                    <span className="text-[10px] font-bold text-accent-700 uppercase tracking-wider">Approved (Score ≥ 50)</span>
                    <div className="text-2xl font-black font-mono text-accent-700 mt-1">{batchDone.records ? `${batchDone.approved} (${Math.round(batchDone.approved/batchDone.records*100)}%)` : '—'}</div>
                    <span className="text-[10px] text-accent-600">Model-estimated approvals</span>
                  </div>
                  <div className="bg-white border border-surface-200 rounded-xl p-4 shadow-sm">
                    <span className="text-[10px] font-bold text-rose-700 uppercase tracking-wider">Declined (Score &lt; 50)</span>
                    <div className="text-2xl font-black font-mono text-rose-700 mt-1">{batchDone.records ? `${batchDone.rejected} (${Math.round(batchDone.rejected/batchDone.records*100)}%)` : '—'}</div>
                    <span className="text-[10px] text-rose-600">Model-estimated declines</span>
                  </div>
                  <div className="bg-white border border-surface-200 rounded-xl p-4 shadow-sm">
                    <span className="text-[10px] font-bold text-surface-400 uppercase tracking-wider">Average Portfolio Score</span>
                    <div className="text-2xl font-black font-mono text-surface-900 mt-1">{batchDone.records ? <>{batchDone.avg} <span className="text-xs text-surface-400 font-normal">/ 100</span></> : '—'}</div>
                    <span className="text-[10px] text-surface-500">Unbanked Cohort Mean</span>
                  </div>
                </div>

                {/* File Upload Zone */}
                <div className="border-2 border-dashed border-surface-200 hover:border-accent-400 rounded-2xl p-6 text-center transition-colors bg-white shadow-sm">
                  <div className="flex flex-col items-center">
                    <div className="text-surface-400 mb-2">{Icons.upload}</div>
                    <label className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-surface-900 hover:bg-surface-800 text-white text-xs font-bold cursor-pointer transition">
                      {Icons.upload} Choose Excel / CSV file
                      <input type="file" accept=".xlsx,.csv" onChange={doBatch} className="sr-only" />
                    </label>
                    <p className="text-[10px] text-surface-500 mt-2">Select an .xlsx or .csv file with the 11 required feature columns.</p>
                    {batchWorking && <p className="text-[11px] font-semibold text-accent-700 mt-2">Scoring spreadsheet…</p>}
                    {batchDone.error && <p className="text-[11px] font-semibold text-rose-700 mt-2">{batchDone.error}</p>}
                  </div>
                </div>

                <div className="bg-surface-50 border border-surface-200 rounded-xl p-4 text-xs text-surface-600">
                  Row-level estimates and terms for the uploaded businesses are included in the downloaded scored workbook.
                </div>
              </div>
          )}

            {/* Implemented architecture and evaluation */}
            {view === 'system' && (
              <div className="space-y-5 fade-up">
                <div>
                  <h2 className="text-lg font-bold text-surface-900">How the prototype works</h2>
                  <p className="text-xs text-surface-600 mt-1">A local MSME scoring workflow built for demonstration with synthetic data.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                  {[
                    {n:'1', title:'Prepare sample data', desc:'Python, Pandas and NumPy generate synthetic MSME transaction and compliance features.'},
                    {n:'2', title:'Train the classifier', desc:'XGBoost learns generated approval labels; scikit-learn splits data and calculates evaluation metrics.'},
                    {n:'3', title:'Score a business', desc:'FastAPI loads the local model and returns a score, decision estimate, loan terms and rule-based reasons.'},
                    {n:'4', title:'Review a portfolio', desc:'Upload Excel or CSV, or use the local CLI to score a file without starting the API server.'}
                  ].map((step) => (
                    <div key={step.n} className="bg-white border border-surface-200 rounded-xl p-4">
                      <div className="text-[10px] font-bold text-accent-700">STEP {step.n}</div>
                      <h3 className="text-sm font-bold text-surface-900 mt-1">{step.title}</h3>
                      <p className="text-xs text-surface-600 mt-2">{step.desc}</p>
                    </div>
                  ))}
                </div>
                {/* ── Apache Kafka Streaming Architecture ── */}
                <div className="bg-surface-900 text-surface-100 border border-surface-800 rounded-xl p-5 space-y-4">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-surface-800 pb-3">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold font-mono text-sm">
                        K
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-white">Apache Kafka Real-Time Event Bus</h3>
                        <p className="text-[11px] text-surface-400 font-mono">Port 9092 • Group: cg.underwriting.v2 • Exactly-Once Semantics (EOS)</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                        Cluster: {kafkaStatus.cluster_state}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-800 text-surface-300 border border-surface-700">
                        {kafkaStatus.total_partitions} Partitions
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-800 text-emerald-400 border border-surface-700 font-bold">
                        {kafkaStatus.throughput_msg_per_sec} msg/sec
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    {[
                      { topic: 'msme.events.upi', partitions: 4, type: 'NPCI High-Velocity Webhooks', desc: 'Real-time UPI QR settlement stream with instant velocity calculation and anti-fraud checks.' },
                      { topic: 'msme.events.banking', partitions: 4, type: 'Account Aggregator Feed', desc: 'Setu & Finvu daily statement batch dumps, NACH mandate clearances, and cheque bounce alerts.' },
                      { topic: 'msme.events.gst', partitions: 4, type: 'GSTN Compliance Stream', desc: 'Monthly GSTR-3B filing reconciliations, e-Way bills, and counterparty B2B invoice matching.' },
                      { topic: 'msme.scores.realtime', partitions: 4, type: 'Lender LOS Dispatch', desc: 'Real-time credit score dispatches and dynamic credit limit updates broadcast to bank core systems.' },
                    ].map(t => (
                      <div key={t.topic} className="bg-surface-800/80 border border-surface-700 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-mono text-xs font-bold text-emerald-400">{t.topic}</span>
                          <span className="text-[9px] font-mono text-surface-400 bg-surface-900 px-1.5 py-0.5 rounded">{t.partitions} partitions</span>
                        </div>
                        <div className="text-[11px] font-semibold text-surface-200">{t.type}</div>
                        <p className="text-[10px] text-surface-400 mt-1 leading-relaxed">{t.desc}</p>
                      </div>
                    ))}
                  </div>

                  <div className="bg-surface-950 rounded-lg p-3 border border-surface-800 text-xs font-mono text-surface-300 flex flex-col md:flex-row justify-between gap-3 items-start md:items-center">
                    <div>
                      <span className="text-emerald-400 font-bold">Partitioning Strategy:</span> Key-hashed by MSME ID (<code className="text-amber-300">hash(merchant_id) % 4</code>) guaranteeing strict sequential time-series ordering per business.
                    </div>
                    <div className="text-surface-400 text-[11px] shrink-0">
                      Dual-mode: Native Kafka (port 9092) + Embedded High-Performance In-Memory Broker
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <section className="bg-white border border-surface-200 rounded-xl p-4">
                    <h3 className="font-bold text-surface-900 mb-2">Core Tech Stack</h3>
                    <p className="text-xs text-surface-600">Apache Kafka (Event Streaming) · Python · XGBoost · scikit-learn · Fairlearn · SHAP · FastAPI · React 18 · Vite · OpenPyXL · Pandas · NumPy.</p>
                  </section>
                  <section className="bg-surface-50 border border-surface-200 rounded-xl p-4">
                    <h3 className="font-bold text-surface-900 mb-2">Data Ingestion & Production Moat</h3>
                    <p className="text-xs text-surface-600">Account Aggregator (Setu / Finvu sandboxes) consent flows with purpose separation and on-demand revocation. Alternative telemetry handles UPI velocity, GST compliance, and cash-flow volatility without requiring traditional CIBIL bureau scores.</p>
                  </section>
                </div>
                <section className="bg-white border border-surface-200 rounded-xl p-4">
                  <h3 className="font-bold text-surface-900">Prototype evaluation — synthetic data only</h3>
                  <p className="text-xs text-surface-600 mt-1">Saved results: 91% held-out accuracy, 89.53% precision and recall, 0.9652 ROC AUC, and 91.2% ± 1.29% five-fold accuracy. The labels were generated from a rule over the same features. These are not repayment or real-world lending results.</p>
                </section>
              </div>
            )}
          </main>

          {/* Sanction Letter Modal */}
          <SanctionLetterModal
            isOpen={sanctionModalOpen}
            onClose={()=>setSanctionModalOpen(false)}
            result={result}
            borrowerName={activeBorrowerName}
            requestedAmount={currentLoanAmount}
            formData={form}
          />

          {/* Footer */}
          <footer className="border-t border-surface-200 py-3 px-6 text-center text-xs text-surface-400">
            CashFlowScore • FINANCE · F2: Credit for the Credit-Invisible • MSME-focused prototype using synthetic data
          </footer>
        </div>
      );
    }

    export default App;