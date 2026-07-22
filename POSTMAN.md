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

### 1. Login Admin

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

### 2. Daftar Semua Gereja

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

### 3. Detail Gereja

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

### 4. Tambah Gereja (Admin/SuperAdmin)

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

### 5. Update Gereja (Admin/SuperAdmin)

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

### 6. Hapus Gereja (Admin/SuperAdmin)

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

### 7. Daftar Semua Kapita

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

### 8. Detail Kapita

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

### 9. Tambah Kapita (Admin/SuperAdmin)

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

### 10. Update Kapita (Admin/SuperAdmin)

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

### 11. Hapus Kapita (Admin/SuperAdmin)

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

### 12. Set Kuota Kapita Gereja (Admin/SuperAdmin)

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

### 13. Daftar Kuota Kapita Gereja

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

### 14. Detail Kuota Kapita Gereja

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

### 15. Update Kuota Kapita Gereja (Admin/SuperAdmin)

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

### 16. Hapus Kuota Kapita Gereja (Admin/SuperAdmin)

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

### 17. Buat Pendaftaran Baru

**POST** `/api/registrations`

Body:
```json
{
  "full_name": "Budi Santoso",
  "email": "budi@email.com",
  "phone": "08123456789",
  "birth_date": "1995-08-17",
  "address": "Jl. Merdeka No. 1, Jakarta",
  "church_gkode": "GKY001",
  "kapita_id": 1,
  "notes": "Tertarik pelayanan musik"
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
    "birth_date": "1995-08-17",
    "address": "Jl. Merdeka No. 1, Jakarta",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "kapita_id": 1,
    "kapita_name": "Pemuda",
    "notes": "Tertarik pelayanan musik",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 18. Cek Email Terdaftar

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

### 19. Detail Pendaftaran

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
    "birth_date": "1995-08-17",
    "address": "Jl. Merdeka No. 1, Jakarta",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "kapita_id": 1,
    "kapita_name": "Pemuda",
    "notes": "Tertarik pelayanan musik",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 20. Update Pendaftaran

**PUT** `/api/registrations/{id}`

Body:
```json
{
  "full_name": "Budi Santoso Updated",
  "email": "budi.updated@email.com",
  "phone": "08123456789",
  "birth_date": "1995-08-17",
  "address": "Jl. Baru No. 2, Jakarta",
  "church_gkode": "GKY001",
  "kapita_id": 1,
  "notes": "Update catatan"
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
    "birth_date": "1995-08-17",
    "address": "Jl. Baru No. 2, Jakarta",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "kapita_id": 1,
    "kapita_name": "Pemuda",
    "notes": "Update catatan",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 21. Hapus Pendaftaran

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

### 22. Tambah User Baru

**POST** `/api/users`

Body:
```json
{
  "full_name": "Budi Santoso",
  "email": "budi@email.com",
  "phone": "08123456789",
  "birth_date": "1995-08-17",
  "address": "Jl. Merdeka No. 1, Jakarta",
  "church_gkode": "GKY001",
  "ukapita": 1,
  "notes": "Pemuda"
}
```

Response (201):
```json
{
  "code": 201,
  "status": true,
  "message": "User berhasil disimpan.",
  "results": {
    "uid": 1,
    "full_name": "Budi Santoso",
    "email": "budi@email.com",
    "phone": "08123456789",
    "birth_date": "1995-08-17",
    "address": "Jl. Merdeka No. 1, Jakarta",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "ukapita": 1,
    "kapita_name": "Pemuda",
    "notes": "Pemuda",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 23. Daftar Semua User

**GET** `/api/users`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Daftar user berhasil ditemukan.",
  "results": [
    {
      "uid": 1,
      "full_name": "Budi Santoso",
      "email": "budi@email.com",
      "phone": "08123456789",
      "birth_date": "1995-08-17",
      "address": "Jl. Merdeka No. 1, Jakarta",
      "church_gkode": "GKY001",
      "church_name": "Gereja Kristus Yesus",
      "ukapita": 1,
      "kapita_name": "Pemuda",
      "notes": "Pemuda",
      "registered_at": "2026-07-22 12:00:00"
    }
  ]
}
```

---

### 24. Detail User

**GET** `/api/users/{uid}`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "Detail user berhasil ditemukan.",
  "results": {
    "uid": 1,
    "full_name": "Budi Santoso",
    "email": "budi@email.com",
    "phone": "08123456789",
    "birth_date": "1995-08-17",
    "address": "Jl. Merdeka No. 1, Jakarta",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "ukapita": 1,
    "kapita_name": "Pemuda",
    "notes": "Pemuda",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 25. Update User

**PUT** `/api/users/{uid}`

Body:
```json
{
  "full_name": "Budi Santoso Updated",
  "email": "budi.updated@email.com",
  "phone": "08123456789",
  "birth_date": "1995-08-17",
  "address": "Jl. Baru No. 2, Jakarta",
  "church_gkode": "GKY001",
  "ukapita": 1,
  "notes": "Updated"
}
```

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "User berhasil diupdate.",
  "results": {
    "uid": 1,
    "full_name": "Budi Santoso Updated",
    "email": "budi.updated@email.com",
    "phone": "08123456789",
    "birth_date": "1995-08-17",
    "address": "Jl. Baru No. 2, Jakarta",
    "church_gkode": "GKY001",
    "church_name": "Gereja Kristus Yesus",
    "ukapita": 1,
    "kapita_name": "Pemuda",
    "notes": "Updated",
    "registered_at": "2026-07-22 12:00:00"
  }
}
```

---

### 26. Hapus User

**DELETE** `/api/users/{uid}`

Response (200):
```json
{
  "code": 200,
  "status": true,
  "message": "User berhasil dihapus.",
  "results": []
}
```

---

### 27. Daftar Semua Admin (SuperAdmin)

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

### 28. Tambah Admin Baru (SuperAdmin)

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

### 29. Detail Admin (SuperAdmin)

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

### 30. Update Admin (SuperAdmin)

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

### 31. Hapus Admin (SuperAdmin)

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
