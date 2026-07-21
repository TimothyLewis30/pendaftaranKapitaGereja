# Panduan Hit API Menggunakan Postman

Dokumen ini berisi daftar endpoint API beserta konfigurasi dan payload contoh untuk diuji menggunakan Postman.

## Konfigurasi

Semua konfigurasi (SECRET_KEY, database, dll) diambil dari file `.env.local` di root project.

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

## Informasi Base URL

- **Base URL**: `http://127.0.0.1:8080`
- **Headers Default**:
  - `Content-Type: application/json`

---

## Autentikasi (Validasi Signature)

Semua endpoint membutuhkan 2 header tambahan untuk autentikasi:

| Header        | Keterangan             | Format                                                 |
| ------------- | ---------------------- | ------------------------------------------------------ |
| `X-Salt`      | Timestamp unik         | `YYYYMMDD` + microseconds (contoh: `2026071912345678`) |
| `X-Signature` | Signature hash SHA-256 | Hex string 64 karakter                                 |

### Cara Generate Signature

Rumus: `SHA256("APIKAPITAGKYALSUT" + SECRET_KEY + SALT + DATA)`

- **SECRET_KEY**: dari `.env.local` → `v_env["application"]["secret"]`
- **SALT**: isi header `X-Salt`
- **DATA**: request body (JSON) untuk POST, atau query params untuk GET

### Contoh Generate di Postman (Pre-request Script)

```javascript
// Untuk POST dengan JSON body
var body = pm.request.body.raw;
var salt = new Date()
  .toISOString()
  .replace(/[-T:\.Z]/g, '')
  .substring(0, 18);
var secret = 'GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai'; // dari .env.local → application.secret
var raw = 'APIKAPITAGKYALSUT' + secret + salt + body;
var signature = CryptoJS.SHA256(raw).toString();

pm.request.headers.add({ key: 'X-Salt', value: salt });
pm.request.headers.add({ key: 'X-Signature', value: signature });
```

```javascript
// Untuk GET (tanpa body, data = "{}")
var salt = new Date()
  .toISOString()
  .replace(/[-T:\.Z]/g, '')
  .substring(0, 18);
var secret = 'GANTI DENGAN SECRETMU //Ganti dengan secret key yang sesuai'; // dari .env.local → application.secret
var raw = 'APIKAPITAGKYALSUT' + secret + salt + '{}';
var signature = CryptoJS.SHA256(raw).toString();

pm.request.headers.add({ key: 'X-Salt', value: salt });
pm.request.headers.add({ key: 'X-Signature', value: signature });
```

### Response Error Autentikasi

- **401 Unauthorized** — Signature tidak valid atau header tidak dikirim:
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

Setiap operasi **CUD** (Create, Update, Delete) pada data **Gereja**, **Kapita**, dan **Admin** memerlukan header tambahan untuk verifikasi role:

| Header       | Keterangan                 | Contoh |
| ------------ | -------------------------- | ------ |
| `X-Admin-ID` | ID admin yang sedang login | `1`    |

### Daftar Role

| Role         | Keterangan                                                          |
| ------------ | ------------------------------------------------------------------- |
| `SuperAdmin` | Boleh melakukan semua operasi: CRUD Gereja, CRUD Kapita, CRUD Admin |
| `Admin`      | Boleh melakukan CRUD Gereja dan CRUD Kapita                         |
| `NULL`       | Tidak boleh melakukan operasi CUD apa pun (hanya bisa login)        |

### Alur Kerja

1. **Login** terlebih dahulu melalui `POST /api/admin/login` untuk mendapatkan `aid` (ID admin).
2. **Simpan `aid`** dan gunakan sebagai nilai header `X-Admin-ID` pada setiap request CUD.
3. **Operasi GET** (Read) pada Gereja, Kapita, dan User tetap bisa diakses tanpa header `X-Admin-ID`.

### Error Role-Based

- **403 Forbidden** — Header `X-Admin-ID` tidak dikirim:

  ```json
  {
    "code": 403,
    "status": false,
    "message": "Forbidden: Header X-Admin-ID diperlukan.",
    "results": []
  }
  ```

