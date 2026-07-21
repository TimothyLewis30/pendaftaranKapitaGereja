# Frontend Integration Guide

Panduan integrasi frontend ke Backend Registration App.

---

## Konfigurasi

Semua konfigurasi diambil dari file `.env.local` di root project, bukan dari environment variable.

```python
# src/settings.py
import ast, os

_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")
with open(_env_path) as _f:
    v_env = ast.literal_eval(_f.read().strip().removeprefix("env = "))
```

Struktur `.env.local`:

```python
env = {
    "application": {
        "secret": "GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai",
        "status": "DEVELOPMENT",
        "server": "LOCAL"
    },
    "db": {
        "host": "127.0.0.1",
        "port": 3307,
        "user": "root",
        "password": "",
        "name": "db_ls_metta"
    }
}
```

---

## Base URL

```
http://127.0.0.1:8080
```

---

## Autentikasi (Wajib di Semua Request)

Setiap request harus mengirim 2 header tambahan:

| Header        | Tipe   | Keterangan                                       |
| ------------- | ------ | ------------------------------------------------ |
| `X-Salt`      | string | Timestamp unik per request                       |
| `X-Signature` | string | SHA-256 hash dari kombinasi secret + salt + data |

### Cara Generate Header

**Rumus Signature:**

```
SHA256("APIKAPITAGKYALSUT" + SECRET_KEY + SALT + DATA)
```

| Parameter    | Keterangan                   | Nilai                                        |
| ------------ | ---------------------------- | -------------------------------------------- |
| `SECRET_KEY` | Secret key dari `.env.local` | `v_env["application"]["secret"]`             |
| `SALT`       | Isi header `X-Salt`          | Format: `YYYYMMDD` + microseconds (18 digit) |
| `DATA`       | Request body / query params  | JSON string (POST) atau `"{}"` (GET)         |

### Contoh Implementasi

**JavaScript (Browser):**

```javascript
// Package: crypto-js (https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.2.0/crypto-js.min.js)

function generateHeaders(body = '{}') {
  const secret = 'GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai'; // dari .env.local → application.secret
  const salt = generateSalt();
  const raw = 'APIKAPITAGKYALSUT' + secret + salt + body;
  const signature = CryptoJS.SHA256(raw).toString();

  return {
    'Content-Type': 'application/json',
    'X-Salt': salt,
    'X-Signature': signature,
  };
}

function generateSalt() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  const micro = String(Date.now() % 1000000).padStart(6, '0');
  return `${y}${m}${d}${micro}`;
}
```

**Python:**

```python
import hashlib
import json
from datetime import datetime

def generate_headers(data: dict = None) -> dict:
    secret = "GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai"  # dari .env.local → application.secret
    salt = datetime.now().strftime("%Y%m%d%f")

    if data is None:
        data_str = "{}"
    else:
        data_str = json.dumps(data, sort_keys=True, separators=(",", ":"))

    raw = f"APIKAPITAGKYALSUT{secret}{salt}{data_str}"
    signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    return {
        "Content-Type": "application/json",
        "X-Salt": salt,
        "X-Signature": signature
    }
```

### Contoh Request

**GET Request:**

```javascript
const headers = generateHeaders('{}'); // GET pakai "{}"

fetch('http://127.0.0.1:8080/api/churches', {
  method: 'GET',
  headers: headers,
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**POST Request:**

```javascript
const body = {
  full_name: 'Budi Santoso',
  email: 'budi@email.com',
  phone: '08123456789',
  birth_date: '1995-08-17',
  address: 'Jl. Merdeka No. 1',
  church_id: 1,
  kapita_id: 1,
  notes: 'Saya tertarik dengan pelayanan musik.',
};

const headers = generateHeaders(JSON.stringify(body)); // POST pakai body

