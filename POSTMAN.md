# Panduan Hit API dengan Postman

Panduan lengkap testing API Pendaftaran Kapita Gereja menggunakan Postman.

---

## Base URL

```
https://pendaftarankapitagereja.onrender.com
```

---

## Setup Signature di Postman

Setiap request harus punya header `X-Salt` dan `X-Signature`. Gunakan **Pre-request Script** berikut:

### Pre-request Script (untuk POST/PUT/DELETE dengan body)

```javascript
var body = pm.request.body.raw || '{}';
var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
var salt = '';
for (var i = 0; i < 16; i++) {
  salt += chars.charAt(Math.floor(Math.random() * chars.length));
}
var secret = 'edit this'; // SECRET_KEY dari server
var raw = 'APIKAPITAGKYALSUT' + secret + salt + body;
var signature = CryptoJS.SHA256(raw).toString();

pm.request.headers.add({ key: 'X-Salt', value: salt });
pm.request.headers.add({ key: 'X-Signature', value: signature });
```

### Pre-request Script (untuk GET tanpa body)

```javascript
var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
var salt = '';
for (var i = 0; i < 16; i++) {
  salt += chars.charAt(Math.floor(Math.random() * chars.length));
}
var secret = 'edit this'; // SECRET_KEY dari server
var raw = 'APIKAPITAGKYALSUT' + secret + salt + '{}';
var signature = CryptoJS.SHA256(raw).toString();

pm.request.headers.add({ key: 'X-Salt', value: salt });
pm.request.headers.add({ key: 'X-Signature', value: signature });
```

### Headers Default

| Header         | Value                    |
| -------------- | ------------------------ |
| `Content-Type` | `application/json`       |

---

## Error Autentikasi

```json
{
  "code": 401,
  "status": false,
  "message": "Unauthorized: Invalid or missing request API key",
  "results": []
}
```

**Penyebab:** Signature tidak cocok atau header `X-Salt` / `X-Signature` tidak dikirim.

---

## Role-Based Access Control

| Role         | Akses                                        |
| ------------ | -------------------------------------------- |
| `SuperAdmin` | CRUD semua data                              |
| `Admin`      | CRUD Gereja, Kapita, Quota                   |
| `NULL`       | Tidak bisa CUD (hanya login)                 |

**Alur:**
1. Login → dapatkan `aid`
2. Simpan `aid`
3. Kirim header `X-Admin-ID: {aid}` di setiap request CUD

---

## Format Response

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

### 1. Ping / Health Check

**GET** `/api/ping`

Tidak perlu signature. Endpoint ini untuk keep-alive (hit setiap 10 menit agar server tidak sleep di free tier).

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Server is running.",
  "results": []
}
```

---

### 2. Login Admin

**POST** `/api/admin/login`

Body:
```json
{
  "email": "superadmin@gereja.com",
  "password": "superadmin123"
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Login berhasil.",
  "results": {
    "aid": 1,
    "username": "superadmin",
    "email": "superadmin@gereja.com",
    "role": "SuperAdmin"
  }
}
```

Response Error (401):
```json
{
  "code": 401,
  "status": false,
  "message": "Email atau password salah.",
  "results": []
}
```

---

### 3. Daftar Semua Gereja

**GET** `/api/churches`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Daftar gereja berhasil ditemukan.",
  "results": [
    {
      "id": "GKY001",
      "name": "Gereja Kristus Yesus",
      "total_quota": 80,
      "total_registered": 5,
      "quota_left": 75,
      "kapita": [
        {
          "gkid": 1,
          "gkode": "GKY001",
          "idkapita": 1,
          "kapita_name": "Pemuda",
          "kuota": 50,
          "registered": 3,
          "quota_left": 47
        }
      ]
    }
  ]
}
```

---

### 4. Detail Gereja

**GET** `/api/churches/{gkode}`

Contoh: `/api/churches/GKY001`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Detail gereja berhasil ditemukan.",
  "results": {
    "id": "GKY001",
    "name": "Gereja Kristus Yesus",
    "total_quota": 80,
    "total_registered": 5,
    "quota_left": 75,
    "kapita": [
      {
        "gkid": 1,
        "gkode": "GKY001",
        "idkapita": 1,
        "kapita_name": "Pemuda",
        "kuota": 50,
        "registered": 3,
        "quota_left": 47
      }
    ]
  }
}
```

---

### 5. Tambah Gereja (Admin/SuperAdmin)

**POST** `/api/churches`

Header: `X-Admin-ID`

Body:
```json
{
  "name": "Gereja Baru"
}
```

Response (201):
```json
{
  "code": 201,
  "status": true,
  "message": "Gereja berhasil disimpan.",
  "results": {
    "id": "GER1",
    "name": "Gereja Baru",
    "total_quota": 0,
    "total_registered": 0,
    "quota_left": 0,
    "kapita": []
  }
}
```

---

### 6. Update Gereja (Admin/SuperAdmin)

**PUT** `/api/churches/{gkode}`

Header: `X-Admin-ID`

Body:
```json
{
  "name": "Gereja Updated"
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Gereja berhasil diupdate.",
  "results": {
    "id": "GKY001",
    "name": "Gereja Updated",
    "total_quota": 80,
    "total_registered": 5,
    "quota_left": 75,
    "kapita": []
  }
}
```

---

### 7. Hapus Gereja (Admin/SuperAdmin)

**DELETE** `/api/churches/{gkode}`

Header: `X-Admin-ID`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Gereja berhasil dihapus.",
  "results": []
}
```