- **403 Forbidden** — Role NULL (tidak punya akses):

  ```json
  {
    "code": 403,
    "status": false,
    "message": "Forbidden: Role anda tidak memiliki akses.",
    "results": []
  }
  ```

- **403 Forbidden** — Role tidak sesuai (misal: Admin mencoba CRUD Admin):
  ```json
  {
    "code": 403,
    "status": false,
    "message": "Forbidden: Role 'Admin' tidak memiliki akses untuk operasi ini.",
    "results": []
  }
  ```

---

## Format Response Standar

Seluruh response dari server (baik sukses maupun error) menggunakan format pembungkus berikut:

```json
{
  "code": 200,
  "status": true,
  "message": "Pesan informasi response",
  "results": { ... }
}
```

---

## 1. Daftar Semua Gereja

Mengambil semua gereja beserta total kuota, jumlah terdaftar, sisa kuota, dan daftar kuota per kapita.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/churches`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Daftar gereja berhasil ditemukan.",
    "results": [
      {
        "id": 1,
        "name": "GBI Keluarga Allah",
        "total_quota": 80,
        "total_registered": 5,
        "quota_left": 75,
        "kapita": [
          {
            "gkid": 1,
            "gid": 1,
            "idkapita": 1,
            "kapita_name": "Kapita 1",
            "kuota": 50,
            "registered": 3,
            "quota_left": 47
          },
          {
            "gkid": 2,
            "gid": 1,
            "idkapita": 2,
            "kapita_name": "Kapita 2",
            "kuota": 30,
            "registered": 2,
            "quota_left": 28
          }
        ]
      },
      ...
    ]
  }
  ```

---

## 2. Detail Gereja

Mengambil detail informasi untuk gereja tertentu berdasarkan ID.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Detail gereja berhasil ditemukan.",
    "results": {
      "id": 1,
      "name": "GBI Keluarga Allah",
      "total_quota": 80,
      "total_registered": 5,
      "quota_left": 75,
      "kapita": [
        {
          "gkid": 1,
          "gid": 1,
          "idkapita": 1,
          "kapita_name": "Kapita 1",
          "kuota": 50,
          "registered": 3,
          "quota_left": 47
        }
      ]
    }
  }
  ```

---

## 3. Daftar Kuota Kapita Gereja

Mengambil daftar kuota semua kapita untuk gereja tertentu.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}/kapita-quota`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Daftar kuota kapita gereja berhasil ditemukan.",
    "results": [
      {
        "gkid": 1,
        "gid": 1,
        "idkapita": 1,
        "kapita_name": "Kapita 1",
        "kuota": 50
      }
    ]
  }
  ```

---

## 4. Set Kuota Kapita Gereja

Menambahkan atau mengupdate kuota kapita untuk gereja tertentu. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `POST`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}/kapita-quota`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "kapita_id": 1,
    "kuota": 50
  }
  ```
- **Response Contoh Sukses (201 Created)**:
  ```json
  {
    "code": 201,
    "status": true,
    "message": "Kuota kapita gereja berhasil disimpan.",
    "results": {
      "gkid": 1,
      "gid": 1,
      "idkapita": 1,
      "kapita_name": "Kapita 1",
      "kuota": 50,
      "registered": 0,
      "quota_left": 50
    }
  }
  ```

---

## 5. Detail Kuota Kapita Gereja

Mengambil detail kuota kapita tertentu untuk gereja tertentu.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}/kapita-quota/{kapita_id}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Detail kuota kapita gereja berhasil ditemukan.",
    "results": {
      "gkid": 1,
      "gid": 1,
      "idkapita": 1,
      "kapita_name": "Kapita 1",
      "kuota": 50,
      "registered": 3,
      "quota_left": 47
    }
  }
  ```

---

## 6. Update Kuota Kapita Gereja

Mengupdate kuota kapita untuk gereja tertentu. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}/kapita-quota/{kapita_id}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "kapita_id": 1,
    "kuota": 100
  }
  ```
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Kuota kapita gereja berhasil diupdate.",
    "results": {
      "gkid": 1,
      "gid": 1,
      "idkapita": 1,
      "kapita_name": "Kapita 1",
      "kuota": 100
    }
  }
  ```

---

## 7. Hapus Kuota Kapita Gereja

