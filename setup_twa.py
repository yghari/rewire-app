import os, urllib.request, struct, zlib

def mkdirs(path):
    os.makedirs(path, exist_ok=True)

dirs = [
    'twa/app/src/main/java/com/yghari/rewire',
    'twa/app/src/main/res/values',
    'twa/app/src/main/res/drawable',
    'twa/app/src/main/res/layout',
    'twa/app/src/main/res/mipmap-hdpi',
    'twa/app/src/main/res/mipmap-mdpi',
    'twa/app/src/main/res/mipmap-xhdpi',
    'twa/app/src/main/res/mipmap-xxhdpi',
    'twa/app/src/main/res/mipmap-xxxhdpi',
    'twa/gradle/wrapper',
]
for d in dirs:
    mkdirs(d)

# settings.gradle
with open('twa/settings.gradle', 'w') as f:
    f.write('rootProject.name = "Rewire"\ninclude \':app\'\n')

# root build.gradle
with open('twa/build.gradle', 'w') as f:
    f.write('''buildscript {
  repositories { google(); mavenCentral() }
  dependencies { classpath 'com.android.tools.build:gradle:8.2.2' }
}
allprojects { repositories { google(); mavenCentral() } }
''')

# app/build.gradle
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
dependencies {}
''')

# gradle.properties
with open('twa/gradle.properties', 'w') as f:
    f.write('''android.useAndroidX=false
org.gradle.jvmargs=-Xmx2048m
''')

# AndroidManifest.xml
with open('twa/app/src/main/AndroidManifest.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET"/>
  <application
    android:label="Rewire"
    android:icon="@mipmap/ic_launcher"
    android:allowBackup="true"
    android:usesCleartextTraffic="true">
    <activity
      android:name=".MainActivity"
      android:exported="true"
      android:configChanges="orientation|screenSize|keyboardHidden"
      android:windowSoftInputMode="adjustResize">
      <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
      </intent-filter>
    </activity>
  </application>
</manifest>
''')

# MainActivity.java — pure WebView, loads GitHub Pages URL
with open('twa/app/src/main/java/com/yghari/rewire/MainActivity.java', 'w') as f:
    f.write('''package com.yghari.rewire;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.Window;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);

        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("https://yghari.github.io/rewire-app/");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
''')

# layout not needed (WebView set directly) but res/values required
with open('twa/app/src/main/res/values/strings.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
  <string name="app_name">Rewire</string>
</resources>
''')

with open('twa/app/src/main/res/values/colors.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
  <color name="colorPrimary">#0b1120</color>
</resources>
''')

with open('twa/app/src/main/res/values/styles.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
  <style name="AppTheme" parent="android:Theme.NoTitleBar.Fullscreen">
    <item name="android:windowBackground">@color/colorPrimary</item>
  </style>
</resources>
''')

# gradle-wrapper.properties
with open('twa/gradle/wrapper/gradle-wrapper.properties', 'w') as f:
    f.write('''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
''')

# PNG icon
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

# gradlew
urllib.request.urlretrieve(
    'https://raw.githubusercontent.com/gradle/gradle/v8.4.0/gradlew',
    'twa/gradlew'
)
os.chmod('twa/gradlew', 0o755)

# gradle-wrapper.jar
urllib.request.urlretrieve(
    'https://github.com/gradle/gradle/raw/v8.4.0/gradle/wrapper/gradle-wrapper.jar',
    'twa/gradle/wrapper/gradle-wrapper.jar'
)

print("Project created successfully!")
