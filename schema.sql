-- ============================================================
-- PENDAFTARAN KAPITA GEREJA - Database Schema
-- Jalankan di Supabase SQL Editor
-- ============================================================

-- DROP tabel jika ada (dalam urutan yang benar karena FK)
DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS gereja_kapita CASCADE;
DROP TABLE IF EXISTS gereja CASCADE;
DROP TABLE IF EXISTS kapita CASCADE;
DROP TABLE IF EXISTS admin CASCADE;

-- ============================================================
-- 1. TABEL ADMIN
-- ============================================================
CREATE TABLE admin (
    aid        SERIAL PRIMARY KEY,
    ausername  TEXT NOT NULL,
    aemail     TEXT NOT NULL UNIQUE,
    apassword  TEXT NOT NULL,
    arole      TEXT
);

-- ============================================================
-- 2. TABEL KAPITA
-- ============================================================
CREATE TABLE kapita (
    idkapita   SERIAL PRIMARY KEY,
    namakapita TEXT NOT NULL
);

-- ============================================================
-- 3. TABEL GEREJA
-- ============================================================
CREATE TABLE gereja (
    gkode  TEXT PRIMARY KEY,
    gnama  TEXT NOT NULL
);

-- ============================================================
-- 4. TABEL GEREJA_KAPITA (kuota per gereja per kapita)
-- ============================================================
CREATE TABLE gereja_kapita (
    gkid      SERIAL PRIMARY KEY,
    gkode     TEXT NOT NULL REFERENCES gereja(gkode) ON DELETE CASCADE,
    idkapita  INTEGER NOT NULL REFERENCES kapita(idkapita) ON DELETE CASCADE,
    kuota     INTEGER NOT NULL DEFAULT 0,
    UNIQUE(gkode, idkapita)
);

-- ============================================================
-- 5. TABEL REGISTRATIONS (pendaftaran via form admin)
-- ============================================================
CREATE TABLE registrations (
    id             SERIAL PRIMARY KEY,
    full_name      TEXT NOT NULL,
    email          TEXT NOT NULL,
    phone          TEXT NOT NULL,
    birth_date     DATE NOT NULL,
    address        TEXT NOT NULL,
    church_gkode   TEXT NOT NULL REFERENCES gereja(gkode) ON DELETE CASCADE,
    kapita_id      INTEGER NOT NULL REFERENCES kapita(idkapita) ON DELETE CASCADE,
    notes          TEXT,
    registered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. TABEL USERS (pendaftaran via form publik)
-- ============================================================
CREATE TABLE users (
    uid             SERIAL PRIMARY KEY,
    unama           TEXT NOT NULL,
    uemail          TEXT NOT NULL,
    uphone          TEXT NOT NULL,
    ubirth_date     DATE NOT NULL,
    uaddress        TEXT NOT NULL,
    ugereja         TEXT NOT NULL REFERENCES gereja(gkode) ON DELETE CASCADE,
    ukapita         INTEGER NOT NULL REFERENCES kapita(idkapita) ON DELETE CASCADE,
    unotes          TEXT,
    uregistered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Admin (SuperAdmin)
INSERT INTO admin (ausername, aemail, apassword, arole)
VALUES ('superadmin', 'superadmin@gereja.com', 'superadmin123', 'SuperAdmin');

-- Kapita
INSERT INTO kapita (idkapita, namakapita) VALUES
(1, 'Bapak'),
(2, 'Ibu'),
(3, 'Pemuda'),
(4, 'Pemudi'),
(5, 'Mambo'),
(6, 'Oikos');

-- Gereja (contoh)
INSERT INTO gereja (gkode, gnama) VALUES
('GKY001', 'Gereja Kristen Yehova'),
('GST001', 'Gereja Santo Thomas'),
('GKI001', 'Gereja Kristen Indonesia');

-- Gereja_Kapita (kuota)
INSERT INTO gereja_kapita (gkode, idkapita, kuota) VALUES
('GKY001', 1, 50),
('GKY001', 2, 50),
('GKY001', 3, 30),
('GKY001', 4, 30),
('GKY001', 5, 20),
('GKY001', 6, 20),
('GST001', 1, 40),
('GST001', 2, 40),
('GST001', 3, 25),
('GST001', 4, 25),
('GST001', 5, 15),
('GST001', 6, 15),
('GKI001', 1, 45),
('GKI001', 2, 45),
('GKI001', 3, 28),
('GKI001', 4, 28),
('GKI001', 5, 18),
('GKI001', 6, 18);
