/* PCompass characters: original illustrated figures, one per political type.
   charSvg(code, campColor, opts) returns an animated inline SVG. */
const INK = "#18212F";
let CH_UID = 0;

const LOOKS = {
  CPI: { skin: "#C98E6B", hair: "bun",    hairC: "#3B2A20", outfit: "cardigan", brows: "friendly",   mouth: "smile", prop: "plant" },
  CPS: { skin: "#F2C9A5", hair: "curly",  hairC: "#9A4A2A", outfit: "hoodie",   brows: "determined", mouth: "open",  prop: "placard", pants: "#3E5A7A" },
  BPI: { skin: "#7A4A30", hair: "long",   hairC: "#15110F", outfit: "coat",     brows: "friendly",   mouth: "smile", acc: "scarf", prop: "suitcase" },
  BPS: { skin: "#C48A62", hair: "curly",  hairC: "#1C1715", outfit: "tee",      brows: "raised",     mouth: "smirk", acc: "headphones", prop: "plane", pants: "#3E5A7A" },
  MPI: { skin: "#F0CFAE", hair: "swoop",  hairC: "#D9B25A", outfit: "shirt",    brows: "raised",     mouth: "grin",  acc: "glasses", prop: "rocket" },
  MPS: { skin: "#E3B08B", hair: "short",  hairC: "#5A3B26", outfit: "jacket",   brows: "calm",       mouth: "smirk", acc: "shades", prop: "coin", pants: "#3E5A7A" },
  CNI: { skin: "#8D5A3B", hair: "short",  hairC: "#1E1A18", outfit: "hivis",    brows: "friendly",   mouth: "grin",  hat: "hardhat", prop: "blueprint", inner: "#4A5260" },
  CNS: { skin: "#B7795A", hair: "short",  hairC: "#8E8A86", outfit: "sweater",  brows: "determined", mouth: "open",  hat: "flatcap", prop: "megaphone" },
  BNI: { skin: "#D9A37E", hair: "bob",    hairC: "#2F2A26", outfit: "blazer",   brows: "calm",       mouth: "calm",  acc: "halfmoon", prop: "scales" },
  BNS: { skin: "#9C6644", hair: "short",  hairC: "#2A1E18", outfit: "hoodie",   brows: "determined", mouth: "calm",  hat: "beanie", prop: "phone", pants: "#3E5A7A" },
  MNI: { skin: "#EAC0A0", hair: "part",   hairC: "#6A4A32", outfit: "shirt",    brows: "calm",       mouth: "smile", prop: "tablet" },
  MNS: { skin: "#A8704A", hair: "swoop",  hairC: "#2E2420", outfit: "vest",     brows: "raised",     mouth: "grin",  prop: "opensign", inner: "#F2EFE6" },
  CTI: { skin: "#E8B894", hair: "long",   hairC: "#B9B4AC", outfit: "cardigan", brows: "friendly",   mouth: "smile", prop: "lantern" },
  CTS: { skin: "#EAC2A0", hair: "bald",   hairC: "#6B5040", outfit: "sweater",  brows: "determined", mouth: "calm",  acc: "beard", prop: "pennant" },
  BTI: { skin: "#D7A07B", hair: "bob",    hairC: "#7A3B22", outfit: "apron",    brows: "friendly",   mouth: "smile", prop: "pie" },
  BTS: { skin: "#A86D47", hair: "braid",  hairC: "#4A2E1E", outfit: "overall",  brows: "calm",       mouth: "smile", hat: "straw", prop: "wheat", inner: "#E7DCC4" },
  MTI: { skin: "#EDC6A3", hair: "part",   hairC: "#8F8A84", outfit: "suit",     brows: "calm",       mouth: "calm",  prop: "briefcase" },
  MTS: { skin: "#F1C8A6", hair: "short",  hairC: "#3A2C22", outfit: "shirt",    brows: "determined", mouth: "open",  acc: "sleeves", prop: "microphone" },
};

function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  const c = [n >> 16, (n >> 8) & 255, n & 255].map(v => Math.round(f < 0 ? v * (1 + f) : v + (255 - v) * f));
  return "#" + c.map(v => Math.max(0, Math.min(255, v)).toString(16).padStart(2, "0")).join("");
}
const SK = `stroke="${INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"`;
const SK2 = `stroke="${INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"`;

