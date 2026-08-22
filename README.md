## Description

Blueman is a GTK+ Bluetooth Manager

Blueman is designed to provide a simple yet effective means for
controlling the BlueZ API and simplifying Bluetooth tasks, such as:

* Connecting to dial-up networks
* Connecting to / Creating Bluetooth networks
* Connecting to input devices
* Connecting to audio devices
* Sending / Receiving files via OBEX
* Pairing

It is lightweight, easy to use, Python based, and GPL licensed.

## Installing

See [Dependencies.md](Dependencies.md) for a list of build and runtime dependencies.

To install a packaged release of blueman, run `./configure && make && make install`.

To generate and run a configure script from source, run `./autogen.sh`.

If you are packaging it for your distribution, please make sure to pass `--disable-schemas-compile` and run `glib-compile-schemas /datadir/glib-2.0/schemas` as part of your (un)install phase.

[![Packaging status](https://repology.org/badge/tiny-repos/blueman.svg?header=blueman%20packages)](https://repology.org/project/blueman/versions)

## Support / Troubleshooting

If you're reporting a bug, please read the [Troubleshooting page](https://github.com/blueman-project/blueman/wiki/Troubleshooting) to provide all relevant info.

Feel free to [open a GitHub issue](https://github.com/blueman-project/blueman/issues/new) to file bugs, or ask about anything you need help with.

## Contributing

Fork, make your changes, and issue a pull request. If you just want to edit a single file, GitHub will guide you through that process.

### Translate

Translations are managed on Hosted Weblate.

[![Translation status](https://hosted.weblate.org/widgets/blueman/-/svg-badge.svg)](https://hosted.weblate.org/engage/blueman/)

## License

All parts of the software are licensed under GPLv3 (or GPLv2) and allow redistribution under any later version.

## Oracle Linux RPM packages (this fork)

This fork is packaged for **Oracle Linux 8, 9 and 10** by GitHub Actions
([`.github/workflows/build.yml`](.github/workflows/build.yml)). Every push to
`main` rebuilds the RPMs from source; pushing a `v*` tag additionally attaches
all RPMs to a GitHub Release.

Because this fork requires Python >= 3.11 while OL8/OL9 only ship PyGObject
bindings for their default interpreters, the CI also builds companion packages
(`python311-pycairo`, `python311-pygobject`) and the blueman RPM on those
releases targets `/usr/bin/python3.11`.

### Install via the dnf repository (recommended)

The built RPMs are published as an **unsigned** dnf repository on GitHub Pages,
so `dnf upgrade` picks up new builds automatically:

```sh
sudo curl -fsSL -o /etc/yum.repos.d/blueman-ol.repo \
  https://raw.githubusercontent.com/saurabhahuja71/blueman/main/packaging/blueman-ol.repo
sudo dnf install -y blueman
```

Since the repository is unsigned it ships with `gpgcheck=0`.

### Install from Releases

Download the RPMs matching your release from the
[Releases](../../releases) page and install them together:

```sh
sudo dnf install -y ./blueman-*.el9.*.rpm ./python311-*.rpm   # OL9 example
```

On OL8/OL9 install the matching `python311-pycairo` / `python311-pygobject`
RPMs from the same release; they are hard requirements of the blueman package.

### CI layout

| Path | Purpose |
| --- | --- |
| `.github/workflows/build.yml` | Matrix build for OL8/OL9/OL10 in official Oracle Linux containers |
| `scripts/build-rpms.sh` | Shared build logic used inside each container |
| `packaging/blueman.spec` | RPM spec for blueman (built from this fork's source) |
| `packaging/python311-py*.spec` | Companion specs for python3.11 bindings on OL8/OL9 |
| `packaging/blueman-ol.repo` | dnf repo definition served to users |

To cut a release: bump `Version:` in `configure.ac` (and `meson.build`), then

```sh
git tag v<version> && git push origin v<version>
```
