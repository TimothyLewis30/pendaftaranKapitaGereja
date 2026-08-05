# Panduan Pengujian API dengan Postman

Dokumen ini berisi daftar endpoint API Sistem Registrasi Gereja beserta detail metode HTTP, parameter, payload request, dan contoh response untuk mempermudah pengujian menggunakan Postman.

## Informasi Umum
- **Base URL**: `http://127.0.0.1:8080`
- **Header Default** (untuk request POST): `Content-Type: application/json`

---

## 1. Health Check
Mengecek status kesehatan server backend.

- **Method**: `GET`
- **Endpoint**: `/`
- **Response**:
  ```json
  {
      "code": 200,
      "status": true,
      "message": "Sistem Registrasi Gereja berjalan dengan baik.",
      "results": null
  }
  ```

---

## 2. Daftar Semua Gereja
Mengambil semua data gereja beserta total kuota, jumlah terdaftar, sisa kuota, dan daftar kuota per kapita.

- **Method**: `GET`
- **Endpoint**: `/churches`
- **Response**:
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

## 3. Detail Gereja
Mengambil detail satu gereja berdasarkan ID gereja.

- **Method**: `GET`
- **Endpoint**: `/churches/<p_church_id>`
  - Contoh: `/churches/1`
- **Response (Sukses)**:
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
- **Response (Error - Tidak Ditemukan)**:
  ```json
  {
      "code": 404,
      "status": false,
      "message": "Gereja dengan ID 999 tidak ditemukan.",
      "results": null
  }
  ```

---

## 4. Daftar Kuota Kapita Gereja
Mengambil daftar kuota semua kapita untuk gereja tertentu.

- **Method**: `GET`
- **Endpoint**: `/churches/<p_church_id>/kapita-quota`
  - Contoh: `/churches/1/kapita-quota`
- **Response**:
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
              "kuota": 50,
              "registered": 3,
              "quota_left": 47
          }
      ]
  }
  ```

---

## 5. Set Kuota Kapita Gereja
Menambahkan atau mengupdate kuota kapita untuk gereja tertentu. **Memerlukan header `X-Admin-ID` dengan role Admin atau SuperAdmin.**

- **Method**: `POST`
- **Endpoint**: `/churches/<p_church_id>/kapita-quota`
- **Headers**:
  - `Content-Type: application/json`
  - `X-Admin-ID: 1`
- **Request Body (Raw JSON)**:
  ```json
  {
      "kapita_id": 1,
      "kuota": 50
  }
  ```
- **Response (Sukses - 201 Created)**:
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

## 6. Pendaftaran Baru (Daftar Baru)
Mendaftarkan user baru ke salah satu gereja dan kapita.

- **Method**: `POST`
- **Endpoint**: `/registrations`
- **Headers**:
  - `Content-Type: application/json`
- **Request Body (Raw JSON)**:
  ```json
  {
      "full_name": "Budi Santoso",
      "email": "budi.santoso@email.com",
      "phone": "081234567890",
      "birth_date": "1995-08-17",
      "address": "Jl. Merdeka No. 1, Jakarta",
      "church_id": 1,
      "kapita_id": 1,
      "notes": "Saya tertarik dengan pelayanan multimedia"
  }
  ```
- **Response (Sukses - 201 Created)**:
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
          "notes": "Saya tertarik dengan pelayanan multimedia",
          "registered_at": "2026-07-19 22:28:15"
      }
  }
  ```
- **Response (Error - Validasi Data Gagal / 400 Bad Request)**:
  ```json
  {
      "code": 400,
      "status": false,
      "message": "Validasi data gagal.",
      "results": [
          {
              "type": "string_too_short",
              "loc": [
                  "full_name"
              ],
              "msg": "String should have at least 3 characters",
              "input": "Bu",
              "ctx": {
                  "min_length": 3
              }
          }
      ]
  }
  ```
- **Response (Error - Email Sudah Terdaftar / 409 Conflict)**:
  ```json
  {
      "code": 409,
      "status": false,
      "message": "Email 'budi.santoso@email.com' sudah terdaftar. Setiap email hanya dapat mendaftar satu kali.",
      "results": null
  }
  ```

---

## 7. Cek Email Terdaftar
Mengecek apakah suatu email sudah pernah digunakan untuk mendaftar.

- **Method**: `GET`
- **Endpoint**: `/registrations/check/<p_email>`
  - Contoh: `/registrations/check/budi.santoso@email.com`
