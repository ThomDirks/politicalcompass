/* PCompass characters: original paper-cut figures, one per political type.
   charSvg(code, familyColor) returns an animated inline SVG. */
const INK = "#18212F";
const LOOKS = {
  CPIE: { skin: "#C98E6B", hair: "bun",    hairC: "#3B2A20", prop: "plant" },
  CPIG: { skin: "#8D5A3B", hair: "short",  hairC: "#1E1A18", hat: "hardhat", prop: "blueprint" },
  CPSE: { skin: "#F2C9A5", hair: "curly",  hairC: "#9A4A2A", prop: "placard" },
  CPSG: { skin: "#B7795A", hair: "short",  hairC: "#8E8A86", hat: "flatcap", prop: "megaphone" },
  CTIE: { skin: "#E8B894", hair: "long",   hairC: "#B9B4AC", prop: "lantern" },
  CTIG: { skin: "#D7A07B", hair: "bob",    hairC: "#7A3B22", acc: "apron", prop: "pie" },
  CTSE: { skin: "#9C6644", hair: "short",  hairC: "#2A1E18", hat: "beanie", prop: "basket" },
  CTSG: { skin: "#EAC2A0", hair: "bald",   hairC: "#6B5040", acc: "beard", prop: "pennant" },
  MPIE: { skin: "#7A4A30", hair: "long",   hairC: "#15110F", acc: "scarf", prop: "suitcase" },
  MPIG: { skin: "#F0CFAE", hair: "swoop",  hairC: "#D9B25A", acc: "glasses", prop: "rocket" },
  MPSE: { skin: "#C48A62", hair: "curly",  hairC: "#1C1715", prop: "plane" },
  MPSG: { skin: "#E3B08B", hair: "short",  hairC: "#5A3B26", acc: "shades", prop: "coin" },
  MTIE: { skin: "#B5764F", hair: "short",  hairC: "#9C968E", hat: "ranger", prop: "binoculars" },
  MTIG: { skin: "#EDC6A3", hair: "part",   hairC: "#8F8A84", acc: "tie", prop: "briefcase" },
  MTSE: { skin: "#A86D47", hair: "long",   hairC: "#4A2E1E", hat: "straw", prop: "wheat" },
  MTSG: { skin: "#F1C8A6", hair: "swoop",  hairC: "#3A2C22", acc: "sleeves", prop: "microphone" },
};

function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  const c = [n >> 16, (n >> 8) & 255, n & 255].map(v => Math.round(f < 0 ? v * (1 + f) : v + (255 - v) * f));
  return "#" + c.map(v => v.toString(16).padStart(2, "0")).join("");
}

const SK = `stroke="${INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"`;