---

### 8. Daftar Semua Kapita

**GET** `/api/kapita`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Daftar kapita berhasil ditemukan.",
  "results": [
    {
      "idkapita": 1,
      "namakapita": "Pemuda"
    },
    {
      "idkapita": 2,
      "namakapita": "Pemudi"
    }
  ]
}
```

---

### 9. Detail Kapita

**GET** `/api/kapita/{idkapita}`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Detail kapita berhasil ditemukan.",
  "results": {
    "idkapita": 1,
    "namakapita": "Pemuda"
  }
}
```

---

### 10. Tambah Kapita (Admin/SuperAdmin)

**POST** `/api/kapita`

Header: `X-Admin-ID`

Body:
```json
{
  "namakapita": "Anak Sekolah Minggu"
}
```

Response (201):
```json
{
  "code": 201,
  "status": true,
  "message": "Kapita berhasil disimpan.",
  "results": {
    "idkapita": 3,
    "namakapita": "Anak Sekolah Minggu"
  }
}
```

---

### 11. Update Kapita (Admin/SuperAdmin)

**PUT** `/api/kapita/{idkapita}`

Header: `X-Admin-ID`

Body:
```json
{
  "namakapita": "Pemuda Updated"
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Kapita berhasil diupdate.",
  "results": {
    "idkapita": 1,
    "namakapita": "Pemuda Updated"
  }
}
```

---

### 12. Hapus Kapita (Admin/SuperAdmin)

**DELETE** `/api/kapita/{idkapita}`

Header: `X-Admin-ID`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Kapita berhasil dihapus.",
  "results": []
}
```

---

### 13. Set Kuota Kapita Gereja (Admin/SuperAdmin)

**POST** `/api/churches/{gkode}/kapita-quota`

Header: `X-Admin-ID`

Body:
```json
{
  "kapita_id": 1,
  "kuota": 50
}
```

Response (201):
```json
{
  "code": 201,
  "status": true,
  "message": "Kuota kapita gereja berhasil disimpan.",
  "results": {
    "gkid": 1,
    "gkode": "GKY001",
    "idkapita": 1,
    "kapita_name": "Pemuda",
    "kuota": 50,
    "registered": 0,
    "quota_left": 50
  }
}
```

---

### 14. Daftar Kuota Kapita Gereja

**GET** `/api/churches/{gkode}/kapita-quota`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Daftar kuota kapita gereja berhasil ditemukan.",
  "results": [
    {
      "gkid": 1,
      "gkode": "GKY001",
      "idkapita": 1,
      "kapita_name": "Pemuda",
      "kuota": 50,
      "registered": 3,
      "quota_left": 47
    }
  ]
}
```

---

### 15. Detail Kuota Kapita Gereja

**GET** `/api/churches/{gkode}/kapita-quota/{idkapita}`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Detail kuota kapita gereja berhasil ditemukan.",
  "results": {
    "gkid": 1,
    "gkode": "GKY001",
    "idkapita": 1,
    "kapita_name": "Pemuda",
    "kuota": 50,
    "registered": 3,
    "quota_left": 47
  }
}
```

---

### 16. Update Kuota Kapita Gereja (Admin/SuperAdmin)

**PUT** `/api/churches/{gkode}/kapita-quota/{idkapita}`

Header: `X-Admin-ID`

Body:
```json
{
  "kapita_id": 1,
  "kuota": 100
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Kuota kapita gereja berhasil diupdate.",
  "results": {
    "gkid": 1,
    "gkode": "GKY001",
    "idkapita": 1,
    "kapita_name": "Pemuda",
    "kuota": 100,
    "registered": 3,
    "quota_left": 97
  }
}
```

---

### 17. Hapus Kuota Kapita Gereja (Admin/SuperAdmin)

**DELETE** `/api/churches/{gkode}/kapita-quota/{idkapita}`

Header: `X-Admin-ID`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Kuota kapita gereja berhasil dihapus.",
  "results": []
}
```

---

### 18. Buat Pendaftaran Baru

**POST** `/api/registrations`

Body:
```json
{
  "full_name": "Budi Santoso",
  "email": "budi@email.com",
  "phone": "08123456789",
  "church_gkode": "GKY001",
  "kapita_id_sesi_1": 1,
  "kapita_id_sesi_2": 2
}
```