- **Response (Sudah Terdaftar)**:
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
- **Response (Belum Terdaftar)**:
  ```json
  {
      "code": 200,
      "status": true,
      "message": "Pengecekan email berhasil.",
      "results": {
          "email": "belum_daftar@email.com",
          "is_registered": false,
          "message": "Email 'belum_daftar@email.com' belum terdaftar. Silakan lakukan pendaftaran."
      }
  }
  ```

---

## 8. Detail Pendaftaran
Mengambil detail pendaftaran berdasarkan ID pendaftaran.

- **Method**: `GET`
- **Endpoint**: `/registrations/<p_reg_id>`
  - Contoh: `/registrations/1`
- **Response (Sukses)**:
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
          "notes": "Saya tertarik dengan pelayanan multimedia",
          "registered_at": "2026-07-19 22:28:15"
      }
  }
  ```
- **Response (Error - Tidak Ditemukan)**:
  ```json
  {
      "code": 404,
      "status": false,
      "message": "Pendaftaran dengan ID 999 tidak ditemukan.",
      "results": null
  }
  ```

---

## 8. Login Admin
Melakukan login admin untuk mendapatkan `aid` yang digunakan sebagai header `X-Admin-ID` pada operasi CUD.

- **Method**: `POST`
- **Endpoint**: `/api/admin/login`
- **Headers**:
  - `Content-Type: application/json`
- **Request Body (Raw JSON)**:
  ```json
  {
      "email": "superadmin@gereja.com",
      "password": "superadmin123"
  }
  ```
- **Response (Sukses)**:
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
- **Response (Error - 401 Unauthorized)**:
  ```json
  {
      "code": 401,
      "status": false,
      "message": "Email atau password salah.",
      "results": null
  }
  ```

---

## 9. Tambah Admin Baru
Menambahkan data admin baru. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `POST`
- **Endpoint**: `/api/admins`
- **Headers**:
  - `Content-Type: application/json`
  - `X-Admin-ID: 1` (ID admin yang login)
- **Request Body (Raw JSON)**:
  ```json
  {
      "username": "admin01",
      "email": "admin01@gereja.com",
      "password": "password123",
      "role": "Admin"
  }
  ```
  > **Keterangan Role:**
  > - `"Admin"` — Boleh CRUD Gereja dan Kapita
  > - `"SuperAdmin"` — Boleh semua operasi
  > - `"NULL"` — Tidak punya akses CUD (default jika tidak diisi)
- **Response (Sukses - 201 Created)**:
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

## 10. Daftar Semua Admin
Mengambil semua data admin. **Memerlukan header `X-Admin-ID` dengan role SuperAdmin.**

- **Method**: `GET`
- **Endpoint**: `/api/admins`
- **Headers**:
  - `X-Admin-ID: 1`
- **Response**:
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

## Role-Based Access Control (RBAC)

Operasi **CUD** (Create, Update, Delete) pada data **Gereja**, **Kapita**, dan **Admin** memerlukan header `X-Admin-ID`.

### Alur Kerja

1. **Login** melalui `POST /api/admin/login` → dapatkan `aid`.
2. **Simpan `aid`** di client.
3. **Kirim header `X-Admin-ID: {aid}`** pada setiap request CUD.
4. **Operasi GET** tetap bisa diakses tanpa `X-Admin-ID`.

### Daftar Role

| Role          | Keterangan                                              |
| ------------- | ------------------------------------------------------- |
| `SuperAdmin`  | Boleh semua operasi: CRUD Gereja, CRUD Kapita, CRUD Admin |
| `Admin`       | Boleh CRUD Gereja dan CRUD Kapita                       |
| `NULL`        | Tidak boleh operasi CUD (hanya bisa login)              |

---

## 21. Cetak / Export Excel Data Peserta

Mencetak data peserta ke dalam format file Excel (.xlsx).

- **Method**: `POST` atau `GET`
- **Endpoint**: `/api/cetak-excel`
- **Payload Request (POST JSON)**:
  ```json
  {
      "pilihan": 1
  }
  ```

### Opsi Pilihan (`pilihan`):
- `1`: Cetak Semua data peserta order by ID Peserta
- `2`: Cetak Data Peserta order by Gereja
- `3`: Cetak Data Peserta order by Kapita
- `4`: Cetak Data Peserta pada Sesi 1 dan Sesi 2

### Filter Opsional (JSON Body atau Query Param):
- `sesi_1` (int): ID Kapita Sesi 1
- `sesi_2` (int): ID Kapita Sesi 2
- `gkode` (string): Kode Gereja

- **Response**: File binary Excel `.xlsx` (`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)

