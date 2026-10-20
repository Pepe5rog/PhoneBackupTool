# -*- coding: utf-8 -*-
"""
Phone Backup GUI — извлекает данные с Android-телефона через adb (без root,
ничего не устанавливает и не меняет на самом телефоне).

Требования: включённая "Отладка по USB" на телефоне, подключённый кабель,
разрешение на компьютер (появится один раз на экране телефона при первом
подключении — нужно подтвердить вручную).

Запуск:  python phone_backup_gui.py
"""

import csv
import os
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


BASE_DIR = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))


def find_adb():
    """adb bundled next to the program (installer puts it in adb\\), otherwise the one in PATH."""
    bundled = os.path.join(BASE_DIR, "adb", "adb.exe")
    return bundled if os.path.exists(bundled) else "adb"


ADB = find_adb()

MEDIA_FOLDERS = [
    "DCIM", "Documents", "Download", "Movies", "Pictures",
    "Recordings", "Samsung", "Alarms", "Notifications",
    "Ringtones", "Podcasts", "Audiobooks",
]


def run(cmd, timeout=None):
    """Run a subprocess command, return (returncode, stdout, stderr) — always UTF-8 safe."""
    # CREATE_NO_WINDOW: the windowed exe would flash a console for every adb call
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return result.returncode, result.stdout, result.stderr


