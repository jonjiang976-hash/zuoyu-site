// Cloudflare Pages Function — POST /api/inquiry
// 接收官网询盘：校验 → 存 KV → 推送通知（企业微信/钉钉/飞书/Slack/Discord/邮件）
// 环境变量（可选，按需配置）：
//   INQUIRIES    : KV namespace 绑定（强烈建议，用于存档+后台查看）
//   ADMIN_KEY    : 查看询盘的密钥（配合 /api/inquiries?key=xxx）
//   WEBHOOK_URL  : 群机器人 webhook（企业微信/钉钉/飞书/Slack/Discord 自动识别）
//   RESEND_API_KEY / NOTIFY_EMAIL / FROM_EMAIL : 邮件通知（可选）

const JSON_HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store',
};

const ok = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: JSON_HEADERS });
const fail = (error, status = 400, extra = {}) =>
  new Response(JSON.stringify({ ok: false, error, ...extra }), { status, headers: JSON_HEADERS });

const clean = (v, max) => String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max);
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/;

function fmtTime(iso) {
  // 转成北京时间，方便直接看
  const d = new Date(iso);
  return new Date(d.getTime() + 8 * 3600 * 1000).toISOString().replace('T', ' ').slice(0, 16) + ' (UTC+8)';
}

function buildText(rec) {
  const lines = [
    '📩 官网新询盘',
    `时间：${fmtTime(rec.ts)}`,
    `姓名：${rec.name}`,
    rec.company ? `公司：${rec.company}` : null,
    `邮箱：${rec.email}`,
    rec.whatsapp ? `WhatsApp：${rec.whatsapp}` : null,
    rec.buyerCountry ? `国家/地区：${rec.buyerCountry}` : null,
    rec.category ? `品类：${rec.category}` : null,
    rec.quantity ? `目标数量：${rec.quantity}` : null,
    '',
    '需求简述：',
    rec.brief,
    '',
    `来源页：${rec.page || '-'}`,
    `IP 国家：${rec.cfCountry || '-'}`,
    `询盘编号：${rec.id}`,
  ].filter((x) => x !== null);
  return lines.join('\n');
}

async function notify(env, rec) {
  const text = buildText(rec);
  const out = [];

  // 1) 群机器人
  if (env.WEBHOOK_URL) {
    const u = env.WEBHOOK_URL;
    let payload;
    try {
      if (u.includes('qyapi.weixin.qq.com')) {
        payload = { msgtype: 'text', text: { content: text.slice(0, 1800) } };
      } else if (u.includes('oapi.dingtalk.com')) {
        payload = { msgtype: 'text', text: { content: text.slice(0, 1800) } };
      } else if (u.includes('open.feishu.cn') || u.includes('open.larksuite.com')) {
        payload = { msg_type: 'text', content: { text: text.slice(0, 1800) } };
      } else if (u.includes('hooks.slack.com')) {
        payload = { text: '```' + text.slice(0, 2500) + '```' };
      } else if (u.includes('discord.com/api/webhooks')) {
        payload = { content: text.slice(0, 1900) };
      } else {
        payload = { source: 'zuoyugarment.com/inquiry', inquiry: rec };
      }
      const r = await fetch(u, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload),
      });
      out.push({ webhook: r.status });
    } catch (e) {
      out.push({ webhook: 'error:' + String(e).slice(0, 80) });
    }
  }

  // 2) 邮件（Resend）
  if (env.RESEND_API_KEY && env.NOTIFY_EMAIL) {
    try {
      const r = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          authorization: 'Bearer ' + env.RESEND_API_KEY,
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          from: env.FROM_EMAIL || 'Zuoyu Website <onboarding@resend.dev>',
          to: [env.NOTIFY_EMAIL],
          reply_to: rec.email,
          subject: `Website inquiry — ${rec.company || rec.name}${rec.buyerCountry ? ' (' + rec.buyerCountry + ')' : ''}`,
          text,
        }),
      });
      out.push({ email: r.status });
    } catch (e) {
      out.push({ email: 'error:' + String(e).slice(0, 80) });
    }
  }

  return out;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  let data = {};
  try {
    const ct = request.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      data = await request.json();
    } else {
      const fd = await request.formData();
      for (const [k, v] of fd.entries()) data[k] = typeof v === 'string' ? v : '[file]';
    }
  } catch (e) {
    return fail('bad_request', 400);
  }

  // 蜜罐字段：机器人会填，直接假装成功
  if (data._hp) return ok({ ok: true, spam: true });

  const rec = {
    id: crypto.randomUUID(),
    ts: new Date().toISOString(),
    name: clean(data.name, 120),
    company: clean(data.company, 160),
    email: clean(data.email, 200),
    whatsapp: clean(data.whatsapp, 60),
    buyerCountry: clean(data.country, 80),
    category: clean(data.category, 80),
    quantity: clean(data.quantity, 80),
    brief: clean(data.brief, 4000),
    page: clean(data.page, 300),
    cfCountry: request.headers.get('cf-ipcountry') || '',
    ip: request.headers.get('cf-connecting-ip') || '',
    ua: clean(request.headers.get('user-agent'), 300),
    referer: clean(request.headers.get('referer'), 300),
  };

  if (!rec.name || !rec.email || !rec.brief) return fail('missing_fields', 422);
  if (!EMAIL_RE.test(rec.email)) return fail('invalid_email', 422);
  if (rec.brief.length < 10) return fail('brief_too_short', 422);

  // 既没有存档也没有通知渠道时，宁可返回 503 让前端降级成邮件，
  // 也不能假装成功、把询盘悄悄丢掉。
  const hasStore = Boolean(env.INQUIRIES);
  const hasNotifier = Boolean(env.WEBHOOK_URL) ||
    Boolean(env.RESEND_API_KEY && env.NOTIFY_EMAIL);
  if (!hasStore && !hasNotifier) {
    return fail('not_configured', 503);
  }

  // 简单限流：同一 IP 每小时最多 5 条
  if (env.INQUIRIES) {
    const hour = new Date().toISOString().slice(0, 13);
    const rlKey = `rl:${rec.ip}:${hour}`;
    try {
      const cur = parseInt((await env.INQUIRIES.get(rlKey)) || '0', 10);
      if (cur >= 5) return fail('rate_limited', 429);
      await env.INQUIRIES.put(rlKey, String(cur + 1), { expirationTtl: 3700 });
    } catch (e) {
      // 限流失败不影响主流程
    }
  }

  // 存档（key 按时间排序，便于倒序列出）
  if (env.INQUIRIES) {
    try {
      await env.INQUIRIES.put(`inq:${rec.ts}:${rec.id}`, JSON.stringify(rec), {
        expirationTtl: 60 * 60 * 24 * 365 * 2,
      });
    } catch (e) {
      return fail('storage_error', 500, { detail: String(e).slice(0, 120) });
    }
  }

  const sent = await notify(env, rec);

  return ok({ ok: true, id: rec.id, notified: sent, stored: Boolean(env.INQUIRIES) });
}

export async function onRequestGet() {
  return new Response(JSON.stringify({ ok: false, error: 'method_not_allowed' }), {
    status: 405,
    headers: { ...JSON_HEADERS, allow: 'POST' },
  });
}
