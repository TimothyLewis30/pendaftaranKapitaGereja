/**
 * API Client JavaScript untuk Pendaftaran Kapita Gereja
 *
 * Dependencies: crypto-js (https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.2.0/crypto-js.min.js)
 *
 * Contoh penggunaan:
 *   const client = new ApiClient({ secretKey: 'edit this' });
 *   const churches = await client.getChurches();
 */

class ApiClient {
  constructor({ secretKey, baseUrl = 'https://pendaftarankapitagereja.onrender.com' }) {
    this.secretKey = secretKey;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.adminId = null;
  }

  setAdmin(adminId) {
    this.adminId = adminId;
    return this;
  }

  _generateSalt(length = 16) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let salt = '';
    for (let i = 0; i < length; i++) {
      salt += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return salt;
  }

  _generateSignature(salt, data) {
    const body = data ? JSON.stringify(data) : '{}';
    const raw = 'APIKAPITAGKYALSUT' + this.secretKey + salt + body;
    return CryptoJS.SHA256(raw).toString();
  }

  _buildHeaders(data = null) {
    const salt = this._generateSalt();
    const headers = {
      'Content-Type': 'application/json',
      'X-Salt': salt,
      'X-Signature': this._generateSignature(salt, data),
    };
    if (this.adminId !== null) {
      headers['X-Admin-ID'] = String(this.adminId);
    }
    return headers;
  }

  async _request(method, path, body = null, params = null) {
    let url = this.baseUrl + path;

    if (method === 'GET' && params) {
      const query = new URLSearchParams(params).toString();
      if (query) url += '?' + query;
    }

    const data = method === 'GET' ? params : body;
    const headers = this._buildHeaders(data);

    const options = { method, headers };
    if (method !== 'GET' && body) {
      options.body = JSON.stringify(body);
    }

    const res = await fetch(url, options);
    try {
      return await res.json();
    } catch {
      return {
        code: res.status,
        status: false,
        message: `Non-JSON response (${res.status}): ${(await res.text()).slice(0, 500)}`,
        results: [],
      };
    }
  }

  // ═══════════════════════════════════════════════════════════
  // Ping
  // ═══════════════════════════════════════════════════════════

  async ping() {
    return this._request('GET', '/api/ping');
  }

  // ═══════════════════════════════════════════════════════════
  // Auth
  // ═══════════════════════════════════════════════════════════

  async login(email, password) {
    return this._request('POST', '/api/admin/login', { email, password });
  }

  // ═══════════════════════════════════════════════════════════
  // Admin
  // ═══════════════════════════════════════════════════════════

  async getAdmins() {
    return this._request('GET', '/api/admins');
  }

  async getAdmin(aid) {
    return this._request('GET', `/api/admins/${aid}`);
  }

  async createAdmin({ username, email, password, role = null }) {
    const body = { username, email, password };
    if (role) body.role = role;
    return this._request('POST', '/api/admins', body);
  }

  async updateAdmin(aid, { username, email, password, role = null }) {
    const body = { username, email, password };
    if (role) body.role = role;
    return this._request('PUT', `/api/admins/${aid}`, body);
  }

  async deleteAdmin(aid) {
    return this._request('DELETE', `/api/admins/${aid}`);
  }

  // ═══════════════════════════════════════════════════════════
  // Church
  // ═══════════════════════════════════════════════════════════

  async getChurches() {
    return this._request('GET', '/api/churches');
  }

  async getChurch(gkode) {
    return this._request('GET', `/api/churches/${gkode}`);
  }

  async createChurch(name) {
    return this._request('POST', '/api/churches', { name });
  }

  async updateChurch(gkode, name) {
    return this._request('PUT', `/api/churches/${gkode}`, { name });
  }

  async deleteChurch(gkode) {
    return this._request('DELETE', `/api/churches/${gkode}`);
  }

  // ═══════════════════════════════════════════════════════════
  // Church Kapita Quota
  // ═══════════════════════════════════════════════════════════

  async getChurchKapitaQuotas(gkode) {
    return this._request('GET', `/api/churches/${gkode}/kapita-quota`);
  }

  async getChurchKapitaQuota(gkode, kapitaId) {
    return this._request('GET', `/api/churches/${gkode}/kapita-quota/${kapitaId}`);
  }

  async setChurchKapitaQuota(gkode, kapitaId, kuota) {
    return this._request('POST', `/api/churches/${gkode}/kapita-quota`, {
      kapita_id: kapitaId,
      kuota,
    });
  }

  async updateChurchKapitaQuota(gkode, kapitaId, kuota) {
    return this._request('PUT', `/api/churches/${gkode}/kapita-quota/${kapitaId}`, {
      kapita_id: kapitaId,
      kuota,
    });
  }

