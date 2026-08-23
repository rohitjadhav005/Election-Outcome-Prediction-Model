/**
 * Grainient — Vanilla JS/WebGL2 port of the React Bits Grainient component.
 * Ported from the OGL-based React component to raw WebGL2 with no dependencies.
 *
 * Usage:
 *   const stop = mountGrainient(document.getElementById('my-canvas-host'), {
 *     color1: '#FF9933', color2: '#1d4ed8', color3: '#0f172a', ...
 *   });
 *   // call stop() to tear down
 */

const VERTEX_SRC = `#version 300 es
in vec2 position;
void main() {
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const FRAGMENT_SRC = `#version 300 es
precision highp float;
uniform vec2 iResolution;
uniform float iTime;
uniform float uTimeSpeed;
uniform float uColorBalance;
uniform float uWarpStrength;
uniform float uWarpFrequency;
uniform float uWarpSpeed;
uniform float uWarpAmplitude;
uniform float uBlendAngle;
uniform float uBlendSoftness;
uniform float uRotationAmount;
uniform float uNoiseScale;
uniform float uGrainAmount;
uniform float uGrainScale;
uniform float uGrainAnimated;
uniform float uContrast;
uniform float uGamma;
uniform float uSaturation;
uniform vec2 uCenterOffset;
uniform float uZoom;
uniform vec3 uColor1;
uniform vec3 uColor2;
uniform vec3 uColor3;
out vec4 fragColor;
#define S(a,b,t) smoothstep(a,b,t)
mat2 Rot(float a){float s=sin(a),c=cos(a);return mat2(c,-s,s,c);}
vec2 hash(vec2 p){p=vec2(dot(p,vec2(2127.1,81.17)),dot(p,vec2(1269.5,283.37)));return fract(sin(p)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p),u=f*f*(3.0-2.0*f);float n=mix(mix(dot(-1.0+2.0*hash(i+vec2(0.0,0.0)),f-vec2(0.0,0.0)),dot(-1.0+2.0*hash(i+vec2(1.0,0.0)),f-vec2(1.0,0.0)),u.x),mix(dot(-1.0+2.0*hash(i+vec2(0.0,1.0)),f-vec2(0.0,1.0)),dot(-1.0+2.0*hash(i+vec2(1.0,1.0)),f-vec2(1.0,1.0)),u.x),u.y);return 0.5+0.5*n;}
void mainImage(out vec4 o, vec2 C){
  float t=iTime*uTimeSpeed;
  vec2 uv=C/iResolution.xy;
  float ratio=iResolution.x/iResolution.y;
  vec2 tuv=uv-0.5+uCenterOffset;
  tuv/=max(uZoom,0.001);
  float degree=noise(vec2(t*0.1,tuv.x*tuv.y)*uNoiseScale);
  tuv.y*=1.0/ratio;
  tuv*=Rot(radians((degree-0.5)*uRotationAmount+180.0));
  tuv.y*=ratio;
  float frequency=uWarpFrequency;
  float ws=max(uWarpStrength,0.001);
  float amplitude=uWarpAmplitude/ws;
  float warpTime=t*uWarpSpeed;
  tuv.x+=sin(tuv.y*frequency+warpTime)/amplitude;
  tuv.y+=sin(tuv.x*(frequency*1.5)+warpTime)/(amplitude*0.5);
  vec3 colLav=uColor1;
  vec3 colOrg=uColor2;
  vec3 colDark=uColor3;
  float b=uColorBalance;
  float s=max(uBlendSoftness,0.0);
  mat2 blendRot=Rot(radians(uBlendAngle));
  float blendX=(tuv*blendRot).x;
  float edge0=-0.3-b-s;
  float edge1=0.2-b+s;
  float v0=0.5-b+s;
  float v1=-0.3-b-s;
  vec3 layer1=mix(colDark,colOrg,S(edge0,edge1,blendX));
  vec3 layer2=mix(colOrg,colLav,S(edge0,edge1,blendX));
  vec3 col=mix(layer1,layer2,S(v0,v1,tuv.y));
  vec2 grainUv=uv*max(uGrainScale,0.001);
  if(uGrainAnimated>0.5){grainUv+=vec2(iTime*0.05);}
  float grain=fract(sin(dot(grainUv,vec2(12.9898,78.233)))*43758.5453);
  col+=(grain-0.5)*uGrainAmount;
  col=(col-0.5)*uContrast+0.5;
  float luma=dot(col,vec3(0.2126,0.7152,0.0722));
  col=mix(vec3(luma),col,uSaturation);
  col=pow(max(col,0.0),vec3(1.0/max(uGamma,0.001)));
  col=clamp(col,0.0,1.0);
  o=vec4(col,1.0);
}
void main(){
  vec4 o=vec4(0.0);
  mainImage(o,gl_FragCoord.xy);
  fragColor=o;
}
`;

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [1, 1, 1];
  return [
    parseInt(result[1], 16) / 255,
    parseInt(result[2], 16) / 255,
    parseInt(result[3], 16) / 255
  ];
}

function compileShader(gl, type, src) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, src);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error('[Grainient] Shader compile error:', gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

function createProgram(gl, vertSrc, fragSrc) {
  const vert = compileShader(gl, gl.VERTEX_SHADER, vertSrc);
  const frag = compileShader(gl, gl.FRAGMENT_SHADER, fragSrc);
  if (!vert || !frag) return null;
  const program = gl.createProgram();
  gl.attachShader(program, vert);
  gl.attachShader(program, frag);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error('[Grainient] Program link error:', gl.getProgramInfoLog(program));
    return null;
  }
  gl.deleteShader(vert);
  gl.deleteShader(frag);
  return program;
}

/**
 * Mount an animated Grainient canvas inside `container`.
 * @param {HTMLElement} container
 * @param {Object} opts
 * @returns {Function} stop — call to tear down
 */
function mountGrainient(container, opts = {}) {
  const options = Object.assign({
    color1:          '#FF9933',
    color2:          '#1d4ed8',
    color3:          '#0a0f1e',
    timeSpeed:        0.18,
    colorBalance:     0.05,
    warpStrength:     1.0,
    warpFrequency:    4.5,
    warpSpeed:        1.5,
    warpAmplitude:    60.0,
    blendAngle:       15.0,
    blendSoftness:    0.08,
    rotationAmount:   420.0,
    noiseScale:       2.0,
    grainAmount:      0.055,
    grainScale:       2.5,
    grainAnimated:    false,
    contrast:         1.35,
    gamma:            1.05,
    saturation:       1.15,
    centerX:          0.0,
    centerY:          0.05,
    zoom:             0.88
  }, opts);

  // Create canvas — promoted to its own GPU compositor layer
  const canvas = document.createElement('canvas');
  canvas.style.cssText = [
    'position:absolute',
    'top:0',
    'left:0',
    'width:100%',
    'height:100%',
    'display:block',
    'will-change:transform',          // own compositor layer
    'transform:translateZ(0)',         // force GPU rasterisation
    '-webkit-transform:translateZ(0)',
    'backface-visibility:hidden',
    '-webkit-backface-visibility:hidden',
  ].join(';');
  container.appendChild(canvas);

  const gl = canvas.getContext('webgl2', {
    alpha: false,
    antialias: false,
    powerPreference: 'high-performance',  // prefer discrete GPU
    preserveDrawingBuffer: false,
    desynchronized: true,                 // reduces latency on supported browsers
  });
  if (!gl) {
    console.warn('[Grainient] WebGL2 not supported — falling back gracefully.');
    container.removeChild(canvas);
    return () => {};
  }

  const program = createProgram(gl, VERTEX_SRC, FRAGMENT_SRC);
  if (!program) { container.removeChild(canvas); return () => {}; }

  // Full-screen triangle (covers NDC [-1,1] with just 3 vertices)
  const vao = gl.createVertexArray();
  gl.bindVertexArray(vao);
  const vbo = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
  const posLoc = gl.getAttribLocation(program, 'position');
  gl.enableVertexAttribArray(posLoc);
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
  gl.bindVertexArray(null);

  // Cache uniform locations
  const uloc = {};
  const uniformNames = [
    'iTime','iResolution','uTimeSpeed','uColorBalance','uWarpStrength','uWarpFrequency',
    'uWarpSpeed','uWarpAmplitude','uBlendAngle','uBlendSoftness','uRotationAmount',
    'uNoiseScale','uGrainAmount','uGrainScale','uGrainAnimated','uContrast','uGamma',
    'uSaturation','uCenterOffset','uZoom','uColor1','uColor2','uColor3'
  ];
  uniformNames.forEach(n => { uloc[n] = gl.getUniformLocation(program, n); });

  gl.useProgram(program);

  // Apply all options to uniforms
  function applyUniforms() {
    const o = options;
    gl.uniform1f(uloc.uTimeSpeed,      o.timeSpeed);
    gl.uniform1f(uloc.uColorBalance,   o.colorBalance);
    gl.uniform1f(uloc.uWarpStrength,   o.warpStrength);
    gl.uniform1f(uloc.uWarpFrequency,  o.warpFrequency);
    gl.uniform1f(uloc.uWarpSpeed,      o.warpSpeed);
    gl.uniform1f(uloc.uWarpAmplitude,  o.warpAmplitude);
    gl.uniform1f(uloc.uBlendAngle,     o.blendAngle);
    gl.uniform1f(uloc.uBlendSoftness,  o.blendSoftness);
    gl.uniform1f(uloc.uRotationAmount, o.rotationAmount);
    gl.uniform1f(uloc.uNoiseScale,     o.noiseScale);
    gl.uniform1f(uloc.uGrainAmount,    o.grainAmount);
    gl.uniform1f(uloc.uGrainScale,     o.grainScale);
    gl.uniform1f(uloc.uGrainAnimated,  o.grainAnimated ? 1.0 : 0.0);
    gl.uniform1f(uloc.uContrast,       o.contrast);
    gl.uniform1f(uloc.uGamma,          o.gamma);
    gl.uniform1f(uloc.uSaturation,     o.saturation);
    gl.uniform2f(uloc.uCenterOffset,   o.centerX, o.centerY);
    gl.uniform1f(uloc.uZoom,           o.zoom);
    gl.uniform3fv(uloc.uColor1, hexToRgb(o.color1));
    gl.uniform3fv(uloc.uColor2, hexToRgb(o.color2));
    gl.uniform3fv(uloc.uColor3, hexToRgb(o.color3));
  }
  applyUniforms();

  // Resize — debounced so rapid layout shifts don't thrash the GL context
  let resizeTimer = 0;
  function resize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      // DPR capped at 1.0 for ambient gradient — saves 75% GPU fill rate on Retina displays
      const dpr = 1.0;
      const rect = container.getBoundingClientRect();
      const w = Math.max(1, Math.floor(rect.width  * dpr));
      const h = Math.max(1, Math.floor(rect.height * dpr));
      if (canvas.width === w && canvas.height === h) return; // skip if unchanged
      canvas.width  = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
      gl.uniform2f(uloc.iResolution, w, h);
    }, 100);
  }

  const ro = new ResizeObserver(resize);
  ro.observe(container);
  resize();

  // Render loop — gl.useProgram is set ONCE outside the loop
  gl.useProgram(program);

  let raf = 0;
  let isVisible = true;
  let isPageVisible = !document.hidden;
  let isScrolling = false;
  let scrollTimeout = 0;
  let lastFrameTime = 0;
  const t0 = performance.now();

  // Pause WebGL rendering during active scroll to give 100% GPU to smooth scrolling
  function onScroll() {
    isScrolling = true;
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      isScrolling = false;
    }, 120);
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  function loop(t) {
    raf = requestAnimationFrame(loop);
    if (isScrolling) return;               // Free 100% GPU during scrolling
    if (t - lastFrameTime < 33) return;    // Cap at ~30 FPS (ambient gradient looks identical)
    lastFrameTime = t;

    gl.uniform1f(uloc.iTime, (t - t0) * 0.001);
    gl.bindVertexArray(vao);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.bindVertexArray(null);
  }

  function tryStart() {
    if (isVisible && isPageVisible && raf === 0) raf = requestAnimationFrame(loop);
  }
  function tryStop() {
    if (raf !== 0) { cancelAnimationFrame(raf); raf = 0; }
  }

  const io = new IntersectionObserver(([entry]) => {
    isVisible = entry.isIntersecting;
    isVisible ? tryStart() : tryStop();
  }, { threshold: 0 });
  io.observe(container);

  function onVisibility() {
    isPageVisible = !document.hidden;
    isPageVisible ? tryStart() : tryStop();
  }
  document.addEventListener('visibilitychange', onVisibility);

  tryStart();

  // Return teardown
  return function stop() {
    tryStop();
    ro.disconnect();
    io.disconnect();
    document.removeEventListener('visibilitychange', onVisibility);
    window.removeEventListener('scroll', onScroll);
    gl.deleteProgram(program);
    gl.deleteBuffer(vbo);
    gl.deleteVertexArray(vao);
    try { container.removeChild(canvas); } catch { /* already removed */ }
  };
}

window.mountGrainient = mountGrainient;