/* ---------- hair ---------- */
function hairBack(kind, c) {
  if (kind === "long") return `<path d="M66 130 Q62 96 68 74 Q74 52 100 52 Q126 52 132 74 Q138 96 134 130 Q124 126 122 104 Q118 74 100 70 Q82 74 78 104 Q76 126 66 130Z" fill="${c}" ${SK}/>`;
  if (kind === "braid") return `<path d="M120 96 Q132 110 128 132" fill="none" stroke="${INK}" stroke-width="13" stroke-linecap="round"/><path d="M120 96 Q132 110 128 132" fill="none" stroke="${c}" stroke-width="8" stroke-linecap="round" stroke-dasharray="5 3"/><circle cx="128" cy="136" r="4" fill="#B5523A" ${SK2}/>`;
  return "";
}
function hairFront(kind, c) {
  const hl = shade(c, .3);
  switch (kind) {
    case "short": return `<path d="M69 86 Q68 54 100 53 Q132 54 131 86 Q126 70 112 66 Q100 72 86 67 Q74 72 69 86Z" fill="${c}" ${SK}/><path d="M84 60 Q96 56 108 58" fill="none" stroke="${hl}" stroke-width="2.6" stroke-linecap="round"/>`;
    case "part":  return `<path d="M69 86 Q68 54 100 53 Q132 54 131 86 Q128 68 110 64 L106 72 Q90 66 78 70 Q72 76 69 86Z" fill="${c}" ${SK}/><path d="M112 60 Q122 64 126 74" fill="none" stroke="${hl}" stroke-width="2.6" stroke-linecap="round"/>`;
    case "swoop": return `<path d="M68 84 Q66 50 104 50 Q134 52 132 84 Q126 66 108 66 Q94 62 84 72 Q74 74 68 84Z" fill="${c}" ${SK}/><path d="M84 60 Q100 53 118 60" fill="none" stroke="${hl}" stroke-width="2.6" stroke-linecap="round"/>`;
    case "bun":   return `<circle cx="100" cy="50" r="12" fill="${c}" ${SK}/><path d="M94 46 Q100 42 106 46" fill="none" stroke="${hl}" stroke-width="2.4" stroke-linecap="round"/><path d="M69 88 Q68 56 100 56 Q132 56 131 88 Q124 70 100 68 Q76 70 69 88Z" fill="${c}" ${SK}/>`;
    case "curly": return `<g fill="${c}" ${SK}>${[[74,74],[80,60],[92,52],[106,51],[119,57],[127,70],[71,88],[129,86]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="11"/>`).join("")}</g><path d="M74 78 Q100 62 126 78 L126 70 Q100 56 74 70Z" fill="${c}"/><g fill="none" stroke="${hl}" stroke-width="2" stroke-linecap="round"><path d="M88 50 Q92 47 96 49"/><path d="M114 53 Q118 52 121 55"/></g>`;
    case "long":
    case "braid": return `<path d="M70 84 Q72 56 100 54 Q128 56 130 84 Q120 68 104 66 Q92 70 84 66 Q74 72 70 84Z" fill="${c}" ${SK}/><path d="M88 60 Q100 56 112 60" fill="none" stroke="${hl}" stroke-width="2.4" stroke-linecap="round"/>`;
    case "bob":   return `<path d="M66 108 Q62 70 74 60 Q86 50 100 51 Q120 50 130 62 Q138 74 134 108 Q126 106 124 92 Q120 70 100 68 Q80 70 76 92 Q74 106 66 108Z" fill="${c}" ${SK}/><path d="M86 58 Q100 53 114 58" fill="none" stroke="${hl}" stroke-width="2.4" stroke-linecap="round"/>`;
    default: return "";
  }
}

/* ---------- hats and face accessories ---------- */
function hatSvg(kind) {
  switch (kind) {
    case "hardhat": return `<path d="M68 76 Q68 44 100 44 Q132 44 132 76Z" fill="#E7B53E" ${SK}/><path d="M78 70 Q80 52 96 48" fill="none" stroke="#F6D88A" stroke-width="3" stroke-linecap="round"/><rect x="62" y="72" width="76" height="8" rx="4" fill="#D9A52E" ${SK}/><path d="M100 45 L100 72" stroke="${INK}" stroke-width="2.4"/>`;
    case "flatcap": return `<path d="M68 72 Q70 50 100 50 Q128 50 132 70 Q152 72 140 79 L68 79Z" fill="#5B5F66" ${SK}/><path d="M76 66 Q92 56 120 60" fill="none" stroke="#7B8088" stroke-width="2.4" stroke-linecap="round"/>`;
    case "beanie":  return `<path d="M70 74 Q70 44 100 44 Q130 44 130 74Z" fill="#C9473D" ${SK}/><g stroke="#A73A31" stroke-width="2"><path d="M82 52 L82 70"/><path d="M92 47 L92 70"/><path d="M108 47 L108 70"/><path d="M118 52 L118 70"/></g><rect x="68" y="68" width="64" height="12" rx="5" fill="#A73A31" ${SK}/><circle cx="100" cy="40" r="6" fill="#C9473D" ${SK}/>`;
    case "straw":   return `<ellipse cx="100" cy="66" rx="50" ry="10" fill="#E2C47C" ${SK}/><path d="M74 64 Q76 40 100 40 Q124 40 126 64Z" fill="#E9CF8E" ${SK}/><path d="M76 58 L124 58" stroke="#B5523A" stroke-width="5"/><g stroke="#C9A85E" stroke-width="1.4"><path d="M60 66 L72 64"/><path d="M128 64 L140 66"/></g>`;
    default: return "";
  }
}
function faceAcc(kind) {
  switch (kind) {
    case "glasses":  return `<g fill="rgba(255,255,255,.18)" stroke="${INK}" stroke-width="2.4"><circle cx="89" cy="88" r="7.5"/><circle cx="111" cy="88" r="7.5"/></g><path d="M96.5 88 L103.5 88 M81.5 86 L72 84 M118.5 86 L128 84" stroke="${INK}" stroke-width="2.2"/>`;
    case "halfmoon": return `<path d="M81 89 Q89 98 97 89 Z M103 89 Q111 98 119 89 Z" fill="rgba(255,255,255,.2)" stroke="${INK}" stroke-width="2.2"/><path d="M97 89 L103 89" stroke="${INK}" stroke-width="2"/>`;
    case "shades":   return `<path d="M78 82 L98 82 L96 95 L82 95Z M102 82 L122 82 L118 95 L104 95Z" fill="${INK}"/><path d="M83 85 L88 85 M107 85 L112 85" stroke="#5B6470" stroke-width="2" stroke-linecap="round"/><path d="M98 85 L102 85" stroke="${INK}" stroke-width="2.4"/>`;
    case "beard":    return `<path d="M72 92 Q74 124 100 126 Q126 124 128 92 Q120 106 110 105 L90 105 Q80 106 72 92Z" fill="#6B5040" ${SK}/><path d="M88 112 Q100 116 112 112" fill="none" stroke="#8A6A55" stroke-width="2" stroke-linecap="round"/>`;
    case "headphones": return `<path d="M70 86 Q70 46 100 46 Q130 46 130 86" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round"/><path d="M70 86 Q70 46 100 46 Q130 46 130 86" fill="none" stroke="#C9473D" stroke-width="3.5" stroke-linecap="round"/><rect x="62" y="80" width="12" height="20" rx="5" fill="#C9473D" ${SK}/><rect x="126" y="80" width="12" height="20" rx="5" fill="#C9473D" ${SK}/>`;
    case "scarf":    return `<path d="M76 124 Q100 136 124 124 L124 134 Q100 146 76 134Z" fill="#D9A441" ${SK}/><path d="M84 132 L84 140 M96 136 L96 143 M108 136 L108 143" stroke="#B9842A" stroke-width="2"/><path class="ch-flutter" style="transform-origin:114px 134px" d="M112 134 L120 172 L106 170 Z" fill="#D9A441" ${SK}/>`;
    default: return "";
  }
}

