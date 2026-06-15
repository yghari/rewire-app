import os, urllib.request, struct, zlib

def mkdirs(path):
    os.makedirs(path, exist_ok=True)

dirs = [
    'twa/app/src/main/java/com/yghari/rewire',
    'twa/app/src/main/assets',
    'twa/app/src/main/res/values',
    'twa/app/src/main/res/mipmap-hdpi',
    'twa/app/src/main/res/mipmap-mdpi',
    'twa/app/src/main/res/mipmap-xhdpi',
    'twa/app/src/main/res/mipmap-xxhdpi',
    'twa/app/src/main/res/mipmap-xxxhdpi',
    'twa/gradle/wrapper',
]
for d in dirs:
    mkdirs(d)

# Copy the app HTML into assets folder so it works OFFLINE too
import shutil
if os.path.exists('index.html'):
    shutil.copy('index.html', 'twa/app/src/main/assets/index.html')
    print("Copied index.html to assets")
else:
    print("WARNING: index.html not found")

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

# app/build.gradle — zero external dependencies
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
    f.write('org.gradle.jvmargs=-Xmx2048m\n')

# AndroidManifest.xml — minimal and safe
with open('twa/app/src/main/AndroidManifest.xml', 'w') as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET"/>
  <application
    android:label="Rewire"
    android:icon="@mipmap/ic_launcher"
    android:allowBackup="true">
    <activity
      android:name=".MainActivity"
      android:exported="true"
      android:theme="@android:style/Theme.Black.NoTitleBar.Fullscreen"
      android:configChanges="orientation|screenSize">
      <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
      </intent-filter>
    </activity>
  </application>
</manifest>
''')

# MainActivity.java — loads local HTML from assets (no internet needed)
# Falls back to GitHub Pages if online
with open('twa/app/src/main/java/com/yghari/rewire/MainActivity.java', 'w') as f:
    f.write('''package com.yghari.rewire;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.Window;
import android.view.WindowManager;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );

        webView = new WebView(this);
        setContentView(webView);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);

        webView.setWebViewClient(new WebViewClient());

        // Load local HTML file from assets (works offline)
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
''')

# strings.xml
with open('twa/app/src/main/res/values/strings.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n  <string name="app_name">Rewire</string>\n</resources>\n')

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

print("Done! Project uses local assets — works offline too.")