function hairSvg(kind, c) {
  switch (kind) {
    case "short": return `<path d="M69 86 Q68 54 100 53 Q132 54 131 86 Q126 70 112 66 Q100 72 86 67 Q74 72 69 86Z" fill="${c}" ${SK}/>`;
    case "part":  return `<path d="M69 86 Q68 54 100 53 Q132 54 131 86 Q128 68 110 64 L106 72 Q90 66 78 70 Q72 76 69 86Z" fill="${c}" ${SK}/>`;
    case "swoop": return `<path d="M68 84 Q66 50 104 50 Q134 52 132 84 Q126 66 108 66 Q94 62 84 72 Q74 74 68 84Z" fill="${c}" ${SK}/><path d="M84 60 Q100 54 118 60" fill="none" stroke="${shade(c, .25)}" stroke-width="3" stroke-linecap="round"/>`;
    case "bun":   return `<circle cx="100" cy="50" r="12" fill="${c}" ${SK}/><path d="M69 88 Q68 56 100 56 Q132 56 131 88 Q124 70 100 68 Q76 70 69 88Z" fill="${c}" ${SK}/>`;
    case "curly": return `<g fill="${c}" ${SK}>${[[74,74],[80,60],[92,52],[106,51],[119,57],[127,70],[71,88],[129,86]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="11"/>`).join("")}</g><path d="M74 78 Q100 62 126 78 L126 70 Q100 56 74 70Z" fill="${c}"/>`;
    case "long":  return `<path d="M66 128 Q62 96 68 74 Q74 52 100 52 Q126 52 132 74 Q138 96 134 128 Q124 124 122 104 Q118 74 100 70 Q82 74 78 104 Q76 124 66 128Z" fill="${c}" ${SK}/>`;
    case "bob":   return `<path d="M66 108 Q62 70 74 60 Q86 50 100 51 Q120 50 130 62 Q138 74 134 108 Q126 106 124 92 Q120 70 100 68 Q80 70 76 92 Q74 106 66 108Z" fill="${c}" ${SK}/>`;
    default: return "";
  }
}

function hatSvg(kind) {
  switch (kind) {
    case "hardhat": return `<path d="M68 76 Q68 46 100 46 Q132 46 132 76Z" fill="#E7B53E" ${SK}/><rect x="62" y="72" width="76" height="8" rx="4" fill="#E7B53E" ${SK}/><path d="M100 47 L100 72" stroke="${INK}" stroke-width="2.4"/>`;
    case "flatcap": return `<path d="M68 72 Q70 50 100 50 Q128 50 132 70 Q150 72 140 78 L68 78Z" fill="#5B5F66" ${SK}/>`;
    case "beanie":  return `<path d="M70 74 Q70 46 100 46 Q130 46 130 74Z" fill="#C9473D" ${SK}/><rect x="68" y="68" width="64" height="12" rx="5" fill="#A73A31" ${SK}/><circle cx="100" cy="42" r="6" fill="#C9473D" ${SK}/>`;
    case "ranger":  return `<ellipse cx="100" cy="68" rx="46" ry="9" fill="#8C7A4E" ${SK}/><path d="M76 66 Q78 42 100 42 Q122 42 124 66Z" fill="#9E8B5C" ${SK}/><path d="M78 60 L122 60" stroke="${INK}" stroke-width="2.4"/>`;
    case "straw":   return `<ellipse cx="100" cy="66" rx="50" ry="10" fill="#E2C47C" ${SK}/><path d="M74 64 Q76 40 100 40 Q124 40 126 64Z" fill="#E9CF8E" ${SK}/><path d="M76 58 L124 58" stroke="#B5523A" stroke-width="5"/>`;
    default: return "";
  }
}

function accSvg(kind, top) {
  switch (kind) {
    case "glasses": return `<g fill="none" stroke="${INK}" stroke-width="2.4"><circle cx="89" cy="88" r="7"/><circle cx="111" cy="88" r="7"/><path d="M96 88 L104 88"/></g>`;
    case "shades":  return `<path d="M78 82 L98 82 L96 94 L82 94Z M102 82 L122 82 L118 94 L104 94Z" fill="${INK}"/><path d="M98 85 L102 85" stroke="${INK}" stroke-width="2.4"/>`;
    case "beard":   return `<path d="M74 92 Q76 122 100 124 Q124 122 126 92 Q118 104 110 104 L90 104 Q82 104 74 92Z" fill="#6B5040" ${SK}/>`;
    case "tie":     return `<path d="M100 126 L94 134 L100 168 L106 134Z" fill="#7C2F35" ${SK}/>`;
    case "apron":   return `<path d="M82 140 L118 140 L122 186 L78 186Z" fill="#FBFCF9" ${SK}/><path d="M86 152 L114 152" stroke="${INK}" stroke-width="2"/>`;
    case "scarf":   return `<path d="M76 124 Q100 136 124 124 L124 134 Q100 146 76 134Z" fill="#D9A441" ${SK}/><path class="ch-flutter" style="transform-origin:114px 134px" d="M114 134 L120 168 L108 166 Z" fill="#D9A441" ${SK}/>`;
    case "sleeves": return `<path d="M64 150 L76 146 M124 146 L136 150" stroke="${shade(top, .35)}" stroke-width="6" stroke-linecap="round"/>`;
    default: return "";
  }
}

function propSvg(kind, fam) {
  switch (kind) {
    case "plant": return `<g><path d="M140 152 L166 152 L162 176 L144 176Z" fill="#B8613E" ${SK}/>
      <g class="ch-sway" style="transform-origin:153px 152px"><path d="M153 152 L153 116" stroke="#2F6B3A" stroke-width="3.4" fill="none"/>
      <path d="M153 130 Q136 124 138 110 Q152 114 153 130Z M153 122 Q170 116 170 102 Q156 104 153 122Z M153 116 Q146 98 156 92 Q162 104 153 116Z" fill="#4E9A5C" ${SK}/></g></g>`;
    case "blueprint": return `<g class="ch-tilt" style="transform-origin:152px 150px"><rect x="138" y="112" width="14" height="58" rx="7" fill="#4C7FB8" ${SK} transform="rotate(-24 145 141)"/><ellipse cx="133" cy="117" rx="7" ry="4" fill="#DCE8F4" ${SK} transform="rotate(-24 133 117)"/></g>`;
    case "placard": return `<g class="ch-wave" style="transform-origin:152px 152px"><path d="M152 152 L152 66" stroke="#8A6A45" stroke-width="5" stroke-linecap="round"/>
      <rect x="122" y="40" width="60" height="36" rx="3" fill="#FBFCF9" ${SK}/><path d="M152 70 Q138 60 142 48 Q150 50 152 58 Q154 50 162 48 Q166 60 152 70Z" fill="#4E9A5C" ${SK}/></g>`;
    case "megaphone": return `<g><path d="M146 140 L168 126 L172 160 L148 152Z" fill="#E7B53E" ${SK}/><rect x="140" y="140" width="10" height="14" rx="3" fill="${INK}"/>
      <g class="ch-pulse" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"><path d="M178 132 Q186 143 178 154"/><path d="M186 124 Q198 143 186 162"/></g></g>`;
    case "lantern": return `<g class="ch-swing" style="transform-origin:152px 140px"><path d="M146 146 Q152 134 158 146" fill="none" stroke="${INK}" stroke-width="3"/>
      <rect x="140" y="146" width="24" height="30" rx="4" fill="#F4E4B0" ${SK}/><circle class="ch-glow" cx="152" cy="161" r="7" fill="#F2B33D"/><rect x="138" y="174" width="28" height="5" rx="2" fill="${INK}"/></g>`;
    case "pie": return `<g><ellipse cx="152" cy="146" rx="22" ry="7" fill="#D8D2C8" ${SK}/><path d="M134 144 Q152 128 170 144Z" fill="#D99B4E" ${SK}/>
      <g class="ch-steam" fill="none" stroke="#9AA3AE" stroke-width="2.4" stroke-linecap="round"><path d="M146 126 Q142 118 146 110 Q150 102 146 94"/><path d="M158 126 Q154 118 158 110 Q162 102 158 94"/></g></g>`;
    case "basket": return `<g class="ch-swing" style="transform-origin:152px 140px"><path d="M138 152 Q152 128 166 152" fill="none" stroke="#8A6A45" stroke-width="3.4"/>
      <circle cx="144" cy="150" r="7" fill="#C9473D" ${SK}/><circle cx="156" cy="148" r="7" fill="#7FAF4A" ${SK}/><circle cx="163" cy="152" r="6" fill="#C9473D" ${SK}/>
      <path d="M134 152 L170 152 L164 176 L140 176Z" fill="#C8A169" ${SK}/><path d="M138 162 L166 162" stroke="${INK}" stroke-width="1.8"/></g>`;
    case "pennant": return `<g><path d="M152 154 L152 52" stroke="#8A6A45" stroke-width="5" stroke-linecap="round"/>
      <g class="ch-flutter" style="transform-origin:152px 66px"><path d="M154 54 L192 66 L154 80Z" fill="${shade(fam, .1)}" ${SK}/><path d="M154 62 L178 66 L154 72" fill="none" stroke="#FBFCF9" stroke-width="2.4"/></g></g>`;
    case "suitcase": return `<g class="ch-swing" style="transform-origin:152px 146px"><path d="M144 154 L144 146 L160 146 L160 154" fill="none" stroke="${INK}" stroke-width="3"/>
      <rect x="132" y="154" width="40" height="30" rx="4" fill="#6E8FA8" ${SK}/><circle cx="142" cy="164" r="4" fill="#E7B53E"/><rect x="152" y="170" width="12" height="7" rx="2" fill="#C9473D"/><circle cx="162" cy="162" r="3" fill="#FBFCF9"/></g>`;
    case "rocket": return `<g class="ch-float"><g transform="rotate(20 160 104)"><path d="M160 74 Q172 90 170 114 L150 114 Q148 90 160 74Z" fill="#FBFCF9" ${SK}/>
      <circle cx="160" cy="96" r="5" fill="#4C7FB8" ${SK}/><path d="M150 106 L142 118 L150 114Z M170 106 L178 118 L170 114Z" fill="#C9473D" ${SK}/>
      <path class="ch-flicker" d="M154 116 Q160 134 166 116Z" fill="#F2B33D" style="transform-origin:160px 116px"/></g></g>`;
    case "plane": return `<g class="ch-fly"><path d="M150 80 L186 66 L162 96 L158 84Z" fill="#FBFCF9" ${SK}/><path d="M158 84 L186 66" stroke="${INK}" stroke-width="2"/></g>`;
    case "coin": return `<g class="ch-toss"><ellipse class="ch-flip" cx="156" cy="104" rx="11" ry="11" fill="#E7B53E" ${SK} style="transform-origin:156px 104px"/></g>`;
    case "binoculars": return `<g><rect x="138" y="136" width="12" height="20" rx="5" fill="#3A3F47" ${SK}/><rect x="152" y="136" width="12" height="20" rx="5" fill="#3A3F47" ${SK}/><rect x="146" y="140" width="10" height="7" fill="#3A3F47"/></g>
      <path class="ch-bird" d="M160 54 Q166 48 172 54 Q178 48 184 54" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"/>`;
    case "briefcase": return `<g class="ch-swing" style="transform-origin:152px 146px"><path d="M145 156 L145 148 L159 148 L159 156" fill="none" stroke="${INK}" stroke-width="3"/>
      <rect x="132" y="156" width="40" height="28" rx="3" fill="#6B4A32" ${SK}/><path d="M132 166 L172 166" stroke="${INK}" stroke-width="2"/><rect x="149" y="163" width="6" height="6" fill="#E7B53E"/></g>`;
    case "wheat": return `<g class="ch-sway" style="transform-origin:152px 160px"><g fill="none" stroke="#B8902F" stroke-width="2.6" stroke-linecap="round"><path d="M152 160 L146 94"/><path d="M152 160 L154 90"/><path d="M152 160 L162 96"/></g>
      ${[[146, 94], [154, 90], [162, 96]].map(([x, y]) => `<ellipse cx="${x}" cy="${y - 8}" rx="5" ry="11" fill="#E2C47C" ${SK}/>`).join("")}<path d="M144 146 L160 146" stroke="#B5523A" stroke-width="5" stroke-linecap="round"/></g>`;
    case "microphone": return `<g><rect x="144" y="118" width="9" height="30" rx="4" fill="#3A3F47" ${SK} transform="rotate(-18 148 133)"/><circle cx="144" cy="114" r="9" fill="#9AA3AE" ${SK}/>
      <g class="ch-pulse" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"><path d="M128 100 Q122 108 126 118"/><path d="M120 94 Q110 108 118 124"/></g></g>`;
    default: return "";
  }
}

