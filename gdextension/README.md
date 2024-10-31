# GDExtension header and API

This repository contains the C header and API JSON for
[**Redot Engine**](https://github.com/Redot-Engine/redot-engine)'s *GDExtensions* API.

## Updating header and API

If the current branch is not up-to-date for your needs, or if you want to sync
the header and API JSON with your own modified version of Redot, here is the
update procedure used to sync this repository with upstream releases:

- Compile [Redot Engine](https://github.com/Redot-Engine/redot-engine) at the specific
  version/commit which you are using.
  * Or if you use an official release, download that version of the Redot editor.
- Use the compiled or downloaded executable to generate the `extension_api.json`
  and `gdextension_interface.h` files with:

```
redot --dump-extension-api --dump-gdextension-interface
```
