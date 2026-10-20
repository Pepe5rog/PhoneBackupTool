# Phone Backup Tool

Окно для снятия данных с Android-телефона через adb: без root, на телефоне ничего не ставится
и не меняется.

- информация об устройстве;
- музыка (по папкам-альбомам);
- фото/видео (DCIM) и все медиа-папки;
- контакты в CSV и VCF.

## Установка
Скачайте `PhoneBackupTool-Setup-*.exe` из Releases и запустите (права администратора не нужны).
adb уже внутри.

На телефоне: включите «Отладку по USB», подключите кабель и подтвердите запрос
«Разрешить отладку» на экране.

## Сборка
```
python -m PyInstaller PhoneBackupTool.spec
"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" installer.iss
```
`installer.iss` берёт adb из `C:\platform-tools` (Android SDK Platform-Tools, Apache 2.0).
Иконка: `python make_icon.py`.
