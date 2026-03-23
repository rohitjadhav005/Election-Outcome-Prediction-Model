# APK Generation Guide

Now that the web application is a Progressive Web App (PWA), we can wrap it into a Trusted Web Activity (TWA) to generate an Android `.apk` (or `.aab` for the Play Store). The easiest and Google-recommended way to do this is using a tool called **Bubblewrap**.

## Prerequisites

Before building the APK, you need:
1.  **Node.js**: Make sure Node.js is installed on your computer. You can download it from [nodejs.org](https://nodejs.org/).
2.  **Java Development Kit (JDK) 11+**: Required for building Android apps.
3.  **Android SDK**: Required for platform tools and build tools. Bubblewrap can help install these automatically if they are missing.
4.  **A Hosted PWA**: Your application **MUST** be deployed to a live server with HTTPS (e.g., Render, Heroku) because Android requires the app to communicate securely. You cannot build an APK pointing to `localhost` or `127.0.0.1` for production use.

## Step 1: Install Bubblewrap CLI

Open your terminal or command prompt and run:

```bash
npm install -g @google/bubblewrap/cli
```

## Step 2: Initialize the Android Project

Create a new folder for your Android app source code, navigate into it, and initialize the project. Replace `https://your-live-url.com/static/manifest.json` with the actual URL where your app is hosted.

```bash
mkdir my-android-app
cd my-android-app
bubblewrap init --manifest=https://your-live-url.com/static/manifest.json
```

Bubblewrap will ask you a series of questions:
- **Web App URL**: Verify it's correct.
- **App Name / Short Name**: It should pull this from your manifest.
- **Application ID / Package Name**: Usually something like `com.yourname.electionpredictor`.
- **Display Mode**: Choose `standalone`.
- **JDK/Android SDK paths**: If it can't find them, it will ask if you want Bubblewrap to download and install them for you. Say **Yes**.

## Step 3: Generate Keystore (Signing Key)

During the `init` process, it will ask for a path to an Android keystore folder and password. This is a secure file used to sign your app.
1. Enter a path: `.\my-release-key.keystore`
2. Create passwords when prompted (keep them safe, you need them to update the app).
3. Fill out the organizational information (Name, Org, Country code, etc.).

## Step 4: Build the APK

Once the initialization is complete, you can build the APK and AAB (Android App Bundle) by running:

```bash
bubblewrap build
```

It will ask for your keystore passwords. Once finished, you will find two new files in your directory:
- `app-release-bundle.aab`: For uploading to the Google Play Store.
- `app-release-signed.apk`: For direct installation on Android devices (sideloading).

## Step 5: Digital Asset Links (Important)

If you install the APK right now, it might open with a browser address bar at the top (like a regular web page). To prove you own both the app and the website and remove the URL bar, you need to configure **Digital Asset Links**.

1.  Bubblewrap will generate a file called `assetlinks.json`.
2.  You must host this file on your live server at exactly this path:
    `https://your-live-url.com/.well-known/assetlinks.json`
3.  Once uploaded, the Android app will verify it upon launch and display your app full-screen.

---

### Alternative: Online Builders

If setting up the Android SDK and Java is too complex, you can use online PWA-to-APK services like [PWA2APK](https://www.pwa2apk.com/) or [PWABuilder](https://www.pwabuilder.com/). You just paste your live website URL, and they generate the APK for you. However, you will still need to host the `assetlinks.json` file on your server to remove the URL bar.
