# Frontend Integration Guide

Panduan lengkap integrasi frontend ke Backend Pendaftaran Kapita Gereja.

---

## Daftar Isi

1. [Base URL](#base-url)
2. [Konfigurasi](#konfigurasi)
3. [Autentikasi (Signature)](#autentikasi-signature)
4. [Role-Based Access Control](#role-based-access-control-rbac)
5. [Format Response](#format-response)
6. [Daftar Endpoint](#daftar-endpoint)
7. [Contoh Lengkap](#contoh-lengkap)

---

## Base URL

```
https://pendaftarankapitagereja.onrender.com
```

Untuk development lokal:

```
http://127.0.0.1:8080
```

---

## Konfigurasi

Semua konfigurasi diambil dari file `.env.local` di root project.

```python
# src/settings.py
SECRET_KEY = _env["application"]["secret"]
```

**Anda perlu tahu SECRET_KEY** karena digunakan untuk generate signature setiap request. Nilai ini sama dengan `application.secret` di `.env.local`.

---

## Autentikasi (Signature)

**Setiap request** ke API harus menyertakan 2 header wajib:

| Header        | Tipe   | Keterangan                              |
| ------------- | ------ | --------------------------------------- |
| `X-Salt`      | string | Salt unik per request (16+ karakter)    |
| `X-Signature` | string | SHA-256 hash (64 karakter hex)          |
| `X-Admin-ID`  | string | ID admin (hanya untuk endpoint admin)   |

### Rumus Signature

```
SHA256("APIKAPITAGKYALSUT" + SECRET_KEY + SALT + DATA)
```

| Parameter    | Keterangan                          |
| ------------ | ----------------------------------- |
| `SECRET_KEY` | Secret key dari server              |
| `SALT`       | Nilai header `X-Salt`               |
| `DATA`       | Request body (JSON string) atau `"{}"` untuk GET |

### Cara Generate Salt

```javascript
// Random string 16 karakter
function generateSalt() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let salt = '';
  for (let i = 0; i < 16; i++) {
    salt += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return salt;
}
```

### Cara Generate Signature (JavaScript)

```javascript
// Menggunakan crypto-js: https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.2.0/crypto-js.min.js

function generateHeaders(data = null, adminId = null) {
  const secret = 'edit this'; // SECRET_KEY dari server
  const salt = generateSalt();
  const body = data ? JSON.stringify(data) : '{}';
  const raw = 'APIKAPITAGKYALSUT' + secret + salt + body;
  const signature = CryptoJS.SHA256(raw).toString();

  const headers = {
    'Content-Type': 'application/json',
    'X-Salt': salt,
    'X-Signature': signature,
  };

  if (adminId) {
    headers['X-Admin-ID'] = String(adminId);
  }

  return headers;
}
```

### Cara Generate Signature (Python)

```python
import hashlib, json, random, string

def generate_headers(data=None, admin_id=None):
    secret = "edit this"  # SECRET_KEY dari server
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    body = json.dumps(data, sort_keys=True, separators=(",", ":")) if data else "{}"
    raw = f"APIKAPITAGKYALSUT{secret}{salt}{body}"
    signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Salt": salt,
        "X-Signature": signature,
    }
    if admin_id:
        headers["X-Admin-ID"] = str(admin_id)
    return headers
```

### Error Autentikasi

| Kode  | Penyebab                                    |
| ----- | ------------------------------------------- |
| `401` | Header `X-Salt` atau `X-Signature` kosong   |
| `401` | Signature tidak cocok (salah secret/data)   |

---

## Role-Based Access Control (RBAC)

### Daftar Role

| Role         | Akses                                        |
| ------------ | -------------------------------------------- |
| `SuperAdmin` | CRUD Gereja, CRUD Kapita, CRUD Admin, CRUD Quota |
| `Admin`      | CRUD Gereja, CRUD Kapita, CRUD Quota         |
| `NULL`       | Tidak bisa CUD (hanya login)                 |

### Alur Login Admin

```
1. POST /api/admin/login  →  dapatkan "aid" dari response
2. Simpan "aid" di client (localStorage / state)
3. Setiap request CUD, kirim header "X-Admin-ID: {aid}"
4. GET tidak butuh X-Admin-ID
```

---

## Format Response

Semua response menggunakan format:

```json
{
  "code": 200,
  "status": true,
  "message": "Pesan informasi",
  "results": {}
}
```

---

## Daftar Endpoint

### PUBLIK (Tidak Butuh Login)

#### Gereja

| Method | Endpoint                           | Keterangan                      |
| ------ | ---------------------------------- | ------------------------------- |
| GET    | `/api/churches`                    | List semua gereja + kuota       |
| GET    | `/api/churches/{gkode}`            | Detail gereja + kuota           |

#### Kapita

| Method | Endpoint                           | Keterangan                      |
| ------ | ---------------------------------- | ------------------------------- |
| GET    | `/api/kapita`                      | List semua kapita               |
| GET    | `/api/kapita/{idkapita}`           | Detail kapita                   |

#### User (Pendaftaran Mandiri)

| Method | Endpoint                           | Keterangan                      |
| ------ | ---------------------------------- | ------------------------------- |
| POST   | `/api/users`                       | Daftar user baru                |
| GET    | `/api/users`                       | List semua user                 |
| GET    | `/api/users/{uid}`                 | Detail user                     |
| PUT    | `/api/users/{uid}`                 | Update user                     |
| DELETE | `/api/users/{uid}`                 | Hapus user                      |

#### Registrasi (Admin Form)

| Method | Endpoint                           | Keterangan                      |
| ------ | ---------------------------------- | ------------------------------- |
| POST   | `/api/registrations`               | Buat pendaftaran baru           |
| GET    | `/api/registrations/{id}`          | Detail pendaftaran              |
| PUT    | `/api/registrations/{id}`          | Update pendaftaran              |
| DELETE | `/api/registrations/{id}`          | Hapus pendaftaran               |
| GET    | `/api/registrations/check/{email}` | Cek apakah email sudah terdaftar|

---

### ADMIN (Butuh Login + X-Admin-ID)

#### Auth

| Method | Endpoint                           | Keterangan                      | Role       |
| ------ | ---------------------------------- | ------------------------------- | ---------- |
| POST   | `/api/admin/login`                 | Login admin                     | -          |

#### Admin Management (Hanya SuperAdmin)

| Method | Endpoint                           | Keterangan                      | Role       |
| ------ | ---------------------------------- | ------------------------------- | ---------- |
| GET    | `/api/admins`                      | List semua admin                | SuperAdmin |
| GET    | `/api/admins/{aid}`                | Detail admin                    | SuperAdmin |
| POST   | `/api/admins`                      | Tambah admin baru               | SuperAdmin |
| PUT    | `/api/admins/{aid}`                | Update admin                    | SuperAdmin |
| DELETE | `/api/admins/{aid}`                | Hapus admin                     | SuperAdmin |

#### Gereja (Admin / SuperAdmin)

| Method | Endpoint                           | Keterangan                      | Role             |
| ------ | ---------------------------------- | ------------------------------- | ---------------- |
| POST   | `/api/churches`                    | Tambah gereja baru              | Admin/SuperAdmin |
| PUT    | `/api/churches/{gkode}`            | Update gereja                   | Admin/SuperAdmin |
| DELETE | `/api/churches/{gkode}`            | Hapus gereja                    | Admin/SuperAdmin |

#### Quota Kapita per Gereja (Admin / SuperAdmin)

| Method | Endpoint                                              | Keterangan                   | Role             |
| ------ | ----------------------------------------------------- | ---------------------------- | ---------------- |
| GET    | `/api/churches/{gkode}/kapita-quota`                  | List kuota                   | -                |
| GET    | `/api/churches/{gkode}/kapita-quota/{idkapita}`       | Detail kuota                 | -                |
| POST   | `/api/churches/{gkode}/kapita-quota`                  | Set kuota baru               | Admin/SuperAdmin |
| PUT    | `/api/churches/{gkode}/kapita-quota/{idkapita}`       | Update kuota                 | Admin/SuperAdmin |
| DELETE | `/api/churches/{gkode}/kapita-quota/{idkapita}`       | Hapus kuota                  | Admin/SuperAdmin |

#### Kapita (Admin / SuperAdmin)

| Method | Endpoint                           | Keterangan                      | Role             |
| ------ | ---------------------------------- | ------------------------------- | ---------------- |
| POST   | `/api/kapita`                      | Tambah kapita baru              | Admin/SuperAdmin |
| PUT    | `/api/kapita/{idkapita}`           | Update kapita                   | Admin/SuperAdmin |
| DELETE | `/api/kapita/{idkapita}`           | Hapus kapita                    | Admin/SuperAdmin |

---

## Contoh Lengkap

### 1. GET (Tanpa Login)

```javascript
// Ambil daftar gereja
const headers = generateHeaders(); // data kosong = "{}"
const res = await fetch('https://pendaftarankapitagereja.onrender.com/api/churches', {
  method: 'GET',
  headers: headers,
});
const data = await res.json();
console.log(data);
```

### 2. POST User (Tanpa Login)

```javascript
const body = {
  full_name: 'Budi Santoso',
  email: 'budi@email.com',
  phone: '08123456789',
  birth_date: '1995-08-17',
  address: 'Jl. Merdeka No. 1, Jakarta',
  church_gkode: 'GKY001',
  ukapita: 1,
  notes: 'Pemuda',
};
const headers = generateHeaders(body);
const res = await fetch('https://pendaftarankapitagereja.onrender.com/api/users', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(body),
});
const data = await res.json();
console.log(data);
```

### 3. Login Admin

```javascript
const loginBody = {
  email: 'superadmin@gereja.com',
  password: 'superadmin123',
};
const headers = generateHeaders(loginBody);
const res = await fetch('https://pendaftarankapitagereja.onrender.com/api/admin/login', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(loginBody),
});
const data = await res.json();

if (data.status) {
  const adminId = data.results.aid;
  localStorage.setItem('admin_id', adminId);
  console.log('Login berhasil, admin_id:', adminId);
}
```

### 4. POST Tambah Kapita (Butuh Admin Login)

```javascript
const adminId = localStorage.getItem('admin_id');
const body = { namakapita: 'Kapita Baru' };
const headers = generateHeaders(body, adminId);

const res = await fetch('https://pendaftarankapitagereja.onrender.com/api/kapita', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(body),
});
const data = await res.json();
console.log(data);
```

---

## Field Reference

### User / Registration

| Field         | Tipe   | Keterangan                    |
| ------------- | ------ | ----------------------------- |
| `full_name`   | string | Nama lengkap (min 3, max 100) |
| `email`       | string | Email valid                   |
| `phone`       | string | Nomor HP (min 8, max 20)     |
| `birth_date`  | string | Format: `YYYY-MM-DD`          |
| `address`     | string | Alamat (min 5 karakter)       |
| `church_gkode`| string | Kode gereja (dari GET churches)|
| `ukapita`     | int    | ID kapita (dari GET kapita)   |
| `kapita_id`   | int    | ID kapita (untuk registration)|
| `notes`       | string | Catatan (opsional)            |

### Church

| Field   | Tipe   | Keterangan                  |
| ------- | ------ | --------------------------- |
| `gkode` | string | Kode gereja (auto-generated)|
| `name`  | string | Nama gereja                 |

### Kapita

| Field        | Tipe   | Keterangan                  |
| ------------ | ------ | --------------------------- |
| `idkapita`   | int    | ID kapita (auto-generated)  |
| `namakapita` | string | Nama kapita                 |

### Quota

| Field      | Tipe   | Keterangan                  |
| ---------- | ------ | --------------------------- |
| `kapita_id`| int    | ID kapita                   |
| `kuota`    | int    | Jumlah kuota                |
