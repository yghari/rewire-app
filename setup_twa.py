import os, urllib.request, struct, zlib

def mkdirs(path):
    os.makedirs(path, exist_ok=True)

# ── Directory structure ────────────────────────────────────────────────
dirs = [
    'twa/app/src/main/res/values',
    'twa/app/src/main/res/drawable',
    'twa/app/src/main/res/mipmap-hdpi',
    'twa/app/src/main/res/mipmap-mdpi',
    'twa/app/src/main/res/mipmap-xhdpi',
    'twa/app/src/main/res/mipmap-xxhdpi',
    'twa/app/src/main/res/mipmap-xxxhdpi',
    'twa/gradle/wrapper',
]
for d in dirs:
    mkdirs(d)

# ── settings.gradle ────────────────────────────────────────────────────
with open('twa/settings.gradle', 'w') as f:
    f.write('rootProject.name = "Rewire"\ninclude \':app\'\n')

# ── root build.gradle ──────────────────────────────────────────────────
with open('twa/build.gradle', 'w') as f:
    f.write('''buildscript {
  repositories { google(); mavenCentral() }
  dependencies { classpath 'com.android.tools.build:gradle:8.2.2' }
}
allprojects { repositories { google(); mavenCentral() } }
''')

# ── app/build.gradle ──────────────────────────────────────────────────
with open('twa/app/build.gradle', 'w') as f:
    f.write('''plugins { id 'com.android.application' }
android {
  namespace 'com.yghari.rewire'
  compileSdk 34
  defaultConfig {
    applicationId 'com.yghari.rewire'
    minSdk 21
    targetSdk 34
    versionCode 1
    versionName '1.0'
  }
  buildTypes {
    debug { debuggable true }
  }
  compileOptions {
    sourceCompatibility JavaVersion.VERSION_17
    targetCompatibility JavaVersion.VERSION_17
  }
}
dependencies {
  implementation 'com.google.androidbrowserhelper:androidbrowserhelper:2.5.0'
}
''')

# ── AndroidManifest.xml ────────────────────────────────────────────────
with open('twa/app/src/main/AndroidManifest.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET"/>
  <application
    android:label="Rewire"
    android:icon="@mipmap/ic_launcher"
    android:theme="@style/AppTheme"
    android:allowBackup="true">
    <activity
      android:name="com.google.androidbrowserhelper.trusted.LauncherActivity"
      android:exported="true">
      <meta-data
        android:name="android.support.customtabs.trusted.DEFAULT_URL"
        android:value="https://yghari.github.io/rewire-app/"/>
      <meta-data
        android:name="android.support.customtabs.trusted.STATUS_BAR_COLOR"
        android:value="@color/colorPrimary"/>
      <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
      </intent-filter>
    </activity>
    <service
      android:name="com.google.androidbrowserhelper.trusted.DelegationService"
      android:exported="true"
      android:enabled="true">
      <intent-filter>
        <action android:name="android.support.customtabs.trusted.TRUSTED_WEB_ACTIVITY_SERVICE"/>
        <category android:name="android.intent.category.DEFAULT"/>
      </intent-filter>
    </service>
  </application>
</manifest>
''')

# ── res/values/colors.xml ─────────────────────────────────────────────
with open('twa/app/src/main/res/values/colors.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
  <color name="colorPrimary">#0b1120</color>
</resources>
''')

# ── res/values/styles.xml ─────────────────────────────────────────────
with open('twa/app/src/main/res/values/styles.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
  <style name="AppTheme" parent="android:Theme.NoTitleBar">
    <item name="android:windowBackground">@color/colorPrimary</item>
  </style>
</resources>
''')

# ── res/drawable/splash.xml ───────────────────────────────────────────
with open('twa/app/src/main/res/drawable/splash.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
  <solid android:color="#0b1120"/>
</shape>
''')

# ── gradle-wrapper.properties ─────────────────────────────────────────
with open('twa/gradle/wrapper/gradle-wrapper.properties', 'w') as f:
    f.write('''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
''')
# ── gradle.properties ─────────────────────────────────────────────────
with open('twa/gradle.properties', 'w') as f:
    f.write('''android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m
''')
# ── PNG icon generator ────────────────────────────────────────────────
def mkpng(w, h, bg, fg):
    rows = []
    cx, cy = w // 2, h // 2
    r = min(w, h) // 2 - 4
    for y in range(h):
        row = [0]
        for x in range(w):
            dx, dy = x - cx, y - cy
            row += list(fg if dx*dx + dy*dy <= r*r else bg)
        rows.append(bytes(row))
    raw = b''.join(rows)
    def chunk(t, d):
        c = zlib.crc32(t + d) & 0xffffffff
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', c)
    return (b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw))
        + chunk(b'IEND', b''))

icon = mkpng(192, 192, (11, 17, 32), (201, 168, 76))
for d in ['hdpi', 'mdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
    with open(f'twa/app/src/main/res/mipmap-{d}/ic_launcher.png', 'wb') as f:
        f.write(icon)

# ── Download gradlew ──────────────────────────────────────────────────
gradlew_url = 'https://raw.githubusercontent.com/gradle/gradle/v8.4.0/gradlew'
urllib.request.urlretrieve(gradlew_url, 'twa/gradlew')
os.chmod('twa/gradlew', 0o755)

# ── Download gradle-wrapper.jar ───────────────────────────────────────
jar_url = 'https://github.com/gradle/gradle/raw/v8.4.0/gradle/wrapper/gradle-wrapper.jar'
urllib.request.urlretrieve(jar_url, 'twa/gradle/wrapper/gradle-wrapper.jar')

print("TWA project created successfully!")