/* ---------- face ---------- */
function faceSvg(L) {
  const browC = L.hair === "bald" ? shade(L.skin, -.5) : shade(L.hairC, -.15);
  const brows = {
    friendly:   "M83 79 Q89 75.5 95 79 M105 79 Q111 75.5 117 79",
    determined: "M83 77.5 L95 81 M105 81 L117 77.5",
    raised:     "M83 76 Q89 71.5 95 76 M105 76 Q111 71.5 117 76",
    calm:       "M84 79 L95 78.5 M105 78.5 L116 79",
  }[L.brows || "friendly"];
  const mouth = {
    smile: `<path d="M92 101 Q100 108 108 101" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`,
    grin:  `<path d="M91 100 Q100 112 109 100 Z" fill="#7A2E2E" ${SK2}/><path d="M93 101 L107 101 L105 104 L95 104Z" fill="#FBFCF9"/>`,
    open:  `<ellipse cx="100" cy="104" rx="6" ry="5" fill="#7A2E2E" ${SK2}/><path d="M96 106.5 Q100 104.5 104 106.5" fill="none" stroke="#D86F6F" stroke-width="2"/>`,
    smirk: `<path d="M93 103 Q101 107 108 100" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`,
    calm:  `<path d="M94 103 Q100 105.5 106 103" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`,
  }[L.mouth || "smile"];
  const hidden = L.acc === "shades";
  return `
    <circle cx="70" cy="90" r="6.5" fill="${L.skin}" ${SK}/><circle cx="130" cy="90" r="6.5" fill="${L.skin}" ${SK}/>
    <path d="M69 88 Q71 91 69 93 M131 88 Q129 91 131 93" fill="none" stroke="${shade(L.skin, -.3)}" stroke-width="1.8" stroke-linecap="round"/>
    <circle cx="100" cy="86" r="30" fill="${L.skin}" ${SK}/>
    <path d="M118 66 Q130 78 128 98" fill="none" stroke="${shade(L.skin, -.12)}" stroke-width="6" stroke-linecap="round" opacity=".7"/>
    ${hidden ? "" : `<g class="ch-eyes"><ellipse cx="89" cy="89" rx="3.6" ry="4.4" fill="${INK}"/><ellipse cx="111" cy="89" rx="3.6" ry="4.4" fill="${INK}"/><circle cx="90.3" cy="87.4" r="1.3" fill="#FFF"/><circle cx="112.3" cy="87.4" r="1.3" fill="#FFF"/></g>`}
    <path d="${brows}" fill="none" stroke="${browC}" stroke-width="3.2" stroke-linecap="round"/>
    <path d="M100 92 Q104 97 99 99" fill="none" stroke="${shade(L.skin, -.35)}" stroke-width="2.2" stroke-linecap="round"/>
    <circle cx="81" cy="99" r="4.5" fill="#E08A7A" opacity=".4"/><circle cx="119" cy="99" r="4.5" fill="#E08A7A" opacity=".4"/>
    ${mouth}`;
}

