const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://pendaftarankapitagereja.onrender.com";
const SECRET_KEY = process.env.NEXT_PUBLIC_API_SECRET || "ISI DENGAN SECRETMU"; // Ganti dengan secret key yang sesuai

function generateSalt(length = 16): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let salt = "";
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  for (let i = 0; i < length; i++) {
    salt += chars[array[i] % chars.length];
  }
  return salt;
}

async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

function sortObject(obj: Record<string, unknown>): Record<string, unknown> {
  return Object.keys(obj)
    .sort()
    .reduce((acc, key) => {
      acc[key] = obj[key];
      return acc;
    }, {} as Record<string, unknown>);
}

async function generateSignature(
  salt: string,
  data: Record<string, unknown> | null
): Promise<string> {
  let body = "";
  if (data && typeof data === "object") {
    body = JSON.stringify(sortObject(data));
  } else if (data) {
    body = String(data);
  }
  const raw = `APIKAPITAGKYALSUT${SECRET_KEY}${salt}${body}`;
  return sha256(raw);
}

async function buildHeaders(
  data?: Record<string, unknown> | null,
  adminId?: number | null
): Promise<Record<string, string>> {
  const salt = generateSalt();
  const headers: Record<string, string> = {
    "X-Signature": await generateSignature(salt, data ?? null),
    "X-Salt": salt,
    "Content-Type": "application/json",
  };
  if (adminId != null) {
    headers["X-Admin-ID"] = String(adminId);
  }
  return headers;
}

async function request<T>(
  method: string,
  path: string,
  body?: Record<string, unknown> | null,
  params?: Record<string, string> | null,
  adminId?: number | null
): Promise<T> {
  let url = `${BASE_URL}${path}`;
  let data: Record<string, unknown> = body || {};

  if (method === "GET" && params) {
    data = params as unknown as Record<string, unknown>;
    const qs = new URLSearchParams(params).toString();
    if (qs) url += `?${qs}`;
  }

  const headers = await buildHeaders(data, adminId);

  const options: RequestInit = { method, headers };

  if (method !== "GET" && body) {
    options.body = JSON.stringify(body);
  }

  const resp = await fetch(url, options);
  return resp.json();
}

// ── Auth ──────────────────────────────────────────────────
export async function login(email: string, password: string) {
  return request<{ status: boolean; results: { aid: number; username: string; email: string; role: string } }>(
    "POST", "/api/admin/login", { email, password }
  );
}

// ── Church ────────────────────────────────────────────────
export async function getChurches() {
  return request<{ status: boolean; results: Church[] }>("GET", "/api/churches");
}

export async function getChurch(gkode: string) {
  return request<{ status: boolean; results: Church }>("GET", `/api/churches/${gkode}`);
}

export async function createChurch(name: string, adminId: number) {
  return request("POST", "/api/churches", { name }, null, adminId);
}

export async function updateChurch(gkode: string, name: string, adminId: number) {
  return request("PUT", `/api/churches/${gkode}`, { name }, null, adminId);
}

export async function deleteChurch(gkode: string, adminId: number) {
  return request("DELETE", `/api/churches/${gkode}`, null, null, adminId);
}

// ── Kapita ────────────────────────────────────────────────
export async function getKapitaList() {
  return request<{ status: boolean; results: Kapita[] }>("GET", "/api/kapita");
}

export async function getKapita(kapitaId: number) {
  return request<{ status: boolean; results: Kapita }>("GET", `/api/kapita/${kapitaId}`);
}

export async function createKapita(namakapita: string, adminId: number) {
  return request("POST", "/api/kapita", { namakapita }, null, adminId);
}

export async function updateKapita(kapitaId: number, namakapita: string, adminId: number) {
  return request("PUT", `/api/kapita/${kapitaId}`, { namakapita }, null, adminId);
}

export async function deleteKapita(kapitaId: number, adminId: number) {
  return request("DELETE", `/api/kapita/${kapitaId}`, null, null, adminId);
}

// ── Church Kapita Quota ───────────────────────────────────
export async function getChurchKapitaQuotas(gkode: string) {
  return request("GET", `/api/churches/${gkode}/kapita-quota`);
}

export async function setChurchKapitaQuota(gkode: string, kapitaId: number, kuota: number, adminId: number) {
  return request("POST", `/api/churches/${gkode}/kapita-quota`, { kapita_id: kapitaId, kuota }, null, adminId);
}

export async function deleteChurchKapitaQuota(gkode: string, kapitaId: number, adminId: number) {
  return request("DELETE", `/api/churches/${gkode}/kapita-quota/${kapitaId}`, null, null, adminId);
}

// ── Registration (admin form) ─────────────────────────────
export async function createRegistration(data: RegistrationPayload, adminId?: number) {
  const body: Record<string, unknown> = {
    full_name: data.fullName,
    email: data.email,
    phone: data.phone,
    birth_date: data.birthDate,
    address: data.address,
    church_gkode: data.churchGkode,
    kapita_id: data.kapitaId,
  };
  if (data.notes) body.notes = data.notes;
  return request("POST", "/api/registrations", body, null, adminId ?? null);
}

export async function checkRegistration(email: string) {
  return request("GET", `/api/registrations/check/${email}`);
}

// ── User (public form) ────────────────────────────────────
export async function createUser(data: UserPayload) {
  const body: Record<string, unknown> = {
    full_name: data.fullName,
    email: data.email,
    phone: data.phone,
    birth_date: data.birthDate,
    address: data.address,
    church_gkode: data.churchGkode,
    ukapita: data.ukapita,
  };
  if (data.notes) body.notes = data.notes;
  return request("POST", "/api/users", body);
}

export async function getUsers() {
  return request("GET", "/api/users");
}

// ── Types ─────────────────────────────────────────────────
export interface Church {
  id: string;
  name: string;
  total_quota: number;
  total_registered: number;
  quota_left: number;
  kapita: ChurchKapitaQuota[];
}

export interface Kapita {
  idkapita: number;
  namakapita: string;
}

export interface ChurchKapitaQuota {
  gkid: number;
  gkode: string;
  idkapita: number;
  kapita_name: string;
  kuota: number;
  registered: number;
  quota_left: number;
}

export interface RegistrationPayload {
  fullName: string;
  email: string;
  phone: string;
  birthDate: string;
  address: string;
  churchGkode: string;
  kapitaId: number;
  notes?: string;
}

export interface UserPayload {
  fullName: string;
  email: string;
  phone: string;
  birthDate: string;
  address: string;
  churchGkode: string;
  ukapita: number;
  notes?: string;
}
