from datetime import datetime, time as dtime, timedelta, timezone
from zoneinfo import ZoneInfo

import streamlit as st

# --------------------------------------------------------------------------- #
# Page setup
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Cashmara Countdown",
    page_icon="💿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Brand palette (mpathic)
MAGENTA, MAGENTA_D = "#ff00c1", "#8f006b"
YELLOW, YELLOW_D = "#FEDA00", "#f3ac02"
CYAN, CYAN_D = "#67dedf", "#1d8587"
PURPLE, LIGHT_GRAY = "#6700a9", "#F9F8F8"
PAGE = "#0d0118"  # everything outside the stage

EVENT_URL = "https://luma.com/jxbrvcvo"
VENUE = "Q Nightclub"
ADDRESS = "1426 Broadway, Seattle"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500&display=swap');
    html, body, [class*="css"], .stApp {{ font-family:'Rubik',sans-serif; }}
    .stApp {{ background:{PAGE}; }}
    #MainMenu, header, footer {{ visibility:hidden; }}
    .block-container {{ padding-top:1.1rem; padding-bottom:2rem; max-width:1120px; }}
    /* Hide the settings sidebar entirely (and its open arrow) for a clean shared link.
       To re-enable the controls, delete these two rules. */
    section[data-testid="stSidebar"] {{ display:none !important; }}
    [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {{ display:none !important; }}
    section[data-testid="stSidebar"] {{ background:#fff; border-right:3px solid {MAGENTA}; }}
    section[data-testid="stSidebar"] * {{ font-family:'Rubik',sans-serif; }}
    .sb-title {{ font-weight:800; font-size:1.1rem; color:{MAGENTA_D}; margin:0 0 .15rem; }}
    .sb-sub {{ color:#6b6b6b; font-size:.82rem; margin-bottom:1rem; }}
    .sb-readout {{ background:{LIGHT_GRAY}; border-left:3px solid {CYAN_D};
                   border-radius:0 10px 10px 0; padding:12px 14px; margin-top:8px;
                   font-size:.85rem; color:#2a2a2a; line-height:1.5; }}
    .sb-readout b {{ color:{MAGENTA_D}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Helpers — 12-hour times without platform-specific strftime flags
# --------------------------------------------------------------------------- #
def clock12(dt_: datetime) -> str:
    return f"{dt_.hour % 12 or 12}:{dt_.minute:02d} {'am' if dt_.hour < 12 else 'pm'}"


def hour_only(dt_: datetime) -> tuple[str, str]:
    """('8:00', 'pm') — split so the meridiem can be set smaller."""
    return f"{dt_.hour % 12 or 12}:{dt_.minute:02d}", "am" if dt_.hour < 12 else "pm"


def long_date(dt_: datetime) -> str:
    return f"{dt_.strftime('%A, %B')} {dt_.day}, {dt_.year}"


def ms(dt_: datetime) -> int:
    return int(dt_.timestamp() * 1000)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------- #
# Sidebar — configure the countdown target
# --------------------------------------------------------------------------- #
TIMEZONES = {
    "Pacific (Seattle), door time": "America/Los_Angeles",
    "Mountain": "America/Denver",
    "Central": "America/Chicago",
    "Eastern": "America/New_York",
    "UTC": "UTC",
}

with st.sidebar:
    st.markdown('<div class="sb-title">Countdown settings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-sub">Pre-filled for System Override at Q Nightclub. '
        "Adjust anything you like.</div>",
        unsafe_allow_html=True,
    )
    headliner = st.text_input("Headliner", value="Cashmara")
    event_date = st.date_input("Event date", value=datetime(2026, 7, 30).date())
    doors_time = st.time_input("Doors open", value=dtime(19, 15))
    set_time = st.time_input("On the decks", value=dtime(20, 0))
    set_length = st.slider("Set length (minutes)", 30, 180, 60, step=15)
    tz_label = st.selectbox("Time zone", list(TIMEZONES.keys()), index=0)

tz = ZoneInfo(TIMEZONES[tz_label])
doors = datetime.combine(event_date, doors_time, tzinfo=tz)
onstage = datetime.combine(event_date, set_time, tzinfo=tz)
if onstage < doors:  # a set that spills past midnight
    onstage += timedelta(days=1)
set_end = onstage + timedelta(minutes=set_length)
drinks_end = doors + timedelta(hours=2)
name = esc(headliner.strip()) or "Cashmara"

with st.sidebar:
    st.markdown(
        f'<div class="sb-readout">Counting down to<br>'
        f"<b>{long_date(onstage)}</b><br>"
        f"decks at <b>{clock12(onstage)}</b> "
        f'({tz_label.split(",")[0]})</div>',
        unsafe_allow_html=True,
    )

    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//System Override//Countdown//EN",
        "BEGIN:VEVENT",
        f"UID:{ms(onstage)}@systemoverride",
        f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{onstage.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"DTEND:{set_end.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{headliner.strip() or 'Cashmara'} @ System Override",
        f"LOCATION:{VENUE}\\, {ADDRESS}",
        f"DESCRIPTION:Doors {clock12(doors)}. On the decks {clock12(onstage)}. {EVENT_URL}",
        "BEGIN:VALARM", "TRIGGER:-PT30M", "ACTION:DISPLAY",
        "DESCRIPTION:Set starts in 30 minutes", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR",
    ])
    st.download_button(
        "Add the set to your calendar",
        ics,
        file_name="cashmara-system-override.ics",
        mime="text/calendar",
        use_container_width=True,
    )

# --------------------------------------------------------------------------- #
# Hero component: a floor lit from below. All HTML/CSS/JS so the clock ticks
# live, client-side, with motion spent in one place — the sound and the booth.
# --------------------------------------------------------------------------- #
HERO = r"""
<link href="https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500&display=swap" rel="stylesheet">
<style>
  :root{
    --mag:#ff00c1; --mag-d:#8f006b; --yel:#FEDA00; --yel-d:#f3ac02;
    --cy:#67dedf; --cy-d:#1d8587; --purple:#6700a9; --ink:#1a1620; --gray:#F9F8F8;
  }
  *{ box-sizing:border-box; margin:0; padding:0; }
  body{ font-family:'Rubik',sans-serif; background:transparent; color:#e9e5ee; }
  .wrap{ max-width:1040px; margin:0 auto; }

  /* ---------- HERO ---------- */
  .stage{
    position:relative; overflow:hidden; border-radius:20px;
    min-height:clamp(560px,70vh,690px);
    box-shadow:0 18px 46px rgba(255,0,193,.16); isolation:isolate;
  }
  .sky{ position:absolute; inset:0;
    background:linear-gradient(177deg,
      #0d0118 0%, #2c0a4a 15%, var(--purple) 37%, var(--mag-d) 60%,
      var(--mag) 84%, #ff5fd6 100%); }
  /* Two still light beams raking the room */
  .beam{ position:absolute; top:-12%; width:clamp(90px,13vw,150px); height:150%;
    background:linear-gradient(to bottom, rgba(103,222,223,.34), rgba(103,222,223,0) 78%);
    filter:blur(3px); }
  .beam.l{ left:12%; transform:rotate(13deg) ; }
  .beam.r{ right:16%; transform:rotate(-16deg);
    background:linear-gradient(to bottom, rgba(254,218,0,.26), rgba(254,218,0,0) 78%); }
  .ball{ position:absolute; left:66%; bottom:36%; width:clamp(84px,11vw,124px);
    aspect-ratio:1; border-radius:50%;
    background:
      repeating-conic-gradient(from 0deg, rgba(255,255,255,.16) 0 9deg, transparent 9deg 18deg),
      radial-gradient(circle at 42% 38%, #ffffff 0%, var(--cy) 46%, var(--cy-d) 100%);
    box-shadow:0 0 58px 16px rgba(103,222,223,.42); }

  .content{ position:relative; z-index:4;
    padding:clamp(30px,4.4vw,52px) clamp(26px,5vw,58px) clamp(238px,32vh,296px); }
  .eyebrow{ color:rgba(255,255,255,.82); font-weight:600;
    letter-spacing:.2em; text-transform:uppercase; font-size:clamp(.62rem,1.5vw,.74rem); }
  .title{ color:#fff; font-weight:900; line-height:.96; letter-spacing:-.015em;
    font-size:clamp(1.7rem,5.2vw,3rem); margin-top:14px;
    text-shadow:0 6px 30px rgba(44,10,74,.45); }
  .title em{ font-style:normal; display:block; }
  .loc{ color:rgba(255,255,255,.9); font-weight:400; margin-top:12px;
    font-size:clamp(.85rem,2.1vw,1rem); max-width:32ch; line-height:1.4; }

  .count{ display:flex; align-items:flex-end; gap:clamp(16px,3vw,30px);
    flex-wrap:wrap; margin-top:clamp(20px,3vw,34px); }
  .hours{ font-weight:900; color:#fff; line-height:.8; letter-spacing:-.04em;
    font-size:clamp(4.6rem,17vw,9.5rem); font-variant-numeric:tabular-nums;
    text-shadow:0 12px 44px rgba(44,10,74,.45); }
  .hours-lab{ color:rgba(255,255,255,.92); font-weight:500; font-style:italic;
    font-size:clamp(.95rem,2.4vw,1.25rem); padding-bottom:clamp(8px,1.4vw,16px); }

  .split{ display:flex; gap:clamp(18px,3.4vw,40px); margin-top:clamp(20px,3vw,30px); }
  .unit{ position:relative; padding-left:clamp(14px,2.6vw,28px); }
  .unit:first-child{ padding-left:0; }
  .unit:not(:first-child)::before{ content:""; position:absolute; left:0; top:4px;
    bottom:4px; width:1px; background:rgba(255,255,255,.28); }
  .unit .v{ font-weight:800; color:#fff; line-height:1;
    font-size:clamp(1.5rem,4.6vw,2.3rem); font-variant-numeric:tabular-nums; }
  .unit .k{ color:rgba(255,255,255,.7); font-weight:600; text-transform:uppercase;
    letter-spacing:.16em; font-size:clamp(.56rem,1.5vw,.66rem); margin-top:7px; }

  /* ---------- THE SOUND ---------- */
  .eq{ position:absolute; left:0; right:0; bottom:0; z-index:3;
    height:clamp(148px,21vh,188px); display:flex; align-items:flex-end;
    gap:clamp(3px,.75vw,7px); padding:0 clamp(12px,2.6vw,26px); }
  .bar{ flex:1; border-radius:7px 7px 0 0; transform-origin:bottom;
    background:linear-gradient(to top, var(--cy-d), var(--cy) 52%, #d6f7f8);
    animation:bounce var(--dur) ease-in-out var(--delay) infinite alternate; }
  @keyframes bounce{ from{ transform:scaleY(.22); } to{ transform:scaleY(1); } }
  .stage.live .bar{ animation-duration:calc(var(--dur) * .45);
    background:linear-gradient(to top, var(--mag-d), var(--mag) 52%, #ffd9f4); }

  .booth{ position:absolute; left:7%; bottom:clamp(126px,18vh,162px); z-index:2;
    width:clamp(120px,17vw,186px); filter:drop-shadow(0 8px 10px rgba(13,1,24,.5));
    animation:bob 1.9s ease-in-out infinite alternate; }
  @keyframes bob{ from{ transform:translateY(0); } to{ transform:translateY(-6px); } }
  .stage.live .booth{ animation-duration:.7s; }

  /* ---------- BELOW THE FOLD ---------- */
  .venue{ margin:22px 2px 0; color:#8d8794; font-weight:600; letter-spacing:.18em;
    text-transform:uppercase; font-size:clamp(.62rem,1.5vw,.72rem); }

  .night{ display:grid; grid-template-columns:repeat(2,1fr);
    border-radius:16px; overflow:hidden; background:transparent; }
  @media(max-width:640px){ .night{ grid-template-columns:1fr; } }
  .act{ padding:22px 24px; transition:background .25s; }
  .act .nm{ font-weight:800; text-transform:uppercase; letter-spacing:.1em; font-size:.74rem; }
  .act.d .nm{ color:var(--cy); } .act.s .nm{ color:var(--mag); }
  .act .at{ font-weight:900; font-size:2rem; color:#fff; line-height:1; margin-top:6px; }
  .act .at small{ font-size:.92rem; font-weight:600; color:#8d8794; margin-left:4px; }
  .act .desc{ color:#a49daf; font-size:.86rem; line-height:1.45; margin-top:9px; }
  .act.done .at, .act.done .desc, .act.done .nm{ opacity:.42; }
  .act.now{ background:linear-gradient(180deg, rgba(255,0,193,.09), rgba(255,0,193,.02)); }
  .act.now .nm::after{ content:" · on now"; color:var(--mag); }

  .rsvp{ display:inline-flex; align-items:center; gap:9px; margin-top:18px;
    color:var(--mag); font-weight:800; font-size:1rem; text-decoration:none;
    border-bottom:2px solid var(--mag); padding-bottom:3px;
    transition:gap .2s, color .2s, border-color .2s; }
  .rsvp:hover{ gap:15px; color:var(--mag-d); border-color:var(--mag-d); }
  .rsvp:focus-visible{ outline:3px solid var(--cy-d); outline-offset:4px; }


  @media (prefers-reduced-motion:reduce){
    .bar,.booth{ animation:none !important; }
    .bar{ transform:scaleY(.62); } }
  #confetti{ position:absolute; inset:0; z-index:5; pointer-events:none; }
</style>

<div class="wrap">
  <div class="stage" id="stage">
    <div class="sky">
      <div class="beam l"></div><div class="beam r"></div>
      <div class="ball"></div>
    </div>

    <div class="content">
      <div class="eyebrow">__NAME__ ON THE DECKS,  __DATE_LONG__</div>
      <h1 class="title"><em>System Override</em><em>Seattle Tech Week Rave</em></h1>
      <p class="loc">When mpathic trades our laptops for lasers. Y2K.</p>

      <div class="count">
        <div class="hours" id="hours">—</div>
        <div class="hours-lab" id="bigword">hours until Cashmara's set</div>
      </div>

      <div class="split">
        <div class="unit"><div class="v" id="d">0</div><div class="k">days</div></div>
        <div class="unit"><div class="v" id="h">0</div><div class="k">hours</div></div>
        <div class="unit"><div class="v" id="m">0</div><div class="k">minutes</div></div>
        <div class="unit"><div class="v" id="sec">0</div><div class="k">seconds</div></div>
      </div>
    </div>

    <svg class="booth" viewBox="0 0 200 130" xmlns="http://www.w3.org/2000/svg">
      <g fill="none" stroke="#0d0118" stroke-width="10" stroke-linecap="round">
        <path d="M82 74 C70 80 62 89 57 101"/>
        <path d="M118 74 C130 80 138 89 143 101"/>
      </g>
      <g fill="#0d0118">
        <path d="M86 28 C74 33 68 45 69 57 C69 62 71 65 75 66 C79 63 79 56 82 48 C82 38 84 31 86 28 Z"/>
        <path d="M114 28 C126 33 132 45 131 57 C131 62 129 65 125 66 C121 63 121 56 118 48 C118 38 116 31 114 28 Z"/>
      </g>
      <g fill="#0d0118">
        <path d="M76 98 C76 70 87 50 100 50 C113 50 124 70 124 98 Z"/>
        <circle cx="100" cy="33" r="18"/>
        <rect x="24" y="96" width="152" height="30" rx="5"/>
      </g>
      <g fill="none" stroke="#67dedf" stroke-width="5" stroke-linecap="round">
        <path d="M82 27 A 19 19 0 0 1 118 27"/>
      </g>
      <g fill="#67dedf">
        <circle cx="81" cy="33" r="5.5"/><circle cx="119" cy="33" r="5.5"/>
        <circle cx="55" cy="111" r="9"/><circle cx="145" cy="111" r="9"/>
        <rect x="88" y="106" width="24" height="4" rx="2"/>
      </g>
      <g fill="#FEDA00"><circle cx="100" cy="117" r="2.6"/></g>
    </svg>

    <div class="eq" id="eq"></div>
    <canvas id="confetti"></canvas>
  </div>

  <div class="night">
    <div class="act d" data-ts="__DOORS_MS__" data-until="__SET_MS__">
      <div class="nm">Doors</div><div class="at">__DOORS_T__<small>__DOORS_AP__</small></div>
      <div class="desc">Free drink tickets.</div></div>
    <div class="act s" data-ts="__SET_MS__" data-until="__SET_END_MS__">
      <div class="nm">__NAME__</div><div class="at">__SET_T__<small>__SET_AP__</small></div>
      <div class="desc">Cashmara reps mpathic.</div></div>
  </div>

  <div class="venue">__VENUE__ &mdash; __ADDRESS__</div>

  <a class="rsvp" href="__EVENT_URL__" target="_blank" rel="noopener">RSVP & Details on Luma <span>&rarr;</span></a>
</div>

<script>
  const DOORS = __DOORS_MS__, SET = __SET_MS__, SET_END = __SET_END_MS__;
  const pad = n => String(n).padStart(2,'0');
  const fmt = n => n.toLocaleString('en-US');
  const $ = id => document.getElementById(id);
  const elHours=$('hours'), elBig=$('bigword'), elD=$('d'), elH=$('h'),
        elM=$('m'), elS=$('sec'), stage=$('stage');

  // The sound: 30 bars, heights and tempos varied so it reads as a mix,
  // not a wave. Deterministic, so it looks composed rather than random.
  const eq = $('eq');
  for(let i=0;i<30;i++){
    const b=document.createElement('div');
    b.className='bar';
    const swell = Math.abs(Math.sin(i*0.72)) * 0.55 + Math.abs(Math.cos(i*0.31)) * 0.3;
    b.style.height = (26 + swell*72) + '%';
    b.style.setProperty('--dur', (0.78 + (i%5)*0.16).toFixed(2) + 's');
    b.style.setProperty('--delay', ((i%7)*0.11).toFixed(2) + 's');
    eq.appendChild(b);
  }

  const acts = document.querySelectorAll('.act[data-ts]');
  function markActs(now){
    acts.forEach(a=>{
      const start = Number(a.dataset.ts);
      const until = a.dataset.until ? Number(a.dataset.until) : Infinity;
      const live = now >= start && now < until;
      a.classList.toggle('now', live);
      a.classList.toggle('done', now >= start && !live);
    });
  }

  let fired=false;
  function tick(){
    const now = Date.now();
    markActs(now);
    stage.classList.toggle('live', now >= SET && now < SET_END);

    if(now >= SET){
      const since = now - SET;
      if(now < SET_END){
        elHours.textContent = fmt(Math.floor(since/60000));
        elBig.textContent = "minutes into the set";
      }else{
        elHours.textContent = fmt(Math.floor((now-SET_END)/3600000));
        elBig.textContent = "hours since the lights came up";
      }
      elD.textContent="—"; elH.textContent="—"; elM.textContent="—"; elS.textContent="—";
      if(!fired){ fired=true; celebrate(); }
      return;
    }

    const diff = SET - now;
    elHours.textContent = fmt(Math.floor(diff/3600000));
    elBig.textContent = now >= DOORS
      ? "hours until the set — doors are open"
      : "hours until the set";
    elD.textContent = Math.floor(diff/86400000);
    elH.textContent = pad(Math.floor(diff/3600000)%24);
    elM.textContent = pad(Math.floor(diff/60000)%60);
    elS.textContent = pad(Math.floor(diff/1000)%60);
  }

  function celebrate(){
    const cv=$('confetti'), ctx=cv.getContext('2d'), st=cv.parentElement;
    cv.width=st.clientWidth; cv.height=st.clientHeight;
    const cols=['#ff00c1','#FEDA00','#67dedf','#6700a9','#8f006b'];
    const bits=Array.from({length:150},()=>({x:Math.random()*cv.width,y:-20-Math.random()*cv.height,
      r:4+Math.random()*6,c:cols[(Math.random()*cols.length)|0],vx:(Math.random()-.5)*2.4,
      vy:2+Math.random()*3.4,a:Math.random()*6.28,va:(Math.random()-.5)*.3}));
    let f=0;(function loop(){ctx.clearRect(0,0,cv.width,cv.height);
      bits.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.a+=p.va;if(p.y>cv.height+20)p.y=-20;
        ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.a);ctx.fillStyle=p.c;
        ctx.fillRect(-p.r/2,-p.r/2,p.r,p.r*1.6);ctx.restore();});
      if(f++<470)requestAnimationFrame(loop);else ctx.clearRect(0,0,cv.width,cv.height);})();
  }
  tick(); setInterval(tick,1000);
</script>
"""

doors_t, doors_ap = hour_only(doors)
set_t, set_ap = hour_only(onstage)

for token, value in {
    "__DOORS_MS__": str(ms(doors)),
    "__SET_MS__": str(ms(onstage)),
    "__SET_END_MS__": str(ms(set_end)),
    "__DATE_LONG__": long_date(onstage).upper(),
    "__DOORS_T__": doors_t, "__DOORS_AP__": doors_ap,
    "__SET_T__": set_t, "__SET_AP__": set_ap,
    "__DRINKS_T__": clock12(drinks_end),
    "__SET_LEN__": str(set_length),
    "__VENUE__": VENUE,
    "__ADDRESS__": ADDRESS,
    "__EVENT_URL__": EVENT_URL,
    "__NAME__": name,
}.items():
    HERO = HERO.replace(token, value)

if hasattr(st, "iframe"):  # Streamlit >= 1.59
    st.iframe(HERO, height="content")
else:
    import streamlit.components.v1 as components

    components.html(HERO, height=1160, scrolling=True)