Menghapus kuota kapita untuk gereja tertentu. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}/kapita-quota/{kapita_id}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Kuota kapita gereja berhasil dihapus.",
    "results": []
  }
  ```

---

## 8. Pendaftaran Baru (Registrations)

Mendaftarkan user baru ke salah satu gereja dan kapita.

- **Method**: `POST`
- **URL**: `http://127.0.0.1:8080/api/registrations`
- **Headers**: `X-Salt`, `X-Signature`
- **Body (Raw JSON)**:
  ```json
  {
    "full_name": "Budi Santoso",
    "email": "budi.santoso@email.com",
    "phone": "081234567890",
    "birth_date": "1995-08-17",
    "address": "Jl. Merdeka No. 1, Jakarta",
    "church_id": 1,
    "kapita_id": 1,
    "notes": "Saya tertarik dengan pelayanan musik."
  }
  ```
- **Response Contoh Sukses (201 Created)**:
  ```json
  {
    "code": 201,
    "status": true,
    "message": "Pendaftaran berhasil disimpan.",
    "results": {
      "id": 1,
      "full_name": "Budi Santoso",
      "email": "budi.santoso@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Merdeka No. 1, Jakarta",
      "church_id": 1,
      "church_name": "GBI Keluarga Allah",
      "kapita_id": 1,
      "kapita_name": "Kapita 1",
      "notes": "Saya tertarik dengan pelayanan musik.",
      "registered_at": "2026-07-19 22:20:00"
    }
  }
  ```

---

## 9. Cek Email Terdaftar

Mengecek apakah email tertentu sudah pernah digunakan untuk mendaftar.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/registrations/check/{email}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Pengecekan email berhasil.",
    "results": {
      "email": "budi.santoso@email.com",
      "is_registered": true,
      "message": "Email 'budi.santoso@email.com' sudah terdaftar atas nama Budi Santoso."
    }
  }
  ```

---

## 10. Detail Pendaftaran

Mengambil detail data pendaftaran berdasarkan ID.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/registrations/{id}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Detail pendaftaran berhasil ditemukan.",
    "results": {
      "id": 1,
      "full_name": "Budi Santoso",
      "email": "budi.santoso@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Merdeka No. 1, Jakarta",
      "church_id": 1,
      "church_name": "GBI Keluarga Allah",
      "kapita_id": 1,
      "kapita_name": "Kapita 1",
      "notes": "Saya tertarik dengan pelayanan musik.",
      "registered_at": "2026-07-19 22:20:00"
    }
  }
  ```

---

## 11. Daftar Semua Kapita

Mengambil semua data kapita.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/kapita`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Daftar kapita berhasil ditemukan.",
    "results": [
      {
        "idkapita": 1,
        "namakapita": "Kapita 1"
      },
      {
        "idkapita": 2,
        "namakapita": "Kapita 2"
      }
    ]
  }
  ```

---

## 12. Tambah Kapita Baru

Menambahkan data kapita baru. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `POST`
- **URL**: `http://127.0.0.1:8080/api/kapita`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "namakapita": "Kapita 1"
  }
  ```
- **Response Contoh Sukses (201 Created)**:
  ```json
  {
    "code": 201,
    "status": true,
    "message": "Kapita berhasil disimpan.",
    "results": {
      "idkapita": 1,
      "namakapita": "Kapita 1"
    }
  }
  ```

---

## 13. Detail Kapita

Mengambil detail data kapita berdasarkan ID.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/kapita/{idkapita}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Detail kapita berhasil ditemukan.",
    "results": {
      "idkapita": 1,
      "namakapita": "Kapita 1"
    }
  }
  ```

---

## 14. Daftar Semua User

Mengambil semua data user beserta nama gereja dan nama kapita.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/users`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Daftar user berhasil ditemukan.",
    "results": [
      {
        "uid": 1,
        "full_name": "Budi Santoso",
        "email": "budi.santoso@email.com",
        "phone": "081234567890",
        "birth_date": "1995-08-17",
        "address": "Jl. Merdeka No. 1, Jakarta",
        "church_id": 1,
        "church_name": "GBI Keluarga Allah",
        "ukapita": 1,
        "kapita_name": "Kapita 1",
        "notes": "Saya tertarik dengan pelayanan musik.",
        "registered_at": "2026-07-19 22:20:00"
      },
      ...
    ]
  }
  ```