/* ---------- outfits ---------- */
const TORSO = "M64 188 Q60 130 100 120 Q140 130 136 188Z";
const COAT  = "M62 198 Q58 130 100 120 Q142 130 138 198Z";
function outfitSvg(L, top, id) {
  const dark = shade(top, -.28), light = shade(top, .45);
  const body = L.outfit === "coat" ? COAT : TORSO;
  const base = ["hivis", "vest", "overall"].includes(L.outfit) ? L.inner : top;
  let d = "";
  switch (L.outfit) {
    case "sweater":  d = `<path d="M86 123 Q100 133 114 123" fill="none" stroke="${dark}" stroke-width="5" stroke-linecap="round"/><path d="M65 180 L135 180" stroke="${dark}" stroke-width="2"/><g stroke="${dark}" stroke-width="1.6">${[72, 80, 88, 96, 104, 112, 120, 128].map(x => `<path d="M${x} 181 L${x} 187"/>`).join("")}</g>`; break;
    case "cardigan": d = `<path d="M89 122 L100 152 L111 122Z" fill="#F2EFE6" ${SK2}/><path d="M90 123 L97 188 M110 123 L103 188" stroke="${INK}" stroke-width="2"/><g fill="${light}" ${SK2}><circle cx="96" cy="160" r="2.4"/><circle cx="96" cy="172" r="2.4"/></g><path d="M72 160 L86 160 L86 172 L72 172Z M114 160 L128 160 L128 172 L114 172Z" fill="none" stroke="${dark}" stroke-width="2"/>`; break;
    case "hoodie":   d = `<path d="M74 128 Q100 108 126 128 Q114 138 100 138 Q86 138 74 128Z" fill="${dark}" ${SK2}/><path d="M95 136 L94 154 M105 136 L106 154" stroke="#FBFCF9" stroke-width="2.2" stroke-linecap="round"/><path d="M82 166 L118 166 L114 184 L86 184Z" fill="none" stroke="${dark}" stroke-width="2.4"/>`; break;
    case "coat":     d = `<path d="M88 122 L100 146 L92 168 L80 134Z M112 122 L100 146 L108 168 L120 134Z" fill="${dark}" ${SK2}/><path d="M100 146 L100 198" stroke="${INK}" stroke-width="2"/><path d="M63 172 L137 172" stroke="${dark}" stroke-width="5"/><g fill="${light}" ${SK2}><circle cx="94" cy="160" r="2.2"/><circle cx="94" cy="184" r="2.2"/></g>`; break;
    case "tee":      d = `<path d="M88 123 Q100 131 112 123" fill="none" stroke="${dark}" stroke-width="4" stroke-linecap="round"/><circle cx="100" cy="154" r="11" fill="${light}" ${SK2}/><path d="M94 154 L106 154 M100 148 L100 160" stroke="${top}" stroke-width="2.6" stroke-linecap="round"/>`; break;
    case "shirt":    d = `<path d="M88 121 L100 132 L96 140 L84 128Z M112 121 L100 132 L104 140 L116 128Z" fill="${light}" ${SK2}/><path d="M100 134 L100 188" stroke="${dark}" stroke-width="2"/><g fill="${light}">${[146, 160, 174].map(y => `<circle cx="100" cy="${y}" r="1.8"/>`).join("")}</g><path d="M110 146 L122 146 L122 158 L110 158Z" fill="none" stroke="${dark}" stroke-width="2"/>`; break;
    case "jacket":   d = `<path d="M84 122 L94 146 L86 152 L76 128Z M116 122 L106 146 L114 152 L124 128Z" fill="${dark}" ${SK2}/><path d="M100 128 L100 188" stroke="#B8BCC2" stroke-width="2.4"/><path d="M70 166 L86 166 M114 166 L130 166" stroke="${dark}" stroke-width="2.4"/>`; break;
    case "hivis":    d = `<path d="M70 132 Q84 124 92 124 L98 188 L66 188 Q64 160 70 132Z M130 132 Q116 124 108 124 L102 188 L134 188 Q136 160 130 132Z" fill="${top}" ${SK2}/><path d="M66 152 L98 152 M102 152 L134 152 M65 168 L98 168 M102 168 L135 168" stroke="#E9EEF0" stroke-width="4"/>`; break;
    case "blazer":   d = `<path d="M90 122 L100 150 L110 122Z" fill="#F2EFE6" ${SK2}/><path d="M86 122 L98 154 L88 160 L78 130Z M114 122 L102 154 L112 160 L122 130Z" fill="${dark}" ${SK2}/><circle cx="100" cy="166" r="2.6" fill="${light}" ${SK2}/><path d="M112 140 L120 136 L122 142Z" fill="#FBFCF9" ${SK2}/>`; break;
    case "suit":     d = `<path d="M90 122 L100 152 L110 122Z" fill="#F2EFE6" ${SK2}/><path d="M100 126 L95 134 L100 160 L105 134Z" fill="#7C2F35" ${SK2}/><path d="M86 122 L98 156 L88 162 L78 130Z M114 122 L102 156 L112 162 L122 130Z" fill="${dark}" ${SK2}/><circle cx="100" cy="170" r="2.6" fill="${light}" ${SK2}/>`; break;
    case "vest":     d = `<path d="M72 132 Q84 124 92 124 L100 154 L100 188 L68 188 Q66 160 72 132Z M128 132 Q116 124 108 124 L100 154 L100 188 L132 188 Q134 160 128 132Z" fill="${top}" ${SK2}/><g fill="${light}" ${SK2}><circle cx="100" cy="162" r="2.2"/><circle cx="100" cy="174" r="2.2"/></g><path d="M78 160 L90 160" stroke="${dark}" stroke-width="2"/><path d="M90 124 L100 136 L110 124" fill="none" stroke="${INK}" stroke-width="2"/>`; break;
    case "apron":    d = `<path d="M88 123 Q100 132 112 123" fill="none" stroke="${dark}" stroke-width="4" stroke-linecap="round"/><path d="M82 136 L118 136 L122 190 L78 190Z" fill="#FBFCF9" ${SK2}/><path d="M86 160 L114 160 L112 172 L88 172Z" fill="none" stroke="${INK}" stroke-width="1.6"/><path d="M82 140 L68 146 M118 140 L132 146" stroke="#FBFCF9" stroke-width="3"/>`; break;
    case "overall":  d = `<path d="M80 146 L120 146 L122 188 L78 188Z" fill="${top}" ${SK2}/><path d="M84 146 L80 124 M116 146 L120 124" stroke="${top}" stroke-width="6"/><path d="M84 146 L80 124 M116 146 L120 124" stroke="${INK}" stroke-width="1.4" opacity=".5"/><g fill="#E7B53E" ${SK2}><circle cx="85" cy="150" r="2.6"/><circle cx="115" cy="150" r="2.6"/></g><path d="M90 158 L110 158 L110 170 L90 170Z" fill="none" stroke="${dark}" stroke-width="2"/><g stroke="${shade(L.inner, -.15)}" stroke-width="1.6"><path d="M70 136 L76 172"/><path d="M130 136 L124 172"/></g>`; break;
  }
  return `<defs><clipPath id="${id}"><path d="${body}"/></clipPath></defs>
    <path d="${body}" fill="${base}" ${SK}/>
    <g clip-path="url(#${id})">${d}<rect x="108" y="110" width="40" height="100" fill="#000" opacity=".11"/><rect x="58" y="110" width="12" height="100" fill="#FFF" opacity=".1"/></g>
    <path d="${body}" fill="none" ${SK}/>`;
}

