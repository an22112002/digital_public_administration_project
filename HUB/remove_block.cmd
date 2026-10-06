@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem 'C:\deploy' -Recurse -File | Unblock-File"