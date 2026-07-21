"use client";

import { useState, useEffect } from "react";
import {
  getChurches,
  getKapitaList,
  createUser,
  checkRegistration,
  type Church,
  type Kapita,
} from "@/lib/api";

export default function Home() {
  const [churches, setChurches] = useState<Church[]>([]);
  const [kapitaList, setKapitaList] = useState<Kapita[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const [form, setForm] = useState({
    fullName: "",
    email: "",
    phone: "",
    birthDate: "",
    address: "",
    churchGkode: "",
    ukapita: 0,
    notes: "",
  });

  useEffect(() => {
    async function loadData() {
      try {
        const [churchRes, kapitaRes] = await Promise.all([
          getChurches(),
          getKapitaList(),
        ]);
        if (churchRes.status) setChurches(churchRes.results);
        if (kapitaRes.status) setKapitaList(kapitaRes.results);
      } catch {
        setMessage({ type: "error", text: "Gagal memuat data server." });
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const selectedChurch = churches.find((c) => c.id === form.churchGkode);
  const availableKapita = selectedChurch
    ? kapitaList.filter((k) =>
        selectedChurch.kapita.some((q) => q.idkapita === k.idkapita && q.quota_left > 0)
      )
    : [];

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "ukapita" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    try {
      const check = await checkRegistration(form.email);
      if (check.status && check.results?.is_registered) {
        setMessage({ type: "error", text: check.results.message });
        setSubmitting(false);
        return;
      }

      const res = await createUser({
        fullName: form.fullName,
        email: form.email,
        phone: form.phone,
        birthDate: form.birthDate,
        address: form.address,
        churchGkode: form.churchGkode,
        ukapita: form.ukapita,
        notes: form.notes || undefined,
      });

      if (res.status) {
        setMessage({ type: "success", text: "Pendaftaran berhasil! Terima kasih." });
        setForm({
          fullName: "",
          email: "",
          phone: "",
          birthDate: "",
          address: "",
          churchGkode: "",
          ukapita: 0,
          notes: "",
        });
      } else {
        setMessage({ type: "error", text: res.detail || "Gagal mendaftar." });
      }
    } catch {
      setMessage({ type: "error", text: "Terjadi kesalahan jaringan." });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <main style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <p>Memuat data...</p>
      </main>
    );
  }

  return (
    <main style={{ maxWidth: 600, margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: "bold", marginBottom: "0.5rem" }}>
        Pendaftaran Kapita Gereja
      </h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Isi form berikut untuk mendaftar.
      </p>

      {message && (
        <div
          style={{
            padding: "0.75rem 1rem",
            borderRadius: 6,
            marginBottom: "1rem",
            background: message.type === "success" ? "#d4edda" : "#f8d7da",
            color: message.type === "success" ? "#155724" : "#721c24",
          }}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Nama Lengkap *</label>
          <input
            type="text"
            name="fullName"
            value={form.fullName}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Email *</label>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Telepon *</label>
          <input
            type="tel"
            name="phone"
            value={form.phone}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Tanggal Lahir *</label>
          <input
            type="date"
            name="birthDate"
            value={form.birthDate}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Alamat *</label>
          <textarea
            name="address"
            value={form.address}
            onChange={handleChange}
            required
            rows={3}
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Gereja *</label>
          <select
            name="churchGkode"
            value={form.churchGkode}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          >
            <option value="">-- Pilih Gereja --</option>
            {churches.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} (Sisa kuota: {c.quota_left})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Kapita *</label>
          <select
            name="ukapita"
            value={form.ukapita}
            onChange={handleChange}
            required
            disabled={!form.churchGkode}
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          >
            <option value={0}>-- Pilih Kapita --</option>
            {availableKapita.map((k) => {
              const quota = selectedChurch?.kapita.find((q) => q.idkapita === k.idkapita);
              return (
                <option key={k.idkapita} value={k.idkapita}>
                  {k.namakapita} (Sisa: {quota?.quota_left ?? 0})
                </option>
              );
            })}
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4 }}>Catatan</label>
          <textarea
            name="notes"
            value={form.notes}
            onChange={handleChange}
            rows={2}
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{
            padding: "0.75rem",
            background: "#0070f3",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            fontWeight: 600,
            cursor: submitting ? "not-allowed" : "pointer",
            opacity: submitting ? 0.7 : 1,
          }}
        >
          {submitting ? "Mengirim..." : "Daftar Sekarang"}
        </button>
      </form>
    </main>
  );
}
