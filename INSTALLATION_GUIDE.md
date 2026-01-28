# 📁 Correct repository structure for artemkaxboy/advanced-shelly

## ✅ Your structure should look like this:

```
artemkaxboy/advanced-shelly/                    ← your GitHub repository
│
├── .github/
│   ├── workflows/
│   │   ├── hacs.yaml                          ← HACS validation
│   │   ├── validate.yaml                      ← Integration checks
│   │   └── release.yaml                       ← Release checks
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── custom_components/                          ← 🔴 CRITICAL!
│   └── advanced_shelly/                       ← 🔴 CRITICAL!
│       ├── __init__.py                        ← Core logic
│       ├── config_flow.py                     ← UI setup
│       ├── const.py                           ← Constants
│       ├── manifest.json                      ← 🔴 REQUIRED!
│       ├── services.yaml                      ← Service descriptions
│       ├── strings.json                       ← Base strings
│       └── translations/                      ← Translations
│           ├── en.json
│           └── ru.json
│
├── docs/                                      ← Documentation
│   ├── API.md
│   └── DEVELOPMENT.md
│
├── examples/                                  ← Examples
│   ├── automations.yaml
│   └── lovelace.yaml
│
├── hacs.json                                  ← 🔴 REQUIRED in root!
├── info.md                                    ← Description for HACS UI
├── README.md                                  ← Main documentation
├── CHANGELOG.md                               ← Change history
├── LICENSE                                    ← MIT License
└── .gitignore                                 ← Git ignores

RELEASES:                                       ← 🔴 REQUIRED!
└── v1.0.15                                    ← Create this release!
```

## 🎯 Checklist before adding to HACS

### ✅ Mandatory requirements:

- [ ] Repository is public
- [ ] Default branch is `main` (not `master`)
- [ ] **A release with tag `v1.0.15` exists** ← MOST IMPORTANT!
- [ ] `custom_components/advanced_shelly/` folder is in the repository root
- [ ] `manifest.json` exists
- [ ] `hacs.json` is in the repository root
- [ ] Version in `manifest.json` = "1.0.15" (no `v`)

## 🚀 Publication steps

### Step 1: Upload files to GitHub

```bash
# Extract the archive
tar -xzf advanced_shelly.tar.gz
cd advanced_shelly

# Initialize git
git init
git add .
git commit -m "Initial commit: Advanced Shelly v1.0.15"

# Connect to GitHub
git remote add origin https://github.com/artemkaxboy/advanced-shelly.git
git branch -M main
git push -u origin main
```

### Step 2: Create a release (CRITICAL!)

#### Via GitHub web UI:
1. Open https://github.com/artemkaxboy/advanced-shelly
2. Click **"Releases"** → **"Create a new release"**
3. Fill in:
   - **Choose a tag**: `v1.0.15` (click "Create new tag")
   - **Target**: `main`
   - **Release title**: `v1.0.15`
   - **Description**:
     ```
     Advanced Shelly v1.0.15

     Key features:
     - Automatic backup of scripts and configuration
     - Restore scripts and device configuration
     - Configurable backup interval and path
     - Sensors for last backup, script count, connectivity
     ```
4. Click **"Publish release"**

#### Via command line:
```bash
git tag -a v1.0.15 -m "Release v1.0.15"
git push origin v1.0.15
```
Then create the release on GitHub from this tag.

### Step 3: Add to HACS

In Home Assistant:
1. **HACS** → **Integrations** → **⋮** (three dots)
2. **Custom repositories**
3. Add:
   - **Repository**: `https://github.com/artemkaxboy/advanced-shelly`
   - **Category**: `Integration`
4. Click **"Add"**
5. Find **"Advanced Shelly"** and click **"Download"**
6. Restart Home Assistant

### Step 4: Configure the integration

1. **Settings** → **Devices & Services** → **"+ Add Integration"**
2. Find **"Advanced Shelly"**
3. Enter the device URL and options
4. Click **"Submit"**

## 📝 Important files and contents

### hacs.json (in root)
```json
{
  "name": "Advanced Shelly",
  "content_in_root": false,
  "filename": "advanced_shelly",
  "render_readme": true,
  "homeassistant": "2024.1.0",
  "zip_release": true,
  "hide_default_branch": false
}
```

### manifest.json (in custom_components/advanced_shelly/)
```json
{
  "domain": "advanced_shelly",
  "name": "Advanced Shelly",
  "codeowners": ["@artemkaxboy"],
  "config_flow": true,
  "documentation": "https://github.com/artemkaxboy/advanced-shelly",
  "integration_type": "device",
  "iot_class": "local_polling",
  "requirements": ["aiohttp>=3.8.0"],
  "version": "1.0.15"
}
```

## 🔍 Readiness check

### Check on GitHub:

1. **File structure:**
   ```
   https://github.com/artemkaxboy/advanced-shelly/tree/main/custom_components
   ```
   You should see the `advanced_shelly` folder

2. **hacs.json:**
   ```
   https://github.com/artemkaxboy/advanced-shelly/blob/main/hacs.json
   ```
   It must exist

3. **Releases:**
   ```
   https://github.com/artemkaxboy/advanced-shelly/releases
   ```
   The `v1.0.15` release should be present

### Via API:

```bash
# Check releases
curl -s https://api.github.com/repos/artemkaxboy/advanced-shelly/releases | jq '.[].tag_name'

# Should output: "v1.0.15"
```

## ❓ FAQ

**Q: Why does the tag need to be `v1.0.15` with a `v`?**  
A: That is the standard Git versioning convention. The tag should start with `v`, but the version in `manifest.json` does not include `v`.

**Q: Can I name the branch `master` instead of `main`?**  
A: Technically yes, but `main` is recommended as the new GitHub standard.

**Q: Is a release required for HACS to work?**  
A: Yes. Without a release, HACS cannot determine the version and download the integration.

**Q: What if the structure is already different?**  
A: Move files to match the structure above. The `custom_components/advanced_shelly/` folder must be in the repository root.

## 🆘 If something went wrong

1. **404 error during HACS install:**
   → Create the `v1.0.15` release (see Step 2)

2. **HACS cannot see the repository:**
   → Make sure the repository is public
   → Ensure `hacs.json` is in the root

3. **Integration does not work after install:**
   → Check logs: `tail -f /config/home-assistant.log | grep advanced_shelly`
   → Ensure the Shelly device is reachable on the network

## 📊 Visual check

After upload, on the main page https://github.com/artemkaxboy/advanced-shelly you should see:

```
artemkaxboy/advanced-shelly                    main ↓

📁 .github
📁 custom_components       ← VISIBLE!
📁 docs
📁 examples
📄 hacs.json              ← VISIBLE!
📄 README.md
📄 LICENSE

Releases: v1.0.15          ← RELEASE PRESENT!
```

---

**Follow this guide and it will work!** ✅
