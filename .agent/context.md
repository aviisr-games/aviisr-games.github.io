# Public website context
Static HTML/CSS site at repository root; index.html and style.css are entry points.
Product landing, privacy and support pages inherit these rules. No package/build/test
runner is present; do not invent npm commands. Preview with python3 -m http.server 8000
and inspect changed pages at desktop/mobile sizes and Hebrew RTL where relevant.
Check relative links and assets for changed pages. Privacy statements must agree with
the corresponding app and SDK behavior; primary reviews those changes.
This repository is public. Never copy private app context, account details or internal
handoffs here. The agent toolkit is generic and may bootstrap other repositories.