  async deleteChurchKapitaQuota(gkode, kapitaId) {
    return this._request('DELETE', `/api/churches/${gkode}/kapita-quota/${kapitaId}`);
  }

  // ═══════════════════════════════════════════════════════════
  // Kapita
  // ═══════════════════════════════════════════════════════════

  async getKapitaList() {
    return this._request('GET', '/api/kapita');
  }

  async getKapita(kapitaId) {
    return this._request('GET', `/api/kapita/${kapitaId}`);
  }

  async createKapita(namakapita) {
    return this._request('POST', '/api/kapita', { namakapita });
  }

  async updateKapita(kapitaId, namakapita) {
    return this._request('PUT', `/api/kapita/${kapitaId}`, { namakapita });
  }

  async deleteKapita(kapitaId) {
    return this._request('DELETE', `/api/kapita/${kapitaId}`);
  }

  // ═══════════════════════════════════════════════════════════
  // Registration
  // ═══════════════════════════════════════════════════════════

  async createRegistration({ fullName, email, phone, churchGkode, kapitaIdSesi1, kapitaIdSesi2 }) {
    const body = {
      full_name: fullName,
      email,
      phone,
      church_gkode: churchGkode,
      kapita_id_sesi_1: kapitaIdSesi1,
      kapita_id_sesi_2: kapitaIdSesi2,
    };
    return this._request('POST', '/api/registrations', body);
  }

  async getRegistration(regId) {
    return this._request('GET', `/api/registrations/${regId}`);
  }

  async checkRegistration(email) {
    return this._request('GET', `/api/registrations/check/${email}`);
  }

  async updateRegistration(regId, { fullName, email, phone, churchGkode, kapitaIdSesi1, kapitaIdSesi2 }) {
    const body = {
      full_name: fullName,
      email,
      phone,
      church_gkode: churchGkode,
      kapita_id_sesi_1: kapitaIdSesi1,
      kapita_id_sesi_2: kapitaIdSesi2,
    };
    return this._request('PUT', `/api/registrations/${regId}`, body);
  }

  async deleteRegistration(regId) {
    return this._request('DELETE', `/api/registrations/${regId}`);
  }

  // ═══════════════════════════════════════════════════════════
  // User
  // ═══════════════════════════════════════════════════════════

  async getUsers() {
    return this._request('GET', '/api/users');
  }

  async getUser(uid) {
    return this._request('GET', `/api/users/${uid}`);
  }

  async createUser({ fullName, email, phone, churchGkode, ukapitaSesi1, ukapitaSesi2 }) {
    const body = {
      full_name: fullName,
      email,
      phone,
      church_gkode: churchGkode,
      ukapita_sesi_1: ukapitaSesi1,
      ukapita_sesi_2: ukapitaSesi2,
    };
    return this._request('POST', '/api/users', body);
  }

  async updateUser(uid, { fullName, email, phone, churchGkode, ukapitaSesi1, ukapitaSesi2 }) {
    const body = {
      full_name: fullName,
      email,
      phone,
      church_gkode: churchGkode,
      ukapita_sesi_1: ukapitaSesi1,
      ukapita_sesi_2: ukapitaSesi2,
    };
    return this._request('PUT', `/api/users/${uid}`, body);
  }

  async deleteUser(uid) {
    return this._request('DELETE', `/api/users/${uid}`);
  }
}

// ── Contoh Penggunaan ──────────────────────────────────────