fetch('http://127.0.0.1:8080/api/registrations', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(body),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

### Error Autentikasi

| Kode  | Keterangan                                       |
| ----- | ------------------------------------------------ |
| `401` | Header `X-Salt` atau `X-Signature` tidak dikirim |
| `401` | Signature tidak cocok (data tidak sesuai)        |

Response error:

```json
{
  "code": 401,
  "status": false,
  "message": "Unauthorized: Invalid or missing request API key",
  "results": []
}
```

---

## Role-Based Access Control (RBAC)

Semua operasi **CUD** (Create, Update, Delete) pada data **Gereja**, **Kapita**, dan **Admin** memerlukan header tambahan:

| Header       | Tipe   | Keterangan                         |
| ------------ | ------ | ---------------------------------- |
| `X-Admin-ID` | string | ID admin yang sedang login (angka) |

### Daftar Role

| Role         | Keterangan                                                |
| ------------ | --------------------------------------------------------- |
| `SuperAdmin` | Boleh semua operasi: CRUD Gereja, CRUD Kapita, CRUD Admin |
| `Admin`      | Boleh CRUD Gereja dan CRUD Kapita                         |
| `NULL`       | Tidak boleh operasi CUD (hanya bisa login)                |

### Alur Autentikasi Admin

1. Login melalui `POST /api/admin/login` → dapatkan `aid` dari response.
2. Simpan `aid` di client (localStorage / state).
3. Kirim header `X-Admin-ID: {aid}` pada setiap request CUD.
4. Operasi **GET** tetap bisa diakses tanpa `X-Admin-ID`.

### Contoh Header dengan X-Admin-ID

```javascript
function generateHeaders(body = '{}', adminId = null) {
  const secret = 'GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai'; // dari .env.local → application.secret
  const salt = generateSalt();
  const raw = 'APIKAPITAGKYALSUT' + secret + salt + body;
  const signature = CryptoJS.SHA256(raw).toString();

  const headers = {
    'Content-Type': 'application/json',
    'X-Salt': salt,
    'X-Signature': signature,
  };

  if (adminId) {
    headers['X-Admin-ID'] = adminId;
  }

  return headers;
}
```

### Error Role

| Kode  | Keterangan                                       |
| ----- | ------------------------------------------------ |
| `403` | Header `X-Admin-ID` tidak dikirim                |
| `403` | Role NULL (tidak punya akses)                    |
| `403` | Role tidak sesuai (misal: Admin coba CRUD Admin) |

---

## Format Response Standar

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

## Endpoint List

### Gereja

| Method | Endpoint              | Keterangan                | Role Required      |
| ------ | --------------------- | ------------------------- | ------------------ |
| GET    | `/api/churches`       | List semua gereja + kuota | -                  |
| GET    | `/api/churches/{gid}` | Detail gereja + kuota     | -                  |
| POST   | `/api/churches`       | Tambah gereja baru        | Admin / SuperAdmin |
| PUT    | `/api/churches/{gid}` | Update gereja             | Admin / SuperAdmin |
| DELETE | `/api/churches/{gid}` | Hapus gereja              | Admin / SuperAdmin |

### Gereja Kapita Quota

| Method | Endpoint                                       | Keterangan                 | Role Required      |
| ------ | ---------------------------------------------- | -------------------------- | ------------------ |
| GET    | `/api/churches/{gid}/kapita-quota`             | List kuota kapita gereja   | -                  |
| POST   | `/api/churches/{gid}/kapita-quota`             | Set kuota kapita gereja    | Admin / SuperAdmin |
| GET    | `/api/churches/{gid}/kapita-quota/{kapita_id}` | Detail kuota kapita gereja | -                  |
| PUT    | `/api/churches/{gid}/kapita-quota/{kapita_id}` | Update kuota kapita gereja | Admin / SuperAdmin |
| DELETE | `/api/churches/{gid}/kapita-quota/{kapita_id}` | Hapus kuota kapita gereja  | Admin / SuperAdmin |

### Kapita

| Method | Endpoint                 | Keterangan         | Role Required      |
| ------ | ------------------------ | ------------------ | ------------------ |
| GET    | `/api/kapita`            | List semua kapita  | -                  |
| GET    | `/api/kapita/{idkapita}` | Detail kapita      | -                  |
| POST   | `/api/kapita`            | Tambah kapita baru | Admin / SuperAdmin |
| PUT    | `/api/kapita/{idkapita}` | Update kapita      | Admin / SuperAdmin |
| DELETE | `/api/kapita/{idkapita}` | Hapus kapita       | Admin / SuperAdmin |

---

### Registrations

| Method | Endpoint                           | Keterangan          |
| ------ | ---------------------------------- | ------------------- |
| POST   | `/api/registrations`               | Daftar baru         |
| GET    | `/api/registrations/check/{email}` | Cek email terdaftar |
| GET    | `/api/registrations/{id}`          | Detail pendaftaran  |
| PUT    | `/api/registrations/{id}`          | Update pendaftaran  |
| DELETE | `/api/registrations/{id}`          | Hapus pendaftaran   |

---

### Users

| Method | Endpoint           | Keterangan       |
| ------ | ------------------ | ---------------- |
| GET    | `/api/users`       | List semua user  |
| GET    | `/api/users/{uid}` | Detail user      |
| POST   | `/api/users`       | Tambah user baru |
| PUT    | `/api/users/{uid}` | Update user      |
| DELETE | `/api/users/{uid}` | Hapus user       |

---

### Admin

| Method | Endpoint            | Keterangan        | Role Required |
| ------ | ------------------- | ----------------- | ------------- |
| POST   | `/api/admin/login`  | Login admin       | -             |
| GET    | `/api/admins`       | List semua admin  | SuperAdmin    |
| GET    | `/api/admins/{aid}` | Detail admin      | SuperAdmin    |
| POST   | `/api/admins`       | Tambah admin baru | SuperAdmin    |
| PUT    | `/api/admins/{aid}` | Update admin      | SuperAdmin    |
| DELETE | `/api/admins/{aid}` | Hapus admin       | SuperAdmin    |

#### Login Admin

```javascript
const loginBody = {
  email: 'superadmin@gereja.com',
  password: 'superadmin123',
};

const headers = generateHeaders(JSON.stringify(loginBody));

fetch('http://127.0.0.1:8080/api/admin/login', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(loginBody),
})
  .then((res) => res.json())
  .then((data) => {
    // Simpan aid dari response
    const adminId = data.results.aid;
    localStorage.setItem('admin_id', adminId);
  });
```

#### Request dengan X-Admin-ID

```javascript
const adminId = localStorage.getItem('admin_id');
const body = { namakapita: 'Kapita Baru' };
const headers = generateHeaders(JSON.stringify(body), adminId);

fetch('http://127.0.0.1:8080/api/kapita', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(body),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```
