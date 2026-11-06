import gradio as gr
import sqlite3, csv, os
from datetime import datetime

DB_PATH = "absensi.db"
# GANTI dengan password rahasia milik petugas sebelum menjalankan aplikasi.
ADMIN_PASSWORD = "GANTI_PASSWORD_ADMIN"

def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    con.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        attendance_code TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
        nim TEXT NOT NULL, student_name TEXT NOT NULL, checked_at TEXT NOT NULL,
        UNIQUE(session_id, nim))""")
    con.commit()
    con.close()

def get_dashboard():
    con = connect()
    active = con.execute("SELECT title, created_at FROM sessions WHERE active=1 ORDER BY id DESC LIMIT 1").fetchone()
    rows = con.execute("""SELECT s.title, a.nim, a.student_name, a.checked_at
        FROM attendance a JOIN sessions s ON s.id=a.session_id ORDER BY a.id DESC LIMIT 500""").fetchall()
    con.close()
    status = ("Sesi aktif: **" + active["title"] + "** — dibuat " + active["created_at"]) if active else "Belum ada sesi absensi aktif."
    return status, [[r["title"], r["nim"], r["student_name"], r["checked_at"]] for r in rows]

def admin_login(password):
    if ADMIN_PASSWORD == "GANTI_PASSWORD_ADMIN":
        return False, "Password belum diganti. Edit ADMIN_PASSWORD di app.py terlebih dahulu."
    if password == ADMIN_PASSWORD:
        return True, "Login admin berhasil."
    return False, "Password admin salah."

def create_session(is_admin, title, code):
    if not is_admin:
        return "Akses ditolak. Login sebagai admin terlebih dahulu.", *get_dashboard()
    title, code = (title or "").strip(), (code or "").strip()
    if not title or not code:
        return "Isi nama sesi dan kode absensi.", *get_dashboard()
    con = connect()
    con.execute("UPDATE sessions SET active=0 WHERE active=1")
    con.execute("INSERT INTO sessions(title, attendance_code, active, created_at) VALUES (?, ?, 1, ?)",
                (title, code, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    con.close()
    return "Sesi berhasil dibuka. Berikan kode absensi kepada mahasiswa.", *get_dashboard()

def close_session(is_admin):
    if not is_admin:
        return "Akses ditolak. Login admin terlebih dahulu.", *get_dashboard()
    con = connect()
    con.execute("UPDATE sessions SET active=0 WHERE active=1")
    con.commit()
    con.close()
    return "Sesi absensi telah ditutup.", *get_dashboard()

def refresh_dashboard(is_admin):
    if not is_admin:
        return "Login admin terlebih dahulu.", []
    return get_dashboard()

def submit_attendance(nim, name, code):
    nim, name, code = (nim or "").strip(), (name or "").strip(), (code or "").strip()
    if not nim or not name or not code:
        return "Lengkapi NIM, nama, dan kode absensi."
    con = connect()
    session = con.execute("SELECT id, title, attendance_code FROM sessions WHERE active=1 ORDER BY id DESC LIMIT 1").fetchone()
    if not session:
        con.close()
        return "Belum ada sesi absensi yang dibuka petugas."
    if code != session["attendance_code"]:
        con.close()
        return "Kode absensi salah. Periksa kembali kode dari petugas."
    try:
        con.execute("INSERT INTO attendance(session_id, nim, student_name, checked_at) VALUES (?, ?, ?, ?)",
                    (session["id"], nim, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        result = "✅ Absensi berhasil untuk **" + session["title"] + "**. Terima kasih, " + name + "!"
    except sqlite3.IntegrityError:
        result = "NIM ini sudah melakukan absensi pada sesi tersebut."
    con.close()
    return result

def export_csv(is_admin):
    if not is_admin:
        raise gr.Error("Login admin diperlukan.")
    con = connect()
    rows = con.execute("""SELECT s.title, a.nim, a.student_name, a.checked_at
        FROM attendance a JOIN sessions s ON s.id=a.session_id ORDER BY a.id DESC""").fetchall()
    con.close()
    path = "rekap_absensi.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Sesi", "NIM", "Nama Mahasiswa", "Waktu Absensi"])
        writer.writerows([[r["title"], r["nim"], r["student_name"], r["checked_at"]] for r in rows])
    return path

init_db()

with gr.Blocks(title="Absensi Mahasiswa", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📋 Aplikasi Absensi Mahasiswa\nMahasiswa mengisi identitas dan kode. Petugas mengelola sesi serta rekap.")
    with gr.Tab("Mahasiswa"):
        gr.Markdown("### Formulir kehadiran")
        nim = gr.Textbox(label="NIM", placeholder="Masukkan NIM")
        name = gr.Textbox(label="Nama lengkap", placeholder="Masukkan nama sesuai identitas")
        code = gr.Textbox(label="Kode absensi dari petugas", placeholder="Masukkan kode")
        submit = gr.Button("Kirim Absensi", variant="primary")
        student_result = gr.Markdown()
        submit.click(submit_attendance, inputs=[nim, name, code], outputs=student_result)
        gr.Markdown("Satu NIM hanya dapat absen satu kali pada setiap sesi.")

    with gr.Tab("Petugas / Admin"):
        gr.Markdown("### Login petugas")
        password = gr.Textbox(label="Password admin", type="password")
        login = gr.Button("Login")
        login_status = gr.Markdown()
        admin_state = gr.State(False)
        login.click(admin_login, inputs=password, outputs=[admin_state, login_status])

        gr.Markdown("### Kelola sesi absensi")
        title = gr.Textbox(label="Nama sesi", placeholder="Contoh: Absensi Kuliah Pemrograman")
        session_code = gr.Textbox(label="Kode absensi", placeholder="Buat kode untuk mahasiswa")
        with gr.Row():
            open_session = gr.Button("Buka Sesi", variant="primary")
            end_session = gr.Button("Tutup Sesi")
        session_status = gr.Markdown()

        gr.Markdown("### Rekap kehadiran")
        dashboard_status = gr.Markdown()
        table = gr.Dataframe(headers=["Sesi", "NIM", "Nama Mahasiswa", "Waktu Absensi"],
                             datatype=["str", "str", "str", "str"], interactive=False)
        with gr.Row():
            refresh = gr.Button("Perbarui Data")
            export = gr.Button("Unduh Rekap CSV")
        csv_output = gr.File(label="File CSV")

        open_session.click(create_session, inputs=[admin_state, title, session_code],
                           outputs=[session_status, dashboard_status, table])
        end_session.click(close_session, inputs=admin_state,
                          outputs=[session_status, dashboard_status, table])
        refresh.click(refresh_dashboard, inputs=admin_state, outputs=[dashboard_status, table])
        export.click(export_csv, inputs=admin_state, outputs=csv_output)

if __name__ == "__main__":
    demo.launch(share=True)