/* ---------- props ---------- */
function propSvg(kind, fam) {
  switch (kind) {
    case "plant": return `<g><path d="M140 152 L166 152 L162 176 L144 176Z" fill="#B8613E" ${SK}/><path d="M139 152 L167 152 L166 158 L140 158Z" fill="#A0522F" ${SK2}/>
      <g class="ch-sway" style="transform-origin:153px 152px"><path d="M153 152 L153 114" stroke="#2F6B3A" stroke-width="3.4" fill="none"/>
      <path d="M153 132 Q136 126 137 110 Q152 114 153 132Z M153 124 Q171 118 171 102 Q156 104 153 124Z M153 116 Q145 98 156 90 Q163 104 153 116Z" fill="#4E9A5C" ${SK}/>
      <path d="M153 130 Q144 122 140 114 M153 122 Q162 114 167 106" fill="none" stroke="#2F6B3A" stroke-width="1.6"/></g></g>`;
    case "blueprint": return `<g class="ch-tilt" style="transform-origin:152px 150px"><g transform="rotate(-24 145 141)"><rect x="138" y="112" width="14" height="58" rx="7" fill="#4C7FB8" ${SK}/><path d="M141 124 L149 124 M141 136 L149 136 M141 148 L149 148" stroke="#DCE8F4" stroke-width="1.6"/></g><ellipse cx="133" cy="117" rx="7" ry="4" fill="#DCE8F4" ${SK} transform="rotate(-24 133 117)"/></g>`;
    case "placard": return `<g class="ch-wave" style="transform-origin:152px 152px"><path d="M152 152 L152 66" stroke="#8A6A45" stroke-width="5" stroke-linecap="round"/>
      <rect x="120" y="38" width="64" height="38" rx="3" fill="#FBFCF9" ${SK}/><path d="M124 72 L180 72" stroke="#E3E7DF" stroke-width="3"/><path d="M152 70 Q137 60 141 47 Q149 49 152 57 Q155 49 163 47 Q167 60 152 70Z" fill="#C9473D" ${SK2}/></g>`;
    case "megaphone": return `<g><path d="M146 140 L168 124 L173 162 L148 152Z" fill="#E7B53E" ${SK}/><path d="M168 124 L173 162" stroke="#C9973A" stroke-width="4"/><rect x="139" y="140" width="10" height="14" rx="3" fill="${INK}"/>
      <g class="ch-pulse" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"><path d="M179 132 Q187 143 179 154"/><path d="M187 124 Q199 143 187 162"/></g></g>`;
    case "lantern": return `<g class="ch-swing" style="transform-origin:152px 140px"><path d="M146 146 Q152 133 158 146" fill="none" stroke="${INK}" stroke-width="3"/>
      <path d="M142 146 L162 146 L160 150 L144 150Z" fill="${INK}"/><rect x="140" y="150" width="24" height="26" rx="4" fill="#F4E4B0" ${SK}/><circle class="ch-glow" cx="152" cy="163" r="7" fill="#F2B33D"/><path d="M146 150 L146 176 M158 150 L158 176" stroke="${INK}" stroke-width="1.6"/><rect x="138" y="174" width="28" height="5" rx="2" fill="${INK}"/></g>`;
    case "pie": return `<g><ellipse cx="152" cy="146" rx="23" ry="7" fill="#D8D2C8" ${SK}/><path d="M133 144 Q152 127 171 144Z" fill="#D99B4E" ${SK}/><path d="M142 139 L146 135 M152 136 L152 131 M162 139 L158 135" stroke="#A86A2E" stroke-width="2" stroke-linecap="round"/>
      <g class="ch-steam" fill="none" stroke="#9AA3AE" stroke-width="2.4" stroke-linecap="round"><path d="M146 126 Q142 118 146 110 Q150 102 146 94"/><path d="M158 126 Q154 118 158 110 Q162 102 158 94"/></g></g>`;
    case "pennant": return `<g><path d="M152 154 L152 50" stroke="#8A6A45" stroke-width="5" stroke-linecap="round"/><circle cx="152" cy="49" r="4" fill="#E7B53E" ${SK2}/>
      <g class="ch-flutter" style="transform-origin:152px 66px"><path d="M154 54 L194 66 L154 80Z" fill="${shade(fam, .1)}" ${SK}/><path d="M154 62 L178 66 L154 72" fill="none" stroke="#FBFCF9" stroke-width="2.4"/></g></g>`;
    case "suitcase": return `<g class="ch-swing" style="transform-origin:152px 146px"><path d="M144 154 L144 146 L160 146 L160 154" fill="none" stroke="${INK}" stroke-width="3"/>
      <rect x="130" y="154" width="44" height="32" rx="4" fill="#6E8FA8" ${SK}/><path d="M130 164 L174 164" stroke="#56778F" stroke-width="2"/><circle cx="141" cy="174" r="5" fill="#E7B53E" ${SK2}/><rect x="152" y="170" width="14" height="9" rx="2" fill="#C9473D" ${SK2}/><circle cx="163" cy="160" r="2.6" fill="#FBFCF9"/></g>`;
    case "rocket": return `<g class="ch-float"><g transform="rotate(20 160 104)"><path d="M160 72 Q173 90 171 114 L149 114 Q147 90 160 72Z" fill="#FBFCF9" ${SK}/><path d="M160 72 Q166 79 168 86 L152 86 Q154 79 160 72Z" fill="#C9473D" ${SK2}/>
      <circle cx="160" cy="98" r="5" fill="#4C7FB8" ${SK}/><path d="M149 104 L140 118 L149 114Z M171 104 L180 118 L171 114Z" fill="#C9473D" ${SK}/>
      <path class="ch-flicker" d="M153 116 Q160 136 167 116Z" fill="#F2B33D" style="transform-origin:160px 116px"/><path class="ch-flicker" d="M156 116 Q160 128 164 116Z" fill="#FBE7A6" style="transform-origin:160px 116px"/></g></g>`;
    case "plane": return `<g class="ch-fly"><path d="M148 82 L188 64 L162 98 L158 86Z" fill="#FBFCF9" ${SK}/><path d="M158 86 L188 64 L162 90Z" fill="#E3E7DF" ${SK2}/></g>`;
    case "coin": return `<g class="ch-toss"><g class="ch-flip" style="transform-origin:156px 104px"><circle cx="156" cy="104" r="11" fill="#E7B53E" ${SK}/><circle cx="156" cy="104" r="6.5" fill="none" stroke="#C9973A" stroke-width="2"/></g></g>`;
    case "scales": return `<g><path d="M152 152 L152 94" stroke="#8A6A45" stroke-width="4" stroke-linecap="round"/><circle cx="152" cy="92" r="4" fill="#E7B53E" ${SK2}/>
      <g class="ch-tilt" style="transform-origin:152px 96px"><path d="M126 96 L178 96" stroke="${INK}" stroke-width="3.4" stroke-linecap="round"/>
      <path d="M126 96 L118 116 M126 96 L134 116 M178 96 L170 116 M178 96 L186 116" stroke="${INK}" stroke-width="1.6"/>
      <path d="M116 116 Q126 126 136 116Z M168 116 Q178 126 188 116Z" fill="#E7B53E" ${SK2}/></g></g>`;
    case "phone": return `<g><rect x="142" y="104" width="20" height="36" rx="4" fill="${INK}"/><rect x="145" y="108" width="14" height="26" rx="2" fill="#9FC3D9"/>
      <path d="M147 124 L151 118 L154 122 L157 116" fill="none" stroke="#FBFCF9" stroke-width="1.6"/><circle class="ch-glow" cx="156" cy="111" r="2.2" fill="#C9473D"/></g>`;
    case "tablet": return `<g class="ch-tilt" style="transform-origin:150px 150px"><rect x="126" y="124" width="46" height="34" rx="4" fill="${INK}"/><rect x="130" y="128" width="38" height="26" rx="2" fill="#FBFCF9"/>
      <path d="M133 150 L133 132 M133 150 L166 150" stroke="#C7CCC3" stroke-width="1.2"/><path class="ch-draw" d="M134 148 L142 142 L149 145 L157 136 L165 131" fill="none" stroke="#3E9A5E" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>`;
    case "opensign": return `<g class="ch-swing" style="transform-origin:150px 150px"><path d="M140 160 L150 150 L160 160" fill="none" stroke="${INK}" stroke-width="2"/>
      <rect x="124" y="160" width="52" height="24" rx="4" fill="${fam}" ${SK}/><text x="150" y="177.5" text-anchor="middle" font-size="13" font-weight="800" fill="#FBFCF9" style="font-family:Archivo,Arial,sans-serif;letter-spacing:.06em">OPEN</text></g>`;
    case "briefcase": return `<g class="ch-swing" style="transform-origin:152px 146px"><path d="M145 156 L145 148 L159 148 L159 156" fill="none" stroke="${INK}" stroke-width="3"/>
      <rect x="130" y="156" width="44" height="30" rx="3" fill="#6B4A32" ${SK}/><path d="M130 167 L174 167" stroke="${INK}" stroke-width="2"/><rect x="148" y="163" width="8" height="7" rx="1" fill="#E7B53E" ${SK2}/><path d="M134 160 L134 182" stroke="#86603F" stroke-width="2"/></g>`;
    case "wheat": return `<g class="ch-sway" style="transform-origin:152px 160px"><g fill="none" stroke="#B8902F" stroke-width="2.6" stroke-linecap="round"><path d="M152 160 L145 94"/><path d="M152 160 L154 88"/><path d="M152 160 L163 96"/></g>
      ${[[145, 94], [154, 88], [163, 96]].map(([x, y]) => `<ellipse cx="${x}" cy="${y - 8}" rx="5.5" ry="12" fill="#E2C47C" ${SK}/><path d="M${x} ${y - 16} L${x} ${y}" stroke="#C9A85E" stroke-width="1.4"/>`).join("")}<path d="M143 146 L161 146" stroke="#B5523A" stroke-width="5" stroke-linecap="round"/></g>`;
    case "microphone": return `<g><rect x="144" y="118" width="9" height="30" rx="4" fill="#3A3F47" ${SK} transform="rotate(-18 148 133)"/><circle cx="144" cy="113" r="9.5" fill="#9AA3AE" ${SK}/><path d="M138 110 L150 116 M138 116 L150 110" stroke="#7B828C" stroke-width="1.4"/>
      <g class="ch-pulse" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"><path d="M128 100 Q122 108 126 118"/><path d="M120 94 Q110 108 118 124"/></g></g>`;
    default: return "";
  }
}