class PhoneBackupApp:
    def __init__(self, root):
        self.root = root
        root.title("Phone Backup Tool")
        root.geometry("720x560")
        icon = os.path.join(BASE_DIR, "icon.ico")
        if os.path.exists(icon):
            root.iconbitmap(icon)

        self.serial = tk.StringVar()
        self.dest_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop"))

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Устройство:").grid(row=0, column=0, sticky="w")
        self.device_combo = ttk.Combobox(top, textvariable=self.serial, width=40, state="readonly")
        self.device_combo.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(top, text="Обновить список", command=self.refresh_devices).grid(row=0, column=2, padx=5)

        ttk.Label(top, text="Папка назначения:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(top, textvariable=self.dest_dir, width=50).grid(row=1, column=1, sticky="w", padx=5, pady=(8, 0))
        ttk.Button(top, text="Выбрать...", command=self.choose_dest).grid(row=1, column=2, padx=5, pady=(8, 0))

        actions = ttk.LabelFrame(root, text="Действия", padding=10)
        actions.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("Инфо об устройстве", self.action_device_info),
            ("Скачать музыку", self.action_music),
            ("Скачать фото/видео (DCIM)", self.action_dcim),
            ("Скачать все медиа-папки", self.action_all_media),
            ("Экспорт контактов (CSV + VCF)", self.action_contacts),
        ]
        for i, (label, cmd) in enumerate(buttons):
            ttk.Button(actions, text=label, command=lambda c=cmd: self.run_action(c), width=32).grid(
                row=i // 2, column=i % 2, padx=5, pady=4, sticky="w"
            )

        log_frame = ttk.LabelFrame(root, text="Журнал", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log = tk.Text(log_frame, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        scroll.pack(side="right", fill="y")
        self.log.config(yscrollcommand=scroll.set)

        self.refresh_devices()

    # --- helpers -----------------------------------------------------

    def print_log(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def choose_dest(self):
        path = filedialog.askdirectory(initialdir=self.dest_dir.get())
        if path:
            self.dest_dir.set(path)

    def refresh_devices(self):
        code, out, err = run([ADB, "devices"])
        devices = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if line and "\tdevice" in line:
                devices.append(line.split("\t")[0])
        self.device_combo["values"] = devices
        if devices and not self.serial.get():
            self.serial.set(devices[0])
        self.print_log(f"Найдено устройств: {len(devices)} -> {devices}")

    def run_action(self, action_fn):
        if not self.serial.get():
            messagebox.showwarning("Нет устройства", "Сначала выберите устройство (кнопка 'Обновить список').")
            return
        threading.Thread(target=action_fn, daemon=True).start()

    def adb_s(self, *args):
        return [ADB, "-s", self.serial.get()] + list(args)

    # --- actions -------------------------------------------------------

    def action_device_info(self):
        s = self.serial.get()
        self.print_log(f"\n=== Информация об устройстве ({s}) ===")
        props = {
            "Производитель": "ro.product.manufacturer",
            "Модель": "ro.product.model",
            "Android версия": "ro.build.version.release",
            "Сборка": "ro.build.display.id",
        }
        for label, prop in props.items():
            _, out, _ = run(self.adb_s("shell", "getprop", prop))
            self.print_log(f"{label}: {out.strip()}")
        _, out, _ = run(self.adb_s("shell", "df", "//sdcard"))
        self.print_log("Память:\n" + out.strip())

    def action_music(self):
        self.print_log("\n=== Скачивание музыки ===")
        dest_root = os.path.join(self.dest_dir.get(), "Музыка")
        code, out, err = run(self.adb_s(
            "shell", "content", "query",
            "--uri", "content://media/external/audio/media",
            "--projection", "_data:bucket_display_name",
            "--where", "is_music=1",
        ))
        if code != 0:
            self.print_log("Ошибка запроса списка музыки:\n" + err)
            return
        pattern = re.compile(r"_data=(.*?), bucket_display_name=(.*)")
        entries = [(m.group(1).strip(), m.group(2).strip()) for m in map(pattern.search, out.splitlines()) if m]
        self.print_log(f"Найдено файлов: {len(entries)}")
        ok = fail = 0
        for remote_path, bucket in entries:
            bucket_safe = re.sub(r'[<>:"/\\|?*]', "_", bucket) or "Other"
            dest_dir = os.path.join(dest_root, bucket_safe)
            os.makedirs(dest_dir, exist_ok=True)
            filename = remote_path.rsplit("/", 1)[-1]
            dest_path = os.path.join(dest_dir, filename)
            if os.path.exists(dest_path):
                ok += 1
                continue
            code, _, err = run(self.adb_s("pull", remote_path, dest_path))
            if code == 0:
                ok += 1
            else:
                fail += 1
        self.print_log(f"Готово. Скачано: {ok}, ошибок: {fail}")

    def action_dcim(self):
        self._pull_folder("DCIM", "Бэкап")

    def action_all_media(self):
        self.print_log("\n=== Скачивание всех медиа-папок ===")
        for folder in MEDIA_FOLDERS:
            self._pull_folder(folder, "Бэкап")
        self.print_log("Готово со всеми папками.")

    def _pull_folder(self, folder, subdir):
        dest_dir = os.path.join(self.dest_dir.get(), subdir)
        os.makedirs(dest_dir, exist_ok=True)
        self.print_log(f"Скачиваю //sdcard/{folder} ...")
        code, out, err = run(self.adb_s("pull", f"//sdcard/{folder}", dest_dir + os.sep))
        self.print_log((out or err).strip())

    def action_contacts(self):
        self.print_log("\n=== Экспорт контактов ===")
        dest_dir = os.path.join(self.dest_dir.get(), "Контакты")
        os.makedirs(dest_dir, exist_ok=True)
        code, out, err = run(self.adb_s(
            "shell", "content", "query",
            "--uri", "content://com.android.contacts/data/phones",
            "--projection", "display_name:data1:data2",
        ))
        if code != 0:
            self.print_log("Ошибка запроса контактов:\n" + err)
            return
        pattern = re.compile(r"display_name=(.*?), data1=(.*?), data2=(.*)")
        type_map = {"0": "Другое", "1": "Дом", "2": "Мобильный", "3": "Рабочий",
                    "4": "Факс (работа)", "5": "Факс (дом)", "6": "Пейджер", "7": "Другое"}
        rows = []
        seen = set()
        for line in out.splitlines():
            m = pattern.search(line)
            if not m:
                continue
            name, phone, t = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            key = (name, phone)
            if key in seen:
                continue
            seen.add(key)
            rows.append((name, phone, type_map.get(t, t)))
        rows.sort(key=lambda r: r[0].lower())

        csv_path = os.path.join(dest_dir, "Контакты.csv")
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Имя", "Телефон", "Тип"])
            writer.writerows(rows)

        vcf_path = os.path.join(dest_dir, "Контакты.vcf")
        by_name = {}
        for name, phone, t in rows:
            by_name.setdefault(name, []).append((phone, t))
        vtype_map = {"Мобильный": "CELL", "Дом": "HOME", "Рабочий": "WORK"}
        with open(vcf_path, "w", encoding="utf-8") as f:
            for name, phones in by_name.items():
                f.write("BEGIN:VCARD\nVERSION:3.0\n")
                f.write(f"FN:{name}\nN:{name};;;;\n")
                for phone, t in phones:
                    f.write(f"TEL;TYPE={vtype_map.get(t, 'OTHER')}:{phone}\n")
                f.write("END:VCARD\n")

        self.print_log(f"Контактов: {len(rows)} записей, {len(by_name)} уникальных имён")
        self.print_log(f"Сохранено: {csv_path}")
        self.print_log(f"Сохранено: {vcf_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBackupApp(root)
    root.mainloop()