Response (201):
```json
{
  "code": 201,
  "status": true,
  "message": "Pendaftaran berhasil disimpan.",
  "results": {
    "id": 1,
    "full_name": "Budi Santoso",
    "email": "budi@email.com",
    "phone": "08123456789",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "kapita_id_sesi_1": 1,
    "kapita_name_sesi_1": "Bapak",
    "kapita_id_sesi_2": 2,
    "kapita_name_sesi_2": "Ibu",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 19. Cek Email Terdaftar

**GET** `/api/registrations/check/{email}`

Contoh: `/api/registrations/check/budi@email.com`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Pengecekan email berhasil.",
  "results": {
    "email": "budi@email.com",
    "is_registered": true,
    "message": "Email 'budi@email.com' sudah terdaftar atas nama Budi Santoso."
  }
}
```

---

### 20. Detail Pendaftaran

**GET** `/api/registrations/{id}`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Detail pendaftaran berhasil ditemukan.",
  "results": {
    "id": 1,
    "full_name": "Budi Santoso",
    "email": "budi@email.com",
    "phone": "08123456789",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "kapita_id_sesi_1": 1,
    "kapita_name_sesi_1": "Bapak",
    "kapita_id_sesi_2": 2,
    "kapita_name_sesi_2": "Ibu",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 21. Update Pendaftaran

**PUT** `/api/registrations/{id}`

Body:
```json
{
  "full_name": "Budi Santoso Updated",
  "email": "budi.updated@email.com",
  "phone": "08123456789",
  "church_gkode": "GKY001",
  "kapita_id_sesi_1": 1,
  "kapita_id_sesi_2": 3
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Pendaftaran berhasil diupdate.",
  "results": {
    "id": 1,
    "full_name": "Budi Santoso Updated",
    "email": "budi.updated@email.com",
    "phone": "08123456789",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "kapita_id_sesi_1": 1,
    "kapita_name_sesi_1": "Bapak",
    "kapita_id_sesi_2": 3,
    "kapita_name_sesi_2": "Pemuda",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 22. Hapus Pendaftaran

**DELETE** `/api/registrations/{id}`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Pendaftaran berhasil dihapus.",
  "results": []
}
```

---

### 23. Daftar Semua Admin (SuperAdmin)

**GET** `/api/admins`

Header: `X-Admin-ID`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Daftar admin berhasil ditemukan.",
  "results": [
    {
      "aid": 1,
      "username": "superadmin",
      "email": "superadmin@gereja.com",
      "role": "SuperAdmin"
    }
  ]
}
```

---

### 24. Tambah Admin Baru (SuperAdmin)

**POST** `/api/admins`

Header: `X-Admin-ID`

Body:
```json
{
  "username": "admin01",
  "email": "admin01@gereja.com",
  "password": "password123",
  "role": "Admin"
}
```

Role: `"Admin"`, `"SuperAdmin"`, atau `"NULL"` (tidak diisi = NULL)

Response (201):
```json
{
  "code": 201,
  "status": true,
  "message": "Admin berhasil disimpan.",
  "results": {
    "aid": 2,
    "username": "admin01",
    "email": "admin01@gereja.com",
    "role": "Admin"
  }
}
```

---

### 25. Detail Admin (SuperAdmin)

**GET** `/api/admins/{aid}`

Header: `X-Admin-ID`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Detail admin berhasil ditemukan.",
  "results": {
    "aid": 2,
    "username": "admin01",
    "email": "admin01@gereja.com",
    "role": "Admin"
  }
}
```

---

### 26. Update Admin (SuperAdmin)

**PUT** `/api/admins/{aid}`

Header: `X-Admin-ID`

Body:
```json
{
  "username": "admin01_updated",
  "email": "admin01_updated@gereja.com",
  "password": "newpassword123",
  "role": "SuperAdmin"
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Admin berhasil diupdate.",
  "results": {
    "aid": 2,
    "username": "admin01_updated",
    "email": "admin01_updated@gereja.com",
    "role": "SuperAdmin"
  }
}
```

---

### 27. Hapus Admin (SuperAdmin)

**DELETE** `/api/admins/{aid}`

Header: `X-Admin-ID`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Admin berhasil dihapus.",
  "results": []
}
```

---

### 28. Cetak / Export Excel Data Peserta

**GET** / **POST** `/api/cetak-excel`

Metode 1: **GET** dengan Query Parameter:
- `pilihan`: `1`, `2`, `3`, atau `4`
  - `1`: Semua data peserta order by ID Peserta
  - `2`: Data peserta order by Gereja
  - `3`: Data peserta order by Kapita
  - `4`: Data peserta pada Sesi 1 dan Sesi 2
- `sesi_1` (opsional): Filter ID Kapita Sesi 1
- `sesi_2` (opsional): Filter ID Kapita Sesi 2
- `gkode` (opsional): Filter Kode Gereja

Contoh GET:
```
GET /api/cetak-excel?pilihan=1
GET /api/cetak-excel?pilihan=2
GET /api/cetak-excel?pilihan=3
GET /api/cetak-excel?pilihan=4&sesi_1=1&sesi_2=2
```

Metode 2: **POST** dengan Body JSON:
```json
{
  "pilihan": 1,
  "sesi_1": 1,
  "sesi_2": 2,
  "gkode": "GKY001"
}
```

Response:
File biner Excel `.xlsx` (`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`) dengan header `Content-Disposition: attachment; filename=Data_Peserta_...xlsx`.