const RAISED = new Set(["placard", "pennant", "rocket", "plane", "coin", "microphone", "wheat", "scales", "phone"]);

function charSvg(code, fam, opts = {}) {
  const L = LOOKS[code];
  if (!L) return "";
  const id = `chc${++CH_UID}`;
  const delay = (code.charCodeAt(0) * 3 + code.charCodeAt(1) * 7 + code.charCodeAt(2) * 5) % 23 / 10;
  const raised = RAISED.has(L.prop);
  const sleeve = ["hivis", "vest", "overall"].includes(L.outfit) ? L.inner : fam;
  const sleeveDark = shade(sleeve, -.15);
  const pants = L.pants || "#2B3445";
  const rightArm = raised ? "M128 134 Q146 140 152 152" : "M128 134 Q144 144 150 150";
  const hx = raised ? 152 : 150, hy = raised ? 152 : 150;
  const title = opts.label ? `<title>${opts.label}</title>` : "";
  return `<svg class="ch" viewBox="0 0 200 220" ${opts.label ? 'role="img"' : 'aria-hidden="true"'} style="--d:${delay}s">${title}
  <ellipse class="ch-shadow" cx="100" cy="211" rx="46" ry="6" fill="${INK}" opacity=".13"/>
  <g class="ch-bob">
    ${hairBack(L.hair, L.hairC)}
    <path d="M83 172 L83 202 Q83 206 89 206 L95 206 Q97 206 97 202 L97 172Z M103 172 L103 202 Q103 206 109 206 L115 206 Q117 206 117 202 L117 172Z" fill="${pants}" ${SK}/>
    <path d="M90 180 L90 200 M110 180 L110 200" stroke="${shade(pants, .18)}" stroke-width="1.6"/>
    <path d="M78 203 Q78 212 92 212 L98 212 L98 203Z M122 203 Q122 212 108 212 L102 212 L102 203Z" fill="#20262F" ${SK2}/>
    <path d="M70 134 Q66 160 62 170" fill="none" stroke="${INK}" stroke-width="16" stroke-linecap="round"/><path d="M70 134 Q66 160 62 170" fill="none" stroke="${sleeveDark}" stroke-width="10" stroke-linecap="round"/>
    ${outfitSvg(L, fam, id)}
    <circle cx="62" cy="173" r="7" fill="${L.skin}" ${SK}/>
    <rect x="92" y="108" width="16" height="16" fill="${shade(L.skin, -.12)}" ${SK}/>
    ${faceSvg(L)}
    ${hairFront(L.hair, L.hairC)}
    ${faceAcc(L.acc === "sleeves" ? "" : L.acc)}
    ${hatSvg(L.hat)}
    <path d="${rightArm}" fill="none" stroke="${INK}" stroke-width="16" stroke-linecap="round"/><path d="${rightArm}" fill="none" stroke="${sleeve}" stroke-width="10" stroke-linecap="round"/>
    ${L.acc === "sleeves" ? `<path d="M64 156 L75 152 M136 138 L142 146" stroke="${shade(sleeve, .45)}" stroke-width="5" stroke-linecap="round"/>` : ""}
    ${propSvg(L.prop, fam)}
    <circle cx="${hx}" cy="${hy}" r="7" fill="${L.skin}" ${SK}/>
  </g>
</svg>`;
}
