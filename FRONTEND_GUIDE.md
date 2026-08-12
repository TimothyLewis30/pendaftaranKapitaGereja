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

| Header        | Tipe   | Keterangan                            |
| ------------- | ------ | ------------------------------------- |
| `X-Salt`      | string | Salt unik per request (16+ karakter)  |
| `X-Signature` | string | SHA-256 hash (64 karakter hex)        |
| `X-Admin-ID`  | string | ID admin (hanya untuk endpoint admin) |

### Rumus Signature

```
SHA256("APIKAPITAGKYALSUT" + SECRET_KEY + SALT + DATA)
```

| Parameter    | Keterangan                                       |
| ------------ | ------------------------------------------------ |
| `SECRET_KEY` | Secret key dari server                           |
| `SALT`       | Nilai header `X-Salt`                            |
| `DATA`       | Request body (JSON string) atau `"{}"` untuk GET |

### Cara Generate Salt

```javascript
// Random string 16 karakter
function generateSalt() {
  const chars =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
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

| Kode  | Penyebab                                  |
| ----- | ----------------------------------------- |
| `401` | Header `X-Salt` atau `X-Signature` kosong |
| `401` | Signature tidak cocok (salah secret/data) |

---

## Role-Based Access Control (RBAC)

### Daftar Role

| Role         | Akses                                            |
| ------------ | ------------------------------------------------ |
| `SuperAdmin` | CRUD Gereja, CRUD Kapita, CRUD Admin, CRUD Quota |
| `Admin`      | CRUD Gereja, CRUD Kapita, CRUD Quota             |
| `NULL`       | Tidak bisa CUD (hanya login)                     |

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
  "results": []
}
```

---

## Daftar Endpoint

### PUBLIK (Tidak Butuh Login)

#### Ping / Health Check

| Method | Endpoint    | Keterangan                             |
| ------ | ----------- | -------------------------------------- |
| GET    | `/api/ping` | Health check server (untuk keep-alive) |

#### Gereja

| Method | Endpoint                | Keterangan                |
| ------ | ----------------------- | ------------------------- |
| GET    | `/api/churches`         | List semua gereja + kuota |
| GET    | `/api/churches/{gkode}` | Detail gereja + kuota     |

#### Kapita

| Method | Endpoint                 | Keterangan        |
| ------ | ------------------------ | ----------------- |
| GET    | `/api/kapita`            | List semua kapita |
| GET    | `/api/kapita/{idkapita}` | Detail kapita     |

#### Registrasi (Pendaftaran Publik)

| Method | Endpoint                  | Keterangan             |
| ------ | ------------------------- | ---------------------- |
| POST   | `/api/registrations`      | Buat pendaftaran baru  |
| GET    | `/api/registrations`      | List semua pendaftaran |
| GET    | `/api/registrations/{id}` | Detail pendaftaran     |
| PUT    | `/api/registrations/{id}` | Update pendaftaran     |
| DELETE | `/api/registrations/{id}` | Hapus pendaftaran      |

#### Users (Pendaftaran Peserta)

| Method | Endpoint           | Keterangan                  |
| ------ | ------------------ | --------------------------- |
| POST   | `/api/users`       | Buat user baru dari peserta |
| GET    | `/api/users`       | List semua user             |
| GET    | `/api/users/{uid}` | Detail user                 |
| PUT    | `/api/users/{uid}` | Update user                 |
| DELETE | `/api/users/{uid}` | Hapus user                  |

#### Participants by Church

| Method | Endpoint                           | Keterangan                           |
| ------ | ---------------------------------- | ------------------------------------ |
| GET    | `/api/participants`                | List peserta berdasarkan gereja      |
|        | `/api/participants?gereja={gkode}` | Isi query param `gereja` dengan kode |

#### Cetak Excel

| Method     | Endpoint           | Keterangan                               |
| ---------- | ------------------ | ---------------------------------------- |
| POST / GET | `/api/cetak-excel` | Cetak / Download file Excel data peserta |

---

### ADMIN (Butuh Login + X-Admin-ID)

#### Auth

| Method | Endpoint           | Keterangan  | Role |
| ------ | ------------------ | ----------- | ---- |
| POST   | `/api/admin/login` | Login admin | -    |

#### Admin Management (Hanya SuperAdmin)

