import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';

export function parseArgs(argv = process.argv.slice(2)) {
  const args = new Map();
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token.startsWith('--')) {
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args.set(token, next);
        i += 1;
      } else {
        args.set(token, 'true');
      }
    }
  }
  return args;
}

function resolveMagick() {
  const candidates = [process.env.MAGICK, '/Users/a136/.homebrew/bin/magick', 'magick'].filter(
    Boolean,
  );
  for (const candidate of candidates) {
    try {
      execFileSync(candidate, ['-version'], { stdio: 'ignore' });
      return candidate;
    } catch {
      // continue
    }
  }
  throw new Error('ImageMagick `magick` command not found. Set MAGICK env if needed.');
}

export function createRuntime(args = new Map()) {
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const repoRoot = path.resolve(scriptDir, '..', '..');
  const baseDir =
    fs.existsSync(path.resolve('package.json')) && fs.existsSync(path.resolve('public'))
      ? path.resolve('.')
      : repoRoot;
  const outDir = path.resolve(
    args.get('--out-dir') || path.join(baseDir, 'public/thesis-diagrams'),
  );
  const srcDir = path.resolve(
    args.get('--src-dir') || path.join(baseDir, 'public/thesis-diagrams-src'),
  );
  fs.mkdirSync(outDir, { recursive: true });
  fs.mkdirSync(srcDir, { recursive: true });

  const MAGICK = resolveMagick();
  const FONT = 'SimSun, Songti SC, serif';
  const BOLD = 'SimHei, PingFang SC, sans-serif';
  const STROKE = '#202020';
  const RED = '#cf1f1f';
  const GRID = 10;

  const esc = (value) =>
    String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');

  const snap = (n, grid = GRID) => Math.round(n / grid) * grid;
  const snapText = (n) => Math.round(n);
  const pt = (x, y) => `${snap(x)} ${snap(y)}`;

  function tokenize(line) {
    return String(line).match(/[A-Za-z0-9_.:/-]+|\s+|[\u4e00-\u9fff]|./g) || [];
  }

  function charWeight(ch) {
    if (ch === ' ') return 0.34;
    if (/[_./:-]/.test(ch)) return 0.42;
    if (/[A-Z0-9]/.test(ch)) return 0.62;
    if (/[a-z]/.test(ch)) return 0.54;
    return /[\u4e00-\u9fff]/.test(ch) ? 1 : 0.58;
  }

  function estimateWidth(value, size) {
    return Array.from(String(value)).reduce((sum, ch) => sum + charWeight(ch) * size, 0);
  }

  function wrapLine(line, maxWidth, size) {
    const tokens = tokenize(line);
    const lines = [];
    let current = '';
    tokens.forEach((token) => {
      if (!current.trim()) {
        current += token;
        return;
      }
      const next = current + token;
      if (estimateWidth(next, size) <= maxWidth) {
        current = next;
        return;
      }
      if (token.trim() && estimateWidth(token, size) > maxWidth) {
        Array.from(token).forEach((ch) => {
          const attempt = current + ch;
          if (current && estimateWidth(attempt, size) > maxWidth) {
            lines.push(current.trimEnd());
            current = ch;
          } else {
            current = attempt;
          }
        });
        return;
      }
      lines.push(current.trimEnd());
      current = token.trimStart();
    });
    if (current.trim()) lines.push(current.trimEnd());
    return lines.length ? lines : [''];
  }

  function fitText(label, maxWidth, maxHeight, opts = {}) {
    const {
      maxSize = 26,
      minSize = 12,
      lineHeightFactor = 1.22,
      preserveLines = false,
      maxLines = Infinity,
    } = opts;
    const sourceLines = Array.isArray(label) ? label.map(String) : [String(label)];
    for (let size = maxSize; size >= minSize; size -= 1) {
      const lineHeight = size * lineHeightFactor;
      let lines = [];
      sourceLines.forEach((line) => {
        lines = lines.concat(preserveLines ? [line] : wrapLine(line, maxWidth, size));
      });
      const widest = Math.max(...lines.map((line) => estimateWidth(line, size)), 0);
      const totalHeight = lines.length * lineHeight;
      if (widest <= maxWidth && totalHeight <= maxHeight && lines.length <= maxLines) {
        return { lines, size, lineHeight };
      }
    }
    const lineHeight = minSize * lineHeightFactor;
    const forced = sourceLines
      .flatMap((line) => (preserveLines ? [line] : wrapLine(line, maxWidth, minSize)))
      .slice(0, maxLines);
    return { lines: forced, size: minSize, lineHeight };
  }

  function svgDoc(width, height, body) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" shape-rendering="geometricPrecision" text-rendering="geometricPrecision">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="${STROKE}" />
    </marker>
    <marker id="dashArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#555" />
    </marker>
  </defs>
  <rect x="0" y="0" width="${width}" height="${height}" fill="#ffffff"/>
  ${body}
</svg>`;
  }

  function text(x, y, value, opts = {}) {
    const {
      size = 24,
      fill = STROKE,
      anchor = 'middle',
      weight = '400',
      family = FONT,
      rotate = 0,
    } = opts;
    const tx = snapText(x);
    const ty = snapText(y);
    const transform = rotate ? ` transform="rotate(${rotate} ${tx} ${ty})"` : '';
    return `<text x="${tx}" y="${ty}" font-family="${family}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}" dominant-baseline="middle"${transform}>${esc(value)}</text>`;
  }

  function multiline(x, y, lines, opts = {}) {
    const {
      size = 24,
      fill = STROKE,
      anchor = 'middle',
      family = FONT,
      weight = '400',
      lineHeight = size * 1.2,
    } = opts;
    const startY = y - ((lines.length - 1) * lineHeight) / 2;
    return lines
      .map((line, idx) =>
        text(x, startY + idx * lineHeight, line, { size, fill, anchor, family, weight }),
      )
      .join('\n');
  }

  function fittedText(cx, cy, width, height, label, opts = {}) {
    const fit = fitText(label, width, height, opts);
    return multiline(cx, cy, fit.lines, {
      size: fit.size,
      lineHeight: fit.lineHeight,
      family: opts.family || FONT,
      weight: opts.weight || '400',
      fill: opts.fill || STROKE,
      anchor: opts.anchor || 'middle',
    });
  }

  function pathLine(points, opts = {}) {
    const { width = 3, arrow = false, dashed = false, color = STROKE } = opts;
    const marker = arrow ? ` marker-end="url(#${dashed ? 'dashArrow' : 'arrow'})"` : '';
    const dash = dashed ? ' stroke-dasharray="8 6"' : '';
    const d = points
      .map((point, idx) => `${idx === 0 ? 'M' : 'L'} ${pt(point[0], point[1])}`)
      .join(' ');
    return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="square" stroke-linejoin="miter"${dash}${marker}/>`;
  }

  const hLine = (x1, x2, y, opts = {}) =>
    pathLine(
      [
        [x1, y],
        [x2, y],
      ],
      opts,
    );
  const vLine = (x, y1, y2, opts = {}) =>
    pathLine(
      [
        [x, y1],
        [x, y2],
      ],
      opts,
    );

  function rect(x, y, width, height, label, opts = {}) {
    const {
      rounded = false,
      fill = '#fff',
      size = 24,
      minSize = 12,
      weight = '400',
      family = FONT,
      preserveLines = false,
      maxLines = Infinity,
      strokeWidth = 3,
    } = opts;
    const rx = rounded ? 16 : 0;
    const sx = snap(x);
    const sy = snap(y);
    const sw = snap(width);
    const sh = snap(height);
    return `<rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" rx="${rx}" ry="${rx}" fill="${fill}" stroke="${STROKE}" stroke-width="${strokeWidth}"/>\n${fittedText(sx + sw / 2, sy + sh / 2, sw - 18, sh - 14, label, { maxSize: size, minSize, weight, family, preserveLines, maxLines })}`;
  }

  function pill(x, y, width, height, label, opts = {}) {
    return rect(x, y, width, height, label, { rounded: true, strokeWidth: 2.6, ...opts });
  }

  function tallRect(x, y, width, height, label, opts = {}) {
    const lines = Array.isArray(label) ? label.map(String) : Array.from(String(label));
    const sx = snap(x);
    const sy = snap(y);
    const sw = snap(width);
    const sh = snap(height);
    const size =
      opts.size ||
      Math.min(19, Math.max(14, Math.floor((sh - 24) / Math.max(lines.length, 1) / 1.05)));
    return `<rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>\n${multiline(sx + sw / 2, sy + sh / 2, lines, { size, lineHeight: size * 1.08, family: opts.family || BOLD, weight: opts.weight || '400' })}`;
  }

  function ellipse(cx, cy, rx, ry, label, opts = {}) {
    const scx = snap(cx);
    const scy = snap(cy);
    const srx = snap(rx);
    const sry = snap(ry);
    return `<ellipse cx="${scx}" cy="${scy}" rx="${srx}" ry="${sry}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>\n${fittedText(scx, scy, srx * 1.45, sry * 1.2, label, { maxSize: opts.size || 24, minSize: opts.minSize || 13, maxLines: opts.maxLines || 2 })}`;
  }

  function diamond(cx, cy, width, height, label, opts = {}) {
    const scx = snap(cx);
    const scy = snap(cy);
    const d = `M ${scx} ${snap(cy - height / 2)} L ${snap(cx + width / 2)} ${scy} L ${scx} ${snap(cy + height / 2)} L ${snap(cx - width / 2)} ${scy} Z`;
    return `<path d="${d}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>\n${fittedText(scx, scy, width * 0.62, height * 0.46, label, { maxSize: opts.size || 22, minSize: opts.minSize || 13, maxLines: opts.maxLines || 2 })}`;
  }

  function cylinder(x, y, width, height, label, opts = {}) {
    const sx = snap(x);
    const sy = snap(y);
    const sw = snap(width);
    const sh = snap(height);
    const rx = width / 2;
    const ry = 18;
    const body = `<ellipse cx="${snap(x + rx)}" cy="${snap(y + ry)}" rx="${snap(rx)}" ry="${ry}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>\n<path d="M ${sx} ${snap(y + ry)} L ${sx} ${snap(y + height - ry)} A ${snap(rx)} ${ry} 0 0 0 ${snap(x + width)} ${snap(y + height - ry)} L ${snap(x + width)} ${snap(y + ry)}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`;
    return `${body}\n${fittedText(sx + sw / 2, sy + sh / 2, sw - 16, sh - 24, label, { maxSize: opts.size || 22, minSize: 12, maxLines: 2 })}`;
  }

  function actor(x, y, label) {
    return `<circle cx="${snap(x)}" cy="${snap(y)}" r="18" fill="#fff" stroke="${STROKE}" stroke-width="3"/>\n<line x1="${snap(x)}" y1="${snap(y + 18)}" x2="${snap(x)}" y2="${snap(y + 92)}" stroke="${STROKE}" stroke-width="3"/>\n<line x1="${snap(x - 36)}" y1="${snap(y + 44)}" x2="${snap(x + 36)}" y2="${snap(y + 44)}" stroke="${STROKE}" stroke-width="3"/>\n<line x1="${snap(x)}" y1="${snap(y + 92)}" x2="${snap(x - 34)}" y2="${snap(y + 142)}" stroke="${STROKE}" stroke-width="3"/>\n<line x1="${snap(x)}" y1="${snap(y + 92)}" x2="${snap(x + 34)}" y2="${snap(y + 142)}" stroke="${STROKE}" stroke-width="3"/>\n${text(x, y + 186, label, { size: 28 })}`;
  }

  function brace(x, y1, y2, label, opts = {}) {
    const mid = (y1 + y2) / 2;
    const d = `M ${snap(x + 40)} ${snap(y1)} C ${snap(x + 18)} ${snap(y1)}, ${snap(x + 18)} ${snap(y1)}, ${snap(x + 18)} ${snap(y1 + 30)} L ${snap(x + 18)} ${snap(mid - 30)} C ${snap(x + 18)} ${snap(mid - 8)}, ${snap(x)} ${snap(mid - 8)}, ${snap(x)} ${snap(mid)} C ${snap(x)} ${snap(mid + 8)}, ${snap(x + 18)} ${snap(mid + 8)}, ${snap(x + 18)} ${snap(mid + 30)} L ${snap(x + 18)} ${snap(y2 - 30)} C ${snap(x + 18)} ${snap(y2)}, ${snap(x + 18)} ${snap(y2)}, ${snap(x + 40)} ${snap(y2)}`;
    const size = opts.size || 24;
    return `<path d="${d}" fill="none" stroke="${STROKE}" stroke-width="3"/>\n${multiline(x - 18, mid, Array.from(label), { size, lineHeight: opts.lineHeight || size * 1.16, family: opts.family || FONT, weight: opts.weight || '400' })}`;
  }

  const activation = (x, y, height) =>
    `<rect x="${snap(x - 12)}" y="${snap(y)}" width="24" height="${snap(height)}" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`;
  const card = (x, y, label) => text(x, y, label, { size: 22 });
  const title = (label) =>
    text(34, 60, label, { size: 58, fill: RED, anchor: 'start', family: BOLD, weight: '700' });

  // ========== Layout helpers: collision detection & auto-placement ==========

  /**
   * Create a layout context for automatic overlap removal.
   * Usage:
   *   const layout = createLayout(canvasWidth, canvasHeight);
   *   layout.registerBox(entityNode);          // register entity as obstacle
   *   layout.autoAttrs(entityNode, ['id','name','age'], { ... }); // place attributes
   *   // attributes are pushed apart automatically via AABB collision detection
   */
  function createLayout(canvasW, canvasH) {
    const boxes = []; // all registered AABB boxes

    const aabbOverlaps = (a, b) =>
      a.x < b.x + b.w && a.x + a.w > b.x &&
      a.y < b.y + b.h && a.y + a.h > b.y;

    const pushApart = (movable, fixed) => {
      const ox = Math.min(movable.x + movable.w - fixed.x, fixed.x + fixed.w - movable.x);
      const oy = Math.min(movable.y + movable.h - fixed.y, fixed.y + fixed.h - movable.y);
      if (ox < oy) {
        movable.x += (movable.x + movable.w / 2 < fixed.x + fixed.w / 2) ? -(ox / 2 + 4) : (ox / 2 + 4);
      } else {
        movable.y += (movable.y + movable.h / 2 < fixed.y + fixed.h / 2) ? -(oy / 2 + 4) : (oy / 2 + 4);
      }
    };

    const clamp = (box) => {
      box.x = Math.max(4, Math.min(canvasW - box.w - 4, box.x));
      box.y = Math.max(4, Math.min(canvasH - box.h - 4, box.y));
      if (box.cx !== undefined) { box.cx = box.x + box.w / 2; box.cy = box.y + box.h / 2; }
    };

    return {
      boxes,

      /** Register an entity rectangle as a collision obstacle */
      registerBox(node, padding = 6) {
        boxes.push({ x: node.x - padding, y: node.y - padding, w: node.w + padding * 2, h: node.h + padding * 2 });
      },

      /**
       * Place attribute ellipses around an entity with automatic overlap removal.
       * @param {Object} body - SVG body array to push elements into
       * @param {Object} entityNode - the entity {x,y,w,h,cx,cy}
       * @param {string[]} labels - attribute labels
       * @param {Object} opts - { rx, ry, radius, startAngle, span, maxIter, fontSize }
       * @returns {Object[]} placed attribute boxes
       */
      autoAttrs(body, entityNode, labels, opts = {}) {
        const rx = opts.rx || 72;
        const ry = opts.ry || 26;
        const radius = opts.radius || 140;
        const startAngle = opts.startAngle ?? -Math.PI / 2;
        const span = opts.span ?? Math.PI * 1.2;
        const maxIter = opts.maxIter || 12;
        const fontSize = opts.fontSize || 15;
        const n = labels.length;

        // Step 1: radial initial placement
        const attrBoxes = labels.map((label, i) => {
          const angle = startAngle + (span / Math.max(n - 1, 1)) * i;
          let cx = entityNode.cx + radius * Math.cos(angle);
          let cy = entityNode.cy + radius * Math.sin(angle);
          cx = Math.max(rx + 8, Math.min(canvasW - rx - 8, cx));
          cy = Math.max(ry + 8, Math.min(canvasH - ry - 8, cy));
          return { cx, cy, x: cx - rx, y: cy - ry, w: rx * 2, h: ry * 2, label };
        });

        // Step 2: iterative AABB push-apart
        for (let iter = 0; iter < maxIter; iter++) {
          let moved = false;
          for (let i = 0; i < attrBoxes.length; i++) {
            for (let j = i + 1; j < attrBoxes.length; j++) {
              if (aabbOverlaps(attrBoxes[i], attrBoxes[j])) {
                pushApart(attrBoxes[i], attrBoxes[j]);
                pushApart(attrBoxes[j], attrBoxes[i]);
                moved = true;
              }
            }
            for (const box of boxes) {
              if (aabbOverlaps(attrBoxes[i], box)) {
                pushApart(attrBoxes[i], box);
                moved = true;
              }
            }
            clamp(attrBoxes[i]);
            attrBoxes[i].cx = attrBoxes[i].x + rx;
            attrBoxes[i].cy = attrBoxes[i].y + ry;
          }
          if (!moved) break;
        }

        // Step 3: render
        const rectAnchorLocal = (node, tx, ty) => {
          const dx = tx - node.cx, dy = ty - node.cy;
          if (Math.abs(dx) * (node.h / 2) > Math.abs(dy) * (node.w / 2))
            return [dx >= 0 ? node.x + node.w : node.x, node.cy];
          return [node.cx, dy >= 0 ? node.y + node.h : node.y];
        };
        const ovalAnchorLocal = (cx, cy, orx, ory, tx, ty) => {
          const dx = tx - cx, dy = ty - cy;
          const s = Math.sqrt((dx * dx) / (orx * orx) + (dy * dy) / (ory * ory)) || 1;
          return [cx + dx / s, cy + dy / s];
        };

        attrBoxes.forEach((ab) => {
          const [x1, y1] = rectAnchorLocal(entityNode, ab.cx, ab.cy);
          const [x2, y2] = ovalAnchorLocal(ab.cx, ab.cy, rx, ry, entityNode.cx, entityNode.cy);
          body.push(pathLine([[x1, y1], [x2, y2]], { width: 2 }));
          body.push(ellipse(ab.cx, ab.cy, rx, ry, ab.label, { size: fontSize, minSize: 11, maxLines: 1 }));
          boxes.push({ x: ab.x, y: ab.y, w: ab.w, h: ab.h });
        });

        return attrBoxes;
      },
    };
  }

  function writeDiagram(name, width, height, body) {
    const svg = svgDoc(width, height, body.join('\n'));
    const svgPath = path.join(srcDir, `${name}.svg`);
    const pngPath = path.join(outDir, `${name}.png`);
    fs.writeFileSync(svgPath, svg, 'utf8');
    execFileSync(MAGICK, [svgPath, pngPath]);
    console.log(`generated ${name}.png`);
  }

  return {
    fs,
    path,
    execFileSync,
    outDir,
    srcDir,
    MAGICK,
    FONT,
    BOLD,
    STROKE,
    RED,
    GRID,
    esc,
    snap,
    pt,
    tokenize,
    charWeight,
    estimateWidth,
    wrapLine,
    fitText,
    svgDoc,
    text,
    multiline,
    fittedText,
    pathLine,
    hLine,
    vLine,
    rect,
    pill,
    tallRect,
    ellipse,
    diamond,
    cylinder,
    actor,
    brace,
    activation,
    card,
    title,
    createLayout,
    writeDiagram,
  };
}
