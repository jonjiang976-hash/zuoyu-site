// Cloudflare Pages Function — GET /api/inquiries?key=<ADMIN_KEY>
// 查看官网收到的询盘。浏览器打开返回表格页面，?format=json 返回 JSON。
// 需要环境变量：ADMIN_KEY（必填，否则一律 404）、INQUIRIES（KV 绑定）

const esc = (s) =>
  String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function cst(iso) {
  try {
    const d = new Date(iso);
    return new Date(d.getTime() + 8 * 3600 * 1000).toISOString().replace('T', ' ').slice(0, 16);
  } catch (e) {
    return iso || '';
  }
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const key = url.searchParams.get('key') || '';
  const wantJson = url.searchParams.get('format') === 'json';

  const notFound = () =>
    new Response(wantJson ? JSON.stringify({ ok: false, error: 'not_found' }) : 'Not found', {
      status: 404,
      headers: { 'content-type': wantJson ? 'application/json' : 'text/plain; charset=utf-8' },
    });

  if (!env.ADMIN_KEY || !env.INQUIRIES) return notFound();
  if (key !== env.ADMIN_KEY) return notFound();

  let list = [];
  try {
    const res = await env.INQUIRIES.list({ prefix: 'inq:', limit: 200 });
    const keys = res.keys.map((k) => k.name).sort().reverse();
    for (const name of keys) {
      const raw = await env.INQUIRIES.get(name);
      if (raw) {
        try {
          list.push(JSON.parse(raw));
        } catch (e) {}
      }
    }
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: 'kv_error', detail: String(e).slice(0, 200) }), {
      status: 500,
      headers: { 'content-type': 'application/json' },
    });
  }

  if (wantJson) {
    return new Response(JSON.stringify({ ok: true, count: list.length, inquiries: list }), {
      headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
    });
  }

  const rows = list
    .map(
      (r) => `<tr>
  <td class="t">${esc(cst(r.ts))}</td>
  <td><b>${esc(r.name)}</b>${r.company ? '<br><span class="m">' + esc(r.company) + '</span>' : ''}</td>
  <td><a href="mailto:${esc(r.email)}">${esc(r.email)}</a>${r.whatsapp ? '<br><span class="m">WA ' + esc(r.whatsapp) + '</span>' : ''}</td>
  <td>${esc(r.buyerCountry || '-')}<br><span class="m">${esc(r.cfCountry || '')}</span></td>
  <td>${esc(r.category || '-')}<br><span class="m">${esc(r.quantity || '')}</span></td>
  <td class="b">${esc(r.brief).replace(/\n/g, '<br>')}</td>
  <td class="m">${esc(r.page || '-')}<br>${esc(r.ip || '')}</td>
</tr>`
    )
    .join('\n');

  const html = `<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>官网询盘 · Zuoyu</title>
<style>
*{box-sizing:border-box}body{margin:0;font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;color:#1c2b3a;background:#f4f6f8}
header{background:#12283f;color:#fff;padding:18px 24px}header h1{margin:0;font-size:17px;font-weight:600}
header p{margin:6px 0 0;font-size:13px;opacity:.75}
.wrap{padding:20px 24px 60px}
table{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08);border-radius:6px;overflow:hidden}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #e6ecf1;vertical-align:top}
th{background:#eef2f6;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#5a6b7d}
td.t{white-space:nowrap;font-variant-numeric:tabular-nums}
td.b{max-width:420px}
.m{color:#7d8b99;font-size:12px}
.empty{padding:40px;text-align:center;color:#7d8b99;background:#fff;border-radius:6px}
a{color:#1a5fb4}
@media(max-width:820px){table,thead,tbody,tr,td,th{display:block}thead{display:none}tr{border-bottom:1px solid #e6ecf1;padding:10px}td{border:0;padding:6px 4px}td.b{max-width:none}}
</style></head><body>
<header><h1>官网询盘 · zuoyugarment.com</h1><p>共 ${list.length} 条　·　自动刷新：<a href="?key=${esc(key)}" style="color:#9fc3e8">刷新</a>　·　JSON：<a href="?key=${esc(key)}&format=json" style="color:#9fc3e8">下载</a></p></header>
<div class="wrap">
${list.length ? `<table><thead><tr><th>时间 (UTC+8)</th><th>联系人</th><th>联系方式</th><th>国家</th><th>需求</th><th>简述</th><th>来源 / IP</th></tr></thead><tbody>${rows}</tbody></table>` : '<div class="empty">还没有收到询盘。<br>收到后刷新本页即可看到。</div>'}
</div></body></html>`;

  return new Response(html, {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' },
  });
}