| Method | Endpoint            | Keterangan        | Role       |
| ------ | ------------------- | ----------------- | ---------- |
| GET    | `/api/admins`       | List semua admin  | SuperAdmin |
| GET    | `/api/admins/{aid}` | Detail admin      | SuperAdmin |
| POST   | `/api/admins`       | Tambah admin baru | SuperAdmin |
| PUT    | `/api/admins/{aid}` | Update admin      | SuperAdmin |
| DELETE | `/api/admins/{aid}` | Hapus admin       | SuperAdmin |

#### Gereja (Admin / SuperAdmin)

| Method | Endpoint                | Keterangan         | Role             |
| ------ | ----------------------- | ------------------ | ---------------- |
| POST   | `/api/churches`         | Tambah gereja baru | Admin/SuperAdmin |
| PUT    | `/api/churches/{gkode}` | Update gereja      | Admin/SuperAdmin |
| DELETE | `/api/churches/{gkode}` | Hapus gereja       | Admin/SuperAdmin |

#### Quota Kapita per Gereja (Admin / SuperAdmin)

| Method | Endpoint                                        | Keterangan     | Role             |
| ------ | ----------------------------------------------- | -------------- | ---------------- |
| GET    | `/api/churches/{gkode}/kapita-quota`            | List kuota     | -                |
| GET    | `/api/churches/{gkode}/kapita-quota/{idkapita}` | Detail kuota   | -                |
| POST   | `/api/churches/{gkode}/kapita-quota`            | Set kuota baru | Admin/SuperAdmin |
| PUT    | `/api/churches/{gkode}/kapita-quota/{idkapita}` | Update kuota   | Admin/SuperAdmin |
| DELETE | `/api/churches/{gkode}/kapita-quota/{idkapita}` | Hapus kuota    | Admin/SuperAdmin |

#### Kapita (Admin / SuperAdmin)

| Method | Endpoint                 | Keterangan         | Role             |
| ------ | ------------------------ | ------------------ | ---------------- |
| POST   | `/api/kapita`            | Tambah kapita baru | Admin/SuperAdmin |
| PUT    | `/api/kapita/{idkapita}` | Update kapita      | Admin/SuperAdmin |
| DELETE | `/api/kapita/{idkapita}` | Hapus kapita       | Admin/SuperAdmin |

---

## Frontend Workflows

1. Ambil daftar gereja (`GET /api/churches`).
2. Ambil daftar kapita (`GET /api/kapita`).
3. Tampilkan kuota per gereja dan detail kapita.
4. Ketika user memilih gereja, ambil peserta dengan `GET /api/participants?gereja={gkode}`.
5. Untuk membuat user baru, gunakan `POST /api/users`.
6. Untuk pendaftaran umum, gunakan `POST /api/registrations`.
7. Untuk admin, login dulu dan sertakan `X-Admin-ID` pada request CUD.

---

## Frontend Page Suggestions

- Dashboard `Gereja` dengan kuota kapita
- Daftar `Kapita`
- Detail `Gereja` + kuota `Kapita`
- Daftar `Peserta` per Gereja
- Form `Buat User` dari participant
- Form `Pendaftaran` publik
- Halaman `Admin Login` dan `Manage Kapita / Gereja / Quota`

---

## Payload Schema

### Registration Payload

| Field              | Tipe   | Keterangan       |
| ------------------ | ------ | ---------------- |
| `full_name`        | string | Nama peserta     |
| `email`            | string | Email peserta    |
| `phone`            | string | Nomor telepon    |
| `church_gkode`     | string | Kode gereja      |
| `kapita_id_sesi_1` | int    | ID kapita sesi 1 |
| `kapita_id_sesi_2` | int    | ID kapita sesi 2 |

### User Payload

| Field            | Tipe | Keterangan                          |
| ---------------- | ---- | ----------------------------------- |
| `uparticipant`   | int  | ID peserta dari tabel `participant` |
| `ukapita_sesi_1` | int  | ID kapita sesi 1                    |
| `ukapita_sesi_2` | int  | ID kapita sesi 2                    |

### Church Quota Payload

| Field          | Tipe | Keterangan   |
| -------------- | ---- | ------------ |
| `kapita_id`    | int  | ID kapita    |
| `kuota_sesi_1` | int  | Kuota sesi 1 |
| `kuota_sesi_2` | int  | Kuota sesi 2 |

### Kapita Payload

