[app]
title = Friday
package.name = friday
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO,CAMERA,CALL_PHONE,FOREGROUND_SERVICE
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
