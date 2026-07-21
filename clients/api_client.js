// 2. clients/api_client.js (JavaScript / Next.js)
/**
 * Client API JavaScript untuk Pendaftaran Kapita Gereja
 * Base URL: https://pendaftarankapitagereja.onrender.com
 *
 * Gunakan:
 *   const client = new ApiClient("GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai");
 *   const res = await client.get("/api/churches");
 */

const crypto = require('crypto');

class ApiClient {
  constructor(
    secretKey,
    baseUrl = 'https://pendaftarankapitagereja.onrender.com',
  ) {
    this.secretKey = secretKey;
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.adminId = null;
  }

  setAdmin(adminId) {
    this.adminId = adminId;
    return this;
  }

  _generateSalt(length = 16) {
    const chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let salt = '';
    const bytes = crypto.randomBytes(length);
    for (let i = 0; i < length; i++) {
      salt += chars[bytes[i] % chars.length];
    }
    return salt;
  }

  _generateSignature(salt, data) {
    let body = '';
    if (data && typeof data === 'object') {
      const sorted = Object.keys(data)
        .sort()
        .reduce((acc, key) => {
          acc[key] = data[key];
          return acc;
        }, {});
      body = JSON.stringify(sorted);
    } else if (data) {
      body = String(data);
    }
    const raw = `APIKAPITAGKYALSUT${this.secretKey}${salt}${body}`;
    return crypto.createHash('sha256').update(raw, 'utf8').digest('hex');
  }

  _buildHeaders(data = null) {
    const salt = this._generateSalt();
    const headers = {
      'X-Signature': this._generateSignature(salt, data),
      'X-Salt': salt,
      'Content-Type': 'application/json',
    };
    if (this.adminId !== null) {
      headers['X-Admin-ID'] = String(this.adminId);
    }
    return headers;
  }

  async _request(method, path, body = null, params = null) {
    let url = `${this.baseUrl}${path}`;
    let data = body || {};

    if (method === 'GET' && params) {
      data = params;
      const qs = new URLSearchParams(params).toString();
      if (qs) url += `?${qs}`;
    }

    const headers = this._buildHeaders(data);

    const options = {
      method,
      headers,
      timeout: 30000,
    };

    if (method !== 'GET' && body) {
      options.body = JSON.stringify(body);
    }

    const resp = await fetch(url, options);
    return resp.json();
  }

  // ── Auth ──────────────────────────────────────────────────

  async login(email, password) {
    return this._request('POST', '/api/admin/login', { email, password });
  }

  // ── Admin ─────────────────────────────────────────────────

  async getAdmins() {
    return this._request('GET', '/api/admins');
  }

  async getAdmin(adminId) {
    return this._request('GET', `/api/admins/${adminId}`);
  }

  async createAdmin(username, email, password, role = null) {
    const body = { username, email, password };
    if (role) body.role = role;
    return this._request('POST', '/api/admins', body);
  }

  async updateAdmin(adminId, username, email, password, role = null) {
    const body = { username, email, password };
    if (role) body.role = role;
    return this._request('PUT', `/api/admins/${adminId}`, body);
  }

  async deleteAdmin(adminId) {
    return this._request('DELETE', `/api/admins/${adminId}`);
  }

  // ── Church ────────────────────────────────────────────────

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

  // ── Church Kapita Quota ───────────────────────────────────

  async getChurchKapitaQuotas(gkode) {
    return this._request('GET', `/api/churches/${gkode}/kapita-quota`);
  }

  async getChurchKapitaQuota(gkode, kapitaId) {
    return this._request(
      'GET',
      `/api/churches/${gkode}/kapita-quota/${kapitaId}`,
    );
  }

  async setChurchKapitaQuota(gkode, kapitaId, kuota) {
    return this._request('POST', `/api/churches/${gkode}/kapita-quota`, {
      kapita_id: kapitaId,
      kuota,
    });
  }

  async updateChurchKapitaQuota(gkode, kapitaId, kuota) {
    return this._request(
      'PUT',
      `/api/churches/${gkode}/kapita-quota/${kapitaId}`,
      {
        kapita_id: kapitaId,
        kuota,
      },
    );
  }

  async deleteChurchKapitaQuota(gkode, kapitaId) {
    return this._request(
      'DELETE',
      `/api/churches/${gkode}/kapita-quota/${kapitaId}`,
    );
  }

  // ── Kapita ────────────────────────────────────────────────

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

  // ── Registration ──────────────────────────────────────────

  async createRegistration({
    fullName,
    email,
    phone,
    birthDate,
    address,
    churchGkode,
    kapitaId,
    notes,
  }) {
    const body = {
      full_name: fullName,
      email,
      phone,
      birth_date: birthDate,
      address,
      church_gkode: churchGkode,
      kapita_id: kapitaId,
    };
    if (notes) body.notes = notes;
    return this._request('POST', '/api/registrations', body);
  }

  async checkRegistration(email) {
    return this._request('GET', `/api/registrations/check/${email}`);
  }

  async getRegistration(regId) {
    return this._request('GET', `/api/registrations/${regId}`);
  }

  async updateRegistration(
    regId,
    {
      fullName,
      email,
      phone,
      birthDate,
      address,
      churchGkode,
      kapitaId,
      notes,
    },
  ) {
    const body = {
      full_name: fullName,
      email,
      phone,
      birth_date: birthDate,
      address,
      church_gkode: churchGkode,
      kapita_id: kapitaId,
    };
    if (notes) body.notes = notes;
    return this._request('PUT', `/api/registrations/${regId}`, body);
  }

  async deleteRegistration(regId) {
    return this._request('DELETE', `/api/registrations/${regId}`);
  }

  // ── User ──────────────────────────────────────────────────

  async getUsers() {
    return this._request('GET', '/api/users');
  }

  async getUser(uid) {
    return this._request('GET', `/api/users/${uid}`);
  }

  async createUser({
    fullName,
    email,
    phone,
    birthDate,
    address,
    churchGkode,
    ukapita,
    notes,
  }) {
    const body = {
      full_name: fullName,
      email,
      phone,
      birth_date: birthDate,
      address,
      church_gkode: churchGkode,
      ukapita,
    };
    if (notes) body.notes = notes;
    return this._request('POST', '/api/users', body);
  }

  async updateUser(
    uid,
    { fullName, email, phone, birthDate, address, churchGkode, ukapita, notes },
  ) {
    const body = {
      full_name: fullName,
      email,
      phone,
      birth_date: birthDate,
      address,
      church_gkode: churchGkode,
      ukapita,
    };
    if (notes) body.notes = notes;
    return this._request('PUT', `/api/users/${uid}`, body);
  }

  async deleteUser(uid) {
    return this._request('DELETE', `/api/users/${uid}`);
  }
}

module.exports = { ApiClient };

// ── Contoh Penggunaan (Node.js) ──────────────────────────────
// const client = new ApiClient("GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai");
//
// (async () => {
//   const login = await client.login("superadmin@gereja.com", "superadmin123");
//   console.log(login);
//
//   if (login.status) {
//     client.setAdmin(login.results.aid);
//     const churches = await client.getChurches();
//     console.log(churches);
//   }
// })();