async function main() {
  const client = new ApiClient({ secretKey: 'edit this' });

  function show(label, data) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`  ${label}`);
    console.log(`${'='.repeat(60)}`);
    console.log(JSON.stringify(data, null, 2));
  }

  // 1. Publik — Church
  let res = await client.getChurches();
  show('GET /api/churches', res);
  const gkode = res.results?.[0]?.id;

  if (gkode) {
    res = await client.getChurch(gkode);
    show(`GET /api/churches/${gkode}`, res);
  }

  // 2. Publik — Kapita
  res = await client.getKapitaList();
  show('GET /api/kapita', res);
  const kapitaId = res.results?.[0]?.idkapita;

  if (kapitaId) {
    res = await client.getKapita(kapitaId);
    show(`GET /api/kapita/${kapitaId}`, res);
  }

  // 3. Publik — User
  res = await client.createUser({
    fullName: 'Yohanes Test',
    email: 'yohanes@test.com',
    phone: '08123456789',
    churchGkode: gkode || 'GKY001',
    ukapitaSesi1: kapitaId || 1,
    ukapitaSesi2: kapitaId || 1,
  });
  show('POST /api/users (create)', res);
  const uid = res.results?.uid;

  res = await client.getUsers();
  show('GET /api/users', res);

  if (uid) {
    res = await client.getUser(uid);
    show(`GET /api/users/${uid}`, res);

    res = await client.updateUser(uid, {
      fullName: 'Yohanes Updated',
      email: 'yohanes@test.com',
      phone: '08123456789',
      churchGkode: gkode || 'GKY001',
      ukapitaSesi1: kapitaId || 1,
      ukapitaSesi2: kapitaId || 1,
    });
    show(`PUT /api/users/${uid} (update)`, res);
  }

  // 4. Publik — Registration
  res = await client.createRegistration({
    fullName: 'Yohanes Test',
    email: 'yohanes@test.com',
    phone: '08123456789',
    churchGkode: gkode || 'GKY001',
    kapitaIdSesi1: kapitaId || 1,
    kapitaIdSesi2: kapitaId || 1,
  });
  show('POST /api/registrations (create)', res);
  const regId = res.results?.id;

  if (regId) {
    res = await client.getRegistration(regId);
    show(`GET /api/registrations/${regId}`, res);
  }

  res = await client.checkRegistration('yohanes@test.com');
  show('GET /api/registrations/check/yohanes@test.com', res);

  // 5. Login Admin
  res = await client.login('superadmin@gereja.com', 'superadmin123');
  show('POST /api/admin/login', res);

  if (!res.status) {
    console.log('\n[SKIP] Semua endpoint admin di-skip karena login gagal.');
    return;
  }

  const adminId = res.results.aid;
  client.setAdmin(adminId);

  // 6. Admin — Admin CRUD
  res = await client.getAdmins();
  show('GET /api/admins', res);

  res = await client.createAdmin({
    username: 'admin_test',
    email: 'admin_test@gereja.com',
    password: 'admin123',
    role: 'Admin',
  });
  show('POST /api/admins (create)', res);
  const newAid = res.results?.aid;

  if (newAid) {
    res = await client.getAdmin(newAid);
    show(`GET /api/admins/${newAid}`, res);

    res = await client.updateAdmin(newAid, {
      username: 'admin_test_updated',
      email: 'admin_test_updated@gereja.com',
      password: 'admin123',
      role: 'Admin',
    });
    show(`PUT /api/admins/${newAid} (update)`, res);

    res = await client.deleteAdmin(newAid);
    show(`DELETE /api/admins/${newAid}`, res);
  }

  // 7. Admin — Church CRUD
  res = await client.createChurch('Gereja Test Admin');
  show('POST /api/churches (create)', res);
  const adminGkode = res.results?.id || gkode;

  if (adminGkode) {
    res = await client.updateChurch(adminGkode, 'Gereja Test Updated');
    show(`PUT /api/churches/${adminGkode} (update)`, res);
  }

  // 8. Admin — Kapita CRUD
  res = await client.createKapita('Kapita Test Admin');
  show('POST /api/kapita (create)', res);
  const adminKapitaId = res.results?.idkapita || kapitaId;

  if (adminKapitaId) {
    res = await client.updateKapita(adminKapitaId, 'Kapita Test Updated');
    show(`PUT /api/kapita/${adminKapitaId} (update)`, res);
  }

  // 9. Admin — Quota CRUD
  if (adminGkode && adminKapitaId) {
    res = await client.setChurchKapitaQuota(adminGkode, adminKapitaId, 50);
    show(`POST /api/churches/${adminGkode}/kapita-quota (set)`, res);

    res = await client.getChurchKapitaQuotas(adminGkode);
    show(`GET /api/churches/${adminGkode}/kapita-quota`, res);

    res = await client.updateChurchKapitaQuota(adminGkode, adminKapitaId, 100);
    show(`PUT /api/churches/${adminGkode}/kapita-quota/${adminKapitaId} (update)`, res);
  }

  // 10. Cleanup
  if (regId) {
    res = await client.deleteRegistration(regId);
    show(`DELETE /api/registrations/${regId}`, res);
  }
  if (uid) {
    res = await client.deleteUser(uid);
    show(`DELETE /api/users/${uid}`, res);
  }
  if (adminGkode && adminKapitaId) {
    res = await client.deleteChurchKapitaQuota(adminGkode, adminKapitaId);
    show(`DELETE /api/churches/${adminGkode}/kapita-quota/${adminKapitaId}`, res);
  }
  if (adminKapitaId) {
    res = await client.deleteKapita(adminKapitaId);
    show(`DELETE /api/kapita/${adminKapitaId}`, res);
  }
  if (adminGkode) {
    res = await client.deleteChurch(adminGkode);
    show(`DELETE /api/churches/${adminGkode}`, res);
  }
}

main().catch(console.error);