const RAISED = new Set(["placard", "pennant", "rocket", "plane", "coin", "microphone", "wheat"]);

function charSvg(code, fam, opts = {}) {
  const L = LOOKS[code];
  if (!L) return "";
  const top = fam;
  const delay = (code.charCodeAt(1) * 7 + code.charCodeAt(3) * 3) % 23 / 10;
  const raised = RAISED.has(L.prop);
  const rightArm = raised ? "M128 134 Q146 140 152 152" : "M128 134 Q144 144 150 150";
  const label = opts.label ? `<title>${opts.label}</title>` : "";
  return `<svg class="ch" viewBox="0 0 200 220" role="${opts.label ? "img" : "presentation"}" ${opts.label ? "" : 'aria-hidden="true"'} style="--d:${delay}s">${label}
  <ellipse class="ch-shadow" cx="100" cy="210" rx="44" ry="6" fill="${INK}" opacity=".12"/>
  <g class="ch-bob">
    <rect x="82" y="172" width="15" height="34" rx="6" fill="#2B3445" ${SK}/><rect x="103" y="172" width="15" height="34" rx="6" fill="#2B3445" ${SK}/>
    <ellipse cx="88" cy="207" rx="11" ry="5" fill="${INK}"/><ellipse cx="112" cy="207" rx="11" ry="5" fill="${INK}"/>
    <path d="M70 134 Q66 160 62 170" fill="none" stroke="${INK}" stroke-width="16" stroke-linecap="round"/><path d="M70 134 Q66 160 62 170" fill="none" stroke="${top}" stroke-width="10" stroke-linecap="round"/>
    <path d="M64 186 Q60 130 100 120 Q140 130 136 186Z" fill="${top}" ${SK}/>
    <path d="M88 122 L100 134 L112 122" fill="${shade(top, .55)}" ${SK}/>
    ${accSvg(L.acc === "apron" || L.acc === "tie" || L.acc === "sleeves" ? L.acc : "", top)}
    <circle cx="62" cy="172" r="7" fill="${L.skin}" ${SK}/>
    <path d="${rightArm}" fill="none" stroke="${INK}" stroke-width="16" stroke-linecap="round"/><path d="${rightArm}" fill="none" stroke="${top}" stroke-width="10" stroke-linecap="round"/>
    ${L.hair === "long" ? hairSvg("long", L.hairC) : ""}
    <rect x="92" y="108" width="16" height="16" fill="${L.skin}" ${SK}/>
    <circle cx="70" cy="90" r="6" fill="${L.skin}" ${SK}/><circle cx="130" cy="90" r="6" fill="${L.skin}" ${SK}/>
    <circle cx="100" cy="86" r="30" fill="${L.skin}" ${SK}/>
    ${L.acc === "scarf" ? accSvg("scarf", top) : ""}
    ${L.hair !== "long" ? hairSvg(L.hair, L.hairC) : `<path d="M72 80 Q76 58 100 56 Q124 58 128 80 Q118 68 100 68 Q82 68 72 80Z" fill="${L.hairC}" ${SK}/>`}
    ${L.acc === "beard" ? accSvg("beard") : ""}
    <g class="ch-eyes"><ellipse cx="89" cy="89" rx="3.4" ry="4.2" fill="${INK}"/><ellipse cx="111" cy="89" rx="3.4" ry="4.2" fill="${INK}"/></g>
    <circle cx="82" cy="99" r="4" fill="#E08A7A" opacity=".45"/><circle cx="118" cy="99" r="4" fill="#E08A7A" opacity=".45"/>
    ${L.acc === "beard" ? `<path d="M93 106 Q100 110 107 106" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"/>` : `<path d="M92 101 Q100 108 108 101" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`}
    ${L.acc === "glasses" || L.acc === "shades" ? accSvg(L.acc) : ""}
    ${hatSvg(L.hat)}
    ${propSvg(L.prop, fam)}
    <circle cx="${raised ? 152 : 150}" cy="${raised ? 152 : 150}" r="7" fill="${L.skin}" ${SK}/>
  </g>
</svg>`;
}