---

## 15. Tambah User Baru

Menambahkan data user baru. Input menggunakan format registration, `church_name` tidak perlu diisi (otomatis join dari `church_id`).

- **Method**: `POST`
- **URL**: `http://127.0.0.1:8080/api/users`
- **Headers**: `X-Salt`, `X-Signature`
- **Body (Raw JSON)**:
  ```json
  {
    "full_name": "Budi Santoso",
    "email": "budi.santoso@email.com",
    "phone": "081234567890",
    "birth_date": "1995-08-17",
    "address": "Jl. Merdeka No. 1, Jakarta",
    "church_id": 1,
    "ukapita": 1,
    "notes": "Saya tertarik dengan pelayanan musik."
  }
  ```
- **Response Contoh Sukses (201 Created)**:
  ```json
  {
    "code": 201,
    "status": true,
    "message": "User berhasil disimpan.",
    "results": {
      "uid": 1,
      "full_name": "Budi Santoso",
      "email": "budi.santoso@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Merdeka No. 1, Jakarta",
      "church_id": 1,
      "church_name": "GBI Keluarga Allah",
      "ukapita": 1,
      "kapita_name": "Kapita 1",
      "notes": "Saya tertarik dengan pelayanan musik.",
      "registered_at": "2026-07-19 22:20:00"
    }
  }
  ```

---

## 16. Detail User

Mengambil detail data user berdasarkan ID.

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/users/{uid}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Detail user berhasil ditemukan.",
    "results": {
      "uid": 1,
      "full_name": "Budi Santoso",
      "email": "budi.santoso@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Merdeka No. 1, Jakarta",
      "church_id": 1,
      "church_name": "GBI Keluarga Allah",
      "ukapita": 1,
      "kapita_name": "Kapita 1",
      "notes": "Saya tertarik dengan pelayanan musik.",
      "registered_at": "2026-07-19 22:20:00"
    }
  }
  ```

---

## 17. Update Gereja

Mengubah data gereja berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "name": "GBI Keluarga Allah Baru"
  }
  ```
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Gereja berhasil diupdate.",
    "results": {
      "id": 1,
      "name": "GBI Keluarga Allah Baru",
      "total_quota": 50,
      "total_registered": 0,
      "quota_left": 50,
      "kapita": [
        {
          "gkid": 1,
          "gid": 1,
          "idkapita": 1,
          "kapita_name": "Kapita 1",
          "kuota": 50,
          "registered": 0,
          "quota_left": 50
        }
      ]
    }
  }
  ```

---

## 18. Hapus Gereja

Menghapus data gereja berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8080/api/churches/{gid}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Gereja berhasil dihapus.",
    "results": []
  }
  ```

---

## 19. Update Kapita

Mengubah data kapita berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8080/api/kapita/{idkapita}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "namakapita": "Kapita Updated"
  }
  ```
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Kapita berhasil diupdate.",
    "results": {
      "idkapita": 1,
      "namakapita": "Kapita Updated"
    }
  }
  ```

---

## 20. Hapus Kapita

Menghapus data kapita berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8080/api/kapita/{idkapita}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Kapita berhasil dihapus.",
    "results": []
  }
  ```

---

## 21. Update Pendaftaran (Registrations)

Mengubah data pendaftaran berdasarkan ID.

- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8080/api/registrations/{id}`
- **Headers**: `X-Salt`, `X-Signature`
- **Body (Raw JSON)**:
  ```json
  {
    "full_name": "Budi Santoso Updated",
    "email": "budi.updated@email.com",
    "phone": "081234567890",
    "birth_date": "1995-08-17",
    "address": "Jl. Baru No. 2, Jakarta",
    "church_id": 1,
    "kapita_id": 1,
    "notes": "Update catatan"
  }
  ```
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Pendaftaran berhasil diupdate.",
    "results": {
      "id": 1,
      "full_name": "Budi Santoso Updated",
      "email": "budi.updated@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Baru No. 2, Jakarta",
      "church_id": 1,
      "church_name": "GBI Keluarga Allah",
      "kapita_id": 1,
      "kapita_name": "Kapita 1",
      "notes": "Update catatan",
      "registered_at": "2026-07-19 22:20:00"
    }
  }
  ```

---

## 22. Hapus Pendaftaran (Registrations)

Menghapus data pendaftaran berdasarkan ID.

- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8080/api/registrations/{id}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Pendaftaran berhasil dihapus.",
    "results": []
  }
  ```

