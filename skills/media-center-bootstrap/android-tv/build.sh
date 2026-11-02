#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
SDK="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
BT="$SDK/build-tools/34.0.0"
JDK="$(/usr/libexec/java_home)"
mkdir -p build/classes build/dex private
"$JDK/bin/javac" -encoding UTF-8 -source 8 -target 8 -classpath "$SDK/platforms/android-34/android.jar" -d build/classes src/local/nuvio/catalog/*.java
"$BT/d8" --lib "$SDK/platforms/android-34/android.jar" --min-api 26 --output build/dex build/classes/local/nuvio/catalog/*.class
"$BT/aapt" package -f -M AndroidManifest.xml -I "$SDK/platforms/android-34/android.jar" -A assets -S res -F build/unsigned.apk
(cd build/dex && zip -q -u ../unsigned.apk classes*.dex)
"$BT/zipalign" -f 4 build/unsigned.apk build/aligned.apk
if [ ! -f private/signing.keystore ]; then
 "$JDK/bin/keytool" -genkeypair -keystore private/signing.keystore -storepass android -keypass android -alias tvcatalog -dname 'CN=Local TV Catalog' -keyalg RSA -keysize 2048 -validity 10000
fi
"$BT/apksigner" sign --ks private/signing.keystore --ks-pass pass:android --out build/nuvio-tv-catalog.apk build/aligned.apk
"$BT/apksigner" verify build/nuvio-tv-catalog.apk