| Field        | Tipe   | Keterangan  |
| ------------ | ------ | ----------- |
| `namakapita` | string | Nama kapita |

### Excel Payload

| Field     | Tipe   | Keterangan                                             |
| --------- | ------ | ------------------------------------------------------ |
| `pilihan` | int    | 1=Semua, 2=Per Gereja, 3=Per Kapita, 4=Sesi 1 & Sesi 2 |
| `sesi_1`  | int    | Opsional ID kapita sesi 1                              |
| `sesi_2`  | int    | Opsional ID kapita sesi 2                              |
| `gkode`   | string | Opsional kode gereja                                   |

---

## Response Shape

Semua response mengikuti format:

```json
{
  "code": 200,
  "status": true,
  "message": "Pesan informasi",
  "results": []
}
```

---

## Example Requests

### GET Daftar Gereja

```javascript
const headers = generateHeaders();
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/churches',
  {
    method: 'GET',
    headers,
  },
);
const data = await res.json();
console.log(data);
```

### GET Peserta Berdasarkan Gereja

```javascript
const headers = generateHeaders();
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/participants?gereja=GKY001',
  { method: 'GET', headers },
);
const data = await res.json();
console.log(data);
```

### POST Buat User

```javascript
const body = {
  uparticipant: 1,
  ukapita_sesi_1: 1,
  ukapita_sesi_2: 2,
};
const headers = generateHeaders(body);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/users',
  {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

### POST Registrasi Publik

```javascript
const body = {
  full_name: 'Budi Santoso',
  email: 'budi@email.com',
  phone: '08123456789',
  church_gkode: 'GKY001',
  kapita_id_sesi_1: 1,
  kapita_id_sesi_2: 2,
};
const headers = generateHeaders(body);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/registrations',
  {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

### POST Admin Login

```javascript
const body = {
  email: 'superadmin@gereja.com',
  password: 'superadmin123',
};
const headers = generateHeaders(body);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/admin/login',
  {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
if (data.status) {
  localStorage.setItem('admin_id', data.results.aid);
}
```

### POST Buat Kapita (Admin)

```javascript
const adminId = localStorage.getItem('admin_id');
const body = { namakapita: 'Kapita Baru' };
const headers = generateHeaders(body, adminId);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/kapita',
  {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

### POST Set Kuota Kapita per Gereja (Admin)

```javascript
const adminId = localStorage.getItem('admin_id');
const body = {
  kapita_id: 1,
  kuota_sesi_1: 50,
  kuota_sesi_2: 50,
};
const headers = generateHeaders(body, adminId);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/churches/GKY001/kapita-quota',
  {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

### POST Cetak Excel

```javascript
const body = { pilihan: 3, gkode: 'GKY001' };
const headers = generateHeaders(body);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/cetak-excel',
  {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  },
);
const blob = await res.blob();
const url = URL.createObjectURL(blob);
const link = document.createElement('a');
link.href = url;
link.download = 'peserta.xlsx';
link.click();
```

---

## Catatan Penting

- Semua request harus mengirim `X-Signature` dan `X-Salt`.
- `X-Admin-ID` hanya diperlukan untuk endpoint admin.
- Kuota kapita dicek per gereja, bukan global.
- `POST /api/users` membuat user baru dari participant dan mengurangi kuota efektif gereja-kapita.
- `POST /api/registrations` membuat pendaftaran publik.

---

## Output untuk AI Frontend

Gunakan dokumen ini sebagai spesifikasi langsung untuk membuat UI:

- daftar gereja + kuota
- detail gereja + quota per kapita
- daftar peserta per gereja
- form registrasi user
- form registrasi publik
- admin login + manajemen quota
- export Excel

### 1. GET (Tanpa Login)

```javascript
// Ambil daftar gereja
const headers = generateHeaders(); // data kosong = "{}"
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/churches',
  {
    method: 'GET',
    headers: headers,
  },
);
const data = await res.json();
console.log(data);
```

### 2. GET Participants by Church

```javascript
const params = new URLSearchParams({ gereja: 'GKY001' });
const headers = generateHeaders();
const res = await fetch(
  `https://pendaftarankapitagereja.onrender.com/api/participants?${params.toString()}`,
  {
    method: 'GET',
    headers: headers,
  },
);
const data = await res.json();
console.log(data);
```

### 3. POST User (Registrasi Peserta via Participant)

```javascript
const body = {
  uparticipant: 1,
  ukapita_sesi_1: 1,
  ukapita_sesi_2: 2,
};
const headers = generateHeaders(body);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/users',
  {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

### 4. POST Registrasi (Tanpa Login)

```javascript
const body = {
  full_name: 'Budi Santoso',
  email: 'budi@email.com',
  phone: '08123456789',
  church_gkode: 'GKY001',
  kapita_id_sesi_1: 1,
  kapita_id_sesi_2: 2,
};
const headers = generateHeaders(body);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/registrations',
  {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

### 5. Login Admin

```javascript
const loginBody = {
  email: 'superadmin@gereja.com',
  password: 'superadmin123',
};
const headers = generateHeaders(loginBody);
const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/admin/login',
  {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(loginBody),
  },
);
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

const res = await fetch(
  'https://pendaftarankapitagereja.onrender.com/api/kapita',
  {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(body),
  },
);
const data = await res.json();
console.log(data);
```

---

## Field Reference

### Registration

| Field              | Tipe   | Keterangan                         |
| ------------------ | ------ | ---------------------------------- |
| `full_name`        | string | Nama lengkap (min 3, max 100)      |
| `email`            | string | Email valid                        |
| `phone`            | string | Nomor HP (min 8, max 20)           |
| `church_gkode`     | string | Kode gereja (dari GET churches)    |
| `kapita_id_sesi_1` | int    | ID kapita sesi 1 (dari GET kapita) |
| `kapita_id_sesi_2` | int    | ID kapita sesi 2 (dari GET kapita) |

### User Create

| Field            | Tipe | Keterangan                          |
| ---------------- | ---- | ----------------------------------- |
| `uparticipant`   | int  | ID peserta dari tabel `participant` |
| `ukapita_sesi_1` | int  | ID kapita sesi 1 (dari GET kapita)  |
| `ukapita_sesi_2` | int  | ID kapita sesi 2 (dari GET kapita)  |

### Church

| Field   | Tipe   | Keterangan                   |
| ------- | ------ | ---------------------------- |
| `gkode` | string | Kode gereja (auto-generated) |
| `name`  | string | Nama gereja                  |

### Kapita

| Field        | Tipe   | Keterangan                 |
| ------------ | ------ | -------------------------- |
| `idkapita`   | int    | ID kapita (auto-generated) |
| `namakapita` | string | Nama kapita                |

### Quota

| Field       | Tipe | Keterangan   |
| ----------- | ---- | ------------ |
| `kapita_id` | int  | ID kapita    |
| `kuota`     | int  | Jumlah kuota |

### Cetak Excel Request

| Field     | Tipe   | Keterangan                                                              |
| --------- | ------ | ----------------------------------------------------------------------- |
| `pilihan` | int    | **Wajib**. 1 (by ID), 2 (by Gereja), 3 (by Kapita), 4 (Sesi 1 & Sesi 2) |
| `sesi_1`  | int    | Opsional. Filter ID kapita sesi 1                                       |
| `sesi_2`  | int    | Opsional. Filter ID kapita sesi 2                                       |
| `gkode`   | string | Opsional. Filter kode gereja                                            |

---

### 5. Download Excel Data Peserta (Frontend JavaScript)

```javascript
// Function untuk men-download file Excel data peserta
async function downloadExcelPeserta(pilihan = 1) {
  const body = { pilihan: pilihan };
  const headers = generateHeaders(body); // Menghasilkan X-Salt dan X-Signature

  try {
    const res = await fetch(
      'https://pendaftarankapitagereja.onrender.com/api/cetak-excel',
      {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(body),
      },
    );

    if (!res.ok) {
      const errorJson = await res.json();
      console.error('Gagal cetak excel:', errorJson);
      alert(errorJson.message || 'Gagal mendownload file Excel.');
      return;
    }

    // Ambil binary blob dan trigger download browser
    const blob = await res.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `Data_Peserta_Pilihan_${pilihan}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  } catch (err) {
    console.error('Error saat download excel:', err);
  }
}

// Contoh pemanggilan:
// downloadExcelPeserta(1); // 1. Order by ID
// downloadExcelPeserta(2); // 2. Order by Gereja
// downloadExcelPeserta(3); // 3. Order by Kapita
// downloadExcelPeserta(4); // 4. Sesi 1 & Sesi 2
```