---

## 23. Update User

Mengubah data user berdasarkan ID.

- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8080/api/users/{uid}`
- **Headers**: `X-Salt`, `X-Signature`
- **Body (Raw JSON)**:
  ```json
  {
    "full_name": "Budi Santoso Updated",
    "email": "budi.updated@email.com",
    "phone": "081234567890",
    "birth_date": "1995-08-17",
    "address": "Jl. Baru No. 2, Jakarta",
    "church_id": 1,
    "ukapita": 1,
    "notes": "Update catatan"
  }
  ```
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "User berhasil diupdate.",
    "results": {
      "uid": 1,
      "full_name": "Budi Santoso Updated",
      "email": "budi.updated@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Baru No. 2, Jakarta",
      "church_id": 1,
      "church_name": "GBI Keluarga Allah",
      "ukapita": 1,
      "kapita_name": "Kapita 1",
      "notes": "Update catatan",
      "registered_at": "2026-07-19 22:20:00"
    }
  }
  ```

---

## 24. Hapus User

Menghapus data user berdasarkan ID.

- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8080/api/users/{uid}`
- **Headers**: `X-Salt`, `X-Signature`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "User berhasil dihapus.",
    "results": []
  }
  ```

---

## 25. Login Admin

Melakukan login admin untuk mendapatkan `aid` (ID admin) yang digunakan sebagai header `X-Admin-ID` pada operasi CUD.

- **Method**: `POST`
- **URL**: `http://127.0.0.1:8080/api/admin/login`
- **Headers**: `X-Salt`, `X-Signature`
- **Body (Raw JSON)**:
  ```json
  {
    "email": "superadmin@gereja.com",
    "password": "superadmin123"
  }
  ```
- **Response Contoh Sukses (200 OK)**:
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
- **Response Error (401 Unauthorized)**:
  ```json
  {
    "code": 401,
    "status": false,
    "message": "Email atau password salah.",
    "results": []
  }
  ```

---

## 26. Daftar Semua Admin

Mengambil semua data admin. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/admins`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Response Contoh (200 OK)**:
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
      },
      {
        "aid": 2,
        "username": "admin01",
        "email": "admin01@gereja.com",
        "role": "Admin"
      }
    ]
  }
  ```

---

## 27. Tambah Admin Baru

Menambahkan data admin baru. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `POST`
- **URL**: `http://127.0.0.1:8080/api/admins`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "username": "admin01",
    "email": "admin01@gereja.com",
    "password": "password123",
    "role": "Admin"
  }
  ```
  > **Keterangan Role:**
  >
  > - `"Admin"` — Boleh CRUD Gereja dan Kapita
  > - `"SuperAdmin"` — Boleh semua operasi
  > - `"NULL"` — Tidak punya akses CUD (default jika tidak diisi)
- **Response Contoh Sukses (201 Created)**:
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

## 28. Detail Admin

Mengambil detail data admin berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `GET`
- **URL**: `http://127.0.0.1:8080/api/admins/{aid}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Response Contoh (200 OK)**:
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

## 29. Update Admin

Mengubah data admin berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8080/api/admins/{aid}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Body (Raw JSON)**:
  ```json
  {
    "username": "admin01_updated",
    "email": "admin01_updated@gereja.com",
    "password": "newpassword123",
    "role": "SuperAdmin"
  }
  ```
  > **Catatan:** Field yang tidak dikirim tidak akan diupdate. Untuk mengatur role ke NULL, kirim `"role": "NULL"`.
- **Response Contoh (200 OK)**:
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

## 30. Hapus Admin

Menghapus data admin berdasarkan ID. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8080/api/admins/{aid}`
- **Headers**: `X-Salt`, `X-Signature`, `X-Admin-ID`
- **Response Contoh (200 OK)**:
  ```json
  {
    "code": 200,
    "status": true,
    "message": "Admin berhasil dihapus.",
    "results": []
  }
  ```
